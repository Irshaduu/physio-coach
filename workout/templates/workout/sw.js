// Bump the version whenever a cached file changes, so installed phones drop their old copies.
const CACHE_NAME = 'physiocoach-cache-v3';
const ASSETS = [
  '/',
  '/static/workout/css/player.css',
  '/static/workout/css/analysis.css',
  '/static/workout/js/player.js',
  '/static/workout/manifest.json',
  '/static/workout/images/Icon-new.png'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

// Delete the app's older caches and take over open pages at once. The voice clips live in
// player.js's own cache ('therapist-audio-v1'), which is kept.
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((k) => k !== CACHE_NAME && (k.startsWith('therapist-cache') || k.startsWith('physiocoach-cache')))
          .map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Pages come from the network, so nobody is shown an old copy; the cache is the offline fallback.
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request).then((r) => r || caches.match('/')))
    );
    return;
  }
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
