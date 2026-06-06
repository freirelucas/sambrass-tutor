// Service worker — network-first p/ código/dados (sempre atualiza; cache só p/ offline),
// cache-first só p/ o soundfont (grande e estático). Bump da versão limpa caches velhos.
const CACHE = 'sambrass-v4';
const SHELL = ['./', './index.html', './estudo.html', './style.css', './app.js',
  './vendor/abcjs.js', './vendor/abcjs-audio.css', './manifest.webmanifest', './icon.svg'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL).catch(() => {})).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.pathname.includes('/soundfont/')) {       // soundfont (mp3 por nota): cache-first
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {
      const cp = r.clone(); caches.open(CACHE).then(c => c.put(e.request, cp)); return r;
    })));
    return;
  }
  e.respondWith(                                     // resto: network-first
    fetch(e.request).then(r => {
      if (r && r.ok && r.type === 'basic') { const cp = r.clone(); caches.open(CACHE).then(c => c.put(e.request, cp)); }
      return r;
    }).catch(() => caches.match(e.request))
  );
});
