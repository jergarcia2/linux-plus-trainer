import json
import re
import difflib

BANK = json.load(open(r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\bank.json", encoding="utf-8"))
PRACTICE = json.load(open(r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\practice_parsed.json", encoding="utf-8"))
PRACTICE = [q for q in PRACTICE if not q.get("unparsed") and q.get("stem")]


def norm(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


bank_norm = [(q, norm(q["q"])) for q in BANK]

results = []
for pq in PRACTICE:
    ps = norm(pq["stem"])
    best, best_ratio = None, 0
    for bq, bs in bank_norm:
        r = difflib.SequenceMatcher(None, ps, bs).quick_ratio()
        if r > best_ratio:
            best_ratio, best = r, bq
    results.append((pq, best, best_ratio))

new_ones = [r for r in results if r[2] < 0.5]
maybe = [r for r in results if 0.5 <= r[2] < 0.75]
dupes = [r for r in results if r[2] >= 0.75]

print(f"total practice.txt questions checked: {len(PRACTICE)}")
print(f"likely duplicates (>=0.75): {len(dupes)}")
print(f"borderline (0.5-0.75): {len(maybe)}")
print(f"likely NEW (<0.5): {len(new_ones)}")

json.dump(
    {
        "new": [{"num": pq["num"], "stem": pq["stem"], "answer": pq.get("answer"), "options": pq.get("options"), "ratio": r} for pq, b, r in new_ones],
        "maybe": [{"num": pq["num"], "stem": pq["stem"], "answer": pq.get("answer"), "closest_bank_idx": b["_idx"], "closest_bank_q": b["q"][:100], "ratio": r} for pq, b, r in maybe],
    },
    open(r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\practice_dedupe.json", "w", encoding="utf-8"),
    indent=1, ensure_ascii=False,
)
