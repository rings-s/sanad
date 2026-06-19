<script>
	import { t } from '$lib/stores/locale.js';
	import Icon from './Icon.svelte';
	import ShareMenu from './ShareMenu.svelte';

	let { item, compact = false } = $props();

	// Bare-icon trigger style that matches the cards' existing action buttons.
	const SHARE_TRIGGER =
		'rounded-lg p-1.5 text-stone-400 hover:text-stone-700 dark:text-stone-500 dark:hover:text-stone-200';

	let saved = $state(item?.is_saved ?? false);
	let completed = $state(item?.is_completed ?? false);
	let saving = $state(false);
	let completing = $state(false);

	function ytId(u) {
		if (!u) return '';
		const m = u.match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([A-Za-z0-9_-]{11})/);
		return m ? m[1] : '';
	}
	const videoId = $derived(ytId(item?.youtube_url));
	const thumbUrl = $derived(videoId ? `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg` : '');

	function formatDuration(secs) {
		if (!secs) return '';
		const h = Math.floor(secs / 3600);
		const m = Math.floor((secs % 3600) / 60);
		const s = secs % 60;
		return h
			? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
			: `${m}:${String(s).padStart(2, '0')}`;
	}

	const TYPE = {
		post: {
			icon: 'notepad',
			labelKey: 'content.type.post',
			pillCls: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
		},
		video: {
			icon: 'video',
			labelKey: 'content.type.video',
			pillCls: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
		},
		audio: {
			icon: 'headphones',
			labelKey: 'content.type.audio',
			pillCls: 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300'
		},
		note: {
			icon: 'spark',
			labelKey: 'content.type.note',
			pillCls: 'bg-stone-100 text-stone-600 dark:bg-stone-800 dark:text-stone-400'
		},
		hadith: {
			icon: 'star',
			labelKey: 'content.type.hadith',
			pillCls: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
		}
	};
	const cfg = $derived(TYPE[item?.type] ?? TYPE.post);
	const href = $derived(`/content/${item?.public_id}`);

	const bodySnippet = $derived(
		item?.body ? (item.body.length > 160 ? item.body.slice(0, 160) + '…' : item.body) : ''
	);

	async function toggleSave(e) {
		e.preventDefault();
		if (saving) return;
		saving = true;
		try {
			const { contentApi } = await import('$lib/api/content.js');
			if (saved) await contentApi.unsave(item.public_id);
			else await contentApi.save(item.public_id);
			saved = !saved;
		} catch {}
		saving = false;
	}

	async function toggleComplete(e) {
		e.preventDefault();
		if (completing || completed) return;
		completing = true;
		try {
			const { contentApi } = await import('$lib/api/content.js');
			await contentApi.markComplete(item.public_id);
			completed = true;
		} catch {}
		completing = false;
	}

	function fmtCount(n) {
		if (!n) return '';
		return n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n);
	}
</script>

{#if item?.type === 'audio'}
	<!-- ─── Audio: horizontal strip ──────────────────────────────────────────── -->
	<article
		class="card gap-4 p-4 ease-standard hover:shadow-md dark:hover:border-stone-700
                @container flex items-center
                transition-all duration-200
                motion-safe:hover:-translate-y-px"
	>
		<a
			{href}
			class="w-12 h-12 rounded-2xl flex shrink-0 items-center justify-center
	                 {cfg.pillCls}
	                 transition-transform duration-150 active:scale-95 motion-safe:hover:scale-105"
		>
			<Icon name="headphones" size={20} />
		</a>
		<a {href} class="min-w-0 flex-1">
			<h3
				class="text-sm font-semibold leading-snug text-stone-900
		           dark:text-stone-50 truncate"
			>
				{item.title}
			</h3>
			<div class="gap-2 mt-1 flex flex-wrap items-center">
				{#if item.duration_seconds}
					<span class="text-xs gap-1 text-stone-400 dark:text-stone-500 flex items-center">
						<Icon name="clock" size={11} />{formatDuration(item.duration_seconds)}
					</span>
				{/if}
				{#if item.category}
					<span
						class="text-xs px-1.5 py-0.5 bg-stone-100
				             dark:bg-stone-800 text-stone-500
				             dark:text-stone-400 rounded-full"
					>
						{item.category.name}
					</span>
				{/if}
				{#if item.subcategory}
					<span
						class="text-xs px-1.5 py-0.5 bg-stone-100
				             dark:bg-stone-800 text-stone-500
				             dark:text-stone-400 rounded-full"
					>
						{item.subcategory.name}
					</span>
				{/if}
			</div>
		</a>
		<!-- Touch actions — each at least 44×44 -->
		<div class="gap-0.5 flex shrink-0 items-center">
			{#if completed}
				<span
					class="p-2.5 rounded-xl text-emerald-600 dark:text-emerald-400"
					title={$t('content.completed')}
				>
					<Icon name="check" size={16} strokeWidth={2.5} />
				</span>
			{:else}
				<button
					onclick={toggleComplete}
					class="p-2.5 rounded-xl text-stone-400 dark:text-stone-500
			               hover:bg-emerald-50 dark:hover:bg-emerald-900/30 hover:text-emerald-600 dark:hover:text-emerald-400
			               transition-colors duration-150 active:scale-95 motion-safe:will-change-transform"
					aria-label={$t('content.markComplete')}
				>
					<Icon name="check" size={16} />
				</button>
			{/if}
			<button
				onclick={toggleSave}
				class="p-2.5 rounded-xl transition-all duration-150 active:scale-90 motion-safe:will-change-transform
		               {saved
					? 'text-emerald-600 dark:text-emerald-400 hover:text-emerald-700'
					: 'text-stone-400 dark:text-stone-500 hover:bg-stone-100 dark:hover:bg-stone-800 hover:text-stone-700 dark:hover:text-stone-200'}"
				aria-label={saved ? $t('content.saved') : $t('content.save')}
			>
				<Icon name="bookmark" size={16} strokeWidth={saved ? 2.5 : 1.5} />
			</button>
			<ShareMenu
				path={href}
				title={item.title}
				size={16}
				triggerClass="rounded-xl p-2.5 text-stone-400 hover:text-stone-700 dark:text-stone-500 dark:hover:text-stone-200"
			/>
		</div>
	</article>
{:else if item?.type === 'video'}
	<!-- ─── Video: thumbnail card ─────────────────────────────────────────────── -->
	<article
		class="card group ease-standard hover:shadow-lg
                dark:hover:border-stone-700 motion-safe:hover:-translate-y-0.5 @container
                overflow-hidden transition-all
                duration-200 motion-safe:will-change-transform"
	>
		<a {href} class="block">
			<!-- 16:9 thumbnail -->
			<div class="bg-stone-100 dark:bg-stone-800 aspect-video relative overflow-hidden">
				{#if thumbUrl}
					<img
						src={thumbUrl}
						alt={item.title}
						class="ease-standard h-full w-full
				            object-cover transition-transform duration-500
				            motion-safe:group-hover:scale-105"
						loading="lazy"
					/>
				{:else}
					<div class="flex h-full w-full items-center justify-center">
						<Icon
							name="video"
							size={32}
							strokeWidth={1}
							class="text-stone-300 dark:text-stone-600"
						/>
					</div>
				{/if}
				<!-- Play overlay -->
				<div
					class="inset-0 bg-black/0 group-hover:bg-black/25 absolute flex
			            items-center justify-center
			            transition-colors duration-200"
				>
					<div
						class="w-12 h-12 bg-white/90 backdrop-blur-sm shadow-xl ease-decelerate flex scale-75
				            items-center justify-center rounded-full opacity-0 transition-all
				            duration-200 group-hover:scale-100 group-hover:opacity-100
				            motion-safe:will-change-transform"
					>
						<Icon name="play" size={18} strokeWidth={2} class="text-stone-900 translate-x-0.5" />
					</div>
				</div>
				{#if item.duration_seconds}
					<span
						class="bottom-2 end-2 text-xs
				             font-mono font-semibold px-1.5 py-0.5 rounded bg-black/70
				             text-white absolute"
					>
						{formatDuration(item.duration_seconds)}
					</span>
				{/if}
			</div>

			<div class="p-4">
				<div class="gap-2 mb-2 flex items-start justify-between">
					<span class="badge text-xs shrink-0 {cfg.pillCls}">{$t(cfg.labelKey)}</span>
					<div class="gap-0.5 flex items-center">
						{#if completed}
							<span class="text-emerald-600 dark:text-emerald-400">
								<Icon name="check" size={14} strokeWidth={2.5} />
							</span>
						{/if}
						<button
							onclick={toggleSave}
							class="p-1.5 rounded-lg transition-all duration-150 active:scale-90
					               {saved
								? 'text-emerald-600 dark:text-emerald-400'
								: 'text-stone-400 dark:text-stone-500 hover:text-stone-700 dark:hover:text-stone-200'}"
							aria-label={saved ? $t('content.saved') : $t('content.save')}
						>
							<Icon name="bookmark" size={15} strokeWidth={saved ? 2.5 : 1.5} />
						</button>
						<ShareMenu path={href} title={item.title} size={15} triggerClass={SHARE_TRIGGER} />
					</div>
				</div>
				<h3
					class="text-sm font-semibold leading-snug mb-1 text-stone-900
			           dark:text-stone-50 line-clamp-2"
				>
					{item.title}
				</h3>
				{#if !compact && item.category}
					<p class="text-xs mt-1 text-stone-400 dark:text-stone-500">
						{item.category.name}{#if item.subcategory}
							· {item.subcategory.name}{/if}
					</p>
				{/if}
				{#if item.saves_count || item.completions_count}
					<div
						class="gap-3 mt-3 pt-2 border-stone-100 dark:border-stone-800
				            flex items-center border-t"
					>
						{#if item.saves_count}
							<span class="text-xs gap-1 text-stone-400 dark:text-stone-500 flex items-center">
								<Icon name="bookmark" size={11} />{fmtCount(item.saves_count)}
							</span>
						{/if}
						{#if item.completions_count}
							<span class="text-xs gap-1 text-stone-400 dark:text-stone-500 flex items-center">
								<Icon name="check" size={11} />{fmtCount(item.completions_count)}
							</span>
						{/if}
					</div>
				{/if}
			</div>
		</a>
	</article>
{:else if item?.type === 'hadith'}
	<!-- ─── Hadith: Arabic text + translation ────────────────────────────────── -->
	<article
		class="card group ease-standard hover:shadow-lg dark:hover:border-stone-700
                motion-safe:hover:-translate-y-0.5 @container relative
                overflow-hidden transition-all
                duration-200 motion-safe:will-change-transform"
	>
		<a {href} class="p-5 md:p-6 block">
			<div class="gap-3 mb-4 flex items-start justify-between">
				<span class="badge text-xs shrink-0 {cfg.pillCls}">{$t(cfg.labelKey)}</span>
				<div class="gap-0.5 flex shrink-0 items-center">
					<button
						onclick={toggleSave}
						class="p-1.5 rounded-lg shrink-0 transition-all duration-150 active:scale-90
				               {saved
							? 'text-emerald-600 dark:text-emerald-400'
							: 'text-stone-400 dark:text-stone-500 hover:text-stone-700 dark:hover:text-stone-200'}"
						aria-label={saved ? $t('content.saved') : $t('content.save')}
					>
						<Icon name="bookmark" size={16} strokeWidth={saved ? 2.5 : 1.5} />
					</button>
					<ShareMenu path={href} title={item.title} size={16} triggerClass={SHARE_TRIGGER} />
				</div>
			</div>
			{#if item.original_text}
				<blockquote
					class="verse-text mb-3 ps-4 text-base
			                   border-emerald-600 dark:border-emerald-500 border-s-4"
				>
					{item.original_text}
				</blockquote>
			{/if}
			{#if item.source_attribution}
				<p class="text-xs font-semibold mb-3 text-emerald-700 dark:text-emerald-400">
					— {item.source_attribution}
				</p>
			{/if}
			{#if !compact && item.translated_text}
				<p class="text-sm leading-relaxed mb-3 text-stone-500 dark:text-stone-400">
					{item.translated_text.length > 180
						? item.translated_text.slice(0, 180) + '…'
						: item.translated_text}
				</p>
			{/if}
			<div
				class="pt-3 border-stone-100 dark:border-stone-800 flex
		            items-center justify-between border-t"
			>
				<div class="gap-3 flex items-center">
					{#if completed}
						<span
							class="text-xs gap-1 font-medium text-emerald-600 dark:text-emerald-400 flex items-center"
						>
							<Icon name="check" size={12} strokeWidth={2.5} />{$t('content.completed')}
						</span>
					{:else}
						<button
							onclick={toggleComplete}
							class="text-xs gap-1 text-stone-400 dark:text-stone-500 hover:text-emerald-600 dark:hover:text-emerald-400
					               flex items-center transition-colors duration-150 active:scale-95"
							aria-label={$t('content.markComplete')}
						>
							<Icon name="check" size={12} />{$t('content.markComplete')}
						</button>
					{/if}
				</div>
				{#if item.saves_count}
					<span class="text-xs gap-1 text-stone-400 dark:text-stone-500 flex items-center">
						<Icon name="bookmark" size={11} />{fmtCount(item.saves_count)}
					</span>
				{/if}
			</div>
		</a>
	</article>
{:else if item?.type === 'note'}
	<!-- ─── Note: minimal ────────────────────────────────────────────────────── -->
	<article
		class="card p-4 ease-standard
                hover:shadow-md dark:hover:border-stone-700 motion-safe:hover:-translate-y-0.5
                @container transition-all
                duration-200"
	>
		<a {href} class="block">
			<p class="text-sm leading-relaxed text-stone-800 dark:text-stone-200">{item.body}</p>
			<div
				class="mt-3 pt-2 border-stone-100 dark:border-stone-800 flex
		            items-center justify-between border-t"
			>
				<div class="gap-2 flex items-center">
					<div
						class="w-5 h-5 bg-emerald-700 text-white text-xs font-bold
				            flex items-center justify-center rounded-full"
					>
						{(item.author?.name || item.author?.username)?.charAt(0)?.toUpperCase() || 'S'}
					</div>
					<span class="text-xs text-stone-400 dark:text-stone-500">
						{item.author?.name || item.author?.username || ''}
					</span>
				</div>
				<div class="gap-0.5 flex items-center">
					<button
						onclick={toggleSave}
						class="p-1.5 rounded-lg transition-all duration-150 active:scale-90
				               {saved
							? 'text-emerald-600 dark:text-emerald-400'
							: 'text-stone-400 dark:text-stone-500 hover:text-stone-700 dark:hover:text-stone-200'}"
						aria-label={saved ? $t('content.saved') : $t('content.save')}
					>
						<Icon name="bookmark" size={14} strokeWidth={saved ? 2.5 : 1.5} />
					</button>
					<ShareMenu
						path={href}
						title={item.body?.slice(0, 60) || $t('content.type.note')}
						size={14}
						triggerClass={SHARE_TRIGGER}
					/>
				</div>
			</div>
		</a>
	</article>
{:else}
	<!-- ─── Post (default): quote + body ─────────────────────────────────────── -->
	<article
		class="card group ease-standard hover:shadow-lg
                dark:hover:border-stone-700 motion-safe:hover:-translate-y-0.5 @container
                overflow-hidden transition-all
                duration-200 motion-safe:will-change-transform"
	>
		<a {href} class="p-5 md:p-6 block">
			<div class="gap-3 mb-4 flex items-start justify-between">
				<div class="gap-2 flex flex-wrap items-center">
					<span class="badge text-xs {cfg.pillCls}">{$t(cfg.labelKey)}</span>
					{#if item?.category}
						<span class="badge badge-stone">{item.category.name}</span>
					{/if}
					{#if item?.subcategory}
						<span class="badge badge-stone">{item.subcategory.name}</span>
					{/if}
				</div>
				<div class="gap-0.5 flex shrink-0 items-center">
					<button
						onclick={toggleSave}
						class="p-1.5 rounded-lg shrink-0 transition-all duration-150 active:scale-90
				               {saved
							? 'text-emerald-600 dark:text-emerald-400'
							: 'text-stone-400 dark:text-stone-500 hover:text-stone-700 dark:hover:text-stone-200'}"
						aria-label={saved ? $t('content.saved') : $t('content.save')}
					>
						<Icon name="bookmark" size={16} strokeWidth={saved ? 2.5 : 1.5} />
					</button>
					<ShareMenu path={href} title={item?.title} size={16} triggerClass={SHARE_TRIGGER} />
				</div>
			</div>
			{#if item?.original_text}
				<blockquote
					class="verse-text mb-3 ps-4 text-base
			                   border-emerald-600 dark:border-emerald-500 border-s-4"
				>
					{item.original_text}
				</blockquote>
			{/if}
			{#if item?.source_attribution}
				<p class="text-xs font-semibold mb-3 text-emerald-700 dark:text-emerald-400">
					— {item.source_attribution}
				</p>
			{/if}
			{#if !compact && bodySnippet}
				<p class="text-sm leading-relaxed text-stone-500 dark:text-stone-400">{bodySnippet}</p>
			{/if}
			<div
				class="mt-4 pt-3 border-stone-100 dark:border-stone-800 flex
		            items-center justify-between border-t"
			>
				<div class="gap-2 flex items-center">
					<div
						class="w-6 h-6 bg-emerald-700 text-white text-xs font-bold
				            flex shrink-0 items-center justify-center rounded-full"
					>
						{(item?.author?.name || item?.author?.username)?.charAt(0)?.toUpperCase() || 'S'}
					</div>
					<span class="text-xs text-stone-400 dark:text-stone-500">
						{item?.author?.name || item?.author?.username || $t('content.sheikh')}
					</span>
				</div>
				<div class="gap-2 flex items-center">
					{#if completed}
						<span
							class="text-xs gap-1 font-medium text-emerald-600 dark:text-emerald-400 flex items-center"
						>
							<Icon name="check" size={12} strokeWidth={2.5} />{$t('content.completed')}
						</span>
					{:else}
						<button
							onclick={toggleComplete}
							class="text-xs gap-1 text-stone-400 dark:text-stone-500
					               hover:text-emerald-600 dark:hover:text-emerald-400 flex items-center
					               transition-colors duration-150 active:scale-95"
							aria-label={$t('content.markComplete')}
						>
							<Icon name="check" size={12} />{$t('content.markComplete')}
						</button>
					{/if}
					{#if item?.saves_count}
						<span class="text-xs gap-1 text-stone-400 dark:text-stone-500 flex items-center">
							<Icon name="bookmark" size={11} />{fmtCount(item.saves_count)}
						</span>
					{/if}
				</div>
			</div>
		</a>
	</article>
{/if}
