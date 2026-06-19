<script>
	/**
	 * Sacred backdrop — the shared atmospheric canvas behind the hero and auth
	 * surfaces. Layers a warm wash, two soft emerald glows and a slowly drifting
	 * 8-point khatam star (the geometric heart of Islamic art) plus fine grain.
	 * Purely decorative; fully aria-hidden and reduced-motion safe.
	 */

	/**
	 * Build an 8-point khatam (octagram {8/2}) star path on a 0–100 viewBox.
	 * @param {number} cx
	 * @param {number} cy
	 * @param {number} R
	 * @param {number} [inner]
	 */
	function khatam(cx, cy, R, inner = 0.414) {
		let d = '';
		for (let i = 0; i < 16; i++) {
			const r = i % 2 === 0 ? R : R * inner;
			const a = (Math.PI / 8) * i - Math.PI / 2;
			d += (i === 0 ? 'M' : 'L') + (cx + Math.cos(a) * r).toFixed(2) + ' ' + (cy + Math.sin(a) * r).toFixed(2) + ' ';
		}
		return d + 'Z';
	}

	// Concentric khatam stars form a refined seal motif.
	const star = $derived.by(() => ({
		outer: khatam(50, 50, 49),
		mid: khatam(50, 50, 37),
		inner: khatam(50, 50, 22)
	}));
</script>

<div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
	<!-- Warm paper wash -->
	<div
		class="absolute inset-0
		       bg-[radial-gradient(120%_120%_at_50%_-10%,#ffffff_0%,#fbfaf7_45%,#f4f2ec_100%)]
		       dark:bg-[radial-gradient(120%_120%_at_50%_-10%,#10201a_0%,#0c1512_45%,#0a0a0a_100%)]"
	></div>

	<!-- Emerald glow — top, locale-aware corner -->
	<div
		class="absolute -top-32 -end-24 h-[26rem] w-[26rem] rounded-full
		       bg-emerald-400/20 blur-[90px] dark:bg-emerald-500/10"
	></div>
	<!-- Gold whisper — bottom, opposite corner -->
	<div
		class="absolute -bottom-40 -start-28 h-[24rem] w-[24rem] rounded-full
		       bg-gold-300/15 blur-[100px] dark:bg-emerald-400/5"
	></div>

	<!-- Giant drifting khatam star — the signature ornament -->
	<svg
		class="khatam-spin absolute -end-[18%] -top-[14%] h-[42rem] w-[42rem]
		       text-emerald-700/[0.06] dark:text-emerald-300/[0.07]"
		viewBox="0 0 100 100"
		fill="none"
		stroke="currentColor"
		stroke-width="0.5"
	>
		<path d={star.outer} />
		<path d={star.mid} />
		<path d={star.inner} class="text-gold-400/20 dark:text-gold-300/15" stroke="currentColor" />
		<circle cx="50" cy="50" r="9" />
	</svg>

	<!-- Film grain for premium texture -->
	<div class="noise-overlay absolute inset-0 opacity-[0.035] mix-blend-overlay dark:opacity-[0.05]"></div>
</div>
