/* Two-tier offline strategy:
   - App shell (html/css/js/manifest/data JSON) is NETWORK-FIRST: whenever
     you're online you always get the current code, and it's cached as a
     fallback for offline use. This avoids the classic "it's fixed on the
     server but my browser won't stop showing the old version" problem --
     the previous cache-first approach for these files meant every code
     fix required users to manually clear/reinstall to ever see it.
   - Images are CACHE-FIRST: they don't change once written, so once
     viewed they're available offline and never re-fetched needlessly.
   Bump CACHE_NAME whenever you want to force a clean slate for everyone. */

const CACHE_NAME = 'linuxplus-examprep-v5';
const SHELL = [
  './',
  './index.html',
  './css/theme.css',
  './js/storage.js',
  './js/adaptive.js',
  './js/quiz.js',
  './js/pbq.js',
  './js/app.js',
  './manifest.json',
  './data/bank.json',
  './data/chapters.json',
  './data/domains.json',
  './data/pbq_scenarios.json',
];

function isImageRequest(url) {
  return /\/data\/images\//.test(url);
}

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      Promise.all(SHELL.map(url =>
        fetch(url, { cache: 'no-store' }).then(res => cache.put(url, res))
      ))
    ).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;

  if (isImageRequest(req.url)) {
    // cache-first: images are static once written
    event.respondWith(
      caches.match(req).then(cached => cached || fetch(req).then(res => {
        if (res && res.status === 200 && res.type === 'basic') {
          const copy = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
        }
        return res;
      }))
    );
    return;
  }

  // network-first for everything else (the app shell + data): always try
  // to get the current version when online, cache it for offline fallback.
  // cache: 'no-store' bypasses the browser's own HTTP cache too, not just
  // this service worker's cache -- otherwise a Cache-Control header from
  // the host can still serve a stale response even though we're on the
  // "network-first" path.
  event.respondWith(
    fetch(req, { cache: 'no-store' }).then(res => {
      if (res && res.status === 200 && res.type === 'basic') {
        const copy = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
      }
      return res;
    }).catch(() => caches.match(req))
  );
});
