<script>
	import { buildGoogleAuthUrl } from '$lib/api/auth.js';
	import { t } from '$lib/stores/locale.js';

	/** Called with an error message string when the flow can't start. */
	let { onError = () => {} } = $props();

	const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
	const CONFIGURED = Boolean(CLIENT_ID);

	let loading = $state(false);

	/**
	 * Generate a cryptographically random base64url string of `byteLength` bytes.
	 * @param {number} byteLength
	 */
	function randomBase64url(byteLength) {
		const bytes = crypto.getRandomValues(new Uint8Array(byteLength));
		return btoa(String.fromCharCode(...bytes))
			.replace(/\+/g, '-')
			.replace(/\//g, '_')
			.replace(/=+$/, '');
	}

	/**
	 * Compute SHA-256 of `plain` and return the digest as base64url.
	 * Used for PKCE code_challenge = BASE64URL(SHA256(code_verifier)).
	 * @param {string} plain
	 */
	async function sha256Base64url(plain) {
		const encoder = new TextEncoder();
		const data = encoder.encode(plain);
		const hash = await crypto.subtle.digest('SHA-256', data);
		return btoa(String.fromCharCode(...new Uint8Array(hash)))
			.replace(/\+/g, '-')
			.replace(/\//g, '_')
			.replace(/=+$/, '');
	}

	async function handleClick() {
		if (!CONFIGURED) {
			onError($t('auth.googleUnavailable'));
			return;
		}

		loading = true;

		try {
			// 1. Generate CSRF state token (32 bytes = 256-bit entropy)
			const state = randomBase64url(32);

			// 2. Generate PKCE code_verifier (32 bytes) and derive code_challenge
			const codeVerifier = randomBase64url(32);
			const codeChallenge = await sha256Base64url(codeVerifier);

			// 3. Persist in sessionStorage — cleared by the callback page after use.
			//    sessionStorage is tab-scoped and cleared on tab close.
			sessionStorage.setItem('google_oauth_state', state);
			sessionStorage.setItem('google_oauth_code_verifier', codeVerifier);

			// 4. Redirect to Google — browser leaves this page.
			window.location.href = buildGoogleAuthUrl(state, codeChallenge);
		} catch (err) {
			loading = false;
			onError($t('auth.googleError'));
			console.error('[GoogleButton] OAuth init error:', err);
		}
	}
</script>

<!--
  Always rendered (dev + prod) so it never silently disappears and never shifts
  the layout. When Google isn't configured it degrades to a disabled, clearly
  labelled state rather than vanishing — keeping the divider + form spacing stable.
-->
<button
	type="button"
	class="btn-google"
	onclick={handleClick}
	disabled={loading || !CONFIGURED}
	aria-label={$t('auth.continueWithGoogle')}
	aria-busy={loading}
	aria-disabled={!CONFIGURED}
	title={CONFIGURED ? undefined : $t('auth.googleUnavailable')}
>
	{#if loading}
		<span
			class="border-stone-300 border-t-stone-600 dark:border-stone-600 dark:border-t-stone-200 motion-safe:animate-spin
			       inline-block h-[18px]
			       w-[18px] rounded-full
			       border-2"
			aria-hidden="true"
		></span>
		<span>{$t('ui.loading')}</span>
	{:else}
		<!-- Google "G" logo — inline SVG, no external request.
		     shrink-0 so it never compresses on narrow (xs/foldable) screens. -->
		<svg
			class="shrink-0"
			class:opacity-40={!CONFIGURED}
			aria-hidden="true"
			width="18"
			height="18"
			viewBox="0 0 18 18"
			xmlns="http://www.w3.org/2000/svg"
		>
			<path
				d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"
				fill="#4285F4"
			/>
			<path
				d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"
				fill="#34A853"
			/>
			<path
				d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z"
				fill="#FBBC05"
			/>
			<path
				d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 6.29C4.672 4.163 6.656 3.58 9 3.58z"
				fill="#EA4335"
			/>
		</svg>
		<span class="truncate">
			{CONFIGURED ? $t('auth.continueWithGoogle') : $t('auth.googleUnavailable')}
		</span>
	{/if}
</button>
