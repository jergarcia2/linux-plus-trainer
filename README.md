# Linux+ XK0-006 Trainer

A merged rebuild of the original `linux-plus-quiz_3.html` / `linux-plus-pbq-interactive_1.html`
single-file apps: your original quiz engine, per-option answer breakdowns, and adaptive
weighting, combined with a left sidebar, favorites, dark/light theme, an objective/difficulty
filter, a readiness dashboard, last-hour cram mode, and offline install — pulled from the
[reference site](https://jasonpinca2-hub.github.io/Linux_Plus_Mobile/) — while keeping the
old "how confident are you" prompt out and adding a 3-way answer-feedback toggle (check as you
go / auto-reveal / hide until end) that neither original app had.

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
- `data/bank.json` — 185 MC questions (extracted from your original `BANK`, images now separate files)
- `data/chapters.json`, `data/domains.json` — module list and the 5 official CompTIA XK0-006 domains
- `data/pbq_scenarios.json` — the 6 interactive PBQ scenarios
- `data/pbq_legacy.json` — the old image-reveal PBQ tab content, kept for reference/future merge
- `data/images/*.png` — every screenshot, extracted from base64 to real files
- `scripts/extract.py`, `scripts/backfill.py` — the one-time extraction/tagging scripts (re-run
  only if you regenerate data from a newer source HTML file)
- `manifest.json`, `sw.js` — offline install (PWA)

## Known gaps / next pass

- `domain` (the 5 official CompTIA domains) is mapped per-module, and `difficulty` is a
  length-based heuristic — both are best-effort editorial tags, not certified ratings. Hand-correct
  in `data/bank.json` as needed.
- Content cross-check against the CompTIA PDFs/VCE dump (new questions, clearer screenshots) is
  intentionally deferred — see the project plan for scope.
