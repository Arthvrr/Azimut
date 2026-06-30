// Un Service Worker basique pour rendre l'app installable (PWA)
const CACHE_NAME = 'azimut-v1';

self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installé avec succès.');
    self.skipWaiting(); // Active le SW immédiatement
});

self.addEventListener('fetch', (event) => {
    // On laisse passer toutes les requêtes normalement, 
    // mais le smartphone est content car il y a un "fetch handler"
    event.respondWith(fetch(event.request));
});