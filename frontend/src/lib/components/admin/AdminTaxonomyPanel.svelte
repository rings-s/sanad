<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/locale.js';
	import { adminApi } from '$lib/api/admin.js';
	import Icon from '$lib/components/Icon.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';

	let categories = $state([]);
	let tags = $state([]);
	let loading = $state(true);
	let error = $state('');
	let busy = $state(false);
	let actionError = $state('');

	// New-item drafts
	let newCat = $state({ name: '', icon: '' });
	let newTag = $state('');
	let newSub = $state({}); // { [categorySlug]: name }

	// Inline edit drafts keyed by slug
	let editCat = $state(null); // { slug, name, icon }
	let editTag = $state(null); // { slug, name }
	let confirmDelete = $state(''); // slug pending confirm

	async function load() {
		loading = true;
		error = '';
		try {
			const [cats, tg] = await Promise.all([adminApi.listCategories(), adminApi.listTags()]);
			categories = cats.results ?? cats;
			tags = tg.results ?? tg;
		} catch (e) {
			error = e.message || $t('ui.error');
		} finally {
			loading = false;
		}
	}

	/** @param {() => Promise<any>} fn */
	async function run(fn) {
		if (busy) return;
		busy = true;
		actionError = '';
		try {
			await fn();
			await load();
		} catch (e) {
			actionError = e?.data?.error?.message || e.message || $t('ui.error');
		} finally {
			busy = false;
			confirmDelete = '';
		}
	}

	const addCategory = () =>
		newCat.name.trim() &&
		run(async () => {
			await adminApi.createCategory({ name: newCat.name.trim(), icon: newCat.icon.trim() });
			newCat = { name: '', icon: '' };
		});

	const saveCategory = () =>
		run(async () => {
			await adminApi.updateCategory(editCat.slug, { name: editCat.name.trim(), icon: editCat.icon.trim() });
			editCat = null;
		});

	const addSubcategory = (catSlug) =>
		newSub[catSlug]?.trim() &&
		run(async () => {
			await adminApi.createSubcategory({ name: newSub[catSlug].trim(), category: catSlug });
			newSub[catSlug] = '';
		});

	const addTag = () =>
		newTag.trim() &&
		run(async () => {
			await adminApi.createTag({ name: newTag.trim() });
			newTag = '';
		});

	const saveTag = () =>
		run(async () => {
			await adminApi.updateTag(editTag.slug, { name: editTag.name.trim() });
			editTag = null;
		});

	onMount(load);
</script>

{#if actionError}
	<p class="mb-3 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300" role="alert">
		{actionError}
	</p>
{/if}

{#if loading}
	<div class="card p-6"><div class="shimmer h-5 w-1/3 rounded"></div></div>
{:else if error}
	<EmptyState icon="x" tone="error" title={error}>
		<button onclick={load} class="btn-ghost text-sm">{$t('ui.retry')}</button>
	</EmptyState>
{:else}
	<!-- ── Categories ──────────────────────────────────────────────────────── -->
	<section class="mb-8">
		<h3 class="mb-3 text-sm font-bold text-stone-900 dark:text-stone-50">{$t('admin.tax.categories')}</h3>

		<!-- Add category -->
		<div class="card mb-4 flex flex-wrap items-end gap-2 p-3">
			<input class="input-field min-h-11 flex-1" placeholder={$t('admin.tax.categoryName')} bind:value={newCat.name} />
			<input class="input-field min-h-11 w-28" placeholder={$t('admin.tax.icon')} bind:value={newCat.icon} />
			<button onclick={addCategory} disabled={busy || !newCat.name.trim()} class="btn-primary min-h-11 px-4 text-sm">
				<Icon name="plus" size={14} />{$t('admin.add')}
			</button>
		</div>

		<div class="space-y-3">
			{#each categories as c (c.slug)}
				<div class="card p-4">
					{#if editCat?.slug === c.slug}
						<div class="flex flex-wrap items-end gap-2">
							<input class="input-field min-h-11 flex-1" bind:value={editCat.name} />
							<input class="input-field min-h-11 w-28" placeholder={$t('admin.tax.icon')} bind:value={editCat.icon} />
							<button onclick={saveCategory} disabled={busy} class="btn-primary min-h-11 px-4 text-sm">{$t('ui.save')}</button>
							<button onclick={() => (editCat = null)} class="btn-ghost min-h-11 px-4 text-sm">{$t('ui.cancel')}</button>
						</div>
					{:else}
						<div class="flex items-center gap-2">
							<span class="text-sm font-semibold text-stone-900 dark:text-stone-50">{c.name}</span>
							{#if c.icon}<span class="badge badge-stone">{c.icon}</span>{/if}
							<span class="ms-auto flex items-center gap-1">
								<button onclick={() => (editCat = { slug: c.slug, name: c.name, icon: c.icon || '' })} class="rounded-lg p-2 text-stone-400 hover:bg-stone-100 hover:text-stone-700 dark:hover:bg-stone-800" aria-label={$t('ui.edit')}>
									<Icon name="edit" size={14} />
								</button>
								{#if confirmDelete === c.slug}
									<button onclick={() => run(() => adminApi.deleteCategory(c.slug))} disabled={busy} class="rounded-lg px-2 py-1 text-xs font-semibold text-red-600 dark:text-red-400">{$t('admin.confirm')}</button>
								{:else}
									<button onclick={() => (confirmDelete = c.slug)} class="rounded-lg p-2 text-stone-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20" aria-label={$t('ui.delete')}>
										<Icon name="x" size={14} />
									</button>
								{/if}
							</span>
						</div>

						<!-- Subcategories -->
						<div class="mt-3 ms-1 flex flex-wrap items-center gap-1.5 border-s border-stone-100 ps-3 dark:border-stone-800">
							{#each c.subcategories ?? [] as s (s.slug)}
								<span class="badge badge-accent gap-1">
									{s.name}
									<button onclick={() => run(() => adminApi.deleteSubcategory(s.slug))} disabled={busy} class="hover:text-red-600" aria-label={$t('ui.delete')}>
										<Icon name="x" size={11} />
									</button>
								</span>
							{/each}
							<span class="inline-flex items-center gap-1">
								<input
									class="input-field min-h-9 w-32 py-1 text-xs"
									placeholder={$t('admin.tax.subName')}
									value={newSub[c.slug] ?? ''}
									oninput={(e) => (newSub[c.slug] = e.currentTarget.value)}
									onkeydown={(e) => e.key === 'Enter' && addSubcategory(c.slug)}
								/>
								<button onclick={() => addSubcategory(c.slug)} disabled={busy} class="rounded-lg p-1.5 text-emerald-700 hover:bg-emerald-50 dark:text-emerald-400 dark:hover:bg-emerald-950/40" aria-label={$t('admin.add')}>
									<Icon name="plus" size={14} />
								</button>
							</span>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	</section>

	<!-- ── Tags ────────────────────────────────────────────────────────────── -->
	<section>
		<h3 class="mb-3 text-sm font-bold text-stone-900 dark:text-stone-50">{$t('admin.tax.tags')}</h3>
		<div class="card mb-4 flex items-end gap-2 p-3">
			<input class="input-field min-h-11 flex-1" placeholder={$t('admin.tax.tagName')} bind:value={newTag} onkeydown={(e) => e.key === 'Enter' && addTag()} />
			<button onclick={addTag} disabled={busy || !newTag.trim()} class="btn-primary min-h-11 px-4 text-sm"><Icon name="plus" size={14} />{$t('admin.add')}</button>
		</div>
		<div class="flex flex-wrap gap-2">
			{#each tags as tag (tag.slug)}
				{#if editTag?.slug === tag.slug}
					<span class="inline-flex items-center gap-1">
						<input class="input-field min-h-9 w-32 py-1 text-xs" bind:value={editTag.name} onkeydown={(e) => e.key === 'Enter' && saveTag()} />
						<button onclick={saveTag} disabled={busy} class="rounded-lg p-1.5 text-emerald-700 dark:text-emerald-400" aria-label={$t('ui.save')}><Icon name="check" size={14} /></button>
					</span>
				{:else}
					<span class="badge badge-stone gap-1.5">
						<button onclick={() => (editTag = { slug: tag.slug, name: tag.name })} class="hover:text-stone-900 dark:hover:text-stone-100">{tag.name}</button>
						<button onclick={() => run(() => adminApi.deleteTag(tag.slug))} disabled={busy} class="hover:text-red-600" aria-label={$t('ui.delete')}><Icon name="x" size={11} /></button>
					</span>
				{/if}
			{/each}
			{#if tags.length === 0}<p class="text-sm text-stone-400">{$t('ui.noResults')}</p>{/if}
		</div>
	</section>
{/if}
