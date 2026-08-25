/* ============================================================
   commands.js — Command Center: a searchable quick-reference of
   common XK0-006 commands (syntax, examples, exam tip). Independent
   of the quiz/PBQ question banks -- just a lookup tool.
   ============================================================ */

const Commands = (() => {
  let LIST = [];
  const expanded = new Set();

  function init(list) {
    LIST = list || [];
    document.getElementById('cmdCount').textContent = LIST.length;

    document.getElementById('commandsBtn').addEventListener('click', () => {
      render();
      showScreen('commandsScreen');
    });
    document.getElementById('commandsBackBtn').addEventListener('click', () => showScreen('setupScreen'));
    document.getElementById('cmdSearch').addEventListener('input', render);
  }

  function render() {
    const q = document.getElementById('cmdSearch').value.trim().toLowerCase();
    const matches = !q ? LIST : LIST.filter(c =>
      c.name.toLowerCase().includes(q) ||
      c.desc.toLowerCase().includes(q) ||
      c.syntax.toLowerCase().includes(q));

    const box = document.getElementById('cmdList');
    box.innerHTML = '';
    if (!matches.length) {
      box.innerHTML = '<div class="ref-empty">No commands match your search.</div>';
      return;
    }
    matches.forEach(c => {
      const row = document.createElement('div');
      row.className = 'ref-row';
      const isOpen = expanded.has(c.name);
      let html = `<div class="ref-row-head"><span class="ref-key">${escHtml(c.name)}</span><span class="ref-desc">${escHtml(c.desc)}</span></div>`;
      if (isOpen) {
        html += `<div class="ref-body">
          <div class="ref-label">Syntax</div>
          <div class="ref-code">${escHtml(c.syntax)}</div>
          <div class="ref-label">Examples</div>
          ${c.examples.map(ex => `<div class="ref-code">${escHtml(ex)}</div>`).join('')}
          <div class="exam-tip"><b>Exam tip:</b> ${escHtml(c.tip)}</div>
        </div>`;
      }
      row.innerHTML = html;
      row.addEventListener('click', () => {
        if (expanded.has(c.name)) expanded.delete(c.name); else expanded.add(c.name);
        render();
      });
      box.appendChild(row);
    });
  }

  return { init };
})();
