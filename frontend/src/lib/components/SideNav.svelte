<script>
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { auth, currentUser } from '$lib/stores/auth.js';
	import { t, locale } from '$lib/stores/locale.js';
	import { toggleTheme, isDark } from '$lib/stores/theme.js';
	import Icon from './Icon.svelte';
	import BrandMark from './BrandMark.svelte';

	let { collapsed = $bindable(false) } = $props();

	const baseItems = [
		{ key: 'feed', href: '/feed', icon: 'house' },
		{ key: 'daily', href: '/daily', icon: 'sun' },
		{ key: 'posts', href: '/posts', icon: 'notepad' },
		{ key: 'videos', href: '/videos', icon: 'video' },
		{ key: 'audios', href: '/audios', icon: 'headphones' },
		{ key: 'saved', href: '/saved', icon: 'bookmark' }
	];

	const navItems = $derived(
		$currentUser?.is_content_creator
			? [...baseItems, { key: 'manage', href: '/manage', icon: 'edit' }]
			: baseItems
	);

	/** @param {string} href */
	function isActive(href) {
		return $page.url.pathname === href || $page.url.pathname.startsWith(href + '/');
	}

	const profileActive = $derived(isActive('/profile'));

	const toggleIcon = $derived(
		collapsed
			? $locale === 'ar'
				? 'chevronLeft'
				: 'chevronRight'
			: $locale === 'ar'
				? 'chevronRight'
				: 'chevronLeft'
	);

	async function handleLogout() {
		try {
			const { authApi } = await import('$lib/api/auth.js');
			await authApi.logout();
		} catch {}
		auth.logout();
		goto('/');
	}
</script>

<nav
	class="md:flex top-0 start-0 bg-white dark:bg-stone-900 border-stone-200/70 dark:border-stone-800 ease-standard
	       fixed z-40
	       hidden h-full flex-col
	       border-e transition-[width] duration-300
	       motion-safe:will-change-[width]"
	style="width: {collapsed ? '64px' : '220px'}; view-transition-name: sidebar;"
	aria-label={$t('nav.primary')}
>
	<!-- Logo / Header row -->
	<div
		class="h-16 px-3 border-stone-200/70 dark:border-stone-800 flex
	            shrink-0 items-center border-b"
		class:justify-center={collapsed}
		class:gap-3={!collapsed}
	>
		{#if !collapsed}
			<BrandMark size={32} />
			<span
				class="font-display font-semibold text-base tracking-tight text-stone-900 dark:text-stone-50 truncate"
			>
				{$t('app.name')}
			</span>
		{/if}
		<button
			onclick={() => (collapsed = !collapsed)}
			class="w-8 h-8 rounded-lg text-stone-400 dark:text-stone-500
			       hover:bg-stone-100 dark:hover:bg-stone-800
			       hover:text-stone-700 dark:hover:text-stone-300 focus-visible:ring-emerald-500 grid
			       place-items-center transition-colors
			       duration-150 focus-visible:ring-2"
			class:ms-auto={!collapsed}
			aria-expanded={!collapsed}
			aria-label={collapsed ? $t('nav.expand') : $t('nav.collapse')}
		>
			<Icon name={toggleIcon} size={16} />
		</button>
	</div>

	<!-- Nav items -->
	<div class="py-3 px-2 space-y-0.5 flex-1 overflow-y-auto">
		{#each navItems as item}
			{@const active = isActive(item.href)}
			<a
				href={item.href}
				class={[
					'px-3 py-2.5 rounded-xl text-sm font-medium ease-standard focus-visible:ring-emerald-500 flex items-center transition-all duration-150 focus-visible:ring-2',
					collapsed ? 'justify-center' : 'gap-3',
					active
						? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 font-semibold'
						: 'text-stone-600 dark:text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800'
				]}
				aria-current={active ? 'page' : undefined}
				title={collapsed ? $t(`nav.${item.key}`) : undefined}
			>
				<Icon name={item.icon} size={18} strokeWidth={active ? 2 : 1.5} />
				{#if !collapsed}<span>{$t(`nav.${item.key}`)}</span>{/if}
			</a>
		{/each}
	</div>

	<!-- Footer actions -->
	<div
		class="px-2 pb-4 pt-2 space-y-0.5 border-stone-200/70
	            dark:border-stone-800 shrink-0 border-t"
	>
		<!-- Theme toggle -->
		<button
			onclick={toggleTheme}
			class="px-3 py-2.5 rounded-xl text-sm font-medium text-stone-500
			       dark:text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800 hover:text-stone-700
			       dark:hover:text-stone-300 focus-visible:ring-emerald-500 flex w-full
			       items-center transition-colors
			       duration-150 focus-visible:ring-2"
			class:justify-center={collapsed}
			class:gap-3={!collapsed}
			title={collapsed ? ($isDark ? $t('nav.lightMode') : $t('nav.darkMode')) : undefined}
			aria-label={$isDark ? $t('nav.lightMode') : $t('nav.darkMode')}
		>
			<Icon name={$isDark ? 'sun' : 'moon'} size={18} strokeWidth={1.5} />
			{#if !collapsed}<span>{$isDark ? $t('nav.lightMode') : $t('nav.darkMode')}</span>{/if}
		</button>

		<!-- Profile -->
		<a
			href="/profile"
			class={[
				'px-3 py-2.5 rounded-xl text-sm font-medium focus-visible:ring-emerald-500 flex items-center transition-colors duration-150 focus-visible:ring-2',
				collapsed ? 'justify-center' : 'gap-3',
				profileActive
					? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 font-semibold'
					: 'text-stone-600 dark:text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800'
			]}
			aria-current={profileActive ? 'page' : undefined}
			title={collapsed ? $t('nav.profile') : undefined}
		>
			<Icon name="user" size={18} strokeWidth={profileActive ? 2 : 1.5} />
			{#if !collapsed}<span>{$t('nav.profile')}</span>{/if}
		</a>

		<!-- Logout -->
		<button
			onclick={handleLogout}
			class="px-3 py-2.5 rounded-xl text-sm font-medium text-stone-400
			       dark:text-stone-500 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600
			       dark:hover:text-red-400 focus-visible:ring-red-400 flex w-full
			       items-center text-start transition-colors
			       duration-150 focus-visible:ring-2"
			class:justify-center={collapsed}
			class:gap-3={!collapsed}
			title={collapsed ? $t('nav.logout') : undefined}
		>
			<Icon name="logout" size={18} strokeWidth={1.5} />
			{#if !collapsed}<span>{$t('nav.logout')}</span>{/if}
		</button>
	</div>
</nav>
