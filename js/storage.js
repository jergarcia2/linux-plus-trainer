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

/* Day streak: derived from the lastDate/last fields already stored per question/
   scenario, rather than a separate counter -- consecutive calendar days (up to and
   including today, or yesterday if you haven't studied yet today) with at least
   one recorded answer. */
function activeDaySet() {
  const days = new Set();
  Object.values(loadPerf()).forEach(p => p.lastDate && days.add(p.lastDate));
  Object.values(loadPbqStats()).forEach(p => p.last && days.add(p.last));
  return days;
}
function computeDayStreak() {
  const days = activeDaySet();
  if (!days.size) return 0;
  const fmt = d => d.toISOString().slice(0, 10);
  const cursor = new Date();
  if (!days.has(fmt(cursor))) cursor.setDate(cursor.getDate() - 1);
  let streak = 0;
  while (days.has(fmt(cursor))) {
    streak++;
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}

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

/* ---- export / import: identical merge-by-attempts logic to the original apps ----
   iOS Safari (especially installed-to-home-screen standalone PWAs) largely ignores
   <a download> -- it just navigates to the blob URL instead of saving a file, which
   makes the classic download-link approach unreliable exactly where "install to
   home screen" users need it most. Try the Web Share API (native share sheet --
   Save to Files, AirDrop, Mail, etc.) first, since that's what actually works
   there; fall back to the download link for desktop/Android browsers where Web
   Share either isn't available or can't share files. */
function exportStats() {
  const payload = {
    version: 1,
    exported: new Date().toISOString(),
    data: loadPerf(),
    pbq: loadPbqStats(),
  };
  const filename = 'linux-plus-stats-' + new Date().toISOString().slice(0, 10) + '.json';
  const json = JSON.stringify(payload, null, 1);
  const file = new File([json], filename, { type: 'application/json' });

  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    navigator.share({ files: [file], title: filename }).catch(() => downloadStatsFile(json, filename));
  } else {
    downloadStatsFile(json, filename);
  }
}
function downloadStatsFile(json, filename) {
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
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
