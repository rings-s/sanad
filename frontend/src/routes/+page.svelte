<script>
	import { fly, fade, scale } from 'svelte/transition';
	import { t, toggleLocale, locale } from '$lib/stores/locale.js';
	import { isAuthenticated } from '$lib/stores/auth.js';
	import { toggleTheme, isDark } from '$lib/stores/theme.js';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Icon from '$lib/components/Icon.svelte';
	import BrandMark from '$lib/components/BrandMark.svelte';
	import SacredBackdrop from '$lib/components/SacredBackdrop.svelte';

	onMount(() => {
		if ($isAuthenticated) goto('/feed');
	});

	/** Quadratic ease-out — a soft, settled entrance. @param {number} t */
	const ease = (t) => 1 - (1 - t) * (1 - t);

	const forward = $derived($locale === 'ar' ? 'arrowLeft' : 'arrowRight');
</script>

<svelte:head>
	<title>{$t('app.name')} — {$t('app.tagline')}</title>
	<meta name="description" content={$t('app.description')} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="{$t('app.name')} — {$t('app.tagline')}" />
	<meta property="og:description" content={$t('app.description')} />
	<meta property="og:locale" content={$locale === 'ar' ? 'ar_AR' : 'en_US'} />
	<meta name="twitter:card" content="summary_large_image" />
</svelte:head>

<!--
  The front door. ONE viewport, ONE job: an instant, calm impression that drives
  a single primary action. Deliberately leaner than /learn-more — it does NOT
  reprise the brochure (no "Why Sanad" eyebrow, no wisdom quote, no trust cards);
  those live on /learn-more so the two surfaces never echo each other. The
  SacredBackdrop khatam canvas (the shared shape animation) and the seal's
  entrance choreography are preserved as the brand's signature.
-->
<div class="relative flex min-h-[100svh] flex-col overflow-hidden">
	<SacredBackdrop />

	<!-- ── Header — brand identity left · controls right ─────────────────── -->
	<header
		class="relative z-10 flex items-center justify-between px-[clamp(1rem,4vw,2.5rem)]"
		style="padding-top: max(0.5rem, env(safe-area-inset-top));
		       min-height: calc(4rem + env(safe-area-inset-top, 0px));"
	>
		<a
			href="/"
			class="gap-2 inline-flex items-center rounded-full focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2"
			aria-label={$t('app.name')}
		>
			<BrandMark size={28} />
			<span
				class="font-display text-sm font-semibold tracking-tight text-stone-900 dark:text-stone-50"
			>
				{$t('app.name')}
			</span>
		</a>

		<div class="gap-0.5 flex items-center">
			<button
				onclick={toggleTheme}
				class="h-12 w-12 text-stone-500 hover:bg-stone-900/5 focus-visible:ring-emerald-500
				       dark:text-stone-400 dark:hover:bg-white/10 grid place-items-center rounded-full
				       transition-colors duration-150 focus-visible:ring-2"
				aria-label={$isDark ? $t('nav.lightMode') : $t('nav.darkMode')}
			>
				<Icon name={$isDark ? 'sun' : 'moon'} size={18} strokeWidth={1.5} />
			</button>
			<button
				onclick={toggleLocale}
				class="h-12 min-w-12 gap-1.5 px-3 text-xs font-medium text-stone-500 hover:bg-stone-900/5
				       focus-visible:ring-emerald-500 dark:text-stone-400 dark:hover:bg-white/10 inline-flex
				       items-center justify-center rounded-full transition-colors duration-150 focus-visible:ring-2"
				aria-label={$t('nav.switchLanguage')}
			>
				<Icon name="globe" size={14} />
				<span>{$locale === 'ar' ? 'EN' : 'عربي'}</span>
			</button>
			<a
				href="/learn-more"
				class="ms-1 h-10 gap-1.5 px-4 text-xs font-medium text-stone-600 border-stone-200/80
				       bg-white/60 backdrop-blur hover:bg-white hover:border-stone-300 dark:text-stone-300
				       dark:border-stone-700/70 dark:bg-stone-900/50 dark:hover:bg-stone-800/80 inline-flex
				       items-center rounded-full border transition-all duration-150
				       focus-visible:ring-2 focus-visible:ring-emerald-500"
			>
				{$t('landing.learnMore')}
				<Icon name={forward} size={12} />
			</a>
		</div>
	</header>

	<!-- ── Hero — single focal point ─────────────────────────────────────── -->
	<main
		class="relative z-10 flex flex-1 flex-col items-center justify-center
		       px-[clamp(1.25rem,5vw,2rem)] pb-10"
	>
		<div class="max-w-xl flex w-full flex-col items-center text-center">

			<!-- Seal — the brand's primary visual identity, enters first -->
			<div in:scale={{ start: 0.82, duration: 520, easing: ease }}>
				<BrandMark size={88} glow />
			</div>

			<!-- Tagline eyebrow — the product's own voice (not the brochure's
			     "Why Sanad"), so the front door reads distinctly from /learn-more -->
			<div in:fly={{ y: 14, duration: 460, delay: 80, easing: ease }}>
				<span class="badge badge-accent mt-7">
					<Icon name="spark" size={12} />
					{$t('app.tagline')}
				</span>
			</div>

			<!-- Editorial headline — two-tone: neutral first line, emerald second.
			     Uses the front-door copy (frontTitle), distinct from the /learn-more
			     hero so the two surfaces never read as duplicates. -->
			<h1
				class="font-display mt-5 font-semibold tracking-tight text-stone-900
				       dark:text-stone-50 text-balance"
				style="font-size: clamp(2.6rem, 9vw, 4.25rem); line-height: 1.05;"
				in:fly={{ y: 16, duration: 460, delay: 160, easing: ease }}
			>
				{#each $t('landing.frontTitle').split('\n') as line, i (i)}
					{#if i > 0}<br />{/if}
					{#if i === 1}
						<span class="text-emerald-700 dark:text-emerald-400">{line}</span>
					{:else}
						{line}
					{/if}
				{/each}
			</h1>

			<!-- Value proposition — front-door voice (frontSubtitle): evocative and
			     calm, distinct from the content-listing subtitle on /learn-more -->
			<p
				class="mt-5 leading-relaxed text-stone-500 dark:text-stone-400 text-balance"
				style="font-size: clamp(0.95rem, 3.2vw, 1.1rem); max-width: 30rem;"
				in:fly={{ y: 14, duration: 460, delay: 240, easing: ease }}
			>
				{$t('landing.frontSubtitle')}
			</p>

			<!-- Gilded khatam divider — ornament only, signals the manuscript register -->
			<div
				class="mt-8 gap-4 flex items-center"
				in:fade={{ duration: 500, delay: 320 }}
				aria-hidden="true"
			>
				<span class="w-10 bg-gold-400/50 h-px"></span>
				<svg
					class="h-3 w-3 text-emerald-700/60 dark:text-emerald-400/60"
					viewBox="0 0 24 24"
					fill="currentColor"
				>
					<path d="M12 0l3.3 8.7L24 12l-8.7 3.3L12 24l-3.3-8.7L0 12l8.7-3.3z" />
				</svg>
				<span class="w-10 bg-gold-400/50 h-px"></span>
			</div>

			<!-- Primary actions — clear hierarchy: create account > sign in -->
			<div
				class="mt-8 gap-3 sm:w-auto sm:flex-row sm:justify-center flex w-full
				       flex-col items-stretch"
				in:fly={{ y: 14, duration: 460, delay: 400, easing: ease }}
			>
				<a
					href="/register"
					class="btn-primary min-h-12 px-8 text-base sm:w-auto w-full justify-center"
				>
					{$t('landing.getStarted')}
					<Icon name={forward} size={16} />
				</a>
				<a
					href="/login"
					class="btn-ghost min-h-12 px-7 text-base sm:w-auto w-full justify-center"
				>
					{$t('auth.login')}
				</a>
			</div>

			<!-- Trust — a single quiet reassurance line (the detailed 3-card trust
			     strip belongs to /learn-more, not here) -->
			<p
				class="mt-7 gap-2 inline-flex items-center text-xs font-medium
				       text-stone-400 dark:text-stone-500"
				in:fade={{ duration: 500, delay: 500 }}
			>
				<Icon
					name="check"
					size={14}
					strokeWidth={2.25}
					class="text-emerald-600 dark:text-emerald-400"
				/>
				{$t('landing.trust')}
			</p>
		</div>
	</main>

	<!-- ── Footer ─────────────────────────────────────────────────────────── -->
	<footer
		class="gap-1 px-6 pt-2 text-xs text-stone-400 dark:text-stone-500 relative z-10
		       flex items-center justify-center"
		style="padding-bottom: max(1rem, env(safe-area-inset-bottom));"
	>
		<span>{$t('app.name')} &copy; {new Date().getFullYear()}</span>
	</footer>
</div>
