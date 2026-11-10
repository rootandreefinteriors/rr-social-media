"""check_pauses.py (run in an episode folder after prep_audio) — find every inserted pause in voice_edit.wav and report how
loud the voice is right before and after it. A loud edge (> -32 dB) means the pause cut into speech: an audible skip."""
import wave, numpy as np, sys
with wave.open("voice_edit.wav") as w:
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
z = np.abs(x) < 1e-6
i, n, bad = 0, len(x), 0
while i < n:
    if z[i]:
        j = i
        while j < n and z[j]:
            j += 1
        if (j - i) / sr >= 0.2:
            pre = x[max(0, i - int(0.03 * sr)):i]; post = x[j:j + int(0.03 * sr)]
            db = lambda s: 20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-9)
            a, b = db(pre), db(post)
            flag = "  <-- SPEECH CUT" if max(a, b) > -32 else ""
            bad += bool(flag)
            print(f"{i/sr+2:6.2f}s (+{(j-i)/sr:.2f}s)  before {a:6.1f} dB  after {b:6.1f} dB{flag}")
        i = j
    else:
        i += 1
print("speech cuts:", bad)
