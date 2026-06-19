<script>
	import { fly } from 'svelte/transition';
	import { t } from '$lib/stores/locale.js';
	import { auth } from '$lib/stores/auth.js';
	import { authApi } from '$lib/api/auth.js';
	import { extractErrors } from '$lib/api/client.js';
	import { goto } from '$app/navigation';
	import Icon from '$lib/components/Icon.svelte';
	import GoogleButton from '$lib/components/GoogleButton.svelte';

	let email    = $state('');
	let username = $state('');
	let password = $state('');
	let loading  = $state(false);
	let errors   = $state({});

	async function handleRegister(e) {
		e.preventDefault();
		errors = {};
		loading = true;
		try {
			const data = await authApi.register(email, username, password);
			auth.login(data.user, data.access);
			goto('/feed');
		} catch (err) {
			errors = extractErrors(err);
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>{$t('auth.registerTitle')} — {$t('app.name')}</title>
</svelte:head>

<div in:fly={{ y: 12, duration: 280, easing: (t) => 1 - (1 - t) * (1 - t) }}>
	<h1 class="font-display text-[1.7rem] font-semibold tracking-tight mb-1 text-stone-900 dark:text-stone-50">
		{$t('auth.registerTitle')}
	</h1>
	<p class="text-sm mb-8 text-stone-500 dark:text-stone-400">
		{$t('auth.registerSubtitle')}
	</p>

	{#if errors.non_field}
		<div class="flex items-start gap-2 p-3 rounded-xl mb-5 text-sm
		            bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400
		            border border-red-200 dark:border-red-800/60"
		     role="alert" aria-live="assertive">
			<Icon name="x" size={15} strokeWidth={2} class="shrink-0 mt-0.5" />
			{errors.non_field}
		</div>
	{/if}

	<form onsubmit={handleRegister} novalidate class="space-y-4">
		<!-- Email -->
		<div>
			<label class="block text-sm font-medium mb-1.5 text-stone-700 dark:text-stone-300"
			       for="reg-email">
				{$t('auth.email')}
			</label>
			<input
				id="reg-email"
				type="email"
				class="input-field"
				placeholder={$t('auth.emailPlaceholder')}
				bind:value={email}
				autocomplete="email"
				aria-invalid={errors.email ? 'true' : undefined}
				required
			/>
			{#if errors.email}
				<p class="text-xs mt-1 text-red-600 dark:text-red-400">
					{Array.isArray(errors.email) ? errors.email[0] : errors.email}
				</p>
			{/if}
		</div>

		<!-- Username -->
		<div>
			<label class="block text-sm font-medium mb-1.5 text-stone-700 dark:text-stone-300"
			       for="reg-username">
				{$t('auth.username')}
			</label>
			<input
				id="reg-username"
				type="text"
				class="input-field"
				placeholder={$t('auth.usernamePlaceholder')}
				bind:value={username}
				autocomplete="username"
				aria-invalid={errors.username ? 'true' : undefined}
				required
			/>
			{#if errors.username}
				<p class="text-xs mt-1 text-red-600 dark:text-red-400">
					{Array.isArray(errors.username) ? errors.username[0] : errors.username}
				</p>
			{/if}
		</div>

		<!-- Password -->
		<div>
			<label class="block text-sm font-medium mb-1.5 text-stone-700 dark:text-stone-300"
			       for="reg-pw">
				{$t('auth.password')}
			</label>
			<input
				id="reg-pw"
				type="password"
				class="input-field"
				placeholder={$t('auth.passwordPlaceholder')}
				bind:value={password}
				autocomplete="new-password"
				minlength="8"
				aria-invalid={errors.password ? 'true' : undefined}
				required
			/>
			{#if errors.password}
				<p class="text-xs mt-1 text-red-600 dark:text-red-400">
					{Array.isArray(errors.password) ? errors.password[0] : errors.password}
				</p>
			{/if}
		</div>

		<button type="submit"
		        class="btn-primary w-full py-3 text-base mt-2"
		        disabled={loading}
		        aria-busy={loading}>
			{#if loading}
				<span class="inline-block w-4 h-4 rounded-full
				             border-2 border-white/30 border-t-white
				             motion-safe:animate-spin" aria-hidden="true"></span>
			{/if}
			{loading ? $t('ui.loading') : $t('auth.register')}
		</button>
	</form>

	<!-- Divider -->
	<div class="flex items-center gap-3 my-6">
		<div class="flex-1 h-px bg-stone-200 dark:bg-stone-800"></div>
		<span class="text-xs text-stone-400 dark:text-stone-500">{$t('auth.orContinue')}</span>
		<div class="flex-1 h-px bg-stone-200 dark:bg-stone-800"></div>
	</div>

	<GoogleButton onError={(msg) => (errors = { non_field: msg })} />

	<p class="text-center text-sm mt-6 text-stone-500 dark:text-stone-400">
		{$t('auth.haveAccount')}
		<a href="/login" class="font-semibold ms-1 text-emerald-700 dark:text-emerald-400 hover:underline">
			{$t('auth.loginHere')}
		</a>
	</p>
</div>
