<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { t } from '$lib/stores/locale.js';
	import { authApi } from '$lib/api/auth.js';
	import { extractErrors } from '$lib/api/client.js';
	import Icon from '$lib/components/Icon.svelte';

	let status  = $state('verifying'); // 'verifying' | 'success' | 'error'
	let message = $state('');

	onMount(async () => {
		const token = $page.url.searchParams.get('token');
		if (!token) {
			status = 'error';
			message = $t('auth.verifyInvalid');
			return;
		}
		try {
			await authApi.verifyEmail(token);
			status = 'success';
		} catch (err) {
			status = 'error';
			message = extractErrors(err).non_field || $t('auth.verifyInvalid');
		}
	});
</script>

<svelte:head>
	<title>{$t('auth.verifyTitle')} — {$t('app.name')}</title>
</svelte:head>

<div class="text-center" aria-live="polite">
	{#if status === 'verifying'}
		<div class="w-12 h-12 rounded-full mx-auto mb-5
		            border-2 border-stone-200 dark:border-stone-700
		            border-t-emerald-600 dark:border-t-emerald-500
		            motion-safe:animate-spin"
		     aria-hidden="true">
		</div>
		<p class="text-sm text-stone-500 dark:text-stone-400">{$t('auth.verifyChecking')}</p>

	{:else if status === 'success'}
		<div class="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-5
		            bg-emerald-100 dark:bg-emerald-900/40">
			<Icon name="check" size={26} strokeWidth={2.5} class="text-emerald-700 dark:text-emerald-400" />
		</div>
		<h1 class="font-display text-2xl font-semibold tracking-tight mb-2 text-stone-900 dark:text-stone-50">
			{$t('auth.verifyDone')}
		</h1>
		<a href="/login" class="btn-primary text-sm mt-4">{$t('auth.login')}</a>

	{:else}
		<div class="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-5
		            bg-red-50 dark:bg-red-900/20">
			<Icon name="x" size={26} strokeWidth={2.5} class="text-red-600 dark:text-red-400" />
		</div>
		<h1 class="font-display text-2xl font-semibold tracking-tight mb-2 text-stone-900 dark:text-stone-50">
			{$t('auth.verifyFailed')}
		</h1>
		<p class="text-sm mb-4 text-stone-500 dark:text-stone-400">{message}</p>
		<a href="/login" class="btn-ghost text-sm">{$t('auth.backToLogin')}</a>
	{/if}
</div>
