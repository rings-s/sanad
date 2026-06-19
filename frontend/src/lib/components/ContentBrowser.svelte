<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/locale.js';
	import { contentApi } from '$lib/api/content.js';
	import ContentCard from './ContentCard.svelte';
	import SkeletonCard from './SkeletonCard.svelte';
	import TopBar from './TopBar.svelte';
	import SearchBar from './SearchBar.svelte';
	import EmptyState from './EmptyState.svelte';

	/**
	 * The single, shared shell behind every browsing page (Discover · Articles ·
	 * Videos · Listen · Saved). Centralising it guarantees one identical layout,
	 * one search affordance, one filter system, and one set of loading/empty/
	 * error states across the whole app — change it here, change it everywhere.
	 *
	 * @type {{
	 *   title: string,
	 *   subtitle?: string,
	 *   layout?: 'discover'|'articles'|'videos'|'listen',
	 *   type?: string,                       // fixed content type; omit for Discover
	 *   showTypes?: boolean,                 // content-type chip row (Discover)
	 *   emptyIcon?: string,
	 *   emptyText?: string,
	 *   searchPlaceholder?: string,
	 *   fetcher?: (params: Record<string, any>) => Promise<any>,  // default: contentApi.list
	 *   mapResults?: (rows: any[]) => any[], // hydrate rows (e.g. Saved → content)
	 *   clientFilter?: boolean               // filter loaded items locally (Saved)
	 * }}
	 */
	let {
		title,
		subtitle = '',
		layout = 'discover',
		type = undefined,
		showTypes = false,
		emptyIcon = 'spark',
		emptyText = '',
		searchPlaceholder = '',
		fetcher = (p) => contentApi.list(p),
		mapResults = (rows) => rows,
		clientFilter = false
	} = $props();

	/* Layout → grid + skeleton mapping. Mobile is always a single, full-width
	   column; columns are added progressively as the viewport grows. */
	const GRID = {
		discover: 'masonry columns-1 md:columns-2 xl:columns-3 2xl:columns-4',
		articles: 'masonry columns-1 lg:columns-2 2xl:columns-3',
		videos:
			'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4 sm:gap-5',
		listen: 'grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-3 sm:gap-4'
	};
	const SKELETON = { discover: 'post', articles: 'post', videos: 'video', listen: 'audio' };
	const gridClass = $derived(GRID[layout] ?? GRID.discover);
	const skeletonType = $derived(SKELETON[layout] ?? 'post');

	/* Discover content-type filter */
	const TYPE_FILTERS = ['all', 'posts', 'videos', 'audios', 'hadiths'];
	const TYPE_MAP = {
		all: undefined,
		posts: 'post',
		videos: 'video',
		audios: 'audio',
		hadiths: 'hadith'
	};

	let items = $state([]);
	let loading = $state(true);
	let error = $state('');
	let page = $state(1);
	let hasMore = $state(false);
	let loadingMore = $state(false);

	let search = $state('');
	let typeFilter = $state('all');
	let categorySlug = $state('');
	let subcategorySlug = $state('');
	let categories = $state([]);
	let searchDebounce;
	let catRailEl = $state(/** @type {HTMLElement|undefined} */ (undefined));

	const resolvedType = $derived(showTypes ? TYPE_MAP[typeFilter] : type);

	/* In client-filter mode (Saved) categories are derived from what's loaded,
	   so we never offer a filter that yields zero results. */
	const clientCategories = $derived.by(() => {
		if (!clientFilter) return [];
		const seen = new Map();
		for (const it of items) if (it?.category?.slug) seen.set(it.category.slug, it.category);
		return [...seen.values()].sort((a, b) => a.name.localeCompare(b.name));
	});
	const categoryOptions = $derived(clientFilter ? clientCategories : categories);

	/* Cascade: subcategories of the selected category (server mode only — the
	   embedded tree comes from contentApi.categories()). Reactive, no fetch. */
	const selectedCategory = $derived(categoryOptions.find((c) => c.slug === categorySlug));
	const subcategoryOptions = $derived(selectedCategory?.subcategories ?? []);

	/* Local filtering for client mode. */
	const visibleItems = $derived.by(() => {
		if (!clientFilter) return items;
		const q = search.trim().toLowerCase();
		return items.filter((it) => {
			if (categorySlug && it?.category?.slug !== categorySlug) return false;
			if (!q) return true;
			const hay = [
				it?.title,
				it?.body,
				it?.original_text,
				it?.translated_text,
				it?.source_attribution
			]
				.filter(Boolean)
				.join(' ')
				.toLowerCase();
			return hay.includes(q);
		});
	});

	async function load(reset = false) {
		if (reset) {
			loading = true;
			items = [];
			page = 1;
		}
		error = '';
		try {
			const params = { page };
			if (resolvedType) params.type = resolvedType;
			if (!clientFilter) {
				if (search.trim()) params.search = search.trim();
				if (categorySlug) params.category = categorySlug;
				if (subcategorySlug) params.subcategory = subcategorySlug;
			}
			const data = await fetcher(params);
			const rows = mapResults(data.results ?? data);
			items = reset ? rows : [...items, ...rows];
			hasMore = data.meta ? data.meta.page < data.meta.total_pages : false;
		} catch (e) {
			error = e?.message || $t('ui.error');
		} finally {
			loading = false;
			loadingMore = false;
		}
	}

	async function loadMore() {
		if (loadingMore || !hasMore) return;
		loadingMore = true;
		page++;
		await load(false);
	}

	function onSearch() {
		clearTimeout(searchDebounce);
		// Client mode filters instantly via the derived list; only server mode
		// needs the debounced round-trip.
		if (clientFilter) return;
		searchDebounce = setTimeout(() => load(true), 350);
	}

	/**
	 * Carousel edge affordance: toggles `data-fade` (start|end|both|none) on the
	 * rail so CSS can fade whichever edge still has scrollable content, hinting
	 * "there's more this way". Direction-agnostic — relies on the magnitude of
	 * `scrollLeft`, which is negative in RTL on modern engines.
	 * @param {HTMLElement} node
	 */
	function edgeFade(node) {
		function update() {
			const max = node.scrollWidth - node.clientWidth;
			if (max <= 1) {
				node.dataset.fade = 'none';
				return;
			}
			const x = Math.abs(node.scrollLeft);
			const atStart = x <= 1;
			const atEnd = x >= max - 1;
			node.dataset.fade = atStart ? 'end' : atEnd ? 'start' : 'both';
		}
		update();
		node.addEventListener('scroll', update, { passive: true });
		const ro = new ResizeObserver(update);
		ro.observe(node);
		return {
			destroy() {
				node.removeEventListener('scroll', update);
				ro.disconnect();
			}
		};
	}

	/** @param {string} slug */
	function pickCategory(slug) {
		categorySlug = categorySlug === slug ? '' : slug;
		subcategorySlug = ''; // changing the parent clears the child
	}

	/** @param {string} slug */
	function pickSubcategory(slug) {
		subcategorySlug = subcategorySlug === slug ? '' : slug;
	}

	onMount(async () => {
		if (clientFilter) {
			load(true);
		} else {
			try {
				categories = (await contentApi.categories()) ?? [];
			} catch {
				categories = [];
			}
		}
	});

	/* Server mode: re-fetch when a chip filter changes (search is debounced
	   separately). Skipped entirely in client mode. */
	$effect(() => {
		if (clientFilter) return;
		void typeFilter;
		void categorySlug;
		void subcategorySlug;
		load(true);
	});

	/* Keep the active category pill in view as selection changes — when the user
	   taps a half-hidden pill (or one off-screen), bring it to centre. */
	$effect(() => {
		void categorySlug;
		const rail = catRailEl;
		if (!rail) return;
		const active = rail.querySelector('[aria-pressed="true"]');
		active?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
	});
</script>

<svelte:head><title>{title} — {$t('app.name')}</title></svelte:head>
<TopBar {title} {subtitle} />

<div class="shell shell-wide">
	<!-- ── Filter region — search + chips, always centered ─────────────────── -->
	<div class="filter-bar">
		<SearchBar
			bind:value={search}
			oninput={onSearch}
			placeholder={searchPlaceholder || $t('ui.searchPlaceholder')}
			big
		/>
	</div>

	{#if showTypes}
		<div class="chip-rail mb-4" role="group" aria-label={$t('ui.search')}>
			{#each TYPE_FILTERS as f}
				<button
					onclick={() => (typeFilter = f)}
					class={['chip', typeFilter === f ? 'chip-on' : 'chip-off']}
					aria-pressed={typeFilter === f}
				>
					{$t(`feed.filters.${f}`)}
				</button>
			{/each}
		</div>
	{/if}

	{#if categoryOptions.length}
		<div
			bind:this={catRailEl}
			use:edgeFade
			class={['chip-rail cat-carousel', subcategoryOptions.length ? 'mb-3' : 'mb-7']}
			role="group"
			aria-label={$t('content.tags')}
		>
			<button
				onclick={() => pickCategory(categorySlug)}
				class={['chip snap-start', categorySlug === '' ? 'chip-on' : 'chip-off']}
				aria-pressed={categorySlug === ''}
			>
				{$t('feed.filters.all')}
			</button>
			{#each categoryOptions as c (c.slug)}
				<button
					onclick={() => pickCategory(c.slug)}
					class={['chip snap-start', categorySlug === c.slug ? 'chip-on' : 'chip-off']}
					aria-pressed={categorySlug === c.slug}
				>
					{c.name}
				</button>
			{/each}
		</div>
	{/if}

	{#if categorySlug && subcategoryOptions.length}
		<div
			use:edgeFade
			class="chip-rail cat-carousel mb-7"
			role="group"
			aria-label={selectedCategory?.name ?? $t('content.tags')}
		>
			<button
				onclick={() => (subcategorySlug = '')}
				class={['subchip snap-start', subcategorySlug === '' ? 'subchip-on' : 'subchip-off']}
				aria-pressed={subcategorySlug === ''}
			>
				{$t('feed.filters.all')}
			</button>
			{#each subcategoryOptions as s (s.slug)}
				<button
					onclick={() => pickSubcategory(s.slug)}
					class={['subchip snap-start', subcategorySlug === s.slug ? 'subchip-on' : 'subchip-off']}
					aria-pressed={subcategorySlug === s.slug}
				>
					{s.name}
				</button>
			{/each}
		</div>
	{/if}

	<!-- ── Content states ──────────────────────────────────────────────────── -->
	{#if loading}
		<div class={[gridClass, 'stagger']} aria-live="polite" aria-label={$t('ui.loading')}>
			<SkeletonCard type={skeletonType} count={8} />
		</div>
	{:else if error}
		<EmptyState icon="x" tone="error" title={error}>
			<button onclick={() => load(true)} class="btn-ghost text-sm">{$t('ui.retry')}</button>
		</EmptyState>
	{:else if visibleItems.length === 0}
		<EmptyState icon={emptyIcon} title={emptyText || $t('ui.noResults')} />
	{:else}
		<div class={[gridClass, 'stagger']}>
			{#each visibleItems as item (item._saved_id ?? item.public_id)}
				<ContentCard {item} />
			{/each}
		</div>

		{#if hasMore && !clientFilter}
			<div class="mt-9 text-center">
				<button
					onclick={loadMore}
					class="btn-ghost px-6 text-sm"
					disabled={loadingMore}
					aria-busy={loadingMore}
				>
					{#if loadingMore}
						<span
							class="h-4 w-4 animate-spin border-stone-300 border-t-stone-600 inline-block rounded-full border-2"
							aria-hidden="true"
						></span>
					{/if}
					{$t('feed.loadMore')}
				</button>
			</div>
		{/if}
	{/if}
</div>
