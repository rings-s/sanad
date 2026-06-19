/**
 * Sanad social sharing — framework-agnostic business logic.
 *
 * No Svelte / DOM-framework dependencies live here so the rules can be unit
 * tested in isolation (vitest `server` project). The UI layer
 * (`ShareMenu.svelte`) consumes these helpers.
 *
 * The Django backend exposes no dedicated "share URL", so the canonical link is
 * composed on the client from the current origin + the content path.
 */

const enc = encodeURIComponent;

/**
 * Compose an absolute, canonical URL for a relative content path.
 *
 * @param {string} origin - e.g. `https://sanad.app` (usually `page.url.origin`)
 * @param {string} [path] - e.g. `/content/abc123`
 * @returns {string}
 */
export function buildShareUrl(origin, path) {
	const rel = path ? (path.startsWith('/') ? path : `/${path}`) : '';
	if (!origin) return rel;
	return `${origin.replace(/\/+$/, '')}${rel}`;
}

/**
 * Web-intent URL builders, keyed by platform id. Each receives `{ url, text }`.
 * Facebook ignores arbitrary text (it scrapes Open Graph tags), so only `u` is
 * sent.
 */
/** @type {Record<string, (p: { url: string, text: string }) => string>} */
const INTENTS = {
	x: ({ url, text }) => `https://twitter.com/intent/tweet?text=${enc(text)}&url=${enc(url)}`,
	facebook: ({ url }) => `https://www.facebook.com/sharer/sharer.php?u=${enc(url)}`,
	telegram: ({ url, text }) => `https://t.me/share/url?url=${enc(url)}&text=${enc(text)}`
};

/**
 * Platform registry — the single source of truth the UI iterates over.
 *
 * `action`: `'intent'` opens a popup; `'copy'` writes to the clipboard
 * (TikTok + Copy Link, which have no reliable web-share intent).
 * `tint` / `tintDark`: brand accent applied on hover (dark variant keeps black
 * brands — X, TikTok — visible on dark surfaces).
 *
 * @typedef {Object} ShareTarget
 * @property {string} id
 * @property {'intent'|'copy'} action
 * @property {string} brand     - BrandIcon glyph name
 * @property {string} labelKey  - i18n key
 * @property {string} tint      - brand color (light theme)
 * @property {string} tintDark  - brand color (dark theme)
 */

/** @type {ShareTarget[]} */
export const SHARE_TARGETS = [
	{
		id: 'x',
		action: 'intent',
		brand: 'x',
		labelKey: 'content.shareTargets.x',
		tint: '#000000',
		tintDark: '#ffffff'
	},
	{
		id: 'facebook',
		action: 'intent',
		brand: 'facebook',
		labelKey: 'content.shareTargets.facebook',
		tint: '#1877F2',
		tintDark: '#3b82f6'
	},
	{
		id: 'telegram',
		action: 'intent',
		brand: 'telegram',
		labelKey: 'content.shareTargets.telegram',
		tint: '#229ED9',
		tintDark: '#38bdf8'
	},
	{
		id: 'tiktok',
		action: 'copy',
		brand: 'tiktok',
		labelKey: 'content.shareTargets.tiktok',
		tint: '#000000',
		tintDark: '#ffffff'
	},
	{
		id: 'link',
		action: 'copy',
		brand: 'link',
		labelKey: 'content.copyLink',
		tint: '#047857',
		tintDark: '#34d399'
	}
];

/**
 * Build the web-intent href for a platform, or `null` when none exists.
 *
 * @param {string} id
 * @param {{ url: string, text?: string }} payload
 * @returns {string|null}
 */
export function intentUrl(id, payload) {
	const fn = INTENTS[id];
	return fn ? fn({ url: payload.url, text: payload.text ?? '' }) : null;
}

/**
 * Open a centered popup for a web-intent share. Safe to call on the server
 * (no-ops without `window`). Detaches `opener` to prevent reverse-tabnabbing.
 *
 * @param {string|null} href
 * @returns {boolean} whether a window was opened
 */
export function openShareWindow(href) {
	if (typeof window === 'undefined' || !href) return false;
	const w = 600;
	const h = 640;
	const dualLeft = window.screenLeft ?? window.screenX ?? 0;
	const dualTop = window.screenTop ?? window.screenY ?? 0;
	const vw = window.innerWidth || document.documentElement.clientWidth || screen.width;
	const vh = window.innerHeight || document.documentElement.clientHeight || screen.height;
	const left = dualLeft + Math.max(0, (vw - w) / 2);
	const top = dualTop + Math.max(0, (vh - h) / 2);
	const win = window.open(
		href,
		'sanad-share',
		`noopener,noreferrer,scrollbars=yes,width=${w},height=${h},top=${top},left=${left}`
	);
	if (win) {
		win.opener = null;
		win.focus?.();
	}
	return true;
}

/**
 * Copy text to the clipboard. Prefers the async Clipboard API, with a legacy
 * `execCommand` fallback for non-secure contexts / older browsers.
 *
 * @param {string} text
 * @returns {Promise<boolean>} success
 */
export async function copyToClipboard(text) {
	if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
		try {
			await navigator.clipboard.writeText(text);
			return true;
		} catch {
			/* fall through to legacy path */
		}
	}
	if (typeof document === 'undefined') return false;
	try {
		const ta = document.createElement('textarea');
		ta.value = text;
		ta.setAttribute('readonly', '');
		ta.style.position = 'fixed';
		ta.style.top = '-9999px';
		ta.style.opacity = '0';
		document.body.appendChild(ta);
		ta.select();
		const ok = document.execCommand('copy');
		document.body.removeChild(ta);
		return ok;
	} catch {
		return false;
	}
}
