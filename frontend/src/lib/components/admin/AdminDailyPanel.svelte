<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/locale.js';
	import { adminApi } from '$lib/api/admin.js';
	import Icon from '$lib/components/Icon.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';

	let entries = $state([]);
	let loading = $state(true);
	let error = $state('');
	let busy = $state(false);
	let actionError = $state('');
	let confirmDelete = $state('');

	// Editor state
	let editorOpen = $state(false);
	let editingId = $state(null); // public_id when editing, null when creating
	let formDate = $state('');
	let formItems = $state([]); // [{ public_id, title }]
	let pickQuery = $state('');
	let pickResults = $state([]);
	let pickDebounce;

	async function load() {
		loading = true;
		error = '';
		try {
			const data = await adminApi.listDaily();
			entries = data.results ?? data;
		} catch (e) {
			error = e.message || $t('ui.error');
		} finally {
			loading = false;
		}
	}

	function openCreate() {
		editingId = null;
		formDate = new Date().toISOString().slice(0, 10);
		formItems = [];
		pickQuery = '';
		pickResults = [];
		editorOpen = true;
	}

	function openEdit(entry) {
		editingId = entry.public_id;
		formDate = entry.date;
		formItems = (entry.items_detail ?? []).map((i) => ({ public_id: i.public_id, title: i.title }));
		pickQuery = '';
		pickResults = [];
		editorOpen = true;
	}

	function onPick() {
		clearTimeout(pickDebounce);
		pickDebounce = setTimeout(async () => {
			const term = pickQuery.trim();
			if (!term) {
				pickResults = [];
				return;
			}
			try {
				const data = await adminApi.listContent({ scope: 'all', search: term });
				const rows = data.results ?? data;
				const have = new Set(formItems.map((i) => i.public_id));
				pickResults = rows.filter((r) => !have.has(r.public_id)).slice(0, 8);
			} catch {
				pickResults = [];
			}
		}, 300);
	}

	function addItem(row) {
		formItems = [...formItems, { public_id: row.public_id, title: row.title }];
		pickResults = pickResults.filter((r) => r.public_id !== row.public_id);
	}

	function removeItem(pid) {
		formItems = formItems.filter((i) => i.public_id !== pid);
	}

	async function save() {
		if (busy || !formDate) return;
		busy = true;
		actionError = '';
		const body = { date: formDate, items: formItems.map((i) => i.public_id) };
		try {
			if (editingId) await adminApi.updateDaily(editingId, body);
			else await adminApi.createDaily(body);
			editorOpen = false;
			await load();
		} catch (e) {
			actionError = e?.data?.error?.message || e.message || $t('ui.error');
		} finally {
			busy = false;
		}
	}

	async function remove(id) {
		if (busy) return;
		busy = true;
		actionError = '';
		try {
			await adminApi.deleteDaily(id);
			await load();
		} catch (e) {
			actionError = e?.data?.error?.message || e.message || $t('ui.error');
		} finally {
			busy = false;
			confirmDelete = '';
		}
	}

	onMount(load);
</script>

<div class="mb-4 flex items-center justify-between">
	<h3 class="text-sm font-bold text-stone-900 dark:text-stone-50">{$t('admin.daily.title')}</h3>
	{#if !editorOpen}
		<button onclick={openCreate} class="btn-primary min-h-10 px-4 text-sm"
			><Icon name="plus" size={14} />{$t('admin.daily.new')}</button
		>
	{/if}
</div>

{#if actionError}
	<p
		class="mb-3 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300"
		role="alert"
	>
		{actionError}
	</p>
{/if}

{#if editorOpen}
	<!-- ── Editor ──────────────────────────────────────────────────────────── -->
	<div class="card mb-5 space-y-4 p-4">
		<div>
			<label
				for="daily-date"
				class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
				>{$t('admin.daily.date')}</label
			>
			<input id="daily-date" type="date" class="input-field min-h-11" bind:value={formDate} />
		</div>

		<div>
			<label
				for="daily-pick"
				class="mb-1.5 text-sm font-medium text-stone-700 dark:text-stone-300 block"
				>{$t('admin.daily.addContent')}</label
			>
			<input
				id="daily-pick"
				type="search"
				class="input-field min-h-11"
				placeholder={$t('admin.daily.searchContent')}
				bind:value={pickQuery}
				oninput={onPick}
			/>
			{#if pickResults.length}
				<div class="mt-2 space-y-1 rounded-xl border-stone-200 p-1 dark:border-stone-700 border">
					{#each pickResults as r (r.public_id)}
						<button
							onclick={() => addItem(r)}
							class="gap-2 rounded-lg px-3 py-2 text-sm hover:bg-stone-100 dark:hover:bg-stone-800 flex w-full items-center text-start"
						>
							<Icon name="plus" size={13} class="text-emerald-600" />
							<span class="text-stone-700 dark:text-stone-300 truncate">{r.title}</span>
							<span class="badge badge-stone ms-auto">{r.type}</span>
						</button>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Staged items -->
		{#if formItems.length}
			<div class="space-y-2">
				{#each formItems as i (i.public_id)}
					<div
						class="gap-2 rounded-lg bg-stone-50 px-3 py-2 dark:bg-stone-800/60 flex items-center"
					>
						<Icon name="spark" size={13} class="text-emerald-600" />
						<span class="text-sm text-stone-700 dark:text-stone-300 truncate">{i.title}</span>
						<button
							onclick={() => removeItem(i.public_id)}
							class="text-stone-400 hover:text-red-600 ms-auto"
							aria-label={$t('ui.delete')}><Icon name="x" size={14} /></button
						>
					</div>
				{/each}
			</div>
		{:else}
			<p class="text-sm text-stone-400 dark:text-stone-500">{$t('admin.daily.noItems')}</p>
		{/if}

		<div class="gap-2 flex">
			<button onclick={save} disabled={busy || !formDate} class="btn-primary min-h-11 px-5 text-sm"
				>{$t('ui.save')}</button
			>
			<button onclick={() => (editorOpen = false)} class="btn-ghost min-h-11 px-5 text-sm"
				>{$t('ui.cancel')}</button
			>
		</div>
	</div>
{/if}

{#if loading}
	<div class="card p-6"><div class="shimmer h-5 rounded w-1/3"></div></div>
{:else if error}
	<EmptyState icon="x" tone="error" title={error}
		><button onclick={load} class="btn-ghost text-sm">{$t('ui.retry')}</button></EmptyState
	>
{:else if entries.length === 0 && !editorOpen}
	<EmptyState icon="sun" title={$t('admin.daily.empty')} />
{:else}
	<div class="space-y-3">
		{#each entries as e (e.public_id)}
			<div class="card p-4">
				<div class="gap-2 flex items-center">
					<Icon name="sun" size={16} class="text-amber-500" />
					<span class="text-sm font-semibold text-stone-900 dark:text-stone-50">{e.date}</span>
					<span class="badge badge-stone"
						>{(e.items_detail ?? []).length} {$t('admin.daily.items')}</span
					>
					<span class="gap-1 ms-auto flex items-center">
						<button
							onclick={() => openEdit(e)}
							class="rounded-lg p-2 text-stone-400 hover:bg-stone-100 hover:text-stone-700 dark:hover:bg-stone-800"
							aria-label={$t('ui.edit')}><Icon name="edit" size={14} /></button
						>
						{#if confirmDelete === e.public_id}
							<button
								onclick={() => remove(e.public_id)}
								disabled={busy}
								class="rounded-lg px-2 py-1 text-xs font-semibold text-red-600 dark:text-red-400"
								>{$t('admin.confirm')}</button
							>
						{:else}
							<button
								onclick={() => (confirmDelete = e.public_id)}
								class="rounded-lg p-2 text-stone-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
								aria-label={$t('ui.delete')}><Icon name="x" size={14} /></button
							>
						{/if}
					</span>
				</div>
				{#if (e.items_detail ?? []).length}
					<div class="mt-2 gap-1.5 flex flex-wrap">
						{#each e.items_detail as i (i.public_id)}<span class="badge badge-accent"
								>{i.title}</span
							>{/each}
					</div>
				{/if}
			</div>
		{/each}
	</div>
{/if}
