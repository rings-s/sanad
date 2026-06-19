<script>
	import { t } from '$lib/stores/locale.js';
	import ContentBrowser from '$lib/components/ContentBrowser.svelte';
</script>

<ContentBrowser
	title={$t('videos.title')}
	subtitle={$t('videos.subtitle')}
	layout="videos"
	type="video"
	emptyIcon="video"
	emptyText={$t('videos.empty')}
	searchPlaceholder={$t('ui.searchPlaceholder')}
/>
