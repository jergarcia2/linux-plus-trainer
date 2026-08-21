/* ============================================================
   quiz.js — multiple-choice quiz: setup, sidebar, question flow,
   the 3-way answer-feedback mode, favorites, results, stats,
   readiness dashboard and last-hour cram.
   ============================================================ */

const Quiz = (() => {
  let BANK = [], CHAPTERS = [], CHAPTER_COUNTS = {}, DOMAINS = {};
  let selectedChapters = new Set();
  let selectedDomain = 'all', selectedDifficulty = 'all', favOnly = false;
  let chosenCount = null, adaptiveMode = true, feedbackMode = 'checkasyougo';
  let session = null;

  function init(data) {
    BANK = data.bank;
    CHAPTERS = data.chapters;
    CHAPTER_COUNTS = data.counts;
    DOMAINS = data.domains;
    selectedChapters = new Set(CHAPTERS);
    feedbackMode = loadSettings().feedbackMode || 'checkasyougo';

    buildChapterList();
    buildDomainSelect();
    refreshCountUI();
    updateFavCount();

    document.getElementById('adaptiveToggle').addEventListener('click', () => {
      adaptiveMode = !adaptiveMode;
      document.getElementById('adaptiveToggle').classList.toggle('active', adaptiveMode);
      document.getElementById('adaptiveDesc').textContent = adaptiveMode
        ? "Questions you've missed more often (and questions you haven't seen yet) appear more frequently."
        : "Questions in your current selection have equal probability.";
    });
    document.getElementById('adaptiveToggle').classList.add('active');

    document.getElementById('chapterToggle').addEventListener('click', () => {
      const boxes = document.querySelectorAll('#chapterList input');
      const allChecked = [...boxes].every(b => b.checked);
      boxes.forEach(b => {
        b.checked = !allChecked;
        if (b.checked) selectedChapters.add(b.dataset.ch); else selectedChapters.delete(b.dataset.ch);
      });
      refreshCountUI();
    });

    document.getElementById('domainSelect').addEventListener('change', e => { selectedDomain = e.target.value; refreshCountUI(); });
    document.getElementById('difficultySelect').addEventListener('change', e => { selectedDifficulty = e.target.value; refreshCountUI(); });
    document.getElementById('favOnlyCheck').addEventListener('change', e => { favOnly = e.target.checked; refreshCountUI(); });

    document.querySelectorAll('.feedback-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.feedback-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        feedbackMode = tab.dataset.mode;
        const s = loadSettings(); s.feedbackMode = feedbackMode; saveSettings(s);
      });
      if (tab.dataset.mode === feedbackMode) { document.querySelectorAll('.feedback-tab').forEach(t => t.classList.remove('active')); tab.classList.add('active'); }
    });

    document.getElementById('startBtn').addEventListener('click', () => { if (chosenCount) startQuiz(currentPool(), chosenCount); });
    document.getElementById('quickTenBtn').addEventListener('click', () => { adaptiveMode = true; startQuiz(BANK, 10); });
    document.getElementById('favBtn').addEventListener('click', () => {
      const favs = loadFavs();
      const pool = BANK.filter(q => favs.has(q._idx));
      if (!pool.length) { alert('No favorites yet — star a question during a quiz to add one.'); return; }
      startQuiz(pool, pool.length);
    });
    document.getElementById('crambtn').addEventListener('click', () => {
      const pool = buildCramPool(BANK, loadPerf(), loadFavs()).slice(0, 25);
      if (!pool.length) { alert('Nothing to cram yet — answer a few questions first.'); return; }
      adaptiveMode = true;
      startQuiz(pool, pool.length, true);
    });
    document.getElementById('readinessBtn').addEventListener('click', () => { buildReadiness(); showScreen('readinessScreen'); });
    document.getElementById('readinessBackBtn').addEventListener('click', () => showScreen('setupScreen'));

    // quiz controls
    document.getElementById('submitBtn').addEventListener('click', () => gradeCurrent(session.idx));
    document.getElementById('nextBtn').addEventListener('click', onNext);
    document.getElementById('prevBtn').addEventListener('click', onPrev);
    document.getElementById('clearBtn').addEventListener('click', () => { session.selections[session.idx] = new Set(); renderQuestion(); });
    document.getElementById('gradeExamBtn').addEventListener('click', finishQuiz);
    document.getElementById('exitExamBtn').addEventListener('click', () => { showScreen('setupScreen'); });
    document.getElementById('sidebarFavToggle').addEventListener('click', () => {
      const q = session.questions[session.idx];
      toggleFav(q._idx);
      updateFavCount();
      renderQuestion();
      renderSidebar();
    });

    // results
    document.getElementById('retryBtn').addEventListener('click', () => showScreen('setupScreen'));
    document.getElementById('statsFromResultsBtn').addEventListener('click', () => { buildStats(); showScreen('statsScreen'); });

    // stats screen
    document.getElementById('statsBtn').addEventListener('click', () => { buildStats(); showScreen('statsScreen'); });
    document.getElementById('statsBackBtn').addEventListener('click', () => showScreen('setupScreen'));
    document.getElementById('clearStatsBtn').addEventListener('click', () => {
      if (confirm('Clear all MC quiz stats? This cannot be undone.')) {
        localStorage.removeItem(PERF_KEY);
        buildChapterList(); refreshCountUI(); buildStats();
      }
    });
    document.getElementById('exportStatsBtn').addEventListener('click', exportStats);
    document.getElementById('importFile').addEventListener('change', e => {
      const f = e.target.files[0];
      if (f) importStatsFile(f, () => { buildChapterList(); refreshCountUI(); buildStats(); updateFavCount(); });
    });

    // lightbox
    document.getElementById('lightbox').addEventListener('click', () => document.getElementById('lightbox').classList.add('hidden'));
  }

  function openLightbox(src) {
    document.getElementById('lightboxImg').src = src;
    document.getElementById('lightbox').classList.remove('hidden');
  }

  function currentPool() {
    return BANK.filter(q => {
      if (!selectedChapters.has(q.chapter)) return false;
      if (selectedDomain !== 'all' && q.domain !== selectedDomain) return false;
      if (selectedDifficulty !== 'all' && q.difficulty !== selectedDifficulty) return false;
      if (favOnly && !loadFavs().has(q._idx)) return false;
      return true;
    });
  }

  function perfColor(pct) { return pct < 50 ? 'var(--red)' : pct < 80 ? 'var(--amber)' : 'var(--green)'; }

  function buildChapterList() {
    const box = document.getElementById('chapterList');
    box.innerHTML = '';
    const perf = loadPerf();
    CHAPTERS.forEach(ch => {
      const chQ = BANK.filter(q => q.chapter === ch);
      let att = 0, cor = 0;
      chQ.forEach(q => { const p = perf['q' + q._idx]; if (p && p.attempts > 0) { att += p.attempts; cor += p.correct; } });
      const pct = att > 0 ? Math.round(cor / att * 100) : null;
      const row = document.createElement('label');
      row.className = 'chapter-row';
      row.innerHTML = `<input type="checkbox" data-ch="${escHtml(ch)}" ${selectedChapters.has(ch) ? 'checked' : ''}>
        <span class="ch-name">${escHtml(ch)}</span>
        <span class="ch-pct" style="${pct !== null ? 'color:' + perfColor(pct) : ''}">${pct !== null ? pct + '%' : '—'}</span>`;
      row.querySelector('input').addEventListener('change', e => {
        if (e.target.checked) selectedChapters.add(ch); else selectedChapters.delete(ch);
        refreshCountUI();
      });
      box.appendChild(row);
    });
  }

  function buildDomainSelect() {
    const sel = document.getElementById('domainSelect');
    Object.values(DOMAINS).forEach(name => {
      const opt = document.createElement('option');
      opt.value = name; opt.textContent = name;
      sel.appendChild(opt);
    });
  }

  function refreshCountUI() {
    const pool = currentPool();
    const total = pool.length;
    document.getElementById('bankTotal').textContent = total;
    document.getElementById('bankAll').textContent = BANK.length;
    const grid = document.getElementById('countGrid');
    grid.innerHTML = '';
    chosenCount = null;
    document.getElementById('startBtn').disabled = true;
    [...new Set([10, 25, 50, 75, 100, 150].filter(n => n < total).concat([total]))].filter(n => n > 0).forEach(n => {
      const b = document.createElement('button');
      b.className = 'count-btn';
      b.textContent = (n === total) ? 'All (' + n + ')' : n;
      b.addEventListener('click', () => {
        document.querySelectorAll('.count-btn').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        chosenCount = n;
        document.getElementById('startBtn').disabled = false;
      });
      grid.appendChild(b);
    });
  }

  function updateFavCount() {
    document.getElementById('favCount').textContent = loadFavs().size;
  }

  function startQuiz(pool, n, preOrdered) {
    const perf = loadPerf();
    const questions = preOrdered ? pool.slice(0, n) : weightedSample(pool, n, perf, adaptiveMode);
    session = {
      questions,
      idx: 0,
      selections: questions.map(() => new Set()),
      checked: questions.map(() => false),
      correct: questions.map(() => null),
      feedbackMode,
    };
    showScreen('quizScreen');
    renderSidebar();
    renderQuestion();
  }

  function gradeCurrent(idx) {
    if (session.checked[idx]) return;
    const q = session.questions[idx];
    const correctSet = new Set(q.answer.split(''));
    const userSet = session.selections[idx];
    const isCorrect = userSet.size === correctSet.size && [...userSet].every(x => correctSet.has(x));
    session.checked[idx] = true;
    session.correct[idx] = isCorrect;
    recordAnswer(q._idx, isCorrect);
    renderQuestion();
    renderSidebar();
  }

  function onNext() {
    if (session.idx + 1 < session.questions.length) { session.idx++; renderQuestion(); renderSidebar(); }
    else finishQuiz();
  }
  function onPrev() {
    if (session.idx > 0) { session.idx--; renderQuestion(); renderSidebar(); }
  }
  function jumpTo(i) { session.idx = i; renderQuestion(); renderSidebar(); }

  function renderSidebar() {
    const answered = session.selections.filter(s => s.size > 0).length;
    document.getElementById('sbAnswered').textContent = answered;
    document.getElementById('sbTotal').textContent = session.questions.length;
    document.getElementById('barFill').style.width = (answered / session.questions.length * 100) + '%';
    const checkedIdx = session.checked.map((c, i) => c ? i : -1).filter(i => i >= 0);
    const correctCount = checkedIdx.filter(i => session.correct[i]).length;
    document.getElementById('sbScore').textContent = correctCount;
    document.getElementById('sbAccuracy').textContent = checkedIdx.length ? Math.round(correctCount / checkedIdx.length * 100) + '%' : '—';

    const favs = loadFavs();
    const grid = document.getElementById('sbJumpGrid');
    grid.innerHTML = '';
    session.questions.forEach((q, i) => {
      const b = document.createElement('button');
      b.textContent = i + 1;
      if (i === session.idx) b.classList.add('current');
      if (session.selections[i].size > 0) b.classList.add('done');
      if (session.checked[i]) b.classList.add(session.correct[i] ? 'correct' : 'wrong');
      if (favs.has(q._idx)) b.classList.add('fav');
      b.addEventListener('click', () => jumpTo(i));
      grid.appendChild(b);
    });
  }

  function perfChipFor(idx) {
    const p = getQPerf(idx);
    if (!p || !p.attempts) return '<span class="chip">never seen</span>';
    const pct = Math.round(p.correct / p.attempts * 100);
    const label = pct < 50 ? 'struggling' : pct < 80 ? 'mixed' : 'solid';
    return `<span class="chip" style="color:${perfColor(pct)}">${label} · ${pct}% (${p.attempts}x)</span>`;
  }

  function renderQuestion() {
    const q = session.questions[session.idx];
    document.getElementById('qChapter').textContent = q.chapter;
    document.getElementById('qDomain').textContent = q.domain || '';
    document.getElementById('qDifficulty').textContent = q.difficulty || '';
    document.getElementById('perfChip').innerHTML = perfChipFor(q._idx);
    document.getElementById('qText').textContent = q.q;

    const favs = loadFavs();
    const favBtn = document.getElementById('sidebarFavToggle');
    favBtn.textContent = favs.has(q._idx) ? '★ Favorited' : '☆ Save to Favorites';
    favBtn.classList.toggle('primary', favs.has(q._idx));

    const imgNote = document.getElementById('imgNote');
    imgNote.classList.toggle('hidden', !(q.hasImage && (!q.images || q.images.length === 0)));
    const shotBox = document.getElementById('qShotBox');
    shotBox.innerHTML = '';
    (q.images || []).forEach(src => {
      const div = document.createElement('div');
      div.className = 'qshot';
      div.innerHTML = `<img src="${src}" alt="question screenshot">`;
      div.addEventListener('click', () => openLightbox(src));
      shotBox.appendChild(div);
    });

    const multi = q.answer.length > 1;
    document.getElementById('multiHint').classList.toggle('hidden', !multi);

    const checked = session.checked[session.idx];
    const userSet = session.selections[session.idx];
    const correctSet = new Set(q.answer.split(''));

    const optsBox = document.getElementById('optsBox');
    optsBox.innerHTML = '';
    Object.entries(q.options).forEach(([letter, text]) => {
      const div = document.createElement('div');
      div.className = 'opt';
      if (userSet.has(letter)) div.classList.add('selected');
      if (checked) {
        div.classList.add('disabled');
        if (correctSet.has(letter)) div.classList.add('correct');
        else if (userSet.has(letter)) div.classList.add('incorrect');
      }
      div.innerHTML = `<span class="optkey">${letter}.</span><span>${escHtml(text)}</span>`;
      div.addEventListener('click', () => onOptionClick(letter, multi));
      optsBox.appendChild(div);
    });

    const breakdown = document.getElementById('breakdown');
    if (checked && session.feedbackMode !== 'hidetilend') {
      breakdown.classList.remove('hidden');
      buildBreakdown(q, correctSet, userSet);
    } else {
      breakdown.classList.add('hidden');
    }

    document.getElementById('prevBtn').disabled = session.idx === 0;
    const submitBtn = document.getElementById('submitBtn');
    const nextBtn = document.getElementById('nextBtn');
    if (session.feedbackMode === 'hidetilend') {
      submitBtn.classList.add('hidden');
      nextBtn.classList.remove('hidden');
      nextBtn.textContent = (session.idx + 1 < session.questions.length) ? 'Next →' : 'Grade Exam →';
    } else if (checked) {
      submitBtn.classList.add('hidden');
      nextBtn.classList.remove('hidden');
      nextBtn.textContent = (session.idx + 1 < session.questions.length) ? 'Next →' : 'See Results →';
    } else {
      submitBtn.classList.remove('hidden');
      submitBtn.disabled = userSet.size === 0;
      nextBtn.classList.add('hidden');
    }
  }

  function onOptionClick(letter, multi) {
    const idx = session.idx;
    if (session.checked[idx]) return;
    const sel = session.selections[idx];
    if (multi) {
      if (sel.has(letter)) sel.delete(letter); else sel.add(letter);
    } else {
      sel.clear(); sel.add(letter);
    }
    if (session.feedbackMode === 'autoreveal' && sel.size > 0) {
      renderQuestion();
      gradeCurrent(idx);
      return;
    }
    renderQuestion();
    renderSidebar();
  }

  function buildBreakdown(q, correctSet, userSet) {
    const rows = document.getElementById('breakdownRows');
    rows.innerHTML = '';
    const tipBox = document.getElementById('examTipBox');
    if (q.examTip) {
      tipBox.classList.remove('hidden');
      tipBox.innerHTML = `<b>Exam tip:</b> ${escHtml(q.examTip)}`;
    } else {
      tipBox.classList.add('hidden');
    }
    Object.entries(q.options).forEach(([letter, text]) => {
      const isCorrect = correctSet.has(letter);
      const picked = userSet.has(letter);
      const div = document.createElement('div');
      div.className = 'bd-row ' + (isCorrect ? 'is-correct' : (picked ? 'is-wrong' : 'is-neutral'));
      const mark = isCorrect ? '✅' : (picked ? '❌' : '');
      const reason = (q.optExpl && q.optExpl[letter]) || '';
      div.innerHTML = `<span class="bd-letter">${mark} ${letter}.</span><span>${escHtml(text)}</span><div class="bd-reason">${escHtml(reason)}</div>`;
      rows.appendChild(div);
    });
  }

  function finishQuiz() {
    session.questions.forEach((q, i) => { if (!session.checked[i]) gradeSilently(i); });
    showResults();
  }
  function gradeSilently(idx) {
    const q = session.questions[idx];
    const correctSet = new Set(q.answer.split(''));
    const userSet = session.selections[idx];
    const isCorrect = userSet.size > 0 && userSet.size === correctSet.size && [...userSet].every(x => correctSet.has(x));
    session.checked[idx] = true;
    session.correct[idx] = isCorrect;
    recordAnswer(q._idx, isCorrect);
  }

  function showResults() {
    const total = session.questions.length;
    const correct = session.correct.filter(Boolean).length;
    const pct = Math.round(correct / total * 100);
    document.getElementById('finalPct').textContent = pct + '%';
    document.getElementById('finalLabel').textContent = `${correct} / ${total} correct`;
    document.getElementById('finalBar').style.width = pct + '%';

    const byChapter = {};
    session.questions.forEach((q, i) => {
      byChapter[q.chapter] = byChapter[q.chapter] || { att: 0, cor: 0 };
      byChapter[q.chapter].att++;
      if (session.correct[i]) byChapter[q.chapter].cor++;
    });
    const weakest = Object.entries(byChapter).map(([c, v]) => [c, v.cor / v.att]).sort((a, b) => a[1] - b[1])[0];
    document.getElementById('sessionInsight').textContent = weakest
      ? `Weakest area this session: ${weakest[0]} (${Math.round(weakest[1] * 100)}%). Adaptive mode will surface more of these next time.`
      : '';

    const favs = loadFavs();
    const box = document.getElementById('reviewBox');
    box.innerHTML = '';
    session.questions.forEach((q, i) => {
      const correctSet = new Set(q.answer.split(''));
      const userSet = session.selections[i];
      const div = document.createElement('div');
      div.className = 'review-item ' + (session.correct[i] ? 'right' : 'wrong');
      const optsHtml = Object.entries(q.options).map(([letter, text]) => {
        const isCorrect = correctSet.has(letter), picked = userSet.has(letter);
        const cls = isCorrect ? 'is-correct' : (picked ? 'is-wrong' : 'is-neutral');
        const mark = isCorrect ? '✅' : (picked ? '❌' : '');
        const reason = (q.optExpl && q.optExpl[letter]) || '';
        return `<div class="bd-row ${cls}"><span class="bd-letter">${mark} ${letter}.</span><span>${escHtml(text)}</span><div class="bd-reason">${escHtml(reason)}</div></div>`;
      }).join('');
      const tip = q.examTip ? `<div class="exam-tip"><b>Exam tip:</b> ${escHtml(q.examTip)}</div>` : '';
      div.innerHTML = `<span class="rv-fav ${favs.has(q._idx) ? 'active' : ''}" data-idx="${q._idx}">${favs.has(q._idx) ? '★' : '☆'}</span>
        <div class="rv-q">Q${i + 1}. ${escHtml(q.q)}</div>${optsHtml}${tip}`;
      div.querySelector('.rv-fav').addEventListener('click', e => {
        toggleFav(q._idx);
        e.target.classList.toggle('active');
        e.target.textContent = e.target.classList.contains('active') ? '★' : '☆';
        updateFavCount();
      });
      box.appendChild(div);
    });

    showScreen('resultsScreen');
  }

  function buildStats() {
    const perf = loadPerf();
    const entries = Object.values(perf);
    const totalAttempts = entries.reduce((a, e) => a + e.attempts, 0);
    const totalCorrect = entries.reduce((a, e) => a + e.correct, 0);
    const seen = entries.length;
    document.getElementById('statCards').innerHTML = `
      <div class="stat-card"><div class="stat-n">${seen}/${BANK.length}</div><div class="stat-l">Questions seen</div></div>
      <div class="stat-card"><div class="stat-n">${totalAttempts}</div><div class="stat-l">Total attempts</div></div>
      <div class="stat-card"><div class="stat-n">${totalAttempts ? Math.round(totalCorrect / totalAttempts * 100) : 0}%</div><div class="stat-l">Overall accuracy</div></div>
      <div class="stat-card"><div class="stat-n">${loadFavs().size}</div><div class="stat-l">Favorites</div></div>`;

    const chBox = document.getElementById('chapterStats');
    chBox.innerHTML = '';
    const chData = CHAPTERS.map(ch => {
      const chQ = BANK.filter(q => q.chapter === ch);
      let att = 0, cor = 0;
      chQ.forEach(q => { const p = perf['q' + q._idx]; if (p) { att += p.attempts; cor += p.correct; } });
      return { ch, att, cor, total: chQ.length, seen: chQ.filter(q => perf['q' + q._idx]).length, pct: att ? cor / att * 100 : -1 };
    }).sort((a, b) => a.pct - b.pct);
    chData.forEach(d => {
      const el = document.createElement('div');
      el.className = 'ch-stat';
      const pctLabel = d.pct < 0 ? 'not started' : Math.round(d.pct) + '%';
      el.innerHTML = `<div class="ch-stat-row"><span>${escHtml(d.ch)}</span><span>${pctLabel}</span></div>
        <div class="cs-bar-track"><div class="cs-bar-fill" style="width:${Math.max(0, d.pct)}%;background:${perfColor(d.pct < 0 ? 0 : d.pct)}"></div></div>
        <div class="ch-stat-row seen"><span>${d.seen}/${d.total} seen</span></div>`;
      chBox.appendChild(el);
    });

    const domBox = document.getElementById('domainStats');
    domBox.innerHTML = '';
    Object.values(DOMAINS).forEach(dom => {
      const domQ = BANK.filter(q => q.domain === dom);
      let att = 0, cor = 0;
      domQ.forEach(q => { const p = perf['q' + q._idx]; if (p) { att += p.attempts; cor += p.correct; } });
      const pct = att ? cor / att * 100 : -1;
      const el = document.createElement('div');
      el.className = 'ch-stat';
      el.innerHTML = `<div class="ch-stat-row"><span>${escHtml(dom)}</span><span>${pct < 0 ? 'not started' : Math.round(pct) + '%'}</span></div>
        <div class="cs-bar-track"><div class="cs-bar-fill" style="width:${Math.max(0, pct)}%;background:${perfColor(pct < 0 ? 0 : pct)}"></div></div>`;
      domBox.appendChild(el);
    });
  }

  function buildReadiness() {
    const perf = loadPerf();
    const entries = Object.entries(perf);
    const scored = entries.filter(([, v]) => v.attempts > 0);
    const overall = scored.length ? Math.round(scored.reduce((a, [, v]) => a + v.correct / v.attempts, 0) / scored.length * 100) : 0;
    const coverage = Math.round(scored.length / BANK.length * 100);
    const hero = document.getElementById('readinessHero');
    const readyLabel = overall >= 80 && coverage >= 70 ? 'Exam ready' : overall >= 60 ? 'Getting there' : 'Building baseline';
    hero.innerHTML = `<div class="pct">${overall}%</div><div class="lbl">${readyLabel}</div><div class="sub">${scored.length} of ${BANK.length} questions scored (${coverage}% coverage)</div>`;

    const modBox = document.getElementById('readinessModules');
    modBox.innerHTML = '';
    CHAPTERS.forEach(ch => {
      const chQ = BANK.filter(q => q.chapter === ch);
      let att = 0, cor = 0;
      chQ.forEach(q => { const p = perf['q' + q._idx]; if (p) { att += p.attempts; cor += p.correct; } });
      const pct = att ? Math.round(cor / att * 100) : -1;
      const el = document.createElement('div');
      el.className = 'ch-stat';
      el.innerHTML = `<div class="ch-stat-row"><span>${escHtml(ch)}</span><span>${pct < 0 ? 'not started' : pct + '%'}</span></div>
        <div class="cs-bar-track"><div class="cs-bar-fill" style="width:${Math.max(0, pct)}%;background:${perfColor(pct < 0 ? 0 : pct)}"></div></div>`;
      modBox.appendChild(el);
    });

    const domBox = document.getElementById('readinessDomains');
    domBox.innerHTML = '';
    Object.values(DOMAINS).forEach(dom => {
      const domQ = BANK.filter(q => q.domain === dom);
      let att = 0, cor = 0;
      domQ.forEach(q => { const p = perf['q' + q._idx]; if (p) { att += p.attempts; cor += p.correct; } });
      const pct = att ? Math.round(cor / att * 100) : -1;
      const el = document.createElement('div');
      el.className = 'ch-stat';
      el.innerHTML = `<div class="ch-stat-row"><span>${escHtml(dom)}</span><span>${pct < 0 ? 'not started' : pct + '%'}</span></div>
        <div class="cs-bar-track"><div class="cs-bar-fill" style="width:${Math.max(0, pct)}%;background:${perfColor(pct < 0 ? 0 : pct)}"></div></div>`;
      domBox.appendChild(el);
    });

    const weakest = CHAPTERS.map(ch => {
      const chQ = BANK.filter(q => q.chapter === ch);
      let att = 0, cor = 0;
      chQ.forEach(q => { const p = perf['q' + q._idx]; if (p) { att += p.attempts; cor += p.correct; } });
      return { ch, pct: att ? cor / att : -1, att };
    }).filter(d => d.att > 0).sort((a, b) => a.pct - b.pct)[0];
    const next = document.getElementById('readinessNextStep');
    if (scored.length < 20) {
      next.innerHTML = `<b>Recommended next step</b>Complete a Quick 10 or a 25-question quiz with every answer checked, so there's enough data for a real baseline.`;
    } else if (weakest) {
      next.innerHTML = `<b>Recommended next step</b>Focus a session on <i>${escHtml(weakest.ch)}</i> (${Math.round(weakest.pct * 100)}% so far) — try Last-Hour Cram, which weights toward it automatically.`;
    } else {
      next.innerHTML = `<b>Recommended next step</b>Keep practicing with Adaptive Mode on — it will keep surfacing whatever you're weakest on.`;
    }
  }

  return { init, currentPool, buildChapterList, refreshCountUI, buildStats, updateFavCount };
})();
