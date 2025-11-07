// MediFlow Lite Service Worker
// Implements offline-first caching strategy

const CACHE_NAME = 'mediflow-v1'
const RUNTIME_CACHE = 'mediflow-runtime-v1'

// Assets to cache on install
const PRECACHE_ASSETS = [
  '/',
  '/login',
  '/dashboard',
  '/offline',
  '/manifest.json',
  '/images/logo.png',
]

// Install event - cache essential assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...')
  
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] Precaching assets')
      return cache.addAll(PRECACHE_ASSETS)
    })
  )
  
  // Force the waiting service worker to become the active service worker
  self.skipWaiting()
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...')
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
            console.log('[ServiceWorker] Deleting old cache:', cacheName)
            return caches.delete(cacheName)
          }
        })
      )
    })
  )
  
  // Take control of all pages immediately
  self.clients.claim()
})

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return
  }
  
  // API requests - Network First strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request))
    return
  }
  
  // Static assets - Cache First strategy
  if (
    request.destination === 'image' ||
    request.destination === 'font' ||
    request.destination === 'style' ||
    request.destination === 'script'
  ) {
    event.respondWith(cacheFirst(request))
    return
  }
  
  // HTML pages - Network First with cache fallback
  if (request.destination === 'document') {
    event.respondWith(networkFirst(request))
    return
  }
  
  // Default - Network First
  event.respondWith(networkFirst(request))
})

// Network First strategy - try network, fallback to cache
async function networkFirst(request) {
  const cache = await caches.open(RUNTIME_CACHE)
  
  try {
    const response = await fetch(request)
    
    // Cache successful responses
    if (response.status === 200) {
      cache.put(request, response.clone())
    }
    
    return response
  } catch (error) {
    console.log('[ServiceWorker] Network request failed, trying cache:', request.url)
    
    const cachedResponse = await cache.match(request)
    
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return offline page for navigation requests
    if (request.destination === 'document') {
      return cache.match('/offline')
    }
    
    // Return error response
    return new Response('Network error', {
      status: 408,
      headers: { 'Content-Type': 'text/plain' },
    })
  }
}

// Cache First strategy - try cache, fallback to network
async function cacheFirst(request) {
  const cache = await caches.open(RUNTIME_CACHE)
  const cachedResponse = await cache.match(request)
  
  if (cachedResponse) {
    return cachedResponse
  }
  
  try {
    const response = await fetch(request)
    
    if (response.status === 200) {
      cache.put(request, response.clone())
    }
    
    return response
  } catch (error) {
    console.log('[ServiceWorker] Cache and network failed:', request.url)
    return new Response('Resource not available', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' },
    })
  }
}

// Background sync for offline operations
self.addEventListener('sync', (event) => {
  console.log('[ServiceWorker] Background sync:', event.tag)
  
  if (event.tag === 'sync-data') {
    event.waitUntil(syncOfflineData())
  }
})

// Sync offline data when connection is restored
async function syncOfflineData() {
  try {
    // Get pending operations from IndexedDB
    const db = await openDatabase()
    const pendingOps = await getPendingOperations(db)
    
    console.log('[ServiceWorker] Syncing', pendingOps.length, 'pending operations')
    
    for (const op of pendingOps) {
      try {
        await fetch(op.url, {
          method: op.method,
          headers: op.headers,
          body: op.body,
        })
        
        // Remove from pending queue
        await removePendingOperation(db, op.id)
      } catch (error) {
        console.error('[ServiceWorker] Failed to sync operation:', error)
      }
    }
  } catch (error) {
    console.error('[ServiceWorker] Sync failed:', error)
  }
}

// Push notifications
self.addEventListener('push', (event) => {
  console.log('[ServiceWorker] Push received')
  
  const data = event.data ? event.data.json() : {}
  const title = data.title || 'MediFlow Notification'
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/images/logo.png',
    badge: '/images/badge.png',
    data: data.url || '/',
  }
  
  event.waitUntil(self.registration.showNotification(title, options))
})

// Notification click
self.addEventListener('notificationclick', (event) => {
  console.log('[ServiceWorker] Notification clicked')
  
  event.notification.close()
  
  event.waitUntil(
    clients.openWindow(event.notification.data || '/')
  )
})

// Helper functions for IndexedDB
function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('mediflow-offline', 1)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result
      if (!db.objectStoreNames.contains('pending_operations')) {
        db.createObjectStore('pending_operations', { keyPath: 'id', autoIncrement: true })
      }
    }
  })
}

function getPendingOperations(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['pending_operations'], 'readonly')
    const store = transaction.objectStore('pending_operations')
    const request = store.getAll()
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
  })
}

function removePendingOperation(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['pending_operations'], 'readwrite')
    const store = transaction.objectStore('pending_operations')
    const request = store.delete(id)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve()
  })
}

