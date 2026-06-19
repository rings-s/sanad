import { describe, it, expect, vi, afterEach } from 'vitest';
import { render } from 'vitest-browser-svelte';
import { readable } from 'svelte/store';

// `$app/stores` isn't wired in the test runtime — provide a minimal page store
// so the component can read `page.url.origin`.
vi.mock('$app/stores', () => ({
	page: readable({ url: new URL('https://sanad.app/feed') })
}));

import ShareMenu from './ShareMenu.svelte';

const trigger = () => document.querySelector('[aria-haspopup="menu"]');
const panel = () => document.querySelector('[role="menu"]');

afterEach(() => {
	// guard against a leaked portal node between tests
	panel()?.remove();
});

describe('ShareMenu', () => {
	it('portals an opened panel to <body> with all five targets', async () => {
		render(ShareMenu, { path: '/content/abc', title: 'A reminder' });

		expect(panel()).toBeNull();
		trigger().click();
		await vi.waitFor(() => expect(panel()).not.toBeNull());

		// escaped its container — mounted directly under <body>
		expect(panel().parentElement).toBe(document.body);
		expect(panel().querySelectorAll('[role="menuitem"]')).toHaveLength(5);
	});

	it('copies the canonical absolute URL for Copy Link', async () => {
		const writeText = vi.fn().mockResolvedValue(undefined);
		Object.defineProperty(navigator, 'clipboard', { value: { writeText }, configurable: true });

		render(ShareMenu, { path: '/content/abc', title: 'A reminder' });
		trigger().click();
		await vi.waitFor(() => expect(panel()).not.toBeNull());

		const items = panel().querySelectorAll('[role="menuitem"]');
		items[items.length - 1].click(); // "Copy link" is last
		await vi.waitFor(() => expect(writeText).toHaveBeenCalledWith('https://sanad.app/content/abc'));
	});

	it('closes on Escape and cleans up the portalled node', async () => {
		render(ShareMenu, { path: '/content/abc' });
		trigger().click();
		await vi.waitFor(() => expect(panel()).not.toBeNull());

		document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
		await vi.waitFor(() => expect(panel()).toBeNull());
	});
});
