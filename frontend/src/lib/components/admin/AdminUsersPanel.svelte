<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/locale.js';
	import { currentUser } from '$lib/stores/auth.js';
	import { adminApi } from '$lib/api/admin.js';
	import Icon from '$lib/components/Icon.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';

	let users = $state([]);
	let loading = $state(true);
	let error = $state('');
	let search = $state('');
	let busyId = $state('');
	let rowError = $state('');
	let searchDebounce;

	const ROLES = ['user', 'content_manager', 'sheikh'];

	async function load() {
		loading = true;
		error = '';
		try {
			const data = await adminApi.listUsers({ search: search.trim() });
			users = data.results ?? data;
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

	/** @param {any} u @param {Record<string, any>} patch */
	async function update(u, patch) {
		if (busyId) return;
		busyId = u.public_id;
		rowError = '';
		try {
			const updated = await adminApi.updateUser(u.public_id, patch);
			users = users.map((x) => (x.public_id === u.public_id ? updated : x));
		} catch (e) {
			rowError = e?.data?.error?.message || e.message || $t('ui.error');
		} finally {
			busyId = '';
		}
	}

	const isSelf = (u) => u.public_id === $currentUser?.public_id;

	onMount(load);
</script>

<div class="mb-4">
	<div class="relative">
		<input
			type="search"
			class="input-field pe-11"
			placeholder={$t('admin.users.search')}
			bind:value={search}
			oninput={onSearch}
		/>
		<Icon
			name="search"
			size={16}
			class="pointer-events-none absolute top-1/2 end-3.5 -translate-y-1/2 text-stone-400 dark:text-stone-500"
		/>
	</div>
</div>

{#if rowError}
	<p class="mb-3 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300" role="alert">
		{rowError}
	</p>
{/if}

{#if loading}
	<div class="space-y-3">
		{#each Array(4) as _}
			<div class="card p-4"><div class="shimmer h-5 w-1/2 rounded"></div></div>
		{/each}
	</div>
{:else if error}
	<EmptyState icon="x" tone="error" title={error}>
		<button onclick={load} class="btn-ghost text-sm">{$t('ui.retry')}</button>
	</EmptyState>
{:else if users.length === 0}
	<EmptyState icon="user" title={$t('ui.noResults')} />
{:else}
	<div class="space-y-3">
		{#each users as u (u.public_id)}
			<div class="card flex flex-wrap items-center gap-3 p-4 {u.is_active ? '' : 'opacity-60'}">
				<div class="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-emerald-700 text-sm font-bold text-white">
					{(u.name || u.username)?.charAt(0)?.toUpperCase() || '?'}
				</div>
				<div class="min-w-0 flex-1">
					<p class="truncate text-sm font-semibold text-stone-900 dark:text-stone-50">
						{u.name || u.username}
						{#if isSelf(u)}<span class="ms-1 text-xs font-normal text-stone-400">({$t('admin.users.you')})</span>{/if}
					</p>
					<p class="truncate text-xs text-stone-400 dark:text-stone-500">{u.email}</p>
				</div>

				<!-- Role -->
				<select
					class="input-field min-h-10 w-auto py-1.5 text-sm"
					value={u.role}
					disabled={isSelf(u) || busyId === u.public_id}
					onchange={(e) => update(u, { role: e.currentTarget.value })}
					aria-label={$t('admin.users.role')}
				>
					{#each ROLES as r}
						<option value={r}>{$t(`profile.role.${r}`)}</option>
					{/each}
				</select>

				<!-- Active toggle -->
				<button
					type="button"
					onclick={() => update(u, { is_active: !u.is_active })}
					disabled={isSelf(u) || busyId === u.public_id}
					class={[
						'min-h-10 rounded-full border px-3 text-xs font-semibold transition-colors disabled:opacity-40',
						u.is_active
							? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-400'
							: 'border-stone-200 bg-stone-50 text-stone-500 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-400'
					]}
				>
					{u.is_active ? $t('admin.users.active') : $t('admin.users.inactive')}
				</button>
			</div>
		{/each}
	</div>
{/if}
