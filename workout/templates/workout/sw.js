const CACHE_NAME = 'therapist-cache-v1';
const ASSETS = [
  '/',
  '/static/workout/css/player.css',
  '/static/workout/css/analysis.css',
  '/static/workout/js/player.js',
  '/static/workout/manifest.json',
  '/static/workout/images/Icon-new.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
