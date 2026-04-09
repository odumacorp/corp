/**
 * Oduma Corp Service Worker
 * Caches the app shell + user-bookmarked pages for offline reading.
 */

const CACHE_NAME = 'oduma-v1';
const OFFLINE_URL = '/offline/';

// Static assets to precache (app shell)
const PRECACHE_URLS = [
  '/',
  '/app/',
  '/offline/',
  '/static/css/design-system.css',
  '/static/css/styles.css',
];

// ── Install: pre-cache app shell ──────────────────────────────────────────────
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(PRECACHE_URLS.map(function(url) {
        return new Request(url, { credentials: 'same-origin' });
      })).catch(function() { /* ignore individual failures */ });
    })
  );
  self.skipWaiting();
});

// ── Activate: clean old caches ────────────────────────────────────────────────
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== CACHE_NAME; })
            .map(function(k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

// ── Fetch: network-first with offline fallback ────────────────────────────────
self.addEventListener('fetch', function(event) {
  var req = event.request;

  // Only handle GET same-origin requests
  if (req.method !== 'GET') return;
  if (!req.url.startsWith(self.location.origin)) return;

  // Skip Django admin, API, and WebSocket
  var path = new URL(req.url).pathname;
  if (path.startsWith('/admin') || path.startsWith('/api/') || path.startsWith('/ws/')) return;

  event.respondWith(
    fetch(req).then(function(response) {
      // Cache successful HTML responses for offline
      if (response.ok && response.headers.get('content-type') &&
          response.headers.get('content-type').includes('text/html')) {
        var clone = response.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(req, clone);
        });
      }
      return response;
    }).catch(function() {
      // Offline: serve from cache or offline page
      return caches.match(req).then(function(cached) {
        return cached || caches.match(OFFLINE_URL);
      });
    })
  );
});

// ── Message: manually cache a URL (called from "Save for offline" button) ─────
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'CACHE_URL') {
    var url = event.data.url;
    caches.open(CACHE_NAME).then(function(cache) {
      return fetch(new Request(url, { credentials: 'same-origin' })).then(function(response) {
        if (response.ok) {
          cache.put(url, response);
          event.ports[0] && event.ports[0].postMessage({ ok: true });
        }
      });
    }).catch(function() {
      event.ports[0] && event.ports[0].postMessage({ ok: false });
    });
  }
  if (event.data && event.data.type === 'REMOVE_URL') {
    caches.open(CACHE_NAME).then(function(cache) {
      cache.delete(event.data.url);
    });
  }
});
