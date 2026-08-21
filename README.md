# Linux+ XK0-006 Exam Prep

A merged rebuild of the original `linux-plus-quiz_3.html` / `linux-plus-pbq-interactive_1.html`
single-file apps: your original quiz engine, per-option answer breakdowns, and adaptive
weighting, combined with a left sidebar, dark/light theme, an objective/difficulty filter, a
readiness dashboard, last-hour cram mode, a setup-screen tracking strip (day streak / questions
practiced / needs practice), and offline install — pulled from the
[reference site](https://jasonpinca2-hub.github.io/Linux_Plus_Mobile/) — while keeping the
old "how confident are you" prompt (and its favorites feature) out, and adding a 3-way
answer-feedback toggle (check as you go / auto-reveal / hide until end) that neither original
app had.

## Run it locally

Any static file server works (the app fetches `data/*.json`, so it must be served over
`http://`, not opened as a `file://` URL):

```bash
py -3 -m http.server 8000
```

Then open `http://localhost:8000/`.

## Structure

- `index.html` / `css/theme.css` — app shell, dark (default) + light theme
- `js/storage.js` — localStorage helpers (same key names as your original apps, so your old
  exported stats JSON still imports cleanly)
- `js/adaptive.js` — weighted sampling toward missed/unseen questions + Last-Hour Cram preset
- `js/quiz.js` — MC quiz: setup, sidebar, filters, the 3 feedback modes, results, stats, readiness
- `js/pbq.js` — the 5-type interactive PBQ engine (hotspot/multidrop/tiles/scriptfill/terminal)
- `data/bank.json` — 206 MC questions: your original 185, plus 21 new ones cross-checked in from the
  VCE dump across two verification passes (images now separate files; see "Content cross-check
  findings" below)
- `data/chapters.json`, `data/domains.json` — module list and the 5 official CompTIA XK0-006 domains
- `data/pbq_scenarios.json` — 7 interactive PBQ scenarios: your original 6, plus 1 new one (SSH
  key setup) cross-checked in from the VCE dump
- `data/pbq_legacy.json` — the old image-reveal PBQ tab content, kept for reference/future merge
- `data/images/*.png` — every screenshot, extracted from base64 to real files
- `scripts/extract.py`, `scripts/backfill.py` — the one-time extraction/tagging scripts (re-run
  only if you regenerate data from a newer source HTML file)
- `manifest.json`, `sw.js` — offline install (PWA)

## Content cross-check findings

Cross-checked your question bank and PBQ scenarios against `Linux+ CompTIA XK0-006 Practice Exam
Questions.pdf` (155 Q), `XK0-006_VCEHome.pdf.pdf` (178 Q + 5 interactive items, plus embedded
screenshots), and all three "Performance Based Questions" sources (June x2 as `.pptx`, August 2026
as `.pdf`), using `scripts/parse_vce.py` / `scripts/parse_practice.py` + `scripts/dedupe_vce.py` /
`scripts/dedupe_practice.py` (text-similarity matching), `scripts/match_images.py` +
`scripts/extract_vce_images.py` for images.

**Round 1** used `difflib.quick_ratio()` (fast but approximate) and found only 1 new question.
**Round 2** re-ran the comparison with the slower, much more accurate `difflib.ratio()`, plus a
second keyword-presence check (do the correct answer's distinctive technical terms appear
*anywhere* in the bank at all), after a user-reported false-negative (a NAT/router-config question
had been wrongly matched as a duplicate of a `$PATH` question) showed the fast method wasn't precise
enough. That surfaced substantially more real gaps:

- **New questions**: **20 more genuinely new questions found and added in round 2** (bringing the
  total to **206**), on top of round 1's single addition — covering XFS repair, RAID identification,
  SSH root/key troubleshooting, `/etc/skel`, compression-ratio tradeoffs, IaC tool identification
  (Chef), and more. The Practice Exam PDF was fully re-checked too (193 parsed blocks, all matched
  as existing duplicates — no misses there). 9 VCE multi-select questions remain unaddable: no
  extractable answer key and no way to independently verify one. 2 of the added questions (a setgid
  permissions question and a GRUB/boot-recovery question) had valid options but no extractable
  answer key either — for those two only, the correct answer was independently determined from the
  options themselves rather than pulled from the source; each is flagged with a `source` field in
  `bank.json` saying so.
- **PBQ scenarios**: the three official PBQ sources (both June `.pptx` files and the August `.pdf`)
  all contain exactly the same 6 scenarios, confirmed by direct text extraction — no additional
  scenarios missed there. The VCE dump's 5 interactive items included 4 repeats and **1 genuinely
  new scenario** (SSH key setup), added as `pbq7`. One more VCE item (log-parsing drag-and-drop) had
  no extractable answer key and was skipped for the same reason as the 9 MC questions above.
- **Clearer screenshots**: automated stem-matching found 46 of your existing images had a
  same-topic candidate in the VCE PDF, but roughly half turned out to be false positives on manual
  visual review (matching generic wording, not the actual screenshot content) — automated matching
  alone isn't reliable enough to trust blindly here. **6 images were manually verified as genuine,
  identical-content matches and swapped in** for clearer VCE renders (`q54`, `q56`, `q57`, `q60`,
  `q62`, `q82`). The rest were left as-is rather than risk swapping in a wrong screenshot.

## Known gaps / next pass

- `domain` (the 5 official CompTIA domains) is mapped per-module, and `difficulty` is a
  length-based heuristic — both are best-effort editorial tags, not certified ratings. Hand-correct
  in `data/bank.json` as needed.
- `examTip` is populated for all 206 questions — concise, question-specific test-taking tips
  authored from each question's actual distinguishing concept (not copied from the reference site,
  whose version of this content is templated boilerplate).
- The remaining ~19 rejected image candidates and the 9 unresolved VCE multi-select questions could be
  revisited by hand using `scripts/pdftext/vce_images/` and `scripts/pdftext/vce_parsed.json` (both
  gitignored scratch output — re-run `scripts/parse_vce.py` etc. to regenerate).
