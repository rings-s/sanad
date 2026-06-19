import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

const THEME_KEY = 'sanad_theme';

/** @returns {'dark' | 'light'} */
function resolveInitial() {
	if (!browser) return 'light';
	const stored = localStorage.getItem(THEME_KEY);
	if (stored === 'dark' || stored === 'light') return stored;
	return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export const theme = writable(/** @type {'dark' | 'light'} */ (browser ? resolveInitial() : 'light'));

if (browser) {
	theme.subscribe((val) => {
		localStorage.setItem(THEME_KEY, val);
		document.documentElement.classList.toggle('dark', val === 'dark');
	});
}

export const isDark = derived(theme, ($t) => $t === 'dark');

export function toggleTheme() {
	theme.update((t) => (t === 'dark' ? 'light' : 'dark'));
}
