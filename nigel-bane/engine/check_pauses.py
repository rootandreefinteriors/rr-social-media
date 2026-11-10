"""check_pauses.py (run in an episode folder after prep_audio) — check every inserted pause in voice_edit.wav for the two
ways a pause can wreck a line:
  SPEECH CUT  the voice is loud right at an edge of the pause (> -32 dB): it was dropped inside a word (audible skip)
  STRAY BIT   a scrap of sound shorter than 0.15 s sits alone right after the pause: a word's tail (a "p" release, a
              breath) got split off and comes back like an echo ("sit up... (up)", D32 2026-11-10)
It must end with "problems: 0"."""
import wave
import numpy as np

with wave.open("voice_edit.wav") as w:
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
hop = int(0.01 * sr)
fr = 20 * np.log10(np.sqrt(np.mean(x[:len(x) // hop * hop].reshape(-1, hop) ** 2, axis=1)) + 1e-9)
db = lambda s: 20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-9)
z = np.abs(x) < 1e-6
i, n, bad = 0, len(x), 0
while i < n:
    if not z[i]:
        i += 1
        continue
    j = i
    while j < n and z[j]:
        j += 1
    if (j - i) / sr >= 0.2:
        a, b = db(x[max(0, i - int(0.03 * sr)):i]), db(x[j:j + int(0.03 * sr)])
        flags = []
        if max(a, b) > -32:
            flags.append("SPEECH CUT")
        k = j // hop   # what follows the pause: a short burst, then silence again?
        while k < len(fr) and fr[k] < -45 and k < j // hop + 30:
            k += 1
        on = k
        while k < len(fr) and fr[k] >= -45:
            k += 1
        quiet = k
        while k < len(fr) and fr[k] < -45 and k - quiet < 8:
            k += 1
        if on < len(fr) and on - j // hop < 30 and 0 < quiet - on < 15 and k - quiet >= 8:
            flags.append(f"STRAY BIT {(quiet - on) * 0.01:.2f}s")
        bad += bool(flags)
        print(f"{i/sr+2:6.2f}s (+{(j-i)/sr:.2f}s)  before {a:6.1f} dB  after {b:6.1f} dB" + ("  <-- " + ", ".join(flags) if flags else ""))
    i = j
print("problems:", bad)
