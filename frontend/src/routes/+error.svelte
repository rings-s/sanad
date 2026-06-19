<script>
	import { page } from '$app/stores';
	import { t } from '$lib/stores/locale.js';
	import Icon from '$lib/components/Icon.svelte';

	const status = $derived($page.status);
	const isNotFound = $derived(status === 404);
</script>

<svelte:head>
	<title>{isNotFound ? $t('error.notFoundTitle') : $t('error.title')} — {$t('app.name')}</title>
</svelte:head>

<div class="min-h-[100dvh] flex flex-col items-center justify-center px-6 text-center bg-stone-50 dark:bg-stone-950">
	<div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-6 bg-stone-100 dark:bg-stone-800">
		<Icon name={isNotFound ? 'search' : 'x'} size={28} strokeWidth={1.5} class="text-stone-400 dark:text-stone-500" />
	</div>

	<p class="font-display text-5xl font-semibold tracking-tight mb-2 text-emerald-700 dark:text-emerald-400">{status}</p>
	<h1 class="font-display text-xl font-semibold mb-2 text-stone-900 dark:text-stone-50">
		{isNotFound ? $t('error.notFoundTitle') : $t('error.title')}
	</h1>
	<p class="text-sm mb-8 max-w-sm text-stone-500 dark:text-stone-400">
		{isNotFound ? $t('error.notFoundBody') : ($page.error?.message || $t('error.body'))}
	</p>

	<div class="flex items-center gap-3">
		<a href="/" class="btn-primary text-sm">{$t('error.home')}</a>
		<a href="/feed" class="btn-ghost text-sm">{$t('nav.feed')}</a>
	</div>
</div>
