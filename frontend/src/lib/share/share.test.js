import { describe, it, expect, vi, afterEach } from 'vitest';
import {
	buildShareUrl,
	intentUrl,
	SHARE_TARGETS,
	openShareWindow,
	copyToClipboard
} from './share.js';

describe('buildShareUrl', () => {
	it('joins origin and path', () => {
		expect(buildShareUrl('https://sanad.app', '/content/abc')).toBe(
			'https://sanad.app/content/abc'
		);
	});

	it('strips a trailing slash from origin', () => {
		expect(buildShareUrl('https://sanad.app/', '/content/abc')).toBe(
			'https://sanad.app/content/abc'
		);
	});

	it('prefixes a missing leading slash on path', () => {
		expect(buildShareUrl('https://sanad.app', 'content/abc')).toBe('https://sanad.app/content/abc');
	});

	it('returns the relative path when origin is absent (SSR)', () => {
		expect(buildShareUrl('', '/content/abc')).toBe('/content/abc');
	});
});

describe('intentUrl', () => {
	const payload = { url: 'https://sanad.app/content/abc?x=1', text: 'Beneficial reminder' };

	it('builds an X intent with encoded url + text', () => {
		const href = intentUrl('x', payload);
		expect(href).toContain('https://twitter.com/intent/tweet');
		expect(href).toContain(`url=${encodeURIComponent(payload.url)}`);
		expect(href).toContain(`text=${encodeURIComponent(payload.text)}`);
	});

	it('builds a Facebook sharer with only the url', () => {
		const href = intentUrl('facebook', payload);
		expect(href).toBe(
			`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(payload.url)}`
		);
	});

	it('builds a Telegram share with url + text', () => {
		const href = intentUrl('telegram', payload);
		expect(href).toContain('https://t.me/share/url');
		expect(href).toContain(`url=${encodeURIComponent(payload.url)}`);
	});

	it('returns null for copy-only platforms (tiktok, link)', () => {
		expect(intentUrl('tiktok', payload)).toBeNull();
		expect(intentUrl('link', payload)).toBeNull();
	});
});

describe('SHARE_TARGETS', () => {
	it('exposes exactly the five required platforms in order', () => {
		expect(SHARE_TARGETS.map((t) => t.id)).toEqual(['x', 'facebook', 'telegram', 'tiktok', 'link']);
	});

	it('marks tiktok and link as copy actions', () => {
		const copy = SHARE_TARGETS.filter((t) => t.action === 'copy').map((t) => t.id);
		expect(copy).toEqual(['tiktok', 'link']);
	});
});

describe('openShareWindow', () => {
	afterEach(() => vi.unstubAllGlobals());

	it('no-ops without a href', () => {
		expect(openShareWindow(null)).toBe(false);
	});

	it('opens a detached popup and returns true', () => {
		const win = { focus: vi.fn(), opener: {} };
		const open = vi.fn(() => win);
		vi.stubGlobal('window', {
			open,
			screenLeft: 0,
			screenTop: 0,
			innerWidth: 1200,
			innerHeight: 800
		});
		vi.stubGlobal('screen', { width: 1200, height: 800 });
		vi.stubGlobal('document', { documentElement: {} });

		expect(openShareWindow('https://t.me/share/url?url=x')).toBe(true);
		expect(open).toHaveBeenCalledOnce();
		expect(win.opener).toBeNull();
	});
});

describe('copyToClipboard', () => {
	afterEach(() => vi.unstubAllGlobals());

	it('uses the async Clipboard API when available', async () => {
		const writeText = vi.fn().mockResolvedValue(undefined);
		vi.stubGlobal('navigator', { clipboard: { writeText } });
		expect(await copyToClipboard('hello')).toBe(true);
		expect(writeText).toHaveBeenCalledWith('hello');
	});

	it('returns false when no clipboard and no document exist', async () => {
		vi.stubGlobal('navigator', {});
		vi.stubGlobal('document', undefined);
		expect(await copyToClipboard('hello')).toBe(false);
	});
});
