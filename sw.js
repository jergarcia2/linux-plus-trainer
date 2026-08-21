/* Cache-first offline support. App shell + data are precached on install;
   images are cached the first time they're viewed (runtime cache), so a
   full quiz run works offline after you've opened it online once. Bump
   CACHE_NAME whenever shell files change to force a refresh. */

const CACHE_NAME = 'linuxplus-examprep-v3';
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

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting())
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

  event.respondWith(
    caches.match(req).then(cached => {
      if (cached) return cached;
      return fetch(req).then(res => {
        if (res && res.status === 200 && res.type === 'basic') {
          const copy = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
        }
        return res;
      }).catch(() => cached);
    })
  );
});
