/* ============================================================
   pbq.js — the real interactive PBQ engine, ported from
   linux-plus-pbq-interactive_1.html. 5 interaction types:
   hotspot (dropdown fill-in), multidrop (terminal-context dropdowns),
   tiles (click-to-build commands), scriptfill (click blank -> click
   snippet), terminal (type real commands at a fake prompt).
   ============================================================ */

const PBQ = (() => {
  let SCENARIOS = [];
  let idx = 0;
  let tileState = {};      // { tabIndex: [tokens...] }
  let activeTab = 0;
  let scriptFilled = {};   // { blankId: text }
  let scriptSelected = null;
  let termStep = 0;
  let termLog = [];
  let answered = false;
  let scriptChecked = false;

  function init(scenarios) {
    SCENARIOS = scenarios;
    document.getElementById('pbqStartBtn').addEventListener('click', () => { idx = 0; startScenario(); showScreen('pbqScreen'); });
    document.getElementById('pbqRetryBtn').addEventListener('click', () => { idx = 0; startScenario(); showScreen('pbqScreen'); });
    document.getElementById('pbqCheckBtn').addEventListener('click', checkCurrent);
    document.getElementById('pbqNextBtn').addEventListener('click', nextScenario);
    document.getElementById('pbqStatsToggleBtn').addEventListener('click', toggleStatsPanel);
    document.getElementById('pbqExitBtn').addEventListener('click', () => { renderSetupStats(); showScreen('setupScreen'); });
    document.getElementById('pbqDoneHomeBtn').addEventListener('click', () => { renderSetupStats(); showScreen('setupScreen'); });
    renderSetupStats();
  }

  function renderSetupStats() {
    document.getElementById('pbqCount').textContent = SCENARIOS.length + ' scenarios';
    const stats = loadPbqStats();
    const box = document.getElementById('pbqStatsBox');
    box.innerHTML = '';
    SCENARIOS.forEach(s => {
      const st = stats[s.id];
      const pct = st && st.attempts ? Math.round(st.correct / st.attempts * 100) : null;
      const row = document.createElement('div');
      row.className = 'scen-stat';
      row.innerHTML = `<span>${escHtml(s.title)}</span>
        <div class="ss-bar-track"><div class="ss-bar-fill" style="width:${pct || 0}%"></div></div>
        <span>${pct === null ? 'not attempted' : pct + '%'}</span>`;
      box.appendChild(row);
    });
  }

  function toggleStatsPanel() { renderSetupStats(); showScreen('setupScreen'); document.getElementById('tabPBQ').click(); }

  function resetInteractionState() {
    tileState = {}; activeTab = 0; scriptFilled = {}; scriptSelected = null; termStep = 0; termLog = []; answered = false; scriptChecked = false;
  }

  function startScenario() { resetInteractionState(); render(); }

  function scenario() { return SCENARIOS[idx]; }

  function render() {
    const s = scenario();
    document.getElementById('pbqNum').textContent = idx + 1;
    document.getElementById('pbqTotal').textContent = SCENARIOS.length;
    document.getElementById('pbqBadge').textContent = s.badge || s.type;
    document.getElementById('pbqBarFill').style.width = ((idx) / SCENARIOS.length * 100) + '%';
    document.getElementById('pbqTitle').textContent = s.title;
    document.getElementById('pbqDesc').textContent = s.desc || '';
    document.getElementById('pbqFeedback').classList.add('hidden');
    document.getElementById('pbqCheckBtn').classList.toggle('hidden', s.type === 'terminal');
    document.getElementById('pbqNextBtn').classList.add('hidden');

    const body = document.getElementById('pbqBody');
    body.innerHTML = '';
    if (s.type === 'hotspot') renderHotspot(s, body);
    else if (s.type === 'multidrop') renderMultidrop(s, body);
    else if (s.type === 'tiles') renderTiles(s, body);
    else if (s.type === 'scriptfill') renderScriptFill(s, body);
    else if (s.type === 'terminal') renderTerminal(s, body);
  }

  /* ---------- hotspot ---------- */
  function renderHotspot(s, body) {
    if (s.tasks && s.tasks.length) {
      const ul = document.createElement('div');
      ul.className = 'pbq-sub';
      ul.innerHTML = '<b>Tasks:</b><ul>' + s.tasks.map(t => `<li>${escHtml(t)}</li>`).join('') + '</ul>';
      body.appendChild(ul);
    }
    if (s.inst) { const d = document.createElement('div'); d.className = 'pbq-sub'; d.textContent = s.inst; body.appendChild(d); }
    s.cmds.forEach((cmd, ci) => {
      const line = document.createElement('div');
      line.className = 'hotspot-cmd';
      cmd.parts.forEach((part, pi) => {
        if (part.t === 'f') {
          line.appendChild(document.createTextNode(part.v + ' '));
        } else {
          const sel = document.createElement('select');
          sel.className = 'select';
          sel.style.width = 'auto';
          sel.dataset.cmd = ci; sel.dataset.part = pi;
          sel.innerHTML = s.opts.map(o => `<option value="${escHtml(o)}">${escHtml(o)}</option>`).join('');
          line.appendChild(sel);
        }
      });
      body.appendChild(line);
    });
  }
  function checkHotspot(s) {
    let ok = true;
    s.cmds.forEach((cmd, ci) => {
      cmd.parts.forEach((part, pi) => {
        if (part.t !== 's') return;
        const sel = document.querySelector(`#pbqBody select[data-cmd="${ci}"][data-part="${pi}"]`);
        const correct = sel && sel.value === part.ok;
        if (sel) sel.style.borderColor = correct ? 'var(--green)' : 'var(--red)';
        if (!correct) ok = false;
      });
    });
    return ok;
  }

  /* ---------- multidrop ---------- */
  function renderMultidrop(s, body) {
    if (s.inst) { const d = document.createElement('div'); d.className = 'pbq-sub'; d.textContent = s.inst; body.appendChild(d); }
    s.parts.forEach((part, pi) => {
      const div = document.createElement('div');
      div.className = 'md-part';
      div.innerHTML = `<div class="ctx-lbl">${escHtml(part.ctxLbl || '')}</div>
        <div class="fterm-out">${escHtml(part.ctx || '')}</div>
        <div style="margin-bottom:8px;font-weight:600;font-size:13px;">${escHtml(part.label)}: ${escHtml(part.prompt)}</div>`;
      const sel = document.createElement('select');
      sel.className = 'select';
      sel.dataset.part = pi;
      sel.innerHTML = '<option value="">— select —</option>' + part.opts.map(o => `<option value="${escHtml(o)}">${escHtml(o)}</option>`).join('');
      div.appendChild(sel);
      body.appendChild(div);
    });
  }
  function checkMultidrop(s) {
    let ok = true;
    s.parts.forEach((part, pi) => {
      const sel = document.querySelector(`#pbqBody select[data-part="${pi}"]`);
      const correct = sel && sel.value === part.ok;
      if (sel) sel.style.borderColor = correct ? 'var(--green)' : 'var(--red)';
      if (!correct) ok = false;
    });
    return ok;
  }

  /* ---------- tiles ---------- */
  function renderTiles(s, body) {
    if (s.inst) { const d = document.createElement('div'); d.className = 'pbq-sub'; d.textContent = s.inst; body.appendChild(d); }
    const tabs = document.createElement('div');
    tabs.className = 'ptabs';
    s.tabs.forEach((tab, ti) => {
      const b = document.createElement('div');
      b.className = 'ptab' + (ti === activeTab ? ' active' : '') + (tabDone(s, ti) ? ' pdone' : '');
      b.textContent = tab.name + (tabDone(s, ti) ? ' ✓' : '');
      b.addEventListener('click', () => { activeTab = ti; render(); });
      tabs.appendChild(b);
    });
    body.appendChild(tabs);

    const tab = s.tabs[activeTab];
    if (!tileState[activeTab]) tileState[activeTab] = [];
    const bld = document.createElement('div');
    bld.className = 'cmd-bld';
    bld.innerHTML = `<span style="color:var(--text-dim);font-family:var(--mono);">${escHtml(tab.pfx)}</span>`;
    tileState[activeTab].forEach((tok, ti) => {
      const chip = document.createElement('span');
      chip.className = 'cmd-tok';
      chip.textContent = tok;
      chip.addEventListener('click', () => { tileState[activeTab].splice(ti, 1); render(); });
      bld.appendChild(chip);
    });
    body.appendChild(bld);

    const bank = document.createElement('div');
    bank.className = 'sim-tabs';
    tab.toks.forEach(tok => {
      const b = document.createElement('span');
      b.className = 'sim-tab tok';
      b.textContent = tok;
      b.addEventListener('click', () => { tileState[activeTab].push(tok); render(); });
      bank.appendChild(b);
    });
    body.appendChild(bank);
  }
  function tabDone(s, ti) {
    const built = tileState[ti] || [];
    const ok = s.tabs[ti].ok;
    return built.length === ok.length && built.every((t, i) => t === ok[i]);
  }
  function checkTiles(s) { return s.tabs.every((_, ti) => tabDone(s, ti)); }

  /* ---------- scriptfill ---------- */
  function renderScriptFill(s, body) {
    if (s.inst) { const d = document.createElement('div'); d.className = 'pbq-sub'; d.textContent = s.inst; body.appendChild(d); }
    const block = document.createElement('div');
    block.className = 'scrblk';
    s.lines.forEach(line => {
      const rowDiv = document.createElement('div');
      if (line.t === 'f') {
        rowDiv.textContent = line.v || ' ';
      } else {
        line.parts.forEach(part => {
          if (part.t === 'f') {
            rowDiv.appendChild(document.createTextNode(part.v));
          } else {
            const span = document.createElement('span');
            const filled = scriptFilled[part.id];
            span.textContent = filled || '____';
            span.className = filled ? 'filled' : 'sel';
            if (scriptChecked && filled) span.classList.add(filled === part.ok ? 'cok' : 'cng');
            if (scriptSelected === part.id) span.style.outline = '2px solid var(--amber)';
            span.addEventListener('click', () => {
              if (scriptChecked) return;
              if (filled) { delete scriptFilled[part.id]; scriptSelected = part.id; }
              else { scriptSelected = part.id; }
              render();
            });
            rowDiv.appendChild(span);
          }
        });
      }
      block.appendChild(rowDiv);
    });
    body.appendChild(block);

    const bank = document.createElement('div');
    bank.className = 'snip-bank';
    s.snips.forEach(snip => {
      const b = document.createElement('span');
      b.className = 'snip';
      b.textContent = snip;
      b.addEventListener('click', () => {
        if (scriptSelected === null) return;
        scriptFilled[scriptSelected] = snip;
        scriptSelected = null;
        render();
      });
      bank.appendChild(b);
    });
    body.appendChild(bank);
  }
  function allBlanks(s) {
    const ids = [];
    s.lines.forEach(line => { if (line.t === 'r') line.parts.forEach(p => { if (p.t === 'b') ids.push(p); }); });
    return ids;
  }
  function checkScriptFill(s) {
    const blanks = allBlanks(s);
    let ok = true;
    blanks.forEach(b => { if (scriptFilled[b.id] !== b.ok) ok = false; });
    scriptChecked = true;
    render();
    return ok;
  }

  /* ---------- terminal ---------- */
  function renderTerminal(s, body) {
    if (s.inst) { const d = document.createElement('div'); d.className = 'pbq-sub'; d.textContent = s.inst; body.appendChild(d); }
    const term = document.createElement('div');
    term.className = 'fterm';
    const logHtml = termLog.map(l => `<div>${l.isCmd ? '<span style="color:var(--green)">[' + s.host + ']# </span>' : ''}${escHtml(l.text)}</div>`).join('');
    term.innerHTML = `<div id="termLogBox">${logHtml}</div>
      <div class="fterm-input"><span>[${escHtml(s.host)}]#</span><input type="text" id="termInput" autocomplete="off" placeholder="${termStep < s.steps.length ? s.steps[termStep].lbl : 'all steps complete'}"></div>`;
    body.appendChild(term);
    const input = document.getElementById('termInput');
    if (termStep >= s.steps.length) { input.disabled = true; }
    else {
      input.focus();
      input.addEventListener('keydown', e => {
        if (e.key !== 'Enter') return;
        const typed = input.value.trim();
        const step = s.steps[termStep];
        const norm = x => x.trim().replace(/\s+/g, ' ');
        const match = norm(typed) === norm(step.cmd) || (step.alt || []).some(a => norm(typed) === norm(a));
        termLog.push({ text: typed, isCmd: true });
        if (match) {
          if (step.out) termLog.push({ text: step.out, isCmd: false });
          termStep++;
          input.value = '';
          if (termStep >= s.steps.length) { answered = true; render(); showFeedback(true); }
          else render();
        } else {
          termLog.push({ text: '(command not recognized for this step — try again)', isCmd: false });
          input.value = '';
          render();
        }
      });
    }
  }

  /* ---------- check / feedback / navigation ---------- */

  /* Builds an HTML breakdown explaining not just "here's the correct
     answer" but specifically why whatever YOU picked was right or wrong --
     the same depth the MC quiz's per-option breakdown gives, adapted to
     each PBQ interaction type. Reuses the .bd-row/.bd-letter/.bd-reason
     classes from the MC quiz's breakdown styling for visual consistency. */
  function buildDetailedFeedback(s, ok) {
    if (s.type === 'hotspot') {
      const rows = [];
      s.cmds.forEach((cmd, ci) => {
        cmd.parts.forEach((part, pi) => {
          if (part.t !== 's') return;
          const sel = document.querySelector(`#pbqBody select[data-cmd="${ci}"][data-part="${pi}"]`);
          const val = sel ? sel.value : '';
          const correct = val === part.ok;
          const reason = (s.blankExpl && s.blankExpl[`${ci}-${pi}`]) || '';
          rows.push(`<div class="bd-row ${correct ? 'is-correct' : 'is-wrong'}">
            <span class="bd-letter">${correct ? '✓' : '✗'} Command ${ci + 1}:</span>
            <span>you picked "${escHtml(val)}"${correct ? '' : ` — correct: "${escHtml(part.ok)}"`}</span>
            <div class="bd-reason">${escHtml(reason)}</div></div>`);
        });
      });
      return rows.join('');
    }
    if (s.type === 'multidrop') {
      return s.parts.map((part, pi) => {
        const sel = document.querySelector(`#pbqBody select[data-part="${pi}"]`);
        const pickedValue = sel ? sel.value : '';
        const opts = Object.keys(part.optExpl || {});
        if (!opts.length) return `<div class="bd-row is-neutral"><span class="bd-letter">${escHtml(part.label)}</span><div class="bd-reason">${escHtml(part.expl || '')}</div></div>`;
        const optRows = opts.map(opt => {
          const isCorrect = opt === part.ok;
          const picked = opt === pickedValue;
          const cls = isCorrect ? 'is-correct' : (picked ? 'is-wrong' : 'is-neutral');
          const mark = isCorrect ? '✓' : (picked ? '✗' : '');
          return `<div class="bd-row ${cls}"><span class="bd-letter">${mark}</span><span>${escHtml(opt)}</span>
            <div class="bd-reason">${escHtml(part.optExpl[opt] || '')}</div></div>`;
        }).join('');
        return `<div class="pbq-label" style="margin-top:14px;">${escHtml(part.label)}</div>${optRows}`;
      }).join('');
    }
    if (s.type === 'tiles') {
      return s.tabs.map((tab, ti) => {
        const built = tileState[ti] || [];
        const done = tabDone(s, ti);
        const cmp = done ? '' : `<div class="bd-reason">You built: ${built.length ? escHtml(built.join(' ')) : '(nothing)'}<br>Correct: ${escHtml(tab.ok.join(' '))}</div>`;
        return `<div class="bd-row ${done ? 'is-correct' : 'is-wrong'}">
          <span class="bd-letter">${done ? '✓' : '✗'} ${escHtml(tab.name)}</span>
          ${cmp}<div class="bd-reason">${escHtml(tab.expl || '')}</div></div>`;
      }).join('');
    }
    if (s.type === 'scriptfill') {
      const rows = allBlanks(s).map(b => {
        const val = scriptFilled[b.id];
        const correct = val === b.ok;
        if (correct) return '';
        return `<div class="bd-row is-wrong"><span class="bd-letter">✗ Blank ${b.id + 1}:</span>
          <span>you filled "${val ? escHtml(val) : '(nothing)'}" — correct: "${escHtml(b.ok)}"</span></div>`;
      }).join('');
      return rows + `<div class="bd-row is-neutral"><div class="bd-reason">${escHtml(s.expl || '')}</div></div>`;
    }
    return `<div class="bd-row is-neutral"><div class="bd-reason">${escHtml(s.expl || '')}</div></div>`;
  }

  /* Returns a message naming the first incomplete part/tab/blank, or null
     if everything required has at least been attempted. */
  function getIncompleteMessage(s) {
    if (s.type === 'hotspot') {
      const unset = [...document.querySelectorAll('#pbqBody select')].some(sel => sel.value === s.opts[0]);
      return unset ? 'Fill in every blank before checking.' : null;
    }
    if (s.type === 'multidrop') {
      for (let pi = 0; pi < s.parts.length; pi++) {
        const sel = document.querySelector(`#pbqBody select[data-part="${pi}"]`);
        if (!sel || !sel.value) return `Answer "${s.parts[pi].label}" before checking.`;
      }
      return null;
    }
    if (s.type === 'tiles') {
      for (let ti = 0; ti < s.tabs.length; ti++) {
        if (!tileState[ti] || tileState[ti].length === 0) return `Complete the "${s.tabs[ti].name}" tab before checking.`;
      }
      return null;
    }
    if (s.type === 'scriptfill') {
      const missing = allBlanks(s).some(b => !(b.id in scriptFilled));
      return missing ? 'Fill in every blank before checking.' : null;
    }
    return null; // terminal grades itself step-by-step, no Check button shown
  }

  function checkCurrent() {
    const s = scenario();
    const incomplete = getIncompleteMessage(s);
    if (incomplete) {
      const fb = document.getElementById('pbqFeedback');
      fb.className = 'fb ng';
      fb.textContent = incomplete;
      fb.classList.remove('hidden');
      return; // not graded -- no result recorded, Next stays hidden
    }
    let ok = false;
    if (s.type === 'hotspot') ok = checkHotspot(s);
    else if (s.type === 'multidrop') ok = checkMultidrop(s);
    else if (s.type === 'tiles') ok = checkTiles(s);
    else if (s.type === 'scriptfill') ok = checkScriptFill(s);
    else if (s.type === 'terminal') { ok = termStep >= s.steps.length; }
    answered = true;
    showFeedback(ok);
  }

  function showFeedback(ok) {
    const s = scenario();
    recordPbqResult(s.id, ok);
    const fb = document.getElementById('pbqFeedback');
    fb.className = 'fb ' + (ok ? 'ok' : 'ng');
    const header = ok ? '✓ Correct.' : '✗ Not quite — see what was right or wrong below:';
    fb.innerHTML = `<div style="margin-bottom:10px;">${header}</div>` + buildDetailedFeedback(s, ok);
    fb.classList.remove('hidden');
    document.getElementById('pbqCheckBtn').classList.add('hidden');
    document.getElementById('pbqNextBtn').classList.remove('hidden');
    document.getElementById('pbqNextBtn').textContent = (idx + 1 < SCENARIOS.length) ? 'Next →' : 'Finish →';
  }

  function nextScenario() {
    if (idx + 1 < SCENARIOS.length) { idx++; startScenario(); }
    else { showScreen('pbqDoneScreen'); renderSetupStats(); }
  }

  return { init, renderSetupStats };
})();
