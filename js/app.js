/* ============================================================
   app.js — bootstrap: load data, wire the top bar/mode tabs/theme,
   screen navigation, PWA install + service worker registration.
   ============================================================ */

const SCREENS = ['setupScreen', 'quizScreen', 'resultsScreen', 'statsScreen', 'readinessScreen', 'commandsScreen', 'acronymsScreen', 'pbqScreen', 'pbqDoneScreen'];

function showScreen(id) {
  SCREENS.forEach(s => document.getElementById(s).classList.toggle('hidden', s !== id));
  window.scrollTo(0, 0);
  if (id === 'setupScreen' && typeof Quiz !== 'undefined' && Quiz.renderDashboard) Quiz.renderDashboard();
}

function applyTheme(theme) {
  if (theme === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
    document.getElementById('themeBtn').textContent = 'Dark';
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
    document.getElementById('themeBtn').textContent = 'Light';
  }
}

async function loadData() {
  const [bank, chaptersFile, domains, pbqScenarios, commands, acronyms] = await Promise.all([
    fetch('data/bank.json').then(r => r.json()),
    fetch('data/chapters.json').then(r => r.json()),
    fetch('data/domains.json').then(r => r.json()),
    fetch('data/pbq_scenarios.json').then(r => r.json()),
    fetch('data/commands.json').then(r => r.json()),
    fetch('data/acronyms.json').then(r => r.json()),
  ]);
  return {
    bank,
    chapters: chaptersFile.chapters,
    counts: chaptersFile.counts,
    domains,
    pbqScenarios,
    commands,
    acronyms,
  };
}

async function main() {
  const settings = loadSettings();
  applyTheme(settings.theme);
  document.getElementById('themeBtn').addEventListener('click', () => {
    const s = loadSettings();
    s.theme = s.theme === 'light' ? 'dark' : 'light';
    saveSettings(s);
    applyTheme(s.theme);
  });

  document.getElementById('tabMC').addEventListener('click', () => {
    document.getElementById('tabMC').classList.add('active');
    document.getElementById('tabPBQ').classList.remove('active');
    document.getElementById('mcSetup').classList.remove('hidden');
    document.getElementById('pbqSetup').classList.add('hidden');
  });
  document.getElementById('tabPBQ').addEventListener('click', () => {
    document.getElementById('tabPBQ').classList.add('active');
    document.getElementById('tabMC').classList.remove('active');
    document.getElementById('pbqSetup').classList.remove('hidden');
    document.getElementById('mcSetup').classList.add('hidden');
  });

  let data;
  try {
    data = await loadData();
  } catch (e) {
    document.getElementById('setupScreen').innerHTML = '<h1>Could not load question data</h1><div class="sub">Make sure this page is served over http:// (not opened directly as a file), so it can fetch data/bank.json.</div>';
    console.error(e);
    return;
  }

  Quiz.init(data);
  PBQ.init(data.pbqScenarios);
  Commands.init(data.commands);
  Acronyms.init(data.acronyms);
  showScreen('setupScreen');

  // --- PWA install prompt ---
  let deferredInstall = null;
  window.addEventListener('beforeinstallprompt', e => {
    e.preventDefault();
    deferredInstall = e;
    document.getElementById('installBtn').classList.remove('hidden');
  });
  document.getElementById('installBtn').addEventListener('click', async () => {
    if (!deferredInstall) return;
    deferredInstall.prompt();
    await deferredInstall.userChoice;
    deferredInstall = null;
    document.getElementById('installBtn').classList.add('hidden');
  });

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }
}

main();
