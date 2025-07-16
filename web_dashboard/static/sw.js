
        // MCP 監控系統 Service Worker
        const CACHE_NAME = 'mcp-monitor-v1';
        const urlsToCache = [
            '/',
            '/static/optimized.min.css',
            '/static/optimized.min.js',
            'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js'
        ];
        
        self.addEventListener('install', function(event) {
            event.waitUntil(
                caches.open(CACHE_NAME)
                    .then(function(cache) {
                        return cache.addAll(urlsToCache);
                    })
            );
        });
        
        self.addEventListener('fetch', function(event) {
            // 只快取 GET 請求
            if (event.request.method !== 'GET') return;
            
            // API 請求不快取
            if (event.request.url.includes('/api/')) return;
            
            event.respondWith(
                caches.match(event.request)
                    .then(function(response) {
                        // 如果有快取，返回快取
                        if (response) {
                            return response;
                        }
                        
                        // 否則發送網路請求
                        return fetch(event.request);
                    }
                )
            );
        });
        