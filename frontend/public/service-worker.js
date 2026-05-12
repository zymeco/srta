// SRTA Service Worker v3
// 핵심 정책:
//  - index.html (네비게이션 요청): network-first  → 새 빌드 즉시 반영
//  - hash 파일명을 가진 /assets/*: cache-first  → 캐시 안전, 빠른 로딩
//  - 그 외 정적 자산: stale-while-revalidate
//  - /api, /health: 캐시 안 함 (항상 라이브)

const VERSION = 'srta-v3';
const RUNTIME = `${VERSION}-runtime`;

self.addEventListener('install', (e) => {
  // 새 SW가 들어오면 즉시 활성화
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    (async () => {
      // 이전 버전 캐시 모두 제거
      const keys = await caches.keys();
      await Promise.all(
        keys.filter((k) => !k.startsWith(VERSION)).map((k) => caches.delete(k))
      );
      await self.clients.claim();
    })()
  );
});

self.addEventListener('message', (e) => {
  if (e.data === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // API / health: 캐시 안 함
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/health')) {
    return;
  }

  // 다른 출처: 캐시 안 함
  if (url.origin !== self.location.origin) return;

  // 네비게이션 (HTML 문서): network-first
  const isNavigation =
    req.mode === 'navigate' ||
    req.destination === 'document' ||
    url.pathname === '/' ||
    url.pathname.startsWith('/index.html');

  if (isNavigation) {
    e.respondWith(
      (async () => {
        try {
          const fresh = await fetch(req);
          // 성공하면 캐시 갱신
          const cache = await caches.open(RUNTIME);
          cache.put('/', fresh.clone()).catch(() => {});
          return fresh;
        } catch (_) {
          // 오프라인 시 캐시 fallback
          const cache = await caches.open(RUNTIME);
          return (await cache.match('/')) || Response.error();
        }
      })()
    );
    return;
  }

  // 해시 파일명 자산 (/assets/index-XXXX.js, .css): cache-first
  if (url.pathname.startsWith('/assets/')) {
    e.respondWith(
      (async () => {
        const cache = await caches.open(RUNTIME);
        const cached = await cache.match(req);
        if (cached) return cached;
        const res = await fetch(req);
        if (res.status === 200) cache.put(req, res.clone()).catch(() => {});
        return res;
      })()
    );
    return;
  }

  // 그 외 정적 자산 (아이콘 등): stale-while-revalidate
  e.respondWith(
    (async () => {
      const cache = await caches.open(RUNTIME);
      const cached = await cache.match(req);
      const fetchedPromise = fetch(req)
        .then((res) => {
          if (res.status === 200) cache.put(req, res.clone()).catch(() => {});
          return res;
        })
        .catch(() => cached);
      return cached || fetchedPromise;
    })()
  );
});
