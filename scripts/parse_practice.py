"""Parses scripts/pdftext/practice.txt (the 155-Q Practice Exam PDF) into
structured questions. Handles both layouts PyMuPDF produced: "A." alone on a
line with the option text on the next line, and "A. text" combined on one
line (the extraction is inconsistent across the document)."""
import re
import json

SRC = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\practice.txt"
OUT = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\practice_parsed.json"

text = open(SRC, encoding="utf-8").read()
lines = [l.strip() for l in text.split("\n") if l.strip()]

q_start = [i for i, l in enumerate(lines) if re.match(r"^QUESTION \d+$", l)]
q_start.append(len(lines))

OPT_RE = re.compile(r"^([A-H])\.\s*(.*)$")

questions = []
for k in range(len(q_start) - 1):
    start, end = q_start[k], q_start[k + 1]
    block = lines[start:end]
    qnum = int(re.match(r"QUESTION (\d+)", block[0]).group(1))
    body = block[1:]

    opt_positions = []  # (index_in_body, letter, inline_text_or_None)
    for i, l in enumerate(body):
        m = OPT_RE.match(l)
        if m:
            opt_positions.append((i, m.group(1), m.group(2) or None))

    if not opt_positions:
        questions.append({"num": qnum, "raw": "\n".join(body), "unparsed": True})
        continue

    stem = " ".join(body[:opt_positions[0][0]]).strip()
    ca_idx = next((i for i, l in enumerate(body) if l.startswith("Correct Answer")), len(body))

    options = {}
    bounds = [p[0] for p in opt_positions] + [ca_idx]
    for oi, (idx, letter, inline) in enumerate(opt_positions):
        seg_end = bounds[oi + 1]
        extra = " ".join(body[idx + 1:seg_end]).strip()
        options[letter] = (inline + " " + extra).strip() if inline else extra

    answer = ""
    if ca_idx < len(body):
        m = re.match(r"Correct Answer:\s*([A-H]+)", body[ca_idx])
        if m:
            answer = m.group(1)

    questions.append({"num": qnum, "stem": stem, "options": options, "answer": answer})

json.dump(questions, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
ok = [q for q in questions if not q.get("unparsed")]
print(f"parsed {len(questions)} blocks: {len(ok)} ok, {len(questions)-len(ok)} unparsed")
no_ans = [q["num"] for q in ok if not q["answer"]]
print("no answer:", no_ans)
