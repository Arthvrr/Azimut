const CACHE_NAME = 'azimut-v1';

self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installé avec succès.');
    self.skipWaiting(); // Active le SW immédiatement
});

self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim()); // Prend le contrôle de la page immédiatement
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // 1. Ignorer les requêtes vers ton API externe (Render) et Supabase
    if (url.origin.includes('onrender.com') || url.origin.includes('supabase.co')) {
        return; // Laisse le navigateur gérer la requête en direct, sans intercepter
    }

    // 2. Ignorer toutes les requêtes qui ne sont pas de type "GET" (ex: les envois de formulaires POST)
    if (event.request.method !== 'GET') {
        return;
    }

    // 3. Pour le reste (HTML, CSS, images locales), on laisse passer avec un handler basique pour valider la PWA
    event.respondWith(fetch(event.request));
});