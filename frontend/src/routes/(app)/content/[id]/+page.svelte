<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { t, locale } from '$lib/stores/locale.js';
	import { contentApi } from '$lib/api/content.js';
	import YouTubeEmbed from '$lib/components/YouTubeEmbed.svelte';
	import TopBar from '$lib/components/TopBar.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import ShareMenu from '$lib/components/ShareMenu.svelte';

	let item = $state(null);
	let comments = $state([]);
	let loading = $state(true);
	let error = $state('');
	let saved = $state(false);
	let completed = $state(false);
	let saving = $state(false);
	let completing = $state(false);
	let commentText = $state('');
	let commenting = $state(false);
	let commentMsg = $state('');

	const TYPE = {
		post: {
			icon: 'notepad',
			labelKey: 'content.type.post',
			pill: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
		},
		video: {
			icon: 'video',
			labelKey: 'content.type.video',
			pill: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
		},
		audio: {
			icon: 'headphones',
			labelKey: 'content.type.audio',
			pill: 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300'
		},
		note: {
			icon: 'spark',
			labelKey: 'content.type.note',
			pill: 'bg-stone-100 text-stone-600 dark:bg-stone-800 dark:text-stone-400'
		},
		hadith: {
			icon: 'star',
			labelKey: 'content.type.hadith',
			pill: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
		}
	};

	const cfg = $derived(item ? (TYPE[item.type] ?? TYPE.post) : TYPE.post);

	function formatDate(s) {
		if (!s) return '';
		return new Date(s).toLocaleDateString($locale === 'ar' ? 'ar-SA' : 'en-US', {
			dateStyle: 'long'
		});
	}

	onMount(async () => {
		const id = $page.params.id;
		try {
			const [itemData, commentsData] = await Promise.all([
				contentApi.get(id),
				contentApi.getComments(id).catch(() => ({ results: [] }))
			]);
			item = itemData;
			saved = itemData.is_saved ?? false;
			completed = itemData.is_completed ?? false;
			comments = commentsData.results ?? commentsData ?? [];
		} catch (e) {
			error = e.message || $t('ui.error');
		} finally {
			loading = false;
		}
	});

	async function toggleSave() {
		if (saving || !item) return;
		saving = true;
		try {
			if (saved) await contentApi.unsave(item.public_id);
			else await contentApi.save(item.public_id);
			saved = !saved;
		} catch {}
		saving = false;
	}

	async function toggleComplete() {
		if (completing || completed || !item) return;
		completing = true;
		try {
			await contentApi.markComplete(item.public_id);
			completed = true;
		} catch {}
		completing = false;
	}

	async function submitComment() {
		if (!commentText.trim() || commenting || !item) return;
		commenting = true;
		commentMsg = '';
		try {
			await contentApi.addComment(item.public_id, commentText.trim());
			commentText = '';
			commentMsg = $t('content.commentPending');
		} catch (e) {
			commentMsg = e.message || $t('ui.error');
		}
		commenting = false;
	}
</script>

<svelte:head>
	<title>{item?.title || $t('content.type.post')} — {$t('app.name')}</title>
</svelte:head>
<TopBar title={item ? $t(cfg.labelKey) : ''} />

<div class="max-w-3xl px-4 sm:px-6 lg:px-8 py-6 lg:py-8 mx-auto w-full">
	<a
		href="/feed"
		class="gap-1.5 text-sm mb-5 text-stone-400 dark:text-stone-500 hover:text-stone-700
	   dark:hover:text-stone-300 inline-flex items-center transition-colors"
	>
		<Icon name={$locale === 'ar' ? 'chevronRight' : 'chevronLeft'} size={14} />
		{$t('ui.back')}
	</a>

	{#if loading}
		<div class="space-y-4">
			<div class="shimmer h-8 rounded w-2/3"></div>
			<div class="shimmer h-4 rounded w-full"></div>
			<div class="shimmer h-4 rounded w-5/6"></div>
			<div class="shimmer aspect-video rounded-2xl mt-4 w-full"></div>
		</div>
	{:else if error || !item}
		<div class="card p-10 text-center">
			<p class="text-sm mb-4 text-stone-500 dark:text-stone-400">{error || $t('ui.noResults')}</p>
			<a href="/feed" class="btn-ghost text-sm">{$t('ui.back')}</a>
		</div>
	{:else}
		<!-- Type badge + engagement row -->
		<div class="gap-3 mb-5 flex items-center justify-between">
			<div class="gap-2 flex flex-wrap items-center">
				<span class="badge text-xs {cfg.pill}">{$t(cfg.labelKey)}</span>
				{#if item.category}<span class="badge badge-stone">{item.category.name}</span>{/if}
			</div>
			<div class="gap-2 flex shrink-0 items-center">
				<!-- Complete -->
				{#if completed}
					<span
						class="gap-1 text-xs font-medium px-2.5 py-1.5 bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700
					             dark:text-emerald-400 flex items-center rounded-full"
					>
						<Icon name="check" size={13} strokeWidth={2.5} />{$t('content.completed')}
					</span>
				{:else}
					<button
						onclick={toggleComplete}
						disabled={completing}
						class="gap-1 text-xs font-medium px-2.5 py-1.5 bg-stone-100 dark:bg-stone-800 text-stone-500
						       dark:text-stone-400 hover:bg-stone-200 dark:hover:bg-stone-700 flex
						       items-center rounded-full transition-colors duration-150"
					>
						<Icon name="check" size={13} />{$t('content.markComplete')}
					</button>
				{/if}
				<!-- Save -->
				<button
					onclick={toggleSave}
					disabled={saving}
					class="p-2.5 rounded-xl transition-all duration-150 active:scale-95
					       {saved
						? 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400'
						: 'bg-stone-100 dark:bg-stone-800 text-stone-400 dark:text-stone-500 hover:text-stone-700 dark:hover:text-stone-200'}"
					aria-label={saved ? $t('content.saved') : $t('content.save')}
				>
					<Icon name="bookmark" size={18} strokeWidth={saved ? 2.5 : 1.5} />
				</button>
				<!-- Share -->
				<ShareMenu path={`/content/${item.public_id}`} title={item.title} />
			</div>
		</div>

		<!-- Title -->
		<h1
			class="font-display text-2xl md:text-3xl font-semibold tracking-tight mb-4 text-stone-900 dark:text-stone-50"
		>
			{item.title}
		</h1>

		<!-- Video embed -->
		{#if item.type === 'video' && item.youtube_url}
			<div class="mb-6"><YouTubeEmbed url={item.youtube_url} title={item.title} /></div>
		{/if}

		<!-- Audio player -->
		{#if item.type === 'audio' && item.audio_file}
			<div class="mb-6 p-4 rounded-2xl bg-stone-100 dark:bg-stone-800">
				<audio src={item.audio_file} controls class="w-full"></audio>
			</div>
		{/if}

		<!-- Featured image (posts) -->
		{#if item.featured_image && item.type === 'post'}
			<img
				src={item.featured_image}
				alt={item.title}
				class="rounded-2xl mb-6 max-h-80 w-full object-cover"
				loading="lazy"
			/>
		{/if}

		<!-- Hadith / verse: Arabic + translation -->
		{#if item.original_text}
			<blockquote
				class="verse-text mb-4 ps-4 border-emerald-600 dark:border-emerald-500 border-s-4"
			>
				{item.original_text}
			</blockquote>
		{/if}
		{#if item.source_attribution}
			<p class="text-sm font-semibold mb-4 text-emerald-700 dark:text-emerald-400">
				— {item.source_attribution}
			</p>
		{/if}
		{#if item.translated_text}
			<p class="text-base leading-relaxed mb-4 text-stone-500 dark:text-stone-400 italic">
				{item.translated_text}
			</p>
		{/if}

		<!-- Body -->
		{#if item.body}
			<div class="content-prose">
				{#each item.body.split('\n\n') as para}<p>{para}</p>{/each}
			</div>
		{/if}

		<!-- Tags -->
		{#if item.tags?.length}
			<div class="gap-1.5 mt-5 flex flex-wrap">
				{#each item.tags as tag}<span class="badge badge-stone">#{tag.name}</span>{/each}
			</div>
		{/if}

		<!-- Author + date -->
		<div
			class="mt-6 pt-4 border-stone-200 dark:border-stone-800 flex items-center justify-between border-t"
		>
			<div class="gap-2 flex items-center">
				<div
					class="w-8 h-8 rounded-xl text-white text-sm font-bold bg-emerald-700 flex shrink-0 items-center justify-center"
				>
					{(item.author?.name || item.author?.username)?.charAt(0)?.toUpperCase() || 'S'}
				</div>
				<div>
					<p class="text-sm font-medium text-stone-900 dark:text-stone-50">
						{item.author?.name || item.author?.username || $t('content.sheikh')}
					</p>
					<p class="text-xs text-stone-400 dark:text-stone-500">{formatDate(item.created_at)}</p>
				</div>
			</div>
			{#if item.youtube_url}
				<a
					href={item.youtube_url}
					target="_blank"
					rel="noopener noreferrer"
					class="btn-ghost text-xs min-h-0 py-2 px-3"
				>
					<Icon name="play" size={12} />{$t('content.watchOnYoutube')}
				</a>
			{/if}
		</div>

		<!-- Engagement stats -->
		{#if item.saves_count || item.completions_count}
			<div class="gap-4 mt-3 flex items-center">
				{#if item.saves_count}<span
						class="text-xs gap-1 text-stone-400 dark:text-stone-500 flex items-center"
						><Icon name="bookmark" size={12} />{item.saves_count}
						{$t('content.saved').toLowerCase()}</span
					>{/if}
				{#if item.completions_count}<span
						class="text-xs gap-1 text-stone-400 dark:text-stone-500 flex items-center"
						><Icon name="check" size={12} />{item.completions_count}
						{$t('content.completed').toLowerCase()}</span
					>{/if}
			</div>
		{/if}

		<!-- Comments -->
		<section class="mt-8">
			<h2 class="text-sm font-bold mb-4 text-stone-900 dark:text-stone-50">
				{$t('content.comments')}
			</h2>
			<!-- Add comment -->
			<div class="mb-5">
				<textarea
					class="input-field text-sm mb-2 resize-none"
					rows="3"
					placeholder={$t('content.addComment')}
					bind:value={commentText}
				></textarea>
				<div class="gap-3 flex items-center justify-between">
					{#if commentMsg}<p class="text-xs text-emerald-700 dark:text-emerald-400">
							{commentMsg}
						</p>{:else}<span></span>{/if}
					<button
						onclick={submitComment}
						class="btn-primary text-sm min-h-0 py-2.5 px-4"
						disabled={commenting || !commentText.trim()}
						aria-busy={commenting}
					>
						{#if commenting}<span
								class="w-3.5 h-3.5 border-white/30 border-t-white motion-safe:animate-spin inline-block rounded-full border-2"
								aria-hidden="true"
							></span>{/if}
						{$t('content.comment')}
					</button>
				</div>
			</div>
			<!-- Comment list -->
			{#if comments.length === 0}
				<p class="text-sm text-stone-400 dark:text-stone-500">{$t('content.noComments')}</p>
			{:else}
				<div class="space-y-3">
					{#each comments as c (c.public_id)}
						<div class="p-4 rounded-xl bg-stone-100 dark:bg-stone-800">
							<div class="gap-2 mb-2 flex items-center">
								<div
									class="w-6 h-6 text-white text-xs font-bold bg-emerald-700 flex items-center justify-center rounded-full"
								>
									{(c.user?.name || c.user?.username)?.charAt(0)?.toUpperCase() || '?'}
								</div>
								<span class="text-xs font-medium text-stone-900 dark:text-stone-50"
									>{c.user?.name || c.user?.username || ''}</span
								>
								<span class="text-xs text-stone-400 dark:text-stone-500 ms-auto"
									>{new Date(c.created_at).toLocaleDateString()}</span
								>
							</div>
							<p class="text-sm leading-relaxed text-stone-500 dark:text-stone-400">{c.text}</p>
						</div>
					{/each}
				</div>
			{/if}
		</section>
	{/if}
</div>
