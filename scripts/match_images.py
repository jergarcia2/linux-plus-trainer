"""
For each of our bank questions that already HAS a captured image, find its
matching VCE question (by stem similarity) and check whether that VCE
question's page contains an embedded image worth comparing.
"""
import json
import re
import difflib
import fitz

BANK = json.load(open(r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\bank.json", encoding="utf-8"))
VCE = json.load(open(r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\vce_parsed.json", encoding="utf-8"))
VCE = [q for q in VCE if not q.get("unparsed") and q.get("stem")]

VCE_PDF = r"C:\Users\Jergarcia\Documents\GitHub\Linux+ Study Guide\Exam Questions\XK0-006_VCEHome.pdf.pdf"


def norm(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


vce_norm = [(q, norm(q["stem"])) for q in VCE]

image_qs = [q for q in BANK if q.get("images")]
print("bank questions with captured images:", len(image_qs))

doc = fitz.open(VCE_PDF)
# figure out which page each QUESTION N starts on, by searching page text
question_page = {}
for pno in range(doc.page_count):
    text = doc[pno].get_text()
    for m in re.finditer(r"QUESTION (\d+)", text):
        n = int(m.group(1))
        if n not in question_page:
            question_page[n] = pno

matches = []
for bq in image_qs:
    bn = norm(bq["q"])
    best, best_ratio = None, 0
    for vq, vs in vce_norm:
        r = difflib.SequenceMatcher(None, bn, vs).quick_ratio()
        if r > best_ratio:
            best_ratio, best = r, vq
    if best and best_ratio >= 0.6:
        pno = question_page.get(best["num"])
        has_img = False
        if pno is not None:
            # check this page and next (question content can spill to next page)
            for p in (pno, pno + 1):
                if p < doc.page_count and doc[p].get_images():
                    has_img = True
                    break
        matches.append({
            "bank_idx": bq["_idx"], "bank_q": bq["q"][:80],
            "vce_num": best["num"], "ratio": round(best_ratio, 2),
            "vce_page": pno, "vce_has_image": has_img,
        })

json.dump(matches, open(r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\image_matches.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("matched:", len(matches))
print("of those, VCE page has an image:", sum(1 for m in matches if m["vce_has_image"]))
