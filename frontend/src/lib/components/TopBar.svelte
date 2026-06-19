<script>
	import { toggleLocale, locale } from '$lib/stores/locale.js';
	import { t } from '$lib/stores/locale.js';
	import { currentUser } from '$lib/stores/auth.js';
	import { toggleTheme, isDark } from '$lib/stores/theme.js';
	import Icon from './Icon.svelte';

	let { title = '', subtitle = '' } = $props();
</script>

<!--
  Sticky top app bar. Shares the EXACT horizontal padding of the page container
  (px-4 sm:px-6 lg:px-8) so the title aligns with content at every breakpoint,
  and the inner row is h-16 to match the SideNav header divider on desktop.
  padding-top carries the safe-area inset so the bar clears the notch in
  standalone/PWA mode (viewport-fit=cover).
-->
<header
	class="sticky top-0 z-30 bg-stone-50/92 dark:bg-stone-950/92 backdrop-blur-xl
	       border-b border-stone-200/70 dark:border-stone-800 transition-colors duration-200"
	style="padding-top: env(safe-area-inset-top, 0px);"
>
	<div class="h-16 flex items-center justify-between px-5 sm:px-6 lg:px-8">
		<!-- Title block -->
		<div class="min-w-0 flex-1">
			{#if title}
				<h1 class="text-base sm:text-lg font-semibold leading-tight truncate text-stone-900 dark:text-stone-50">
					{title}
				</h1>
				{#if subtitle}
					<p class="text-xs hidden sm:block truncate mt-0.5 text-stone-400 dark:text-stone-500">
						{subtitle}
					</p>
				{/if}
			{/if}
		</div>

		<!-- Action row -->
		<div class="flex items-center gap-1 ms-4 shrink-0">
			<!-- Theme toggle — 44px target -->
			<button
				onclick={toggleTheme}
				class="grid place-items-center w-11 h-11 rounded-full
				       text-stone-500 dark:text-stone-400
				       hover:bg-stone-100 dark:hover:bg-stone-800
				       transition-colors duration-150
				       focus-visible:ring-2 focus-visible:ring-emerald-500"
				aria-label={$isDark ? $t('nav.lightMode') : $t('nav.darkMode')}
			>
				<Icon name={$isDark ? 'sun' : 'moon'} size={18} strokeWidth={1.5} />
			</button>

			<!-- Language toggle -->
			<button
				onclick={toggleLocale}
				class="flex items-center gap-1.5 h-11 px-3 rounded-full
				       text-xs font-semibold
				       text-stone-600 dark:text-stone-300
				       hover:bg-stone-100 dark:hover:bg-stone-800
				       transition-colors duration-150
				       focus-visible:ring-2 focus-visible:ring-emerald-500"
				aria-label={$t('nav.switchLanguage')}
			>
				<Icon name="globe" size={14} />
				<span>{$locale === 'ar' ? 'EN' : 'عربي'}</span>
			</button>

			<!-- User avatar -->
			<a
				href="/profile"
				class="w-10 h-10 ms-0.5 rounded-full flex items-center justify-center
				       bg-emerald-700 text-white text-sm font-bold
				       ring-2 ring-emerald-700/20 dark:ring-emerald-400/20
				       hover:scale-105 active:scale-95
				       transition-transform duration-150
				       focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-stone-950
				       shrink-0"
				aria-label={$t('nav.profile')}
			>
				{($currentUser?.username ?? $currentUser?.email ?? '?').charAt(0).toUpperCase()}
			</a>
		</div>
	</div>
</header>
