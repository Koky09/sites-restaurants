// Работа без сети: страница — сначала из сети, остальное — из кэша. Версия меняется при каждой сборке.
const V = 'ryumochnaya_kulturno_korotko-ee12d94a57';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', '../../book.js', '../../app.js'];
self.addEventListener('install', (e) => { e.waitUntil(caches.open(V).then((c) => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', (e) => { e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== V).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', (e) => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin) return; // сервер брони и шрифты — напрямую
  if (r.mode === 'navigate') {
    e.respondWith(fetch(r).then((res) => { caches.open(V).then((c) => c.put('index.html', res.clone())); return res; }).catch(() => caches.match('index.html')));
    return;
  }
  e.respondWith(caches.match(r).then((hit) => hit || fetch(r).then((res) => { if (res.ok) { const cl = res.clone(); caches.open(V).then((c) => c.put(r, cl)); } return res; })));
});
