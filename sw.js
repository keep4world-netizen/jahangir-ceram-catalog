const C = 'jc-catalog-v1';
const SHELL = ['/', '/index.html', '/data/catalog-data.js', '/manifest.webmanifest', '/icon-192.png', '/icon-512.png',
  '/assets/images/cover.webp', '/assets/images/jahangir-ceram-logo.webp', '/assets/images/sialk-ceram-logo.webp'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(C).then(c => Promise.allSettled(SHELL.map(u => c.add(u)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

function save(req, res) {
  if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); caches.open(C).then(c => c.put(req, copy)); }
  return res;
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const same = url.origin === location.origin;
  const isImage = req.destination === 'image' || /\.(webp|png|jpe?g|gif|svg|avif)$/i.test(url.pathname);

  if (same && !isImage) {
    // Pages and data: internet first (so updates arrive), saved copy when offline
    e.respondWith(fetch(req, { cache: 'no-cache' }).then(res => save(req, res))
      .catch(() => caches.match(req).then(hit => hit || caches.match('/index.html'))));
  } else {
    // Images and fonts: show saved copy instantly, refresh it quietly in the background
    e.respondWith(caches.match(req).then(hit => {
      const net = fetch(req).then(res => save(req, res)).catch(() => hit);
      return hit || net;
    }));
  }
});
