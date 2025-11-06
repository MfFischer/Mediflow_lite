/**
 * Service Worker for MediFlow Lite
 * 
 * Provides offline-first capabilities with intelligent caching.
 */

const CACHE_NAME = 'mediflow-v1';
const API_CACHE_NAME = 'mediflow-api-v1';

// Assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/patients',
  '/appointments',
  '/prescriptions',
  '/lab-results',
  '/offline',
  '/manifest.json'
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/v1/patients',
  '/api/v1/appointments',
  '/api/v1/prescriptions',
  '/api/v1/lab-results'
];

/**
 * Install event - cache static assets
 */
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME && name !== API_CACHE_NAME)
            .map((name) => caches.delete(name))
        );
      })
      .then(() => self.clients.claim())
  );
});

/**
 * Fetch event - implement caching strategies
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // API requests - Network First, fallback to Cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request, API_CACHE_NAME));
    return;
  }

  // Static assets - Cache First, fallback to Network
  event.respondWith(cacheFirstStrategy(request, CACHE_NAME));
});

/**
 * Cache First Strategy
 * Try cache first, fallback to network
 */
async function cacheFirstStrategy(request, cacheName) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error('Fetch failed:', error);
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      const offlineResponse = await caches.match('/offline');
      if (offlineResponse) {
        return offlineResponse;
      }
    }

    throw error;
  }
}

/**
 * Network First Strategy
 * Try network first, fallback to cache
 */
async function networkFirstStrategy(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error('Network request failed, trying cache:', error);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    throw error;
  }
}

/**
 * Background sync event
 */
self.addEventListener('sync', (event) => {
  console.log('Background sync triggered:', event.tag);
  
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

/**
 * Sync data with server
 */
async function syncData() {
  try {
    // This will be handled by the SyncManager in the app
    console.log('Background sync: Data sync requested');
    
    // Notify all clients to sync
    const clients = await self.clients.matchAll();
    clients.forEach((client) => {
      client.postMessage({
        type: 'SYNC_REQUESTED',
        timestamp: new Date().toISOString()
      });
    });
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

/**
 * Push notification event
 */
self.addEventListener('push', (event) => {
  console.log('Push notification received');
  
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'MediFlow Notification';
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    data: data.data || {},
    actions: data.actions || []
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

/**
 * Notification click event
 */
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event.notification.tag);
  
  event.notification.close();

  event.waitUntil(
    clients.openWindow(event.notification.data.url || '/')
  );
});

/**
 * Message event - handle messages from clients
 */
self.addEventListener('message', (event) => {
  console.log('Service Worker received message:', event.data);
  
  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((name) => caches.delete(name))
        );
      })
    );
  }
});

