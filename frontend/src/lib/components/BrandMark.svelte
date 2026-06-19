<script>
	import { locale } from '$lib/stores/locale.js';

	/**
	 * Premium brand seal — the emerald "Sanad" mark used on entry surfaces
	 * (hero + auth). Keeps the established emerald + letter identity but adds
	 * a gilded hairline ring, soft top highlight and ambient shadow so the
	 * entry surfaces feel crafted. Decorative: callers provide the label.
	 *
	 * @type {{ size?: number, glow?: boolean }}
	 */
	let { size = 48, glow = false } = $props();

	const letter = $derived($locale === 'ar' ? 'س' : 'S');
</script>

<span class="relative inline-grid place-items-center shrink-0" style="width:{size}px;height:{size}px">
	{#if glow}
		<!-- Soft emerald halo behind the seal -->
		<span
			class="bg-emerald-500/25 dark:bg-emerald-400/20 pointer-events-none absolute -inset-4 rounded-full blur-2xl"
			aria-hidden="true"
		></span>
	{/if}

	<!-- Gilded outer hairline ring -->
	<span
		class="absolute rounded-[34%] ring-1 ring-gold-400/40 dark:ring-gold-300/30"
		style="inset:{-Math.round(size * 0.07)}px"
		aria-hidden="true"
	></span>

	<!-- Seal body -->
	<span
		class="relative grid h-full w-full place-items-center overflow-hidden rounded-[30%]
		       bg-gradient-to-br from-emerald-600 to-emerald-800
		       shadow-[0_6px_18px_-6px_rgba(4,120,87,0.55)]"
	>
		<!-- Top inner highlight for a polished, dimensional surface -->
		<span
			class="pointer-events-none absolute inset-x-0 top-0 h-1/2 bg-gradient-to-b from-white/25 to-transparent"
			aria-hidden="true"
		></span>
		<span
			class="relative font-bold leading-none text-white select-none"
			style="font-size:{Math.round(size * 0.5)}px; font-family:'Cairo', serif;"
		>
			{letter}
		</span>
	</span>
</span>
