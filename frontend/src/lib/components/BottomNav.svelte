<script>
	import { page } from '$app/stores';
	import { t } from '$lib/stores/locale.js';
	import { currentUser } from '$lib/stores/auth.js';
	import Icon from './Icon.svelte';

	const baseItems = [
		{ key: 'feed', href: '/feed', icon: 'house' },
		{ key: 'daily', href: '/daily', icon: 'sun' },
		{ key: 'videos', href: '/videos', icon: 'video' },
		{ key: 'audios', href: '/audios', icon: 'headphones' },
		{ key: 'saved', href: '/saved', icon: 'bookmark' }
	];

	// Content creators (Sheikh + content managers) get a Studio shortcut here too,
	// so the admin CRUD surface is reachable on mobile, not just the desktop rail.
	const items = $derived(
		$currentUser?.is_content_creator
			? [...baseItems, { key: 'manage', href: '/manage', icon: 'edit' }]
			: baseItems
	);

	function isActive(href) {
		return $page.url.pathname === href || $page.url.pathname.startsWith(href + '/');
	}
</script>

<!--
  M3 Navigation Bar — mobile only.
  view-transition-name keeps it stable during page transitions.
  safe-area-inset-bottom handled via padding so content clears the home indicator.
-->
<nav
	class="md:hidden bottom-0 inset-x-0 bg-white/95 dark:bg-stone-900/95
	       backdrop-blur-xl border-stone-200/80
	       dark:border-stone-800
	       px-2 pt-2 fixed
	       z-40 flex
	       items-end justify-around border-t
	       shadow-[0_-4px_24px_rgba(0,0,0,0.06)] dark:shadow-[0_-4px_24px_rgba(0,0,0,0.3)]"
	style="padding-bottom: max(0.5rem, env(safe-area-inset-bottom)); view-transition-name: bottom-nav;"
	aria-label={$t('nav.primary')}
>
	{#each items as item}
		{@const active = isActive(item.href)}
		<a
			href={item.href}
			class="gap-1 pb-2 min-w-12 max-w-20 ease-standard focus-visible:outline-emerald-600 focus-visible:rounded-xl
			       relative flex flex-1
			       flex-col items-center justify-end
			       transition-colors duration-150 focus-visible:outline-2"
			aria-label={$t(`nav.${item.key}`)}
			aria-current={active ? 'page' : undefined}
		>
			<!-- Active indicator pill — slides up under the icon -->
			<span
				class={[
					'top-0 h-8 w-14 absolute left-1/2 -translate-x-1/2 rounded-full',
					'ease-standard transition-all duration-200 motion-safe:will-change-transform',
					active ? 'bg-emerald-100 dark:bg-emerald-900/40' : 'opacity-0'
				]}
				aria-hidden="true"
			></span>

			<!-- Icon -->
			<span
				class="w-6 h-6 relative z-10 flex items-center justify-center
			             motion-safe:transition-transform motion-safe:duration-150"
				class:scale-110={active}
			>
				<Icon
					name={item.icon}
					size={22}
					strokeWidth={active ? 2 : 1.5}
					class={active
						? 'text-emerald-700 dark:text-emerald-400'
						: 'text-stone-400 dark:text-stone-500'}
				/>
			</span>

			<!-- Label -->
			<span
				class={[
					'font-medium tracking-tight relative z-10 text-[10px] leading-none transition-colors duration-150',
					active
						? 'text-emerald-700 dark:text-emerald-400 font-semibold'
						: 'text-stone-400 dark:text-stone-500'
				]}
			>
				{$t(`nav.${item.key}`)}
			</span>
		</a>
	{/each}
</nav>
