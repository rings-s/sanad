<script>
	import { t } from '$lib/stores/locale.js';
	import Icon from '$lib/components/Icon.svelte';

	/**
	 * Reusable image picker: click or drag-and-drop, live preview, client-side
	 * type/size validation, and a remove affordance that understands the
	 * difference between dropping a freshly-picked file and clearing an
	 * already-saved image (edit mode).
	 *
	 * @typedef {Object} Props
	 * @property {string} id                       Unique id linking label → input.
	 * @property {File|null} [value]               The picked file (bindable).
	 * @property {string} [existingUrl]            URL of the already-saved image, if any.
	 * @property {boolean} [removeExisting]        Set true when the saved image is cleared (bindable).
	 * @property {number} [maxSizeMb]              Max accepted size in MB.
	 * @property {string} [accept]                 Accepted MIME pattern.
	 */

	/** @type {Props} */
	let {
		id,
		value = $bindable(null),
		existingUrl = '',
		removeExisting = $bindable(false),
		maxSizeMb = 5,
		accept = 'image/*',
	} = $props();

	let error = $state('');
	let dragging = $state(false);
	/** @type {HTMLInputElement} */
	let inputEl;

	// Preview source: a freshly-picked file wins; otherwise the saved image
	// (unless it has been explicitly removed). Object URLs are revoked on change.
	let previewUrl = $state('');
	$effect(() => {
		if (value) {
			const url = URL.createObjectURL(value);
			previewUrl = url;
			return () => URL.revokeObjectURL(url);
		}
		previewUrl = existingUrl && !removeExisting ? existingUrl : '';
	});

	const hasImage = $derived(!!previewUrl);

	/** @param {File|undefined|null} file */
	function accept_file(file) {
		if (!file) return;
		if (!file.type.startsWith('image/')) {
			error = $t('upload.errorType');
			return;
		}
		if (file.size > maxSizeMb * 1024 * 1024) {
			error = $t('upload.errorSize').replace('{max}', String(maxSizeMb));
			return;
		}
		error = '';
		removeExisting = false; // a new pick supersedes any prior removal
		value = file;
	}

	/** @param {Event} e */
	function onInput(e) {
		const target = /** @type {HTMLInputElement} */ (e.currentTarget);
		accept_file(target.files?.[0]);
	}

	/** @param {DragEvent} e */
	function onDrop(e) {
		e.preventDefault();
		dragging = false;
		accept_file(e.dataTransfer?.files?.[0]);
	}

	function clear() {
		if (value) {
			// Drop the freshly-picked file; reverts to the saved image if one exists.
			value = null;
		} else if (existingUrl) {
			// Clear the already-saved image (signals the backend on submit).
			removeExisting = true;
		}
		error = '';
		if (inputEl) inputEl.value = '';
	}

	function openPicker() {
		inputEl?.click();
	}

	/** @param {KeyboardEvent} e */
	function onKey(e) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			openPicker();
		}
	}
</script>

<div>
	<input
		bind:this={inputEl}
		{id}
		type="file"
		{accept}
		class="sr-only"
		onchange={onInput}
	/>

	{#if hasImage}
		<!-- Preview with replace / remove controls -->
		<div
			class="group border-stone-200 bg-stone-50 dark:border-stone-700 dark:bg-stone-900 relative overflow-hidden rounded-2xl border"
		>
			<img src={previewUrl} alt="" class="max-h-56 w-full object-cover" />
			<div
				class="end-2 top-2 gap-1.5 absolute flex"
			>
				<button
					type="button"
					onclick={openPicker}
					class="gap-1.5 rounded-lg bg-white/90 px-2.5 py-1.5 text-xs font-semibold text-stone-700 shadow-sm backdrop-blur hover:bg-white dark:bg-stone-800/90 dark:text-stone-200 dark:hover:bg-stone-800 inline-flex items-center"
				>
					<Icon name="edit" size={13} />{$t('upload.replace')}
				</button>
				<button
					type="button"
					onclick={clear}
					class="rounded-lg bg-white/90 p-1.5 text-red-600 shadow-sm backdrop-blur hover:bg-white dark:bg-stone-800/90 dark:hover:bg-stone-800"
					aria-label={$t('upload.remove')}
				>
					<Icon name="x" size={14} />
				</button>
			</div>
			{#if value}
				<span
					class="start-2 bottom-2 rounded-lg bg-emerald-600/90 px-2 py-0.5 text-[11px] font-semibold text-white absolute"
				>
					{$t('upload.newBadge')}
				</span>
			{/if}
		</div>
	{:else}
		<!-- Empty dropzone -->
		<div
			role="button"
			tabindex="0"
			onclick={openPicker}
			onkeydown={onKey}
			ondragover={(e) => {
				e.preventDefault();
				dragging = true;
			}}
			ondragleave={() => (dragging = false)}
			ondrop={onDrop}
			class={[
				'min-h-32 w-full cursor-pointer flex-col items-center justify-center gap-2 rounded-2xl border-2 border-dashed px-4 py-6 text-center transition-colors flex',
				dragging
					? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/30'
					: 'border-stone-300 bg-stone-50 hover:border-stone-400 hover:bg-stone-100 dark:border-stone-700 dark:bg-stone-900 dark:hover:border-stone-600',
			]}
		>
			<span
				class="h-10 w-10 rounded-xl bg-white text-stone-400 shadow-sm dark:bg-stone-800 dark:text-stone-500 grid place-items-center"
			>
				<Icon name="image" size={18} />
			</span>
			<span class="text-sm font-medium text-stone-600 dark:text-stone-300">
				{$t('upload.prompt')}
			</span>
			<span class="text-xs text-stone-400 dark:text-stone-500">
				{$t('upload.hint').replace('{max}', String(maxSizeMb))}
			</span>
		</div>
	{/if}

	{#if error}
		<p class="mt-1.5 text-xs font-medium text-red-600 dark:text-red-400" role="alert">
			{error}
		</p>
	{/if}
</div>
