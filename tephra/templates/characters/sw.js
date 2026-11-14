/* Offline read-only shell. Network first for sheet pages and static files; the last good copy is the
   fallback when offline. Never caches POSTs, HTMX partials or redirects (locked sheets); locking a
   character or logging out forgets every cached sheet. */
const CACHE = "tephra-sheets-v1";
const STATIC = "{{ static_prefix|escapejs }}";
const SHEET = /\/c\/\d+\/$/;

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (req.method !== "GET") {
    if (/\/(lock|logout)\/$/.test(url.pathname)) e.waitUntil(caches.delete(CACHE));
    return;
  }
  const isSheet = req.mode === "navigate" && SHEET.test(url.pathname) && !url.searchParams.has("print");
  const isStatic = url.pathname.startsWith(STATIC);
  if (!isSheet && !isStatic) return;
  e.respondWith(fetch(req).then((resp) => {
    const key = isSheet ? url.origin + url.pathname : req;
    if (resp.ok && !resp.redirected && resp.type === "basic") {
      const copy = resp.clone();
      e.waitUntil(caches.open(CACHE).then((c) => c.put(key, copy)));
    } else if (isSheet) {
      e.waitUntil(caches.open(CACHE).then((c) => c.delete(key)));
    }
    return resp;
  }).catch(() => caches.match(isSheet ? url.origin + url.pathname : req).then((r) => r || Response.error())));
});
