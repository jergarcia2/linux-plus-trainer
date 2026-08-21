/* ============================================================
   storage.js — all localStorage read/write in one place.
   Key names are kept identical to the original apps so your
   existing exported stats JSON files still import cleanly.
   ============================================================ */

function escHtml(s) {
  const d = document.createElement('div');
  d.textContent = String(s == null ? '' : s);
  return d.innerHTML;
}

const PERF_KEY = 'linuxplus_perf_v1';        // MC quiz per-question perf (unchanged shape)
const PBQ_KEY = 'linuxplus_pbq_v1';          // interactive PBQ per-scenario perf (unchanged shape)
const SETTINGS_KEY = 'linuxplus_settings_v1';// NEW: theme + answer-feedback mode etc.

function loadPerf() {
  try { return JSON.parse(localStorage.getItem(PERF_KEY) || '{}'); } catch (e) { return {}; }
}
function savePerf(p) {
  try { localStorage.setItem(PERF_KEY, JSON.stringify(p)); } catch (e) {}
}
function recordAnswer(idx, correct) {
  const p = loadPerf();
  const key = 'q' + idx;
  const today = new Date().toISOString().slice(0, 10);
  if (!p[key]) p[key] = { attempts: 0, correct: 0, streak: 0, lastDate: today };
  p[key].attempts++;
  if (correct) { p[key].correct++; p[key].streak++; }
  else { p[key].streak = 0; }
  p[key].lastDate = today;
  savePerf(p);
}
function getQPerf(idx) { return loadPerf()['q' + idx] || null; }

function loadPbqStats() {
  try { return JSON.parse(localStorage.getItem(PBQ_KEY) || '{}'); } catch (e) { return {}; }
}
function savePbqStats(s) {
  try { localStorage.setItem(PBQ_KEY, JSON.stringify(s)); } catch (e) {}
}
function recordPbqResult(id, correct) {
  const s = loadPbqStats();
  const today = new Date().toISOString().slice(0, 10);
  if (!s[id]) s[id] = { attempts: 0, correct: 0, last: today };
  s[id].attempts++;
  if (correct) s[id].correct++;
  s[id].last = today;
  savePbqStats(s);
}

function loadSettings() {
  try { return Object.assign({ theme: 'dark', feedbackMode: 'checkasyougo' }, JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}')); }
  catch (e) { return { theme: 'dark', feedbackMode: 'checkasyougo' }; }
}
function saveSettings(s) {
  try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); } catch (e) {}
}

/* ---- export / import: identical merge-by-attempts logic to the original apps ---- */
function exportStats() {
  const payload = {
    version: 1,
    exported: new Date().toISOString(),
    data: loadPerf(),
    pbq: loadPbqStats(),
  };
  const blob = new Blob([JSON.stringify(payload, null, 1)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'linux-plus-stats-' + new Date().toISOString().slice(0, 10) + '.json';
  a.click();
  URL.revokeObjectURL(url);
}

function importStatsFile(file, onDone) {
  const r = new FileReader();
  r.onload = () => {
    try {
      const obj = JSON.parse(r.result);
      if (obj.data) {
        const merged = loadPerf();
        for (const [k, v] of Object.entries(obj.data)) {
          if (!merged[k] || v.attempts > merged[k].attempts) merged[k] = v;
        }
        savePerf(merged);
      }
      if (obj.pbq) {
        const mergedPbq = loadPbqStats();
        for (const [k, v] of Object.entries(obj.pbq)) {
          if (!mergedPbq[k] || v.attempts > mergedPbq[k].attempts) mergedPbq[k] = v;
        }
        savePbqStats(mergedPbq);
      }
      if (onDone) onDone(true);
    } catch (e) {
      alert('Could not read stats file.');
      if (onDone) onDone(false);
    }
  };
  r.readAsText(file);
}
