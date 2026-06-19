<script>
	import { fade } from 'svelte/transition';
	import Icon from './Icon.svelte';

	/**
	 * Unified empty / error / hint state used across all collection pages.
	 * Centralises what used to be duplicated markup (with broken CSS vars) so
	 * every "nothing here" and "something failed" moment looks identical
	 * (Consistency & Standards). Pass action buttons/links as children.
	 *
	 * @type {{
	 *   icon?: string,
	 *   title?: string,
	 *   tone?: 'neutral' | 'error',
	 *   children?: import('svelte').Snippet
	 * }}
	 */
	let { icon = 'spark', title = '', tone = 'neutral', children } = $props();

	const toneCls =
		tone === 'error'
			? 'bg-red-50 dark:bg-red-900/20 text-red-500 dark:text-red-400'
			: 'bg-stone-100 dark:bg-stone-800 text-stone-400 dark:text-stone-500';
</script>

<div
	class="py-16 sm:py-20 flex flex-col items-center text-center"
	role={tone === 'error' ? 'alert' : undefined}
	in:fade={{ duration: 200 }}
>
	<div class="w-14 h-14 mb-4 grid place-items-center rounded-2xl {toneCls}">
		<Icon name={icon} size={24} strokeWidth={1.5} />
	</div>
	<p class="text-sm text-stone-500 dark:text-stone-400 max-w-xs text-balance">{title}</p>
	{#if children}
		<div class="mt-5">{@render children()}</div>
	{/if}
</div>
