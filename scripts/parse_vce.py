"""
Parses the VCEHome XK0-006 PDF text dump (scripts/pdftext/vce.txt) into
structured question objects, filtering out page-header/footer boilerplate.

Format per question block:
  QUESTION <n>
  <type line>
  <stem, may span multiple lines>
  A
  <option text>
  B
  <option text>
  ...
  CORRECT ANSWER <letters>
  EXPLANATION
  <explanation text, may span multiple lines, until next QUESTION marker>
"""
import re
import json

SRC = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\vce.txt"
OUT = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\pdftext\vce_parsed.json"

NOISE_SUBSTR = [
    "vcehome.com",
    "For personal study use",
    "ORDER",
    "XQ2HR2KEGAT9",
    "PREPARED FOR",
    "jason.pinca2@gmail.com",
]

PAGE_RE = re.compile(r"^Page \d+ of \d+\s*$")
TIME_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*(AM|PM)\s*$")
TYPES = {"Single choice", "Multiple choice", "Hotspot", "Drag & drop", "Lab simulation"}


def clean_lines(raw_lines):
    out = []
    for ln in raw_lines:
        s = ln.strip()
        if not s:
            continue
        if any(n in s for n in NOISE_SUBSTR):
            continue
        if PAGE_RE.match(s) or TIME_RE.match(s):
            continue
        out.append(s)
    return out


def main():
    text = open(SRC, encoding="utf-8").read()
    lines = clean_lines(text.split("\n"))

    # split into per-question chunks on "QUESTION <n>"
    q_start_idx = [i for i, l in enumerate(lines) if re.match(r"^QUESTION \d+$", l)]
    q_start_idx.append(len(lines))

    questions = []
    for k in range(len(q_start_idx) - 1):
        start, end = q_start_idx[k], q_start_idx[k + 1]
        block = lines[start:end]
        qnum = int(re.match(r"QUESTION (\d+)", block[0]).group(1))
        qtype = block[1] if block[1] in TYPES else "Single choice"
        body = block[2:]

        # find option markers (single-char lines A-H) - stem is everything before first one
        opt_idx = [i for i, l in enumerate(body) if re.match(r"^[A-H]$", l)]
        if not opt_idx:
            questions.append({"num": qnum, "type": qtype, "raw": "\n".join(body), "unparsed": True})
            continue
        stem = " ".join(body[:opt_idx[0]]).strip()

        # find CORRECT ANSWER line
        ca_idx = next((i for i, l in enumerate(body) if l.startswith("CORRECT ANSWER")), None)
        expl_idx = next((i for i, l in enumerate(body) if l == "EXPLANATION"), None)

        options = {}
        bounds = opt_idx + [ca_idx if ca_idx is not None else len(body)]
        for oi in range(len(opt_idx)):
            letter = body[opt_idx[oi]]
            seg_end = bounds[oi + 1]
            options[letter] = " ".join(body[opt_idx[oi] + 1:seg_end]).strip()

        answer = ""
        if ca_idx is not None:
            m = re.match(r"CORRECT ANSWER\s+([A-H]+)", body[ca_idx])
            if m:
                answer = m.group(1)

        explanation = ""
        if expl_idx is not None:
            explanation = "\n".join(body[expl_idx + 1:]).strip()

        questions.append({
            "num": qnum, "type": qtype, "stem": stem, "options": options,
            "answer": answer, "explanation": explanation,
        })

    json.dump(questions, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    ok = [q for q in questions if not q.get("unparsed")]
    bad = [q for q in questions if q.get("unparsed")]
    print(f"parsed {len(questions)} question blocks: {len(ok)} ok, {len(bad)} unparsed")
    if bad:
        print("unparsed nums:", [q["num"] for q in bad])
    no_answer = [q["num"] for q in ok if not q["answer"]]
    print("ok-but-no-answer:", no_answer[:20], "..." if len(no_answer) > 20 else "")


if __name__ == "__main__":
    main()
