const CACHE_NAME = 'lg-remote-v5';
const ASSETS = [
    '/',
    '/index.html',
    '/style.css',
    '/app.js',
    '/manifest.json'
];

self.addEventListener('install', event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME)
        .then(cache => cache.addAll(ASSETS))
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        Promise.all([
            self.clients.claim(),
            caches.keys().then(keys => {
                return Promise.all(
                    keys.map(key => {
                        if (key !== CACHE_NAME) {
                            return caches.delete(key);
                        }
                    })
                );
            })
        ])
    );
});

self.addEventListener('fetch', event => {
    // Only cache GET requests (don't cache POST to /api)
    if (event.request.method === 'GET' && !event.request.url.includes('/api/')) {
        event.respondWith(
            caches.match(event.request)
            .then(response => response || fetch(event.request))
        );
    }
});
