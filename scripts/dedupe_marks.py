"""
The UI's breakdown row already prefixes each option with a computed check/cross
mark (bd-letter). The original data ALSO baked a leading unicode checkmark/cross
into every optExpl string, so every row showed the same mark twice. Strip the
redundant leading mark from stored text now that both marks are the same glyph.
"""
import json
import re

PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\bank.json"
bank = json.load(open(PATH, encoding="utf-8"))

changed = 0
for q in bank:
    for letter, txt in (q.get("optExpl") or {}).items():
        new_txt = re.sub(r"^[✓✗]\s*", "", txt)
        if new_txt != txt:
            q["optExpl"][letter] = new_txt
            changed += 1

json.dump(bank, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("stripped leading mark from", changed, "optExpl entries")
