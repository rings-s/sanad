// Same-origin reverse proxy: the browser calls `/api/*` on the frontend origin,
// and this hook forwards it to the real backend. This makes the backend's
// HttpOnly refresh cookie FIRST-PARTY (set on the frontend's own domain), so it
// survives browser restarts — fixing the "must log in again" issue caused by
// third-party cookie blocking. It also removes the need for CORS / SameSite=None.
//
// Set API_PROXY_TARGET to the backend origin (e.g. https://sanad-api.fly.dev).
// Defaults to the local backend for development.
const TARGET = (process.env.API_PROXY_TARGET || 'http://localhost:8000').replace(/\/$/, '');

// Headers we must not forward verbatim (hop-by-hop or recomputed by fetch).
const STRIP_REQUEST = ['host', 'connection', 'content-length', 'transfer-encoding'];
// Response headers tied to the original (compressed) body, which undici has
// already decoded by the time we read `res.body`.
const STRIP_RESPONSE = ['content-encoding', 'content-length', 'transfer-encoding', 'connection'];

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
	if (event.url.pathname.startsWith('/api/')) {
		const target = TARGET + event.url.pathname + event.url.search;

		const headers = new Headers(event.request.headers);
		for (const h of STRIP_REQUEST) headers.delete(h);

		/** @type {RequestInit} */
		const init = { method: event.request.method, headers };
		if (event.request.method !== 'GET' && event.request.method !== 'HEAD') {
			// Buffer the body so fetch sets a correct Content-Length. Streaming with
			// duplex:'half' produced a chunked request the backend read as empty.
			init.body = await event.request.arrayBuffer();
		}

		const backendRes = await fetch(target, init);

		const resHeaders = new Headers();
		backendRes.headers.forEach((value, key) => {
			if (!STRIP_RESPONSE.includes(key.toLowerCase()) && key.toLowerCase() !== 'set-cookie') {
				resHeaders.set(key, value);
			}
		});
		// Preserve EACH Set-Cookie separately (undici joins them into one string
		// via .get('set-cookie'), which corrupts the cookies).
		for (const cookie of backendRes.headers.getSetCookie?.() ?? []) {
			resHeaders.append('set-cookie', cookie);
		}

		return new Response(backendRes.body, {
			status: backendRes.status,
			statusText: backendRes.statusText,
			headers: resHeaders,
		});
	}

	return resolve(event);
}
