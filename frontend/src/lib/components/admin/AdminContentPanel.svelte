<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/locale.js';
	import { currentUser } from '$lib/stores/auth.js';
	import { adminApi } from '$lib/api/admin.js';
	import { contentApi } from '$lib/api/content.js';
	import Icon from '$lib/components/Icon.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import ImageUploadField from '$lib/components/ImageUploadField.svelte';

	// Sheikh manages every author's content (incl. drafts + archived) and is the
	// only role that can archive / restore / delete. A content manager manages
	// only their own non-archived content. The backend enforces both.
	const isSheikh = $derived($currentUser?.is_sheikh === true);

	const TYPES = ['post', 'video', 'audio', 'note', 'hadith'];
	const TYPE_ICON = {
		post: 'notepad',
		video: 'video',
		audio: 'headphones',
		note: 'notepad',
		hadith: 'star'
	};

	let items = $state([]);
	let categories = $state([]);
	let allTags = $state([]);
	let loading = $state(true);
	let error = $state('');
	let search = $state('');
	let typeFilter = $state('');
	let busyId = $state('');
	let listError = $state('');
	let searchDebounce;

	// Editor
	let editorOpen = $state(false);
	let editingId = $state(null);
	let saving = $state(false);
	let formError = $state('');
	let confirmDelete = $state('');

	const blank = () => ({
		type: 'post',
		title: '',
		body: '',
		category: '',
		subcategory: '',
		tags: [],
		youtube_url: '',
		duration_seconds: '',
		original_text: '',
		translated_text: '',
		source_attribution: '',
		is_published: false,
		is_archived: false,
		featured_image: null,
		featured_image_url: '',
		remove_featured_image: false,
		audio_file: null,
		document: null
	});
	let form = $state(blank());

	const subcategoryOptions = $derived(
		categories.find((c) => c.slug === form.category)?.subcategories ?? []
	);

	async function load() {
		loading = true;
		listError = '';
		try {
			const data = await adminApi.listContent(
				isSheikh
					? { scope: 'all', search: search.trim(), type: typeFilter }
					: { mine: 1, search: search.trim(), type: typeFilter }
			);
			items = data.results ?? data;
		} catch (e) {
			error = e.message || $t('ui.error');
		} finally {
			loading = false;
		}
	}

	function onSearch() {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(load, 300);
	}

	$effect(() => {
		void typeFilter;
		load();
	});

	function openCreate() {
		editingId = null;
		form = blank();
		formError = '';
		editorOpen = true;
	}

	async function openEdit(row) {
		editingId = row.public_id;
		formError = '';
		try {
			const d = await adminApi.getContent(row.public_id);
			form = {
				type: d.type,
				title: d.title || '',
				body: d.body || '',
				category: d.category?.slug || '',
				subcategory: d.subcategory?.slug || '',
				tags: (d.tags ?? []).map((tg) => tg.slug),
				youtube_url: d.youtube_url || '',
				duration_seconds: d.duration_seconds || '',
				original_text: d.original_text || '',
				translated_text: d.translated_text || '',
				source_attribution: d.source_attribution || '',
				is_published: !!d.is_published,
				is_archived: !!d.is_archived,
				featured_image: null,
				featured_image_url: d.featured_image || '',
				remove_featured_image: false,
				audio_file: null,
				document: null
			};
			editorOpen = true;
		} catch (e) {
			listError = e.message || $t('ui.error');
		}
	}

	function toggleTag(slug) {
		form.tags = form.tags.includes(slug)
			? form.tags.filter((s) => s !== slug)
			: [...form.tags, slug];
	}

	function buildForm() {
		const fd = new FormData();
		fd.append('type', form.type);
		fd.append('title', form.title.trim());
		fd.append('body', form.body);
		fd.append('source_attribution', form.source_attribution);
		fd.append('is_published', String(form.is_published));
		if (form.category) fd.append('category', form.category);
		if (form.subcategory) fd.append('subcategory', form.subcategory);
		for (const slug of form.tags) fd.append('tags', slug);
		if (form.type === 'video' && form.youtube_url)
			fd.append('youtube_url', form.youtube_url.trim());
		if (form.duration_seconds) fd.append('duration_seconds', String(form.duration_seconds));
		if (form.type === 'hadith') {
			fd.append('original_text', form.original_text);
			fd.append('translated_text', form.translated_text);
		}
		if (form.featured_image) fd.append('featured_image', form.featured_image);
		else if (editingId && form.remove_featured_image)
			fd.append('remove_featured_image', 'true');
		if (form.type === 'audio' && form.audio_file) fd.append('audio_file', form.audio_file);
		if (form.document) fd.append('document', form.document);
		if (editingId && isSheikh) fd.append('is_archived', String(form.is_archived));
		return fd;
	}

	async function save() {
		if (saving || !form.title.trim()) return;
		saving = true;
		formError = '';
		try {
			const fd = buildForm();
			if (editingId) await adminApi.updateContent(editingId, fd);
			else await adminApi.createContent(fd);
			editorOpen = false;
			await load();
		} catch (e) {
			formError = e?.data?.error?.message || e.message || $t('ui.error');
		} finally {
			saving = false;
		}
	}

	async function rowAction(row, fn) {
		if (busyId) return;
		busyId = row.public_id;
		listError = '';
		try {
			await fn();
			await load();
		} catch (e) {
			listError = e?.data?.error?.message || e.message || $t('ui.error');
		} finally {
			busyId = '';
			confirmDelete = '';
		}
	}

	const togglePublish = (row) =>
		rowAction(row, () => {
			const fd = new FormData();
			fd.append('is_published', String(!row.is_published));
			return adminApi.updateContent(row.public_id, fd);
		});

	onMount(async () => {
		// Public taxonomy endpoints (AllowAny) so both the Sheikh and content
		// managers get the category/tag pickers — the Sheikh-only admin taxonomy
		// endpoints would 403 for a content manager.
		try {
			const [cats, tg] = await Promise.all([contentApi.categories(), contentApi.tags()]);
			categories = cats.results ?? cats;
			allTags = tg.results ?? tg;
		} catch {
			/* taxonomy optional for the editor */
		}
	});
</script>

{#if editorOpen}
	<!-- ── Editor ──────────────────────────────────────────────────────────── -->
	<div class="card mb-5 space-y-4 p-4 sm:p-5">
		<div class="flex items-center justify-between">
			<h3 class="text-sm font-bold text-stone-900 dark:text-stone-50">
				{editingId ? $t('admin.content.edit') : $t('admin.content.new')}
			</h3>
			<button
				onclick={() => (editorOpen = false)}
				class="rounded-lg p-2 text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800"
				aria-label={$t('ui.cancel')}><Icon name="x" size={16} /></button
			>
		</div>

		{#if formError}
			<p
				class="rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300"
				role="alert"
			>
				{formError}
			</p>
		{/if}

		<!-- Type -->
		<div>
			<label
				for="c-type"
				class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
				>{$t('admin.content.type')}</label
			>
			<select
				id="c-type"
				class="input-field min-h-11"
				bind:value={form.type}
				disabled={!!editingId}
			>
				{#each TYPES as ty}<option value={ty}>{$t(`content.type.${ty}`)}</option>{/each}
			</select>
		</div>

		<!-- Title -->
		<div>
			<label
				for="c-title"
				class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
				>{$t('admin.content.titleLabel')} <span class="text-red-600">*</span></label
			>
			<input id="c-title" class="input-field min-h-11" maxlength="300" bind:value={form.title} />
		</div>

		<!-- Type-specific media -->
		{#if form.type === 'video'}
			<div>
				<label
					for="c-yt"
					class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
					>{$t('manage.create.urlLabel')}</label
				>
				<input
					id="c-yt"
					type="url"
					class="input-field min-h-11"
					placeholder={$t('manage.create.urlPlaceholder')}
					bind:value={form.youtube_url}
				/>
			</div>
		{:else if form.type === 'audio'}
			<div>
				<label
					for="c-audio"
					class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
					>{$t('admin.content.audioFile')}</label
				>
				<input
					id="c-audio"
					type="file"
					accept="audio/*"
					class="input-field min-h-11 py-2"
					onchange={(e) => (form.audio_file = e.currentTarget.files?.[0] ?? null)}
				/>
			</div>
		{:else if form.type === 'hadith'}
			<div>
				<label
					for="c-orig"
					class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
					>{$t('admin.content.originalText')}</label
				>
				<textarea id="c-orig" rows="2" class="input-field resize-y" bind:value={form.original_text}
				></textarea>
			</div>
			<div>
				<label
					for="c-trans"
					class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
					>{$t('admin.content.translatedText')}</label
				>
				<textarea
					id="c-trans"
					rows="2"
					class="input-field resize-y"
					bind:value={form.translated_text}
				></textarea>
			</div>
		{/if}

		<!-- Body -->
		<div>
			<label
				for="c-body"
				class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
				>{$t('admin.content.body')}</label
			>
			<textarea id="c-body" rows="4" class="input-field resize-y" bind:value={form.body}></textarea>
		</div>

		<!-- Source attribution -->
		<div>
			<label for="c-src" class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
				>{$t('admin.content.source')}</label
			>
			<input
				id="c-src"
				class="input-field min-h-11"
				maxlength="300"
				bind:value={form.source_attribution}
			/>
		</div>

		<!-- Category / Subcategory -->
		<div class="gap-4 sm:grid-cols-2 grid">
			<div>
				<label
					for="c-cat"
					class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
					>{$t('manage.create.categoryLabel')}</label
				>
				<select
					id="c-cat"
					class="input-field min-h-11"
					bind:value={form.category}
					onchange={() => (form.subcategory = '')}
				>
					<option value="">{$t('manage.create.categoryNone')}</option>
					{#each categories as c (c.slug)}<option value={c.slug}>{c.name}</option>{/each}
				</select>
			</div>
			{#if subcategoryOptions.length}
				<div>
					<label
						for="c-sub"
						class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
						>{$t('manage.create.subcategoryLabel')}</label
					>
					<select id="c-sub" class="input-field min-h-11" bind:value={form.subcategory}>
						<option value="">{$t('manage.create.categoryNone')}</option>
						{#each subcategoryOptions as s (s.slug)}<option value={s.slug}>{s.name}</option>{/each}
					</select>
				</div>
			{/if}
		</div>

		<!-- Tags -->
		{#if allTags.length}
			<div>
				<span class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
					>{$t('admin.tax.tags')}</span
				>
				<div class="gap-2 flex flex-wrap">
					{#each allTags as tg (tg.slug)}
						<button
							type="button"
							onclick={() => toggleTag(tg.slug)}
							class={['chip', form.tags.includes(tg.slug) ? 'chip-on' : 'chip-off']}
							aria-pressed={form.tags.includes(tg.slug)}>{tg.name}</button
						>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Files: featured image + document -->
		<div class="gap-4 sm:grid-cols-2 grid">
			<div>
				<label
					for="c-img"
					class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
					>{$t('admin.content.featuredImage')}</label
				>
				<ImageUploadField
					id="c-img"
					bind:value={form.featured_image}
					existingUrl={form.featured_image_url}
					bind:removeExisting={form.remove_featured_image}
				/>
			</div>
			<div>
				<label
					for="c-doc"
					class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
					>{$t('admin.content.document')}</label
				>
				<input
					id="c-doc"
					type="file"
					accept=".pdf,.doc,.docx"
					class="input-field min-h-11 py-2"
					onchange={(e) => (form.document = e.currentTarget.files?.[0] ?? null)}
				/>
			</div>
		</div>

		<!-- Flags -->
		<div class="gap-5 flex flex-wrap">
			<label class="gap-2.5 flex cursor-pointer items-center">
				<input
					type="checkbox"
					bind:checked={form.is_published}
					class="h-5 w-5 rounded accent-emerald-600"
				/>
				<span class="text-sm text-stone-700 dark:text-stone-300"
					>{$t('admin.content.published')}</span
				>
			</label>
			{#if editingId && isSheikh}
				<label class="gap-2.5 flex cursor-pointer items-center">
					<input
						type="checkbox"
						bind:checked={form.is_archived}
						class="h-5 w-5 rounded accent-red-600"
					/>
					<span class="text-sm text-stone-700 dark:text-stone-300"
						>{$t('admin.content.archived')}</span
					>
				</label>
			{/if}
		</div>

		<div class="gap-2 flex">
			<button
				onclick={save}
				disabled={saving || !form.title.trim()}
				class="btn-primary min-h-11 px-5 text-sm">{$t('ui.save')}</button
			>
			<button onclick={() => (editorOpen = false)} class="btn-ghost min-h-11 px-5 text-sm"
				>{$t('ui.cancel')}</button
			>
		</div>
	</div>
{:else}
	<!-- ── List header: search + type filter + new ─────────────────────────── -->
	<div class="mb-4 gap-2 flex flex-wrap items-center">
		<div class="min-w-48 relative flex-1">
			<input
				type="search"
				class="input-field pe-11"
				placeholder={$t('admin.content.search')}
				bind:value={search}
				oninput={onSearch}
			/>
			<Icon
				name="search"
				size={16}
				class="end-3.5 text-stone-400 dark:text-stone-500 pointer-events-none absolute top-1/2 -translate-y-1/2"
			/>
		</div>
		<button onclick={openCreate} class="btn-primary min-h-12 px-4 text-sm"
			><Icon name="plus" size={14} />{$t('admin.content.new')}</button
		>
	</div>

	<div class="chip-rail mb-4">
		<button
			onclick={() => (typeFilter = '')}
			class={['chip', typeFilter === '' ? 'chip-on' : 'chip-off']}>{$t('feed.filters.all')}</button
		>
		{#each TYPES as ty}
			<button
				onclick={() => (typeFilter = ty)}
				class={['chip', typeFilter === ty ? 'chip-on' : 'chip-off']}
				>{$t(`content.type.${ty}`)}</button
			>
		{/each}
	</div>

	{#if listError}
		<p
			class="mb-3 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300"
			role="alert"
		>
			{listError}
		</p>
	{/if}

	{#if loading}
		<div class="space-y-3">
			{#each Array(5) as _}<div class="card p-4">
					<div class="shimmer h-5 rounded w-2/3"></div>
				</div>{/each}
		</div>
	{:else if error}
		<EmptyState icon="x" tone="error" title={error}
			><button onclick={load} class="btn-ghost text-sm">{$t('ui.retry')}</button></EmptyState
		>
	{:else if items.length === 0}
		<EmptyState icon="notepad" title={$t('ui.noResults')} />
	{:else}
		<div class="space-y-3">
			{#each items as row (row.public_id)}
				<div
					class="card gap-3 p-4 flex flex-wrap items-center {row.is_archived ? 'opacity-60' : ''}"
				>
					<span
						class="h-9 w-9 rounded-xl bg-stone-100 text-stone-500 dark:bg-stone-800 dark:text-stone-400 grid shrink-0 place-items-center"
					>
						<Icon name={TYPE_ICON[row.type] || 'notepad'} size={16} />
					</span>
					<div class="min-w-0 flex-1">
						<p class="text-sm font-semibold text-stone-900 dark:text-stone-50 truncate">
							{row.title}
						</p>
						<div class="mt-0.5 gap-1.5 flex flex-wrap items-center">
							<span class="badge badge-stone">{$t(`content.type.${row.type}`)}</span>
							{#if row.is_archived}
								<span class="badge bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-300"
									>{$t('admin.content.archived')}</span
								>
							{:else if row.is_published}
								<span class="badge badge-accent">{$t('admin.content.published')}</span>
							{:else}
								<span
									class="badge bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300"
									>{$t('admin.content.draft')}</span
								>
							{/if}
						</div>
					</div>

					<div class="gap-1 flex items-center">
						{#if !row.is_archived}
							<button
								onclick={() => togglePublish(row)}
								disabled={busyId === row.public_id}
								class="rounded-lg px-2.5 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-50 dark:text-emerald-400 dark:hover:bg-emerald-950/40"
							>
								{row.is_published ? $t('admin.content.unpublish') : $t('admin.content.publish')}
							</button>
						{/if}
						<button
							onclick={() => openEdit(row)}
							class="rounded-lg p-2 text-stone-400 hover:bg-stone-100 hover:text-stone-700 dark:hover:bg-stone-800"
							aria-label={$t('ui.edit')}><Icon name="edit" size={15} /></button
						>
						{#if isSheikh}
							{#if row.is_archived}
								<button
									onclick={() => rowAction(row, () => adminApi.restoreContent(row.public_id))}
									disabled={busyId === row.public_id}
									class="rounded-lg px-2.5 py-1.5 text-xs font-semibold text-stone-500 hover:bg-stone-100 dark:hover:bg-stone-800"
									>{$t('admin.content.restore')}</button
								>
							{:else if confirmDelete === row.public_id}
								<button
									onclick={() => rowAction(row, () => adminApi.deleteContent(row.public_id))}
									disabled={busyId === row.public_id}
									class="rounded-lg px-2 py-1 text-xs font-semibold text-red-600 dark:text-red-400"
									>{$t('admin.confirm')}</button
								>
							{:else}
								<button
									onclick={() => (confirmDelete = row.public_id)}
									class="rounded-lg p-2 text-stone-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
									aria-label={$t('ui.delete')}><Icon name="x" size={15} /></button
								>
							{/if}
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
{/if}
