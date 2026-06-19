<script>
	import { t } from '$lib/stores/locale.js';
	import { authApi } from '$lib/api/auth.js';
	import { extractErrors } from '$lib/api/client.js';
	import Icon from '$lib/components/Icon.svelte';

	let email   = $state('');
	let loading = $state(false);
	let sent    = $state(false);
	let errors  = $state({});

	async function handleSubmit(e) {
		e.preventDefault();
		errors = {};
		loading = true;
		try {
			await authApi.requestPasswordReset(email);
			sent = true;
		} catch (err) {
			errors = extractErrors(err);
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>{$t('auth.forgotTitle')} — {$t('app.name')}</title>
</svelte:head>

<div>
	<h1 class="font-display text-[1.7rem] font-semibold tracking-tight mb-1 text-stone-900 dark:text-stone-50">
		{$t('auth.forgotTitle')}
	</h1>
	<p class="text-sm mb-8 text-stone-500 dark:text-stone-400">{$t('auth.forgotSubtitle')}</p>

	{#if sent}
		<div class="flex items-start gap-2 p-4 rounded-xl mb-5 text-sm
		            bg-emerald-50 dark:bg-emerald-900/30
		            border border-emerald-200 dark:border-emerald-800/50
		            text-emerald-700 dark:text-emerald-400">
			<Icon name="check" size={16} strokeWidth={2.5} class="shrink-0 mt-0.5" />
			{$t('auth.forgotSent')}
		</div>
		<a href="/login" class="btn-ghost text-sm">
			<Icon name="arrowLeft" size={14} />
			{$t('auth.backToLogin')}
		</a>

	{:else}
		{#if errors.non_field}
			<div class="flex items-start gap-2 p-3 rounded-xl mb-5 text-sm
			            bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400
			            border border-red-200 dark:border-red-800/60"
			     role="alert">
				<Icon name="x" size={15} strokeWidth={2} class="shrink-0 mt-0.5" />
				{errors.non_field}
			</div>
		{/if}

		<form onsubmit={handleSubmit} novalidate>
			<div class="mb-6">
				<label class="block text-sm font-medium mb-1.5 text-stone-700 dark:text-stone-300"
				       for="fp-email">
					{$t('auth.email')}
				</label>
				<input
					id="fp-email"
					type="email"
					class="input-field"
					placeholder={$t('auth.emailPlaceholder')}
					bind:value={email}
					autocomplete="email"
					required
				/>
			</div>

			<button type="submit" class="btn-primary w-full py-3 text-base" disabled={loading} aria-busy={loading}>
				{#if loading}
					<span class="inline-block w-4 h-4 rounded-full border-2 border-white/30 border-t-white
					             motion-safe:animate-spin" aria-hidden="true"></span>
				{/if}
				{loading ? $t('ui.loading') : $t('auth.sendResetLink')}
			</button>
		</form>

		<p class="text-center text-sm mt-6 text-stone-500 dark:text-stone-400">
			<a href="/login" class="font-semibold text-emerald-700 dark:text-emerald-400 hover:underline">
				{$t('auth.backToLogin')}
			</a>
		</p>
	{/if}
</div>
