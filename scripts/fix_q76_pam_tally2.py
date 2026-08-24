# -*- coding: utf-8 -*-
# Fixes question 76 (PAM dictionary-attack question):
#  1. options.A was corrupted mojibake -- a Cyrillic look-alike "u" (U+0443)
#     that had itself been double-UTF8-encoded into "pam_tallÑƒ2". Both the
#     per-option explanation and the exam tip already correctly say
#     "pam_tally2" (Latin y) -- only the option label itself was wrong.
#  2. options.D was a plain typo, "pam_idap" (missing the l), while its own
#     optExpl already correctly reads "pam_ldap integrates with LDAP...".
#  3. The legacy (unused, dead) top-level `explanation` field also said
#     "pam_tally" instead of "pam_tally2" -- fixed for data consistency,
#     though the app doesn't render this field anywhere.
import json

PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\bank.json"
data = json.load(open(PATH, encoding="utf-8"))
q = next(x for x in data if x.get("_idx") == 76)

assert q["options"]["A"] == "pam_tall\u00d1\u01922", "options.A doesn't match expected corrupted value -- aborting"
assert q["options"]["D"] == "pam_idap", "options.D doesn't match expected typo -- aborting"

q["options"]["A"] = "pam_tally2"
q["options"]["D"] = "pam_ldap"
q["explanation"] = q["explanation"].replace("pam_tally tracks", "pam_tally2 tracks")

json.dump(data, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("fixed q76: options.A -> pam_tally2, options.D -> pam_ldap")
