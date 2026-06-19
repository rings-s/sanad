// Static sitemap for publicly reachable routes. Content detail pages live
// behind authentication today, so only the public marketing/auth routes are
// listed. Extend this once content pages are server-rendered and public.
const PUBLIC_PATHS = ['/', '/login', '/register', '/forgot-password'];

export const prerender = true;

export function GET({ url }) {
	const origin = url.origin;
	const urls = PUBLIC_PATHS.map(
		(path) => `	<url><loc>${origin}${path}</loc><changefreq>weekly</changefreq></url>`,
	).join('\n');

	const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;

	return new Response(xml, {
		headers: { 'Content-Type': 'application/xml' },
	});
}
