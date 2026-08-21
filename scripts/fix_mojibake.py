# -*- coding: utf-8 -*-
"""
Fixes mojibake left over from the original PDF-extraction pipeline: a
unicode character (e.g. the right single quote U+2019) got UTF-8 encoded,
then those raw bytes were mis-decoded a second time as Windows-1252,
producing sequences like 'â€™' (U+00E2 U+20AC U+2122) in place of '''.

This is reversible in almost all cases: re-encoding the mangled text back to
cp1252 bytes and decoding those bytes as UTF-8 recovers the original
character. Applied only to substrings that actually contain a mojibake
marker, and only kept if the round-trip both succeeds and actually removes
the marker (never applied blindly to clean text).
"""
import json
import re

PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\bank.json"
OUT_LOG = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\scripts\mojibake_fixes.log"

MARKERS = ["â€", "\ufffd", "Ã©", "Ã¨", "Ã¢", "Â"]


def try_fix(s):
    if not any(m in s for m in MARKERS):
        return s, False
    try:
        fixed = s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s, False
    # only accept if it actually removed the mojibake markers (didn't just shuffle them)
    if any(m in fixed for m in MARKERS):
        return s, False
    return fixed, True


def walk(obj, log):
    if isinstance(obj, dict):
        return {k: walk(v, log) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(v, log) for v in obj]
    if isinstance(obj, str):
        fixed, changed = try_fix(obj)
        if changed:
            log.append((obj, fixed))
        return fixed
    return obj


def main():
    bank = json.load(open(PATH, encoding="utf-8"))
    log = []
    fixed_bank = walk(bank, log)
    json.dump(fixed_bank, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    with open(OUT_LOG, "w", encoding="utf-8") as f:
        for before, after in log:
            f.write("BEFORE: " + before[:200] + "\n")
            f.write("AFTER:  " + after[:200] + "\n\n")
    print(f"fixed {len(log)} strings; details in {OUT_LOG}")

    # report any markers that survived (unrecoverable -- e.g. real U+FFFD data loss)
    remaining_text = json.dumps(fixed_bank, ensure_ascii=False)
    remaining = [m for m in MARKERS if m in remaining_text]
    print("markers still present after fix:", remaining)
    if "\ufffd" in remaining_text:
        idx = remaining_text.find("\ufffd")
        print("U+FFFD context:", repr(remaining_text[idx-40:idx+40]))


if __name__ == "__main__":
    main()
