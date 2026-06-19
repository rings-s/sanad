<script>
	import { t, toggleLocale, locale } from '$lib/stores/locale.js';
	import { toggleTheme, isDark } from '$lib/stores/theme.js';
	import Icon from '$lib/components/Icon.svelte';
	import BrandMark from '$lib/components/BrandMark.svelte';
	import SacredBackdrop from '$lib/components/SacredBackdrop.svelte';

	/*
	 * Learn More — the public "entry surface". Built on the brand's established
	 * manuscript system (emerald · stone · gilded gold, Fraunces/Amiri display,
	 * the SacredBackdrop khatam canvas and the BrandMark seal) rather than a
	 * generic marketing template. The page moves through four calm movements:
	 * an atmospheric hero, an honest trust strip, an asymmetric bento of real
	 * capabilities, a three-step path, and a closing invitation.
	 */

	const forward = $derived($locale === 'ar' ? 'arrowLeft' : 'arrowRight');

	// Bento of capabilities — reuses the shared landing.features copy so the
	// marketing promise stays in lockstep with the product. Sizes are
	// intentionally uneven to create a clear focal point (Gestalt: figure/ground).
	const features = [
		{ key: 'daily', icon: 'sun', span: 'lg:col-span-3 lg:row-span-2', feature: true },
		{ key: 'content', icon: 'layers', span: 'lg:col-span-3' },
		{ key: 'progress', icon: 'check', span: 'lg:col-span-3' },
		{ key: 'search', icon: 'search', span: 'lg:col-span-6' }
	];

	const trust = [
		{ key: 'scholars', icon: 'check' },
		{ key: 'bilingual', icon: 'globe' },
		{ key: 'calm', icon: 'spark' }
	];

	const steps = [
		{ key: 'discover', icon: 'spark' },
		{ key: 'reflect', icon: 'bookmark' },
		{ key: 'grow', icon: 'check' }
	];
</script>

<svelte:head>
	<title>{$t('landing.learnMore')} — {$t('app.name')}</title>
	<meta name="description" content={$t('app.description')} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="{$t('app.name')} — {$t('app.tagline')}" />
	<meta property="og:description" content={$t('app.description')} />
	<meta property="og:locale" content={$locale === 'ar' ? 'ar_AR' : 'en_US'} />
</svelte:head>

<div class="bg-stone-50 dark:bg-stone-950 flex min-h-[100svh] flex-col">
	<main class="flex-1">
		<!-- ── Hero ─────────────────────────────────────────────────────────
		     Centered seal + editorial headline over the drifting khatam canvas.
		     The navbar lives inside this section so it floats over the backdrop,
		     exactly like the hero page. -->
		<section class="relative isolate flex flex-col overflow-hidden">
			<SacredBackdrop />

			<!-- ── Navbar — transparent, matches hero header exactly ── -->
			<header
				class="relative z-10 flex items-center justify-between px-[clamp(1rem,4vw,2.5rem)]"
				style="padding-top: max(0.5rem, env(safe-area-inset-top));
				       min-height: calc(4rem + env(safe-area-inset-top, 0px));"
			>
				<a
					href="/"
					class="gap-2.5 focus-visible:ring-emerald-500 flex items-center rounded-full no-underline focus-visible:ring-2"
					aria-label={$t('app.name')}
				>
					<BrandMark size={32} />
					<span
						class="font-display text-base font-semibold tracking-tight text-stone-900 dark:text-stone-50"
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
					<a href="/register" class="btn-primary ms-1 text-sm">{$t('auth.register')}</a>
				</div>
			</header>

			<div
				class="stagger max-w-3xl px-6 pt-10 pb-24 sm:pt-14 sm:pb-32 relative mx-auto
				       flex flex-col items-center text-center"
			>
				<BrandMark size={64} glow />

				<span class="badge badge-accent mt-8">
					<Icon name="spark" size={12} />
					{$t('learn.eyebrow')}
				</span>

				<h1
					class="font-display mt-6 font-semibold tracking-tight text-stone-900 dark:text-stone-50 text-balance"
					style="font-size: clamp(2.5rem, 8vw, 4.5rem); line-height: 1.04;"
				>
					{#each $t('landing.heroTitle').split('\n') as line, i (i)}
						{#if i > 0}<br />{/if}
						{#if i === 1}
							<span class="text-emerald-700 dark:text-emerald-400">{line}</span>
						{:else}
							{line}
						{/if}
					{/each}
				</h1>

				<p
					class="mt-6 max-w-xl text-base leading-relaxed text-stone-500 dark:text-stone-400 sm:text-lg text-pretty"
				>
					{$t('landing.heroSubtitle')}
				</p>

				<!-- Gilded hairline + wisdom line (gold = ornament only) -->
				<div class="mt-9 gap-4 flex items-center">
					<span class="w-10 bg-gold-400/50 h-px"></span>
					<p class="font-display text-sm text-stone-500 dark:text-stone-400 italic">
						{$t('learn.wisdom')}
					</p>
					<span class="w-10 bg-gold-400/50 h-px"></span>
				</div>

				<div class="mt-10 gap-3 flex flex-wrap items-center justify-center">
					<a href="/register" class="btn-primary min-h-12 px-7 text-base">
						{$t('landing.getStarted')}
						<Icon name={forward} size={16} />
					</a>
					<a href="/login" class="btn-ghost min-h-12 px-7 text-base">{$t('auth.login')}</a>
				</div>
			</div>
		</section>

		<!-- ── Trust strip ──────────────────────────────────────────────────
		     Honest, qualitative assurances (no invented numbers). -->
		<section
			class="border-stone-200/70 bg-white/70 backdrop-blur dark:border-stone-800 dark:bg-stone-900/50 border-y"
		>
			<div class="max-w-5xl gap-6 px-6 py-7 sm:grid-cols-3 mx-auto grid grid-cols-1">
				{#each trust as item, i (item.key)}
					<div
						class={[
							'gap-3 flex items-start',
							i > 0 && 'sm:border-s sm:border-stone-200/70 sm:ps-6 dark:sm:border-stone-800'
						]}
					>
						<span
							class="mt-0.5 h-9 w-9 rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400 grid shrink-0 place-items-center"
						>
							<Icon name={item.icon} size={16} strokeWidth={2} />
						</span>
						<div>
							<p class="text-sm font-semibold text-stone-900 dark:text-stone-50">
								{$t(`learn.trust.${item.key}.title`)}
							</p>
							<p class="mt-0.5 text-sm leading-snug text-stone-500 dark:text-stone-400">
								{$t(`learn.trust.${item.key}.desc`)}
							</p>
						</div>
					</div>
				{/each}
			</div>
		</section>

		<!-- ── Capabilities (bento) ─────────────────────────────────────────── -->
		<section class="px-6 py-20 sm:py-28">
			<div class="max-w-6xl mx-auto">
				<div class="max-w-2xl mx-auto text-center">
					<h2
						class="font-display font-semibold tracking-tight text-stone-900 dark:text-stone-50"
						style="font-size: clamp(1.85rem, 5vw, 2.5rem);"
					>
						{$t('learn.featuresTitle')}
					</h2>
					<p class="mt-4 text-base leading-relaxed text-stone-500 dark:text-stone-400 text-pretty">
						{$t('learn.featuresLede')}
					</p>
				</div>

				<div class="stagger mt-14 gap-4 sm:gap-5 lg:grid-cols-6 grid grid-cols-1">
					{#each features as f (f.key)}
						<article
							class={[
								'card-elevated group p-7 ease-standard hover:-translate-y-0.5 sm:p-8 relative overflow-hidden transition-all duration-300',
								f.span
							]}
						>
							{#if f.feature}
								<!-- Signature card carries a faint geometric texture + a soft
								     emerald wash so the focal point reads first. -->
								<div class="geom-pattern inset-0 absolute opacity-[0.05]"></div>
								<div
									class="-end-16 -top-16 h-44 w-44 bg-emerald-500/10 blur-3xl dark:bg-emerald-400/10 pointer-events-none absolute rounded-full"
								></div>
							{/if}

							<div class="relative flex h-full flex-col">
								<span
									class="h-11 w-11 rounded-2xl bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400 grid place-items-center transition-transform duration-200 group-hover:scale-105"
								>
									<Icon name={f.icon} size={20} />
								</span>
								<h3
									class="font-display mt-5 font-semibold tracking-tight text-stone-900 dark:text-stone-50"
									style="font-size: {f.feature ? '1.5rem' : '1.2rem'};"
								>
									{$t(`landing.features.${f.key}.title`)}
								</h3>
								<p
									class="mt-2 text-sm leading-relaxed text-stone-500 dark:text-stone-400 text-pretty"
								>
									{$t(`landing.features.${f.key}.desc`)}
								</p>

								{#if f.feature}
									<!-- Contextual proof: the actual content types on offer. -->
									<div class="gap-2 pt-7 mt-auto flex flex-wrap">
										<span class="badge badge-accent">{$t('content.type.post')}</span>
										<span class="badge badge-stone">{$t('content.type.video')}</span>
										<span class="badge badge-stone">{$t('content.type.audio')}</span>
										<span class="badge badge-stone">{$t('content.type.hadith')}</span>
									</div>
								{/if}
							</div>
						</article>
					{/each}
				</div>
			</div>
		</section>

		<!-- ── The path (3 steps) ───────────────────────────────────────────── -->
		<section
			class="border-stone-200/70 bg-white px-6 py-20 sm:py-28 dark:border-stone-800 dark:bg-stone-900 border-t"
		>
			<div class="max-w-5xl mx-auto">
				<div class="max-w-2xl mx-auto text-center">
					<h2
						class="font-display font-semibold tracking-tight text-stone-900 dark:text-stone-50"
						style="font-size: clamp(1.85rem, 5vw, 2.5rem);"
					>
						{$t('learn.journeyTitle')}
					</h2>
					<p class="mt-4 text-base leading-relaxed text-stone-500 dark:text-stone-400 text-pretty">
						{$t('learn.journeyLede')}
					</p>
				</div>

				<ol class="stagger mt-16 gap-10 md:grid-cols-3 md:gap-8 relative grid grid-cols-1">
					<!-- Gold thread connecting the three seals on desktop -->
					<div
						class="top-7 via-gold-400/40 md:block pointer-events-none absolute inset-x-[16%] hidden h-px bg-gradient-to-r from-transparent to-transparent"
						aria-hidden="true"
					></div>

					{#each steps as step, i (step.key)}
						<li class="relative flex flex-col items-center text-center">
							<span
								class="h-14 w-14 border-gold-300/50 bg-stone-50 dark:border-gold-300/25 dark:bg-stone-900 relative grid place-items-center rounded-full border"
							>
								<span
									class="font-display text-lg font-semibold text-emerald-700 dark:text-emerald-400"
								>
									{String(i + 1).padStart(2, '0')}
								</span>
							</span>
							<span
								class="mt-5 h-10 w-10 rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400 grid place-items-center"
							>
								<Icon name={step.icon} size={18} strokeWidth={1.75} />
							</span>
							<h3
								class="font-display mt-4 text-xl font-semibold tracking-tight text-stone-900 dark:text-stone-50"
							>
								{$t(`learn.steps.${step.key}.title`)}
							</h3>
							<p
								class="mt-2 max-w-xs text-sm leading-relaxed text-stone-500 dark:text-stone-400 text-pretty"
							>
								{$t(`learn.steps.${step.key}.desc`)}
							</p>
						</li>
					{/each}
				</ol>
			</div>
		</section>

		<!-- ── Closing invitation ───────────────────────────────────────────── -->
		<section class="bg-emerald-800 px-6 py-24 dark:bg-emerald-950 relative isolate overflow-hidden">
			<div
				class="geom-pattern inset-0 absolute opacity-[0.08]"
				style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.5) 1px, transparent 0);"
				aria-hidden="true"
			></div>
			<div
				class="-bottom-24 h-72 w-72 bg-emerald-500/20 blur-3xl pointer-events-none absolute left-1/2 -translate-x-1/2 rounded-full"
				aria-hidden="true"
			></div>

			<div class="max-w-2xl relative mx-auto text-center">
				<h2
					class="font-display font-semibold tracking-tight text-white"
					style="font-size: clamp(1.85rem, 5vw, 2.5rem);"
				>
					{$t('landing.cta.title')}
				</h2>
				<p class="mt-4 text-base leading-relaxed text-emerald-50/85 text-pretty">
					{$t('landing.cta.subtitle')}
				</p>
				<a
					href="/register"
					class="ease-standard mt-9 min-h-12 gap-2 bg-white px-8 py-3.5 text-base font-semibold
					       text-emerald-800 shadow-lg hover:shadow-xl focus-visible:ring-white focus-visible:ring-offset-emerald-800 inline-flex items-center
					       rounded-full transition-all duration-150 hover:-translate-y-px
					       focus-visible:ring-2 focus-visible:ring-offset-2 active:scale-[0.97]"
				>
					{$t('landing.cta.button')}
					<Icon name={forward} size={16} />
				</a>
			</div>
		</section>
	</main>

	<!-- ── Footer ───────────────────────────────────────────────────────── -->
	<footer
		class="gap-4 border-stone-200/70 bg-white py-6 text-sm text-stone-400 dark:border-stone-800 dark:bg-stone-900
		       dark:text-stone-500 flex items-center justify-between border-t px-[clamp(1.25rem,4vw,2.5rem)]"
	>
		<span>{$t('app.name')} &copy; {new Date().getFullYear()}</span>
		<a
			href="/"
			class="px-2 py-1 font-medium hover:text-stone-700 focus-visible:ring-emerald-500 dark:hover:text-stone-200 rounded-full
			       transition-colors duration-150 focus-visible:ring-2"
		>
			{$t('error.home')}
		</a>
	</footer>
</div>
