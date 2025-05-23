const CACHE_NAME = 'mindy-v1';
const urlsToCache = [
'/',
'/static/js/main.js',
'/static/css/style.css',
'/static/img/icon.png',
'/static/manifest.json',
// Agrega más archivos si los necesitas
];

// Instalación del service worker
self.addEventListener('install', event => {
console.log('[SW] Instalando...');
event.waitUntil(
    caches.open(CACHE_NAME)
    .then(cache => {
        console.log('[SW] Archivos cacheados');
        return cache.addAll(urlsToCache);
    })
);
});

// Activación del service worker
self.addEventListener('activate', event => {
console.log('[SW] Activado');
event.waitUntil(
    caches.keys().then(cacheNames =>
    Promise.all(
        cacheNames.map(cache => {
        if (cache !== CACHE_NAME) {
            console.log('[SW] Eliminando caché antigua:', cache);
            return caches.delete(cache);
        }
        })
    )
    )
);
});

// Interceptar peticiones y responder desde el caché
self.addEventListener('fetch', event => {
event.respondWith(
    caches.match(event.request)
    .then(response => {
        // Si está en caché, retorna
        if (response) return response;
        // Si no, va a la red
        return fetch(event.request);
    })
);
});