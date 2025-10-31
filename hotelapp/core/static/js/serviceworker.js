var staticCacheName = "baselink-pwa-v" + new Date().getTime();
var filesToCache = [
    '/offline/',
    '/static/css/style.css',
    '/static/css/django-pwa-app.css',
    '/static/js/app.js',
    '/static/images/icons/icon-72x72.png',
    '/static/images/icons/icon-96x96.png',
    '/static/images/icons/icon-128x128.png',
    '/static/images/icons/icon-144x144.png',
    '/static/images/icons/icon-152x152.png',
    '/static/images/icons/icon-192x192.png',
    '/static/images/icons/icon-384x384.png',
    '/static/images/icons/icon-512x512.png',
    '/static/images/icons/splash-640x1136.png',
    '/static/images/icons/splash-750x1334.png',
    '/static/images/icons/splash-1242x2208.png',
    '/static/images/icons/splash-1125x2436.png',
    '/static/images/icons/splash-828x1792.png',
    '/static/images/icons/splash-1242x2688.png',
    '/static/images/icons/splash-1536x2048.png',
    '/static/images/icons/splash-1668x2224.png',
    '/static/images/icons/splash-1668x2388.png',
    '/static/images/icons/splash-2048x2732.png',
    '/static/image/assets/BASELINK-LOGO.png',
    '/static/image/assets/BASELINK-LOGO.jpg',
    '/static/image/assets/BASELINK-FAV-1.png'
];

// Cache on install
self.addEventListener("install", event => {
    this.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                return cache.addAll(filesToCache);
            })
    )
});

// Clear cache on activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(cacheName => (cacheName.startsWith("baselink-pwa-") || cacheName.startsWith("django-pwa-")))
                    .filter(cacheName => (cacheName !== staticCacheName))
                    .map(cacheName => caches.delete(cacheName))
            );
        })
    );
});

// Serve from Cache with Network First strategy for API calls
self.addEventListener("fetch", event => {
    // Network first for API calls and dynamic content
    if (event.request.url.includes('/api/') || event.request.url.includes('/admin/') || event.request.method !== 'GET') {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Cache successful responses
                    if (response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(staticCacheName).then(cache => {
                            cache.put(event.request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // Fallback to cache
                    return caches.match(event.request).then(response => {
                        return response || caches.match('/offline/');
                    });
                })
        );
    } else {
        // Cache first for static assets
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    if (response) {
                        return response;
                    }
                    // If not in cache, fetch from network
                    return fetch(event.request)
                        .then(response => {
                            // Cache the response for future use
                            if (response.status === 200) {
                                const responseClone = response.clone();
                                caches.open(staticCacheName).then(cache => {
                                    cache.put(event.request, responseClone);
                                });
                            }
                            return response;
                        })
                        .catch(() => {
                            // If both cache and network fail, show offline page
                            if (event.request.destination === 'document') {
                                return caches.match('/offline/');
                            }
                        });
                })
        );
    }
});