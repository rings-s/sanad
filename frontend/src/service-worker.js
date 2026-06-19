/// <reference types="@sveltejs/kit" />
import { build, files, version } from '$service-worker';

const CACHE = `sanad-cache-${version}`;
// Pre-cache the app shell (build artifacts) and static files.
const ASSETS = [...build, ...files];

self.addEventListener('install', (event) => {
	event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
	self.skipWaiting();
});

self.addEventListener('activate', (event) => {
	event.waitUntil(
		caches.keys().then((keys) =>
			Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))),
		),
	);
	self.clients.claim();
});

self.addEventListener('fetch', (event) => {
	const { request } = event;
	if (request.method !== 'GET') return;

	const url = new URL(request.url);

	// Never cache API calls — always go to the network.
	if (url.pathname.startsWith('/api/')) return;

	// Cache-first for hashed build assets and static files.
	if (ASSETS.includes(url.pathname)) {
		event.respondWith(
			caches.open(CACHE).then(async (cache) => {
				const cached = await cache.match(request);
				return cached || fetch(request);
			}),
		);
		return;
	}

	// Network-first for everything else, falling back to cache when offline.
	event.respondWith(
		(async () => {
			try {
				const response = await fetch(request);
				if (response.ok && url.origin === self.location.origin) {
					const cache = await caches.open(CACHE);
					cache.put(request, response.clone());
				}
				return response;
			} catch {
				const cached = await caches.match(request);
				if (cached) return cached;
				throw new Error('Network error and no cache available.');
			}
		})(),
	);
});
