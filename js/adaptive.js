/* ============================================================
   adaptive.js — weighted sampling toward missed / unseen questions.
   Ported from your original quiz's calcWeight/weightedSample, with one
   deliberate tightening: a never-attempted question now always gets the
   top weight tier, so "auto force not-yet-reviewed" is guaranteed rather
   than just likely (previously an unseen question could still be out-
   weighed by a badly-missed one).
   ============================================================ */

function calcWeight(idx, perf) {
  const p = perf['q' + idx];
  if (!p || !p.attempts) return 3.0; // never attempted -> always highest priority tier
  const missRate = 1 - (p.correct / p.attempts);
  const daysSince = p.lastDate ? Math.max(0, (Date.now() - new Date(p.lastDate).getTime()) / 86400000) : 30;
  const recency = Math.min(1.6, 0.5 + daysSince / 14); // longer since last seen -> slightly higher weight
  const streakFactor = Math.max(0.35, 1 - p.streak * 0.15); // long correct streak -> dampen weight
  return Math.max(0.1, Math.min(3.0, (0.2 + missRate * 2.6) * recency * streakFactor));
}

function shuffle(a) {
  a = a.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function weightedSample(pool, n, perf, adaptive) {
  if (!adaptive) return shuffle(pool).slice(0, n);
  const remaining = pool.map(q => ({ q, w: calcWeight(q._idx, perf) }));
  const result = [];
  for (let k = 0; k < n && remaining.length > 0; k++) {
    const total = remaining.reduce((a, x) => a + x.w, 0);
    let r = Math.random() * total, cum = 0, chosen = remaining.length - 1;
    for (let i = 0; i < remaining.length; i++) {
      cum += remaining[i].w;
      if (r < cum) { chosen = i; break; }
    }
    result.push(remaining[chosen].q);
    remaining.splice(chosen, 1);
  }
  return result;
}

/* Preset used by "Last-Hour Cram": a small pool, heavily adaptive-weighted
   toward weak modules/domains and favorites, skipping questions you've
   already nailed with a streak. */
function buildCramPool(bank, perf, favs) {
  const weak = new Set();
  const chapterAcc = {};
  bank.forEach(q => {
    const p = perf['q' + q._idx];
    if (!p || !p.attempts) return;
    const c = q.chapter;
    chapterAcc[c] = chapterAcc[c] || { att: 0, cor: 0 };
    chapterAcc[c].att += p.attempts;
    chapterAcc[c].cor += p.correct;
  });
  Object.entries(chapterAcc).forEach(([c, v]) => {
    if (v.att > 0 && v.cor / v.att < 0.75) weak.add(c);
  });
  return bank.filter(q => {
    const p = perf['q' + q._idx];
    const mastered = p && p.attempts >= 2 && p.streak >= 2;
    if (mastered && !favs.has(q._idx)) return false;
    return true;
  }).sort((a, b) => {
    const score = q => (weak.has(q.chapter) ? 2 : 0) + (favs.has(q._idx) ? 1 : 0) + calcWeight(q._idx, perf);
    return score(b) - score(a);
  });
}
