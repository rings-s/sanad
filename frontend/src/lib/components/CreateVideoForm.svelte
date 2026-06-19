<script>
	/**
	 * Admin authoring flow: paste a YouTube URL → fetch title + high-res thumbnail
	 * from Django (`contentApi.youtubeMetadata`) → preview/play → publish as a
	 * `video` content item.
	 *
	 * State machine: idle → invalid | (debounce) fetching → ready | error
	 * The preview slot reserves space (SkeletonCard ↔ play-preview share the same
	 * aspect-video footprint) so resolved metadata causes zero layout shift.
	 *
	 * @property {number} [debounceMs] Delay before firing the metadata fetch.
	 *                                 Lowered in tests for determinism.
	 */
	let { debounceMs = 600 } = $props();

	import { onMount } from 'svelte';
	import { t } from '$lib/stores/locale.js';
	import { contentApi } from '$lib/api/content.js';
	import { slide } from 'svelte/transition';
	import SkeletonCard from '$lib/components/SkeletonCard.svelte';
	import YouTubeEmbed from '$lib/components/YouTubeEmbed.svelte';
	import Icon from '$lib/components/Icon.svelte';

	// Same safe 11-char-ID matcher used by YouTubeEmbed — accepts watch, youtu.be,
	// embed and shorts forms. Used as an Error-Prevention guard so we never call
	// the API for input that obviously isn't a YouTube link.
	const YT_ID = /(?:v=|youtu\.be\/|embed\/|shorts\/)([A-Za-z0-9_-]{11})/;
	function extractId(u) {
		const m = u?.match(YT_ID);
		return m ? m[1] : '';
	}

	/** @typedef {{ video_id:string, title:string, description:string, thumbnail_url:string, duration_seconds:number|null, channel_title:string }} VideoMeta */

	let url = $state('');
	/** @type {'idle'|'invalid'|'fetching'|'ready'|'error'} */
	let status = $state('idle');
	/** @type {VideoMeta|null} */
	let meta = $state(null);
	let fetchError = $state('');

	let title = $state('');
	let body = $state('');
	let publishNow = $state(true);

	/** @typedef {{ slug:string, name:string }} Subcategory */
	/** @typedef {{ slug:string, name:string, subcategories:Subcategory[] }} Category */
	/** @type {Category[]} */
	let categories = $state([]);
	let categorySlug = $state('');
	let subcategorySlug = $state('');

	// Subcategories of the chosen category — the cascade source. Reactive, no fetch.
	const subcategoryOptions = $derived(
		categories.find((c) => c.slug === categorySlug)?.subcategories ?? []
	);

	onMount(async () => {
		try {
			categories = (await contentApi.categories()) ?? [];
		} catch {
			categories = [];
		}
	});

	// Changing the parent clears the child so a stale pair can never be submitted.
	$effect(() => {
		void categorySlug;
		subcategorySlug = '';
	});

	let submitting = $state(false);
	let submitError = $state('');
	let done = $state(false);
	let lastPublished = $state(true);

	let debounce;
	// Monotonic request id — guards against a slow earlier fetch resolving after a
	// newer one (race) and clobbering fresher state.
	let reqId = 0;

	const canSubmit = $derived(
		status === 'ready' && url.trim().length > 0 && title.trim().length > 0 && !submitting
	);

	// Respect prefers-reduced-motion for the field reveal.
	let reduceMotion = $state(false);
	$effect(() => {
		if (typeof window === 'undefined' || !window.matchMedia) return;
		const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
		reduceMotion = mq.matches;
		const sync = () => (reduceMotion = mq.matches);
		mq.addEventListener('change', sync);
		return () => mq.removeEventListener('change', sync);
	});

	function onUrlInput() {
		clearTimeout(debounce);
		fetchError = '';
		meta = null;
		const trimmed = url.trim();
		if (!trimmed) {
			status = 'idle';
			return;
		}
		if (!extractId(trimmed)) {
			status = 'invalid';
			return;
		}
		// Surface feedback immediately (Doherty), fetch after the debounce settles.
		status = 'fetching';
		debounce = setTimeout(fetchMeta, debounceMs);
	}

	async function fetchMeta() {
		const trimmed = url.trim();
		if (!extractId(trimmed)) {
			status = 'invalid';
			return;
		}
		const myReq = ++reqId;
		status = 'fetching';
		fetchError = '';
		try {
			const data = await contentApi.youtubeMetadata(trimmed);
			if (myReq !== reqId) return; // stale response
			meta = data;
			if (!title.trim()) title = data.title ?? '';
			if (!body.trim()) body = data.description ?? '';
			status = 'ready';
		} catch (e) {
			if (myReq !== reqId) return;
			fetchError = e?.data?.error?.message || e?.message || $t('manage.create.fetchError');
			status = 'error';
		}
	}

	async function submit() {
		if (!canSubmit) return;
		submitting = true;
		submitError = '';
		try {
			await contentApi.create({
				type: 'video',
				title: title.trim(),
				body: body.trim(),
				youtube_url: url.trim(),
				duration_seconds: meta?.duration_seconds ?? null,
				category: categorySlug || null,
				subcategory: subcategorySlug || null,
				is_published: publishNow
			});
			lastPublished = publishNow;
			done = true;
			reset();
		} catch (e) {
			submitError = e?.data?.error?.message || e?.message || $t('manage.create.submitError');
		} finally {
			submitting = false;
		}
	}

	function reset() {
		url = '';
		title = '';
		body = '';
		meta = null;
		publishNow = true;
		categorySlug = '';
		subcategorySlug = '';
		fetchError = '';
		status = 'idle';
		reqId++; // invalidate any in-flight fetch
	}

	function createAnother() {
		done = false;
	}

	function formatDuration(secs) {
		if (!secs) return '';
		const h = Math.floor(secs / 3600);
		const m = Math.floor((secs % 3600) / 60);
		const s = secs % 60;
		const pad = (n) => String(n).padStart(2, '0');
		return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`;
	}
</script>

{#if done}
	<div class="py-16 text-center" aria-live="polite">
		<div
			class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900/40"
		>
			<Icon name="check" size={28} strokeWidth={2.5} class="text-emerald-600 dark:text-emerald-400" />
		</div>
		<h2 class="mb-1 text-lg font-bold text-stone-900 dark:text-stone-50">
			{$t('manage.create.successTitle')}
		</h2>
		<p class="mb-6 text-sm text-stone-500 dark:text-stone-400">
			{lastPublished ? $t('manage.create.successPublished') : $t('manage.create.successDraft')}
		</p>
		<button type="button" onclick={createAnother} class="btn-primary min-h-12 px-6">
			{$t('manage.create.another')}
		</button>
	</div>
{:else}
	<form class="space-y-5" novalidate onsubmit={(e) => (e.preventDefault(), submit())}>
		<!-- ── YouTube URL ──────────────────────────────────────────────────────── -->
		<div>
			<label for="yt-url" class="mb-1.5 block text-sm font-medium text-stone-700 dark:text-stone-300">
				{$t('manage.create.urlLabel')}
			</label>
			<div class="relative">
				<input
					id="yt-url"
					type="url"
					inputmode="url"
					autocomplete="off"
					class="input-field min-h-12 pe-11"
					placeholder={$t('manage.create.urlPlaceholder')}
					bind:value={url}
					oninput={onUrlInput}
					aria-describedby="yt-url-status"
					aria-invalid={status === 'invalid' || status === 'error'}
				/>
				<span class="pointer-events-none absolute inset-y-0 end-3 flex items-center">
					{#if status === 'fetching'}
						<span
							class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-stone-300 border-t-emerald-600 dark:border-stone-600 dark:border-t-emerald-400"
							aria-hidden="true"
						></span>
					{:else if status === 'ready'}
						<span class="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-600 text-white">
							<Icon name="check" size={12} strokeWidth={3} />
						</span>
					{/if}
				</span>
			</div>
			<p id="yt-url-status" class="mt-1.5 min-h-4 text-xs" aria-live="polite">
				{#if status === 'invalid'}
					<span class="text-amber-600 dark:text-amber-500">{$t('manage.create.invalidUrl')}</span>
				{:else if status === 'fetching'}
					<span class="text-stone-500 dark:text-stone-400">{$t('manage.create.fetching')}</span>
				{:else if status === 'error'}
					<span class="text-red-600 dark:text-red-400">{fetchError}</span>
					<button
						type="button"
						onclick={fetchMeta}
						class="ms-1 font-semibold text-emerald-700 underline underline-offset-2 dark:text-emerald-400"
					>
						{$t('manage.create.retry')}
					</button>
				{:else}
					<span class="text-stone-500 dark:text-stone-500">{$t('manage.create.urlHint')}</span>
				{/if}
			</p>
		</div>

		<!-- ── Preview slot (skeleton ↔ play-preview share the aspect-video footprint) ── -->
		{#if status === 'fetching'}
			<div aria-busy="true">
				<span class="sr-only">{$t('manage.create.fetching')}</span>
				<SkeletonCard type="video" count={1} />
			</div>
		{:else if status === 'ready' && meta}
			<figure class="card overflow-hidden" transition:slide={{ duration: reduceMotion ? 0 : 200 }}>
				<YouTubeEmbed {url} title={meta.title} thumbnail={meta.thumbnail_url} />
				<figcaption class="space-y-2 p-4">
					{#if meta.channel_title || meta.duration_seconds}
						<div class="flex flex-wrap items-center gap-2">
							{#if meta.channel_title}
								<span class="badge badge-stone">{meta.channel_title}</span>
							{/if}
							{#if meta.duration_seconds}
								<span class="badge badge-stone gap-1">
									<Icon name="clock" size={12} />
									{formatDuration(meta.duration_seconds)}
								</span>
							{/if}
						</div>
					{/if}
					<h3 class="text-base font-bold leading-snug text-stone-900 dark:text-stone-50">
						{meta.title}
					</h3>
				</figcaption>
			</figure>
		{/if}

		<!-- ── Details (progressive disclosure — revealed once metadata resolves) ──── -->
		{#if status === 'ready'}
			<div class="space-y-5" transition:slide={{ duration: reduceMotion ? 0 : 200 }}>
				<div>
					<label
						for="v-title"
						class="mb-1.5 block text-sm font-medium text-stone-700 dark:text-stone-300"
					>
						{$t('manage.create.titleLabel')}
						<span class="text-red-600" aria-hidden="true">*</span>
					</label>
					<input
						id="v-title"
						type="text"
						required
						maxlength="300"
						class="input-field min-h-12"
						placeholder={$t('manage.create.titlePlaceholder')}
						bind:value={title}
					/>
				</div>

				<div>
					<label
						for="v-desc"
						class="mb-1.5 block text-sm font-medium text-stone-700 dark:text-stone-300"
					>
						{$t('manage.create.descriptionLabel')}
					</label>
					<textarea
						id="v-desc"
						rows="4"
						class="input-field resize-y"
						placeholder={$t('manage.create.descriptionPlaceholder')}
						bind:value={body}
					></textarea>
				</div>

				<!-- ── Classification (cascading category → subcategory) ─────────────── -->
				<div>
					<label
						for="v-category"
						class="mb-1.5 block text-sm font-medium text-stone-700 dark:text-stone-300"
					>
						{$t('manage.create.categoryLabel')}
					</label>
					<select id="v-category" class="input-field min-h-12" bind:value={categorySlug}>
						<option value="">{$t('manage.create.categoryNone')}</option>
						{#each categories as c (c.slug)}
							<option value={c.slug}>{c.name}</option>
						{/each}
					</select>
				</div>

				{#if subcategoryOptions.length > 0}
					<div transition:slide={{ duration: reduceMotion ? 0 : 200 }}>
						<label
							for="v-subcategory"
							class="mb-1.5 block text-sm font-medium text-stone-700 dark:text-stone-300"
						>
							{$t('manage.create.subcategoryLabel')}
						</label>
						<select id="v-subcategory" class="input-field min-h-12" bind:value={subcategorySlug}>
							<option value="">{$t('manage.create.categoryNone')}</option>
							{#each subcategoryOptions as s (s.slug)}
								<option value={s.slug}>{s.name}</option>
							{/each}
						</select>
					</div>
				{/if}

				<label class="flex min-h-12 cursor-pointer select-none items-center gap-3">
					<input type="checkbox" bind:checked={publishNow} class="h-5 w-5 rounded accent-emerald-600" />
					<span class="text-sm text-stone-700 dark:text-stone-300">
						{$t('manage.create.publishNow')}
					</span>
					<span class="text-xs text-stone-500 dark:text-stone-500">
						{$t('manage.create.publishHint')}
					</span>
				</label>
			</div>
		{/if}

		{#if submitError}
			<p
				class="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300"
				aria-live="assertive"
			>
				{submitError}
			</p>
		{/if}

		<button type="submit" disabled={!canSubmit} class="btn-primary min-h-12 w-full">
			{#if submitting}
				<span
					class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"
					aria-hidden="true"
				></span>
				{$t('manage.create.submitting')}
			{:else}
				<Icon name={publishNow ? 'check' : 'video'} size={16} />
				{publishNow ? $t('manage.create.publish') : $t('manage.create.saveDraft')}
			{/if}
		</button>
	</form>
{/if}
