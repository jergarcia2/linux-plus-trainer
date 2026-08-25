/* ============================================================
   acronyms.js — Acronym Glossary: a searchable quick-reference of
   XK0-006 acronyms/abbreviations and what they stand for. Same
   "reference lookup" pattern as commands.js, but simpler rows --
   no expand/collapse needed since each entry is already short.
   ============================================================ */

const Acronyms = (() => {
  let LIST = [];

  function init(list) {
    LIST = list || [];
    document.getElementById('acrCount').textContent = LIST.length;

    document.getElementById('acronymsBtn').addEventListener('click', () => {
      render();
      showScreen('acronymsScreen');
    });
    document.getElementById('acronymsBackBtn').addEventListener('click', () => showScreen('setupScreen'));
    document.getElementById('acrSearch').addEventListener('input', render);
  }

  function render() {
    const q = document.getElementById('acrSearch').value.trim().toLowerCase();
    const matches = !q ? LIST : LIST.filter(a =>
      a.abbr.toLowerCase().includes(q) ||
      a.full.toLowerCase().includes(q) ||
      a.desc.toLowerCase().includes(q));

    const box = document.getElementById('acrList');
    box.innerHTML = '';
    if (!matches.length) {
      box.innerHTML = '<div class="ref-empty">No acronyms match your search.</div>';
      return;
    }
    matches.forEach(a => {
      const row = document.createElement('div');
      row.className = 'ref-row ref-static';
      row.innerHTML = `<div class="ref-row-head"><span class="ref-key">${escHtml(a.abbr)}</span><span class="ref-desc"><b>${escHtml(a.full)}</b> — ${escHtml(a.desc)}</span></div>`;
      box.appendChild(row);
    });
  }

  return { init };
})();
