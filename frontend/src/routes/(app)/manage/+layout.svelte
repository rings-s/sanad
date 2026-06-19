<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { t } from '$lib/stores/locale.js';
	import { currentUser } from '$lib/stores/auth.js';
	import TopBar from '$lib/components/TopBar.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';

	let { children } = $props();

	// ── Role gates ─────────────────────────────────────────────────────────────
	// Content managers + the Sheikh reach the Studio. Content + comments are open
	// to both; daily guidance, taxonomy, and user administration are Sheikh-only.
	// The backend enforces every gate — this only mirrors it in the UI.
	const isCreator = $derived($currentUser?.is_content_creator === true);
	const isSheikh = $derived($currentUser?.is_sheikh === true);

	/** @type {{ key: string, href: string, icon: string }[]} */
	const sections = $derived([
		{ key: 'content', href: '/manage/content', icon: 'notepad' },
		{ key: 'comments', href: '/manage/comments', icon: 'chat' },
		...(isSheikh
			? [
					{ key: 'daily', href: '/manage/daily', icon: 'sun' },
					{ key: 'taxonomy', href: '/manage/taxonomy', icon: 'layers' },
					{ key: 'users', href: '/manage/users', icon: 'user' }
				]
			: [])
	]);

	const onHub = $derived($page.url.pathname === '/manage');

	/** @param {string} href */
	const isActive = (href) => $page.url.pathname === href;

	onMount(() => {
		if ($currentUser && !$currentUser.is_content_creator) goto('/feed');
	});
</script>

<svelte:head><title>{$t('manage.title')} — {$t('app.name')}</title></svelte:head>
<TopBar title={$t('manage.title')} subtitle={$t('manage.subtitle')} />

<div class="max-w-3xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8 mx-auto w-full">
	{#if !isCreator}
		<EmptyState icon="x" title={$t('manage.noAccess')} />
	{:else}
		<!-- Section nav — hidden on the hub, where the cards already do the job. -->
		{#if !onHub}
			<div
				class="mb-6 gap-1 rounded-xl bg-stone-100 p-1 dark:bg-stone-800 flex overflow-x-auto"
				aria-label={$t('manage.title')}
			>
				{#each sections as s (s.key)}
					<a
						href={s.href}
						aria-current={isActive(s.href) ? 'page' : undefined}
						class={[
							'min-h-11 gap-1.5 rounded-lg px-4 text-sm font-medium flex shrink-0 items-center justify-center transition-colors duration-150',
							isActive(s.href)
								? 'bg-white text-stone-900 shadow-sm dark:bg-stone-900 dark:text-stone-50'
								: 'text-stone-500 hover:text-stone-700 dark:text-stone-400 dark:hover:text-stone-200'
						]}
					>
						<Icon name={s.icon} size={15} />
						{$t(`admin.tabs.${s.key}`)}
					</a>
				{/each}
			</div>
		{/if}

		{@render children()}
	{/if}
</div>
