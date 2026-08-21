"""
One-time extraction: pulls the BANK/CHAPTERS/CHAPTER_COUNTS/PBQS consts out of
linux-plus-quiz_3.html and the SCENARIOS const out of linux-plus-pbq-interactive_1.html,
without ever loading them as raw text into an LLM context (they're megabytes of base64).

Writes:
  data/bank.json         - 185 MC questions, images replaced with relative file paths
  data/chapters.json     - module list + counts
  data/pbq_legacy.json   - the old image-reveal PBQ tab content (kept for reference/merge)
  data/pbq_scenarios.json- the real interactive PBQ engine's scenario data
  data/images/*.png      - every embedded base64 image, decoded to real files
"""
import json
import base64
import os

SRC_DIR = r"C:\Users\Jergarcia\Documents\GitHub\Linux+ Study Guide"
QUIZ_HTML = os.path.join(SRC_DIR, "linux-plus-quiz_3.html")
PBQ_HTML = os.path.join(SRC_DIR, "linux-plus-pbq-interactive_1.html")

OUT_DIR = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)


def extract_const(text, name):
    marker = f"const {name}="
    i = text.index(marker)
    start = i + len(marker)
    decoder = json.JSONDecoder()
    obj, end = decoder.raw_decode(text, start)
    return obj


def save_image(b64_str, filename):
    path = os.path.join(IMG_DIR, filename)
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64_str))
    return f"images/{filename}"


def main():
    print("Reading", QUIZ_HTML)
    with open(QUIZ_HTML, "r", encoding="utf-8") as f:
        quiz_text = f.read()
    print(f"  quiz_3.html: {len(quiz_text):,} chars")

    bank = extract_const(quiz_text, "BANK")
    chapters = extract_const(quiz_text, "CHAPTERS")
    chapter_counts = extract_const(quiz_text, "CHAPTER_COUNTS")
    pbqs = extract_const(quiz_text, "PBQS")
    print(f"  BANK: {len(bank)} questions, CHAPTERS: {len(chapters)}, PBQS: {len(pbqs)} scenarios")

    img_count = 0
    for idx, q in enumerate(bank):
        q["_idx"] = idx
        imgs = q.get("images") or []
        new_paths = []
        for n, b64 in enumerate(imgs, start=1):
            if not b64:
                continue
            fname = f"q{idx}-{n}.png"
            new_paths.append(save_image(b64, fname))
            img_count += 1
        q["images"] = new_paths
        # new fields to be backfilled in a later pass
        q.setdefault("objective", None)
        q.setdefault("difficulty", None)
        q.setdefault("examTip", None)

    print(f"  decoded {img_count} bank images")

    # legacy image-reveal PBQ tab (quiz_3.html's PBQS) - kept for reference/merge, not the
    # canonical interactive engine
    legacy_img_count = 0
    for si, scenario in enumerate(pbqs):
        for pi, part in enumerate(scenario.get("parts", [])):
            for key in ("qImg", "aImg"):
                b64 = part.get(key)
                if b64:
                    fname = f"pbq-legacy-{si}-{pi}-{key}.png"
                    part[key] = save_image(b64, fname)
                    legacy_img_count += 1
    print(f"  decoded {legacy_img_count} legacy PBQ images")

    with open(os.path.join(OUT_DIR, "bank.json"), "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "chapters.json"), "w", encoding="utf-8") as f:
        json.dump({"chapters": chapters, "counts": chapter_counts}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "pbq_legacy.json"), "w", encoding="utf-8") as f:
        json.dump(pbqs, f, ensure_ascii=False, indent=1)

    # --- second file: the real interactive PBQ engine ---
    print("Reading", PBQ_HTML)
    with open(PBQ_HTML, "r", encoding="utf-8") as f:
        pbq_text = f.read()
    scenarios = extract_const(pbq_text, "SCENARIOS")
    print(f"  SCENARIOS: {len(scenarios)} scenarios")
    with open(os.path.join(OUT_DIR, "pbq_scenarios.json"), "w", encoding="utf-8") as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=1)

    print("Done.")
    print("bank.json size:", os.path.getsize(os.path.join(OUT_DIR, "bank.json")))


if __name__ == "__main__":
    main()
