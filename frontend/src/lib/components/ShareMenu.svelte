<script>
	import { page } from '$app/stores';
	import { t, dir } from '$lib/stores/locale.js';
	import Icon from './Icon.svelte';
	import BrandIcon from '$lib/share/BrandIcon.svelte';
	import {
		SHARE_TARGETS,
		buildShareUrl,
		intentUrl,
		openShareWindow,
		copyToClipboard
	} from '$lib/share/share.js';

	/**
	 * Reusable social share control. Provide either an absolute `url` or a
	 * relative `path` (the canonical URL is then composed from the current
	 * origin). `title` seeds the share text for X / Telegram.
	 *
	 * The dropdown panel is portalled to `<body>` and positioned with
	 * `position: fixed`, so it never gets clipped by a card's `overflow-hidden`
	 * or a transformed ancestor — making it safe to embed inside `ContentCard`
	 * (including inside its wrapping `<a>`).
	 *
	 * @typedef {Object} Props
	 * @property {string} [url]    - absolute URL (wins over `path`)
	 * @property {string} [path]   - relative path, e.g. `/content/abc123`
	 * @property {string} [title]  - content title (used as share text)
	 * @property {string} [text]   - explicit share text (overrides `title`)
	 * @property {'start'|'end'} [align] - panel edge aligned to the trigger
	 * @property {number} [size]   - trigger icon size
	 * @property {string} [triggerClass] - visual classes for the trigger (a11y
	 *   focus ring is always applied on top)
	 * @property {string} [class]  - extra classes appended to the trigger
	 */

	/** @type {Props} */
	let {
		url,
		path,
		title = '',
		text = '',
		align = 'end',
		size = 18,
		triggerClass = 'rounded-xl p-2.5 bg-stone-100 text-stone-400 hover:text-stone-700 dark:bg-stone-800 dark:text-stone-500 dark:hover:text-stone-200',
		class: klass = ''
	} = $props();

	let open = $state(false);
	let copiedId = $state(/** @type {string|null} */ (null));
	/** @type {ReturnType<typeof setTimeout>} */
	let copyTimer;
	let coords = $state({ top: 0, left: 0 });

	let triggerEl = $state(/** @type {HTMLButtonElement|undefined} */ (undefined));
	let panelEl = $state(/** @type {HTMLDivElement|undefined} */ (undefined));

	const shareUrl = $derived(url || buildShareUrl($page.url.origin, path));
	const shareText = $derived(text || title);
	const rtl = $derived($dir === 'rtl');

	/**
	 * Svelte action: relocate the node to `<body>` so it escapes any ancestor
	 * `overflow`/`transform`. Runs only in the browser.
	 * @param {HTMLElement} node
	 */
	function portal(node) {
		document.body.appendChild(node);
		return {
			destroy() {
				node.remove();
			}
		};
	}

	/** Pin the panel under (or above, if it would overflow) the trigger. */
	function reposition() {
		if (!triggerEl || !panelEl) return;
		const r = triggerEl.getBoundingClientRect();
		const pw = panelEl.offsetWidth || 240;
		const ph = panelEl.offsetHeight || 300;
		const gap = 8;
		const m = 8;

		let top = r.bottom + gap;
		if (top + ph > window.innerHeight - m) {
			const above = r.top - gap - ph;
			top = above >= m ? above : Math.max(m, window.innerHeight - ph - m);
		}

		// `end` aligns the panel's inline-end edge to the trigger (direction-aware).
		const alignRightEdge = align === 'end' ? !rtl : rtl;
		let left = alignRightEdge ? r.right - pw : r.left;
		left = Math.min(Math.max(m, left), window.innerWidth - pw - m);

		coords = { top, left };
	}

	/** @param {MouseEvent} e */
	function toggle(e) {
		e.preventDefault(); // safe when nested inside a card's <a> wrapper
		open = !open;
	}

	/**
	 * @param {import('$lib/share/share.js').ShareTarget} target
	 * @param {MouseEvent} e
	 */
	async function activate(target, e) {
		e.preventDefault();
		if (target.action === 'intent') {
			openShareWindow(intentUrl(target.id, { url: shareUrl, text: shareText }));
			open = false;
			triggerEl?.focus();
			return;
		}
		// copy actions (TikTok + Copy Link) — keep panel open to show feedback
		const ok = await copyToClipboard(shareUrl);
		if (ok) {
			copiedId = target.id;
			clearTimeout(copyTimer);
			copyTimer = setTimeout(() => (copiedId = null), 1800);
		}
	}

	// While open: position, focus first item, and wire outside-close / Escape /
	// reposition listeners. All torn down on close.
	$effect(() => {
		if (!open || !panelEl) return;
		reposition();
		const first = panelEl.querySelector('[role="menuitem"]');
		if (first instanceof HTMLElement) first.focus();

		/** @param {PointerEvent} e */
		function onPointer(e) {
			const target = /** @type {Node} */ (e.target);
			if (!panelEl?.contains(target) && !triggerEl?.contains(target)) open = false;
		}
		/** @param {KeyboardEvent} e */
		function onKey(e) {
			if (e.key === 'Escape') {
				open = false;
				triggerEl?.focus();
			}
		}
		window.addEventListener('pointerdown', onPointer);
		window.addEventListener('keydown', onKey);
		window.addEventListener('resize', reposition);
		window.addEventListener('scroll', reposition, true);
		return () => {
			window.removeEventListener('pointerdown', onPointer);
			window.removeEventListener('keydown', onKey);
			window.removeEventListener('resize', reposition);
			window.removeEventListener('scroll', reposition, true);
		};
	});
</script>

{#snippet shareItem(/** @type {import('$lib/share/share.js').ShareTarget} */ target)}
	{@const copied = copiedId === target.id}
	<button
		type="button"
		role="menuitem"
		onclick={(e) => activate(target, e)}
		style="--tint:{target.tint}; --tint-dark:{target.tintDark}"
		class="group/item min-h-12 gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-stone-700 dark:text-stone-200
		       hover:bg-stone-100 dark:hover:bg-stone-800 focus-visible:bg-stone-100 dark:focus-visible:bg-stone-800
		       flex w-full items-center text-start
		       transition-colors duration-150 focus-visible:outline-none"
	>
		<span
			class="h-9 w-9 bg-stone-100 text-stone-600 dark:bg-stone-800 dark:text-stone-300 flex
			       shrink-0 items-center justify-center rounded-full
			       transition-colors duration-150
			       group-hover/item:text-[var(--tint)] group-focus-visible/item:text-[var(--tint)]
			       dark:group-hover/item:text-[var(--tint-dark)] dark:group-focus-visible/item:text-[var(--tint-dark)]"
		>
			{#if copied}
				<Icon name="check" size={18} strokeWidth={2.5} />
			{:else if target.id === 'link'}
				<Icon name="link" size={18} />
			{:else}
				<BrandIcon name={target.brand} size={18} />
			{/if}
		</span>
		<span class="flex-1">{copied ? $t('content.copied') : $t(target.labelKey)}</span>
	</button>
{/snippet}

<button
	bind:this={triggerEl}
	type="button"
	onclick={toggle}
	aria-haspopup="menu"
	aria-expanded={open}
	aria-label={$t('content.share')}
	class="focus-visible:ring-emerald-500 dark:focus-visible:ring-offset-stone-950 inline-flex items-center
	       justify-center transition-all duration-150 focus-visible:ring-2 focus-visible:ring-offset-1
	       focus-visible:outline-none active:scale-95 {triggerClass} {klass}"
>
	<Icon name="share" {size} />
</button>

{#if open}
	<div
		bind:this={panelEl}
		use:portal
		role="menu"
		aria-label={$t('content.shareThis')}
		style="position: fixed; top: {coords.top}px; left: {coords.left}px;"
		class="card-elevated w-60 p-1.5 z-50
		       origin-top motion-safe:animate-[share-pop_140ms_var(--ease-decelerate)_backwards]"
	>
		<p
			class="px-3 pt-1 pb-1.5 text-xs font-semibold tracking-wide text-stone-400 dark:text-stone-500"
		>
			{$t('content.shareThis')}
		</p>
		{#each SHARE_TARGETS as target (target.id)}
			{@render shareItem(target)}
		{/each}
	</div>
{/if}

<style>
	@keyframes share-pop {
		from {
			opacity: 0;
			transform: scale(0.95) translateY(-2px);
		}
		to {
			opacity: 1;
			transform: scale(1) translateY(0);
		}
	}
</style>
