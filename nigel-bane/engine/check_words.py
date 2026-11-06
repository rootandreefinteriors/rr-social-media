"""Catch the #1 timing bug: a T("word") / TE("word") lookup that silently grabs the FIRST of several occurrences.
Usage (in an episode folder): python ../../engine/check_words.py   -> lists every looked-up word that occurs more than
once in words.json, with the occurrence the script uses and the times of all of them. Check each one by eye."""
import json, re
words = json.load(open("words.json"))
texts = [w["text"].lower().strip(".,?!") for w in words]
src = open("episode.py", encoding="utf-8").read()
seen = set()
for m in re.finditer(r'\bTE?\("([^"]+)"(?:,\s*(\d+))?\)', src):
    word, n = m.group(1).lower(), int(m.group(2) or 1)
    if (word, n) in seen:
        continue
    seen.add((word, n))
    times = [round(w["start"] + 2.0, 2) for w, t in zip(words, texts) if t == word]
    if len(times) > 1:
        print(f"{word!r}: uses #{n} of {len(times)} at {times}")
print("done")
