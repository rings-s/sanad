<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { auth } from '$lib/stores/auth.js';
	import { authApi, GOOGLE_REDIRECT_URI } from '$lib/api/auth.js';
	import { get } from 'svelte/store';
	import Icon from '$lib/components/Icon.svelte';

	/** @type {'loading' | 'error'} */
	let uiState = $state('loading');
	let errorMessage = $state('');

	onMount(async () => {
		const url = get(page).url;
		const code = url.searchParams.get('code');
		const returnedState = url.searchParams.get('state');
		const errorParam = url.searchParams.get('error');

		// ── 1. Check if Google returned an error (user cancelled, etc.) ──────
		if (errorParam) {
			showError(
				errorParam === 'access_denied'
					? 'Sign-in was cancelled. You can try again.'
					: `Google returned an error: ${errorParam}`
			);
			return;
		}

		// ── 2. Validate required parameters ──────────────────────────────────
		if (!code || !returnedState) {
			showError('Invalid callback — missing code or state parameter.');
			return;
		}

		// ── 3. CSRF validation: compare state ────────────────────────────────
		const storedState = sessionStorage.getItem('google_oauth_state');
		const codeVerifier = sessionStorage.getItem('google_oauth_code_verifier');

		// Clear sessionStorage immediately — one-time use only
		sessionStorage.removeItem('google_oauth_state');
		sessionStorage.removeItem('google_oauth_code_verifier');

		if (!storedState || returnedState !== storedState) {
			// State mismatch — possible CSRF attack or stale tab
			console.warn('[GoogleCallback] State mismatch — aborting.');
			showError('Security check failed. Please try signing in again.');
			return;
		}

		if (!codeVerifier) {
			showError('PKCE verifier missing. Please try signing in again.');
			return;
		}

		// ── 4. Exchange the code with the backend ─────────────────────────────
		try {
			const data = await authApi.googleCallback(code, GOOGLE_REDIRECT_URI, codeVerifier);
			// data = { user, access } — refresh token is in the HttpOnly cookie set by backend
			auth.login(data.user, data.access);
			goto('/feed');
		} catch (err) {
			const msg = err?.data?.error?.message || err?.message || 'Sign-in failed. Please try again.';
			showError(msg);
		}
	});

	function showError(msg) {
		errorMessage = msg;
		uiState = 'error';
	}
</script>

<svelte:head>
	<title>Signing in… — Sanad</title>
</svelte:head>

<!-- Full-page states — rendered inside the (auth) layout's form-side panel -->

{#if uiState === 'loading'}
	<div
		class="flex flex-col items-center justify-center gap-5 py-16"
		aria-live="polite"
		aria-label="Signing in with Google"
	>
		<!-- Spinner -->
		<div
			class="w-12 h-12 rounded-full
			       border-4 border-stone-200 dark:border-stone-800
			       border-t-emerald-600 dark:border-t-emerald-500
			       motion-safe:animate-spin"
			aria-hidden="true"
		></div>

		<div class="text-center">
			<p class="text-base font-semibold text-stone-900 dark:text-stone-50">Signing you in…</p>
			<p class="text-sm mt-1 text-stone-500 dark:text-stone-400">Verifying your Google account</p>
		</div>
	</div>
{:else}
	<!-- Error state -->
	<div
		class="flex flex-col items-center gap-6 py-10 text-center"
		role="alert"
		aria-live="assertive"
	>
		<!-- Error icon -->
		<div
			class="w-14 h-14 rounded-full flex items-center justify-center
			       bg-red-50 dark:bg-red-900/20"
			aria-hidden="true"
		>
			<Icon name="x" size={28} strokeWidth={2} class="text-red-600 dark:text-red-400" />
		</div>

		<div>
			<h1 class="text-xl font-bold mb-2 text-stone-900 dark:text-stone-50">Sign-in failed</h1>
			<p class="text-sm max-w-xs mx-auto text-stone-500 dark:text-stone-400">{errorMessage}</p>
		</div>

		<a
			href="/login"
			class="btn-primary px-6 py-2.5"
		>
			Try again
		</a>
	</div>
{/if}
