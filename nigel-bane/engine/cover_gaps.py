"""Cover-frame helper: list the moments with NO caption on screen (mirrors the engine's caption timing).
Usage (in an episode folder): python ../../engine/cover_gaps.py words.json  -> pick a frame in a free window where
he is in a distinctive pose with eyes open, check it from the MP4, pass its time in ms as thumbnailOffset."""
import json, sys
ws = json.load(open(sys.argv[1]))
for w in ws: w["start"] += 2; w["end"] += 2
chunks, cur = [], []
for w in ws:
    if cur and len(" ".join(x["text"] for x in cur + [w])) > 20: chunks.append(cur); cur = []
    cur.append(w)
    if w["text"][-1] in ".,?!": chunks.append(cur); cur = []
if cur: chunks.append(cur)
prev = 0
for i, ch in enumerate(chunks):
    s = ch[0]["start"] - 0.05; e = ch[-1]["end"] + 0.45
    if i + 1 < len(chunks):
        e = min(e if chunks[i + 1][0]["start"] - ch[-1]["end"] >= 0.9 else chunks[i + 1][0]["start"] - 0.02, chunks[i + 1][0]["start"] - 0.02)
    e = max(e, s + 0.4)
    if s - prev > 0.3: print(f"  free {prev:.2f}-{s:.2f}  (before: {' '.join(x['text'] for x in ch)[:30]})")
    prev = e
print(f"  end {prev:.2f}")
