"""Tighten the long pauses in the raw ElevenLabs take and remap word timings to match."""
import json, wave, sys
import numpy as np

SR = 44100
DEFAULT_GAP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.55
# gaps that keep more air: key = text of the word that FOLLOWS the gap
import sys
SPECIAL_GAPS = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}

with wave.open("voice_raw.wav") as w:
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

words = [w for w in json.load(open("words_raw.json"))["words"]
         if w["type"] == "word" and not w["text"].startswith("[")]

# silence detection on 10ms hops
hop = SR // 100
rms = np.sqrt(np.convolve(x**2, np.ones(hop) / hop, mode="same")[::hop] + 1e-12)
silent = 20 * np.log10(rms) < -40
runs, i = [], 0
while i < len(silent):
    if silent[i]:
        j = i
        while j < len(silent) and silent[j]:
            j += 1
        if (j - i) * 0.01 >= 0.3 and i > 0 and j < len(silent):
            runs.append((i * 0.01, j * 0.01))
        i = j
    else:
        i += 1

def next_word_after(t):
    for w in words:
        if w["start"] >= t - 0.6 and w["end"] > t:
            return w["text"]
    return None

# build kept segments
cuts = []  # (orig_cut_start, orig_cut_end)
for a, b in runs:
    target = DEFAULT_GAP
    nw = next_word_after(b)
    if nw in SPECIAL_GAPS:
        target = SPECIAL_GAPS[nw]
    if b - a > target:
        mid = (a + b) / 2
        cuts.append((mid - (b - a - target) / 2, mid + (b - a - target) / 2))

def remap(t):
    shift = 0.0
    for a, b in cuts:
        if t >= b:
            shift += b - a
        elif t > a:
            return a - shift
    return t - shift

pieces, prev = [], 0
fade = int(0.01 * SR)
for a, b in cuts:
    seg = x[prev:int(a * SR)].copy()
    pieces.append(seg)
    prev = int(b * SR)
pieces.append(x[prev:])
for p in pieces:  # tiny fades so cuts (in silence anyway) never click
    if len(p) > 2 * fade:
        p[:fade] *= np.linspace(0, 1, fade)
        p[-fade:] *= np.linspace(1, 0, fade)
y = np.concatenate(pieces)
out = [{"text": w["text"], "start": round(remap(w["start"]), 3), "end": round(remap(w["end"]), 3)} for w in words]
# optional: insert extra silence after given words (midway into the following gap) {"word.": seconds}
INSERT = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
def quietest(t0, t1):
    """Where to drop a pause in [t0, t1] of the edit so far: the middle of the longest stretch of real silence, so a
    word's tail stays attached to it. Transcript timings can be off by a few hundred ms (D32, 2026-11-10: a pause at
    their midpoint cut words, and one at the single quietest instant split "u-p" so the "p" came back as an echo)."""
    hop = int(0.01 * SR)
    a, b = max(0, int(t0 * SR)), min(len(y), int(t1 * SR))
    if b - a < 2 * hop:
        return (t0 + t1) / 2
    seg = y[a:b]
    fr = 20 * np.log10(np.sqrt(np.mean(seg[:len(seg) // hop * hop].reshape(-1, hop) ** 2, axis=1)) + 1e-9)
    best, run, start = (0, 0), 0, 0
    for k, v in enumerate(fr):
        if v < -55:
            if run == 0:
                start = k
            run += 1
            if run > best[1]:
                best = (start, run)
        else:
            run = 0
    if best[1] >= 8:   # >= 80 ms of silence: drop it in the middle
        return (a + (best[0] + best[1] / 2) * hop) / SR
    return (a + int(np.argmin(fr)) * hop + hop // 2) / SR

for i, w in enumerate(out):
    if w["text"] in INSERT and i + 1 < len(out):
        at = quietest(w["end"] - 0.3, out[i + 1]["start"] + 0.4)
        k = int(at * SR)
        y = np.concatenate([y[:k], np.zeros(int(INSERT[w["text"]] * SR), np.float32), y[k:]])
        for v in out[i + 1:]:
            v["start"] = round(v["start"] + INSERT[w["text"]], 3); v["end"] = round(v["end"] + INSERT[w["text"]], 3)
with wave.open("voice_edit.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())

json.dump(out, open("words.json", "w"), indent=1)
print(f"raw {len(x)/SR:.2f}s -> edit {len(y)/SR:.2f}s, {len(cuts)} gaps tightened, {len(INSERT)} inserts")
for w in out:
    print(f'{w["start"]:6.2f} {w["end"]:6.2f} {w["text"]}')
