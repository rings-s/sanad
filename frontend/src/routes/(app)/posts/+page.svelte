<script>
	import { t } from '$lib/stores/locale.js';
	import ContentBrowser from '$lib/components/ContentBrowser.svelte';
</script>

<ContentBrowser
	title={$t('posts.title')}
	subtitle={$t('posts.subtitle')}
	layout="articles"
	type="post"
	emptyIcon="notepad"
	emptyText={$t('posts.empty')}
	searchPlaceholder={$t('ui.searchPlaceholder')}
/>
