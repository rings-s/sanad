<script>
	import { onMount } from 'svelte';
	import { t, locale } from '$lib/stores/locale.js';
	import { contentApi } from '$lib/api/content.js';
	import Icon from '$lib/components/Icon.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';

	let comments = $state([]);
	let loading = $state(true);
	let error = $state('');
	let busyId = $state('');

	async function load() {
		loading = true;
		error = '';
		try {
			const data = await contentApi.pendingComments();
			comments = data.results ?? data;
		} catch (e) {
			error = e.message || $t('ui.error');
		} finally {
			loading = false;
		}
	}

	async function approve(c) {
		if (busyId) return;
		busyId = c.public_id;
		try {
			await contentApi.approveComment(c.public_id);
			comments = comments.filter((x) => x.public_id !== c.public_id);
		} catch (e) {
			error = e.message || $t('ui.error');
		}
		busyId = '';
	}

	async function reject(c) {
		if (busyId) return;
		busyId = c.public_id;
		try {
			await contentApi.rejectComment(c.public_id);
			comments = comments.filter((x) => x.public_id !== c.public_id);
		} catch (e) {
			error = e.message || $t('ui.error');
		}
		busyId = '';
	}

	function formatDate(s) {
		if (!s) return '';
		return new Date(s).toLocaleDateString($locale === 'ar' ? 'ar-SA' : 'en-US', {
			dateStyle: 'medium'
		});
	}

	onMount(load);
</script>

{#if loading}
	<div class="space-y-3">
		{#each Array(3) as _}
			<div class="card p-4">
				<div class="shimmer mb-2 h-4 rounded w-full"></div>
				<div class="shimmer h-4 rounded w-2/3"></div>
			</div>
		{/each}
	</div>
{:else if error}
	<EmptyState icon="x" tone="error" title={error}>
		<button onclick={load} class="btn-ghost text-sm">{$t('ui.retry')}</button>
	</EmptyState>
{:else if comments.length === 0}
	<EmptyState icon="check" title={$t('manage.noComments')} />
{:else}
	<h2 class="mb-4 text-sm font-bold text-stone-900 dark:text-stone-50">
		{$t('manage.comments')} ({comments.length})
	</h2>
	<div class="space-y-3">
		{#each comments as c (c.public_id)}
			<article class="card p-4">
				<p class="mb-2 text-sm leading-snug text-stone-900 dark:text-stone-50">{c.text}</p>
				<p class="mb-3 text-xs text-stone-400 dark:text-stone-500">
					{c.user?.name || c.user?.username || ''} · {formatDate(c.created_at)}
				</p>
				<div class="gap-2 flex items-center">
					<button
						onclick={() => approve(c)}
						class="btn-primary min-h-0 px-4 py-2 text-sm"
						disabled={!!busyId}
					>
						<Icon name="check" size={13} />{$t('manage.approve')}
					</button>
					<button
						onclick={() => reject(c)}
						class="btn-ghost min-h-0 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
						disabled={!!busyId}
					>
						{$t('manage.reject')}
					</button>
				</div>
			</article>
		{/each}
	</div>
{/if}
