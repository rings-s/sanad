<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import { onNavigate } from '$app/navigation';
	import { auth } from '$lib/stores/auth.js';
	import { theme } from '$lib/stores/theme.js';
	import { locale } from '$lib/stores/locale.js';
	import { browser } from '$app/environment';

	let { children } = $props();

	// ── View Transitions API cross-fade ──────────────────────────────────────
	onNavigate((navigation) => {
		if (!browser || !document.startViewTransition) return;
		return new Promise((resolve) => {
			document.startViewTransition(async () => {
				resolve();
				await navigation.complete;
			});
		});
	});

	onMount(async () => {
		// Restore auth session from HttpOnly cookie
		await auth.init();

		// Apply theme class synchronously before first paint
		document.documentElement.classList.toggle('dark', $theme === 'dark');

		// Apply locale/dir
		if (browser) {
			const stored = localStorage.getItem('sanad_locale') || 'ar';
			document.documentElement.lang = stored;
			document.documentElement.dir = stored === 'ar' ? 'rtl' : 'ltr';
		}
	});
</script>

{@render children()}
