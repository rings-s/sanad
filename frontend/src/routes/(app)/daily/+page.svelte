<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/locale.js';
	import { contentApi } from '$lib/api/content.js';
	import ContentCard from '$lib/components/ContentCard.svelte';
	import SkeletonCard from '$lib/components/SkeletonCard.svelte';
	import TopBar from '$lib/components/TopBar.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Icon from '$lib/components/Icon.svelte';

	let date  = $state('');
	let items = $state([]);
	let loading = $state(true);
	let error   = $state('');

	onMount(async () => {
		try {
			const data = await contentApi.daily();
			date  = data.date  ?? '';
			items = data.items ?? [];
		} catch (e) {
			error = e.message || $t('ui.error');
		} finally {
			loading = false;
		}
	});

	/* ── Date helpers ──────────────────────────────────────────────────────── */
	const dateObj = $derived(date ? new Date(date) : null);
	const weekday = $derived(
		dateObj?.toLocaleDateString(undefined, { weekday: 'long' }) ?? ''
	);
	const longDate = $derived(
		dateObj?.toLocaleDateString(undefined, {
			month: 'long', day: 'numeric', year: 'numeric'
		}) ?? ''
	);

	/* ── Sheikh / author helpers ───────────────────────────────────────────── */
	/*
	  Collect unique authors from today's items, preserving first-seen order.
	  The author object now carries `role` (added to AuthorMixin on the backend)
	  so we can badge Sheikh-role users distinctly.
	*/
	const curators = $derived.by(() => {
		const seen = new Map();
		for (const item of items) {
			const a = item?.author;
			if (a?.public_id && !seen.has(a.public_id)) seen.set(a.public_id, a);
		}
		return [...seen.values()];
	});

	const primaryCurator = $derived(curators[0] ?? null);
	const isSingleSheikh = $derived(
		curators.length === 1 && primaryCurator?.role === 'sheikh'
	);
</script>

<svelte:head><title>{$t('daily.title')} — {$t('app.name')}</title></svelte:head>
<TopBar title={$t('daily.title')} subtitle={$t('daily.subtitle')} />

<!--
  Shell: without shell-read so responsive max-w-* utilities work cleanly
  (shell-read lives outside @layer and outranks Tailwind utilities).
    default → max-w-[44rem]   1-col reading width
    lg      → max-w-5xl       3-col fits
    xl      → max-w-7xl       4-col editorial spread
    2xl     → max-w-[88rem]   generous, never edge-to-edge
-->
<div class="shell max-w-[44rem] lg:max-w-5xl xl:max-w-7xl 2xl:max-w-[88rem]">

	<!-- ── Loading ──────────────────────────────────────────────────────────── -->
	{#if loading}
		<!-- Sheikh header skeleton -->
		<div class="mb-7 sheikh-header" aria-hidden="true">
			<div class="flex items-center gap-4">
				<div class="shimmer w-14 h-14 sm:w-16 sm:h-16 rounded-2xl shrink-0"></div>
				<div class="flex-1 space-y-2">
					<div class="shimmer h-5 w-40 rounded-lg"></div>
					<div class="shimmer h-3 w-24 rounded-lg"></div>
					<div class="shimmer h-3 w-32 rounded-lg"></div>
				</div>
			</div>
		</div>
		<!-- Card grid skeleton — mirrors the loaded layout -->
		<div
			class="grid grid-cols-1 gap-4
			       md:grid-cols-2 md:gap-5
			       lg:grid-cols-3 lg:gap-5
			       xl:grid-cols-4 xl:gap-6
			       2xl:gap-7 items-start"
			aria-live="polite"
			aria-label={$t('ui.loading')}
		>
			<div class="xl:col-span-2"><SkeletonCard type="post" /></div>
			<SkeletonCard type="post" count={3} />
		</div>

	<!-- ── Error ────────────────────────────────────────────────────────────── -->
	{:else if error}
		<EmptyState icon="x" tone="error" title={error}>
			<a href="/feed" class="btn-ghost text-sm">{$t('ui.back')}</a>
		</EmptyState>

	<!-- ── Empty ────────────────────────────────────────────────────────────── -->
	{:else if items.length === 0}
		<EmptyState icon="sun" title={$t('daily.noContent')}>
			<a href="/feed" class="btn-ghost text-sm">{$t('feed.title')}</a>
		</EmptyState>

	<!-- ── Loaded ───────────────────────────────────────────────────────────── -->
	{:else}
		<!--
		  ── Sheikh attribution header ──────────────────────────────────────────
		  Warm emerald-tinted surface with a subtle Islamic geometric dot-grid.
		  Gold hairline at the top mirrors the auth-card premium treatment.
		  Animates in first (delay 0) so the guide is instantly identified.
		-->
		{#if primaryCurator}
			<div class="sheikh-header mb-7 daily-card" style="animation-delay: 0ms">

				{#if isSingleSheikh}
					<!-- Single Sheikh: prominent attribution layout -->
					<div class="flex items-center gap-4 sm:gap-5">
						<!-- Avatar -->
						<div class="sheikh-avatar shrink-0">
							{(primaryCurator.name || primaryCurator.username).charAt(0).toUpperCase()}
						</div>

						<!-- Identity -->
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-2 mb-1 flex-wrap">
								<h2 class="font-display text-lg sm:text-xl font-semibold leading-tight truncate
								           text-stone-900 dark:text-stone-50">
									{primaryCurator.name || primaryCurator.username}
								</h2>
								<span class="badge shrink-0"
								      style="background: rgba(245,158,11,0.12); color: #92400e;"
								      class:dark-sheikh-badge={true}>
									<Icon name="star" size={9} strokeWidth={2} />
									{$t('profile.role.sheikh')}
								</span>
							</div>
							<p class="text-xs text-stone-500 dark:text-stone-400 mb-0.5">
								{$t('daily.guidedBy')}
							</p>
							{#if weekday && longDate}
								<p class="text-xs font-medium text-stone-400 dark:text-stone-500">
									{weekday} · {longDate}
								</p>
							{/if}
						</div>
					</div>

				{:else}
					<!-- Multiple curators: compact horizontal layout -->
					<div class="mb-3">
						<p class="text-xs font-semibold uppercase tracking-[0.12em] mb-3
						           text-emerald-700 dark:text-emerald-500">
							{$t('daily.curators')}
						</p>
						<div class="flex flex-wrap gap-3 sm:gap-4">
							{#each curators as c (c.public_id)}
								<div class="flex items-center gap-2.5">
									<div class="sheikh-avatar sheikh-avatar-sm shrink-0">
										{(c.name || c.username).charAt(0).toUpperCase()}
									</div>
									<div>
										<p class="text-sm font-semibold leading-tight
										           text-stone-900 dark:text-stone-50">
											{c.name || c.username}
										</p>
										{#if c.role === 'sheikh'}
											<p class="text-[10px] font-medium text-amber-700 dark:text-amber-400">
												{$t('profile.role.sheikh')}
											</p>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					</div>
					{#if weekday && longDate}
						<p class="text-xs text-stone-400 dark:text-stone-500">
							{weekday} · {longDate}
						</p>
					{/if}
				{/if}

				<!-- Ornamental base-line: gold gradient + diamond — bridges header → adhkar -->
				<div class="flex items-center gap-3 mt-5">
					<div class="flex-1 h-px"
					     style="background: linear-gradient(to right, transparent, rgba(196,163,90,0.45))">
					</div>
					<span class="text-[9px] font-semibold uppercase tracking-[0.18em]
					             text-stone-400 dark:text-stone-600 select-none px-1">
						{$t('daily.adhkar')}
					</span>
					<div class="flex-1 h-px"
					     style="background: linear-gradient(to left, transparent, rgba(196,163,90,0.45))">
					</div>
				</div>
			</div>
		{/if}

		<!--
		  ── The Illuminated Spread — Daily Adhkar grid ─────────────────────────
		  xs / sm  →  1 col        single reading column
		  md        →  2 equal cols  comfortable tablet pair
		  lg        →  3 equal cols  desktop trio
		  xl        →  4 cols; item[0] spans 2 = 50 % feature + two 25 % cards
		  2xl       →  same 4-col, wider gaps

		  items-start preserves natural card heights for mixed content types.
		  Each wrapper carries the `daily-card` class + a proportional delay
		  so cards stagger in after the Sheikh header has already appeared.
		-->
		<div
			class="grid grid-cols-1 gap-4
			       md:grid-cols-2 md:gap-5
			       lg:grid-cols-3 lg:gap-5
			       xl:grid-cols-4 xl:gap-6
			       2xl:gap-7 items-start"
		>
			{#each items as item, i (item.public_id)}
				<div
					class="daily-card {i === 0 ? 'xl:col-span-2' : ''}"
					style="animation-delay: {120 + i * 80}ms"
				>
					<ContentCard {item} />
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	/*
	  Sheikh attribution surface — warm emerald tint, not a card so it reads
	  as a "masthead" above the content cards rather than a peer element.
	  The geom-pattern pseudo-element adds an Islamic geometric texture.
	*/
	.sheikh-header {
		position: relative;
		overflow: hidden;
		border-radius: 1.5rem;
		padding: 1.25rem 1.25rem 1rem;
		background: rgba(5, 150, 105, 0.05);
		border: 1px solid rgba(5, 150, 105, 0.12);
	}

	:global(.dark) .sheikh-header {
		background: rgba(5, 150, 105, 0.08);
		border-color: rgba(5, 150, 105, 0.18);
	}

	@media (min-width: 640px) {
		.sheikh-header {
			padding: 1.5rem 1.5rem 1.125rem;
		}
	}

	/* Subtle Islamic dot-grid texture behind the header */
	.sheikh-header::before {
		content: '';
		position: absolute;
		inset: 0;
		pointer-events: none;
		background-image: radial-gradient(circle at 1px 1px, rgba(4, 120, 87, 0.18) 1px, transparent 0);
		background-size: 24px 24px;
		opacity: 0.7;
	}
	:global(.dark) .sheikh-header::before {
		opacity: 0.25;
	}

	/* Gold hairline at the very top — matches auth-card premium treatment */
	.sheikh-header::after {
		content: '';
		position: absolute;
		top: 0;
		pointer-events: none;
		inset-inline: 1.5rem;
		height: 1px;
		background: linear-gradient(
			90deg,
			transparent,
			rgba(196, 163, 90, 0.55) 28%,
			rgba(196, 163, 90, 0.55) 72%,
			transparent
		);
	}

	/*
	  Sheikh avatar — large circular emerald button with display-font initial.
	  The box-shadow gives it the same subtle emerald glow as btn-primary hover.
	*/
	.sheikh-avatar {
		width: 3.5rem;
		height: 3.5rem;
		border-radius: 1rem;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #047857;
		color: #ffffff;
		font-size: 1.25rem;
		font-weight: 700;
		font-family: var(--font-display, Georgia, serif);
		box-shadow: 0 4px 14px rgba(4, 120, 87, 0.32);
		ring: 2px solid rgba(4, 120, 87, 0.2);
		flex-shrink: 0;
	}
	@media (min-width: 640px) {
		.sheikh-avatar {
			width: 4rem;
			height: 4rem;
			font-size: 1.375rem;
		}
	}

	.sheikh-avatar-sm {
		width: 2.25rem;
		height: 2.25rem;
		border-radius: 0.625rem;
		font-size: 0.875rem;
		box-shadow: 0 2px 8px rgba(4, 120, 87, 0.25);
	}

	/* Dark-mode sheikh role badge (amber) */
	:global(.dark) .dark-sheikh-badge {
		background: rgba(245, 158, 11, 0.15) !important;
		color: #fcd34d !important;
	}

	/*
	  Entrance animation — references the globally-defined card-rise keyframe
	  from app.css. `backwards` holds opacity:0 during the per-card delay so
	  there is never a flash before each item animates in.
	*/
	.daily-card {
		animation: card-rise 0.45s var(--ease-decelerate, cubic-bezier(0, 0, 0.2, 1)) backwards;
	}

	@media (prefers-reduced-motion: reduce) {
		.daily-card {
			animation: none;
		}
	}
</style>
