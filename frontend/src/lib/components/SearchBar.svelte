<script>
	import Icon from './Icon.svelte';

	/**
	 * Consistent, accessible search field with a trailing icon. Replaces the
	 * earlier per-page inputs that referenced undefined CSS variables.
	 * RTL-aware (icon sits at the inline-end, text at the inline-start), 48px
	 * tall via `.input-field`.
	 *
	 * @type {{ value?: string, placeholder?: string, oninput?: (e: Event) => void, big?: boolean }}
	 */
	let { value = $bindable(''), placeholder = '', oninput = () => {}, big = false } = $props();
</script>

<div class="relative">
	<input
		type="search"
		class="input-field pe-11 {big ? 'text-base font-medium' : 'text-sm'}"
		{placeholder}
		bind:value
		{oninput}
		aria-label={placeholder}
	/>
	<Icon
		name="search"
		size={big ? 18 : 16}
		class="pointer-events-none absolute top-1/2 end-3.5 -translate-y-1/2 text-stone-400 dark:text-stone-500"
	/>
</div>
