import json
import re
import difflib

BANK = json.load(open(r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\bank.json", encoding="utf-8"))
VCE = json.load(open(r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\vce_parsed.json", encoding="utf-8"))
VCE = [q for q in VCE if not q.get("unparsed") and q["answer"] and q["type"] == "Single choice"]


def norm(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


bank_norm = [(q, norm(q["q"])) for q in BANK]

results = []
for vq in VCE:
    vs = norm(vq["stem"])
    best = None
    best_ratio = 0
    for bq, bs in bank_norm:
        r = difflib.SequenceMatcher(None, vs, bs).quick_ratio()
        if r > best_ratio:
            best_ratio = r
            best = bq
    results.append((vq, best, best_ratio))

new_ones = [r for r in results if r[2] < 0.5]
maybe = [r for r in results if 0.5 <= r[2] < 0.75]
dupes = [r for r in results if r[2] >= 0.75]

print(f"total VCE single-choice w/ answer: {len(VCE)}")
print(f"likely duplicates (>=0.75 similarity): {len(dupes)}")
print(f"maybe/borderline (0.5-0.75): {len(maybe)}")
print(f"likely NEW (< 0.5 similarity): {len(new_ones)}")

json.dump(
    {
        "new": [{"vce_num": vq["num"], "stem": vq["stem"], "ratio": r} for vq, b, r in new_ones],
        "maybe": [{"vce_num": vq["num"], "stem": vq["stem"], "closest_bank_q": b["q"][:100], "ratio": r} for vq, b, r in maybe],
    },
    open(r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\vce_dedupe.json", "w", encoding="utf-8"),
    indent=1, ensure_ascii=False,
)
