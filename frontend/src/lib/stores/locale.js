import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { ar } from '../i18n/ar.js';
import { en } from '../i18n/en.js';

const STORAGE_KEY = 'sanad_locale';
const SUPPORTED = ['ar', 'en'];

const translations = { ar, en };

function getInitialLocale() {
	if (!browser) return 'ar';
	const stored = localStorage.getItem(STORAGE_KEY);
	if (stored && SUPPORTED.includes(stored)) return stored;
	const browserLang = navigator.language.slice(0, 2);
	return SUPPORTED.includes(browserLang) ? browserLang : 'ar';
}

export const locale = writable(browser ? getInitialLocale() : 'ar');

if (browser) {
	locale.subscribe((val) => {
		localStorage.setItem(STORAGE_KEY, val);
		document.documentElement.lang = val;
		document.documentElement.dir = val === 'ar' ? 'rtl' : 'ltr';
	});
}

export const dir = derived(locale, ($l) => ($l === 'ar' ? 'rtl' : 'ltr'));

export const t = derived(locale, ($l) => {
	/**
	 * @param {string} key - dot-separated key like 'nav.feed'
	 * @returns {string}
	 */
	return (key) => {
		const keys = key.split('.');
		let value = translations[$l];
		for (const k of keys) {
			value = value?.[k];
		}
		return value ?? key;
	};
});

export function setLocale(lang) {
	if (SUPPORTED.includes(lang)) {
		locale.set(lang);
	}
}

export function toggleLocale() {
	locale.update((l) => (l === 'ar' ? 'en' : 'ar'));
}
