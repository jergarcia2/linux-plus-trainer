import json
import os
import fitz

VCE_PDF = r"C:\Users\Jergarcia\Documents\GitHub\Linux+ Study Guide\Exam Questions\XK0-006_VCEHome.pdf.pdf"
OUT_DIR = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\vce_images"
os.makedirs(OUT_DIR, exist_ok=True)

matches = json.load(open(r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\image_matches.json", encoding="utf-8"))
doc = fitz.open(VCE_PDF)

saved = []
for m in matches:
    pno = m["vce_page"]
    best_img = None
    best_area = 0
    for p in (pno, pno + 1):
        if p >= doc.page_count:
            continue
        for img in doc[p].get_images():
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            area = pix.width * pix.height
            if area > best_area and pix.width > 150 and pix.height > 100:
                best_area = area
                best_img = (p, xref, pix)
    if best_img:
        p, xref, pix = best_img
        if pix.n - pix.alpha >= 4:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        fname = f"idx{m['bank_idx']}_vceQ{m['vce_num']}_p{p}.png"
        pix.save(os.path.join(OUT_DIR, fname))
        saved.append({"bank_idx": m["bank_idx"], "file": fname, "w": pix.width, "h": pix.height})

json.dump(saved, open(os.path.join(OUT_DIR, "_index.json"), "w", encoding="utf-8"), indent=1)
print("saved", len(saved), "images out of", len(matches), "matches")
