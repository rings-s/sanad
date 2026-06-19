<script>
	import { fly } from 'svelte/transition';
	import { t, toggleLocale, locale } from '$lib/stores/locale.js';
	import { toggleTheme, isDark } from '$lib/stores/theme.js';
	import { isAuthenticated } from '$lib/stores/auth.js';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Icon from '$lib/components/Icon.svelte';
	import BrandMark from '$lib/components/BrandMark.svelte';
	import SacredBackdrop from '$lib/components/SacredBackdrop.svelte';

	let { children } = $props();

	onMount(() => {
		if ($isAuthenticated) goto('/feed');
	});

	/** @param {number} t */
	const ease = (t) => 1 - (1 - t) * (1 - t);
</script>

<!-- Single centred column on EVERY viewport — xs · foldable · tablet · desktop.
     No grid: the form is the sole focus, floating on the sacred backdrop. -->
<div class="relative flex min-h-dvh flex-col">
	<SacredBackdrop />

	<!-- ── Top utility bar — brand (home) + theme/locale ──────────────── -->
	<header
		class="relative z-10 flex shrink-0 items-center justify-between
		       px-[clamp(1rem,5vw,1.75rem)]"
		style="padding-top: max(0.5rem, env(safe-area-inset-top));
		       min-height: calc(3.5rem + env(safe-area-inset-top, 0px));"
	>
		<a
			href="/"
			class="group gap-2.5 -ms-1 flex items-center rounded-full p-1 no-underline
			       focus-visible:ring-emerald-500 focus-visible:ring-2"
			aria-label={$t('app.name')}
		>
			<BrandMark size={30} />
			<span class="font-display text-[1.05rem] font-semibold tracking-tight text-stone-900 dark:text-stone-50">
				{$t('app.name')}
			</span>
		</a>

		<div class="gap-0.5 flex items-center">
			<!-- 48 × 48 px touch targets (WCAG 2.5.8) -->
			<button
				onclick={toggleTheme}
				class="w-12 h-12 text-stone-500 dark:text-stone-400 hover:bg-stone-900/5
				       dark:hover:bg-white/10 focus-visible:ring-emerald-500 grid place-items-center
				       rounded-full transition-colors duration-150 focus-visible:ring-2"
				aria-label={$isDark ? $t('nav.lightMode') : $t('nav.darkMode')}
			>
				<Icon name={$isDark ? 'sun' : 'moon'} size={18} strokeWidth={1.5} />
			</button>
			<button
				onclick={toggleLocale}
				class="gap-1.5 min-w-12 h-12 px-3 text-xs font-medium text-stone-500 dark:text-stone-400
				       hover:bg-stone-900/5 dark:hover:bg-white/10 focus-visible:ring-emerald-500 inline-flex
				       items-center justify-center rounded-full transition-colors duration-150 focus-visible:ring-2"
				aria-label={$t('nav.switchLanguage')}
			>
				<Icon name="globe" size={14} />
				{$locale === 'ar' ? 'EN' : 'عربي'}
			</button>
		</div>
	</header>

	<!-- ── Centred form column ────────────────────────────────────────── -->
	<main class="relative z-10 flex flex-1 items-center justify-center px-[clamp(1rem,5vw,1.5rem)] py-8">
		<div
			class="w-full max-w-[25rem]"
			in:fly={{ y: 18, duration: 420, easing: ease }}
		>
			<div class="auth-card p-6 sm:p-8">
				{@render children()}
			</div>

			<!-- Quiet reassurance line under the card -->
			<p class="mt-6 gap-1.5 text-xs text-stone-400 dark:text-stone-500 flex items-center justify-center">
				<span class="h-1 w-1 rounded-full bg-gold-400/70" aria-hidden="true"></span>
				{$t('landing.trust')}
			</p>
		</div>
	</main>

	<!-- Home-indicator safe area -->
	<div class="shrink-0" style="height: env(safe-area-inset-bottom, 0px);" aria-hidden="true"></div>
</div>
