<script>
	import { t } from '$lib/stores/locale.js';
	import ContentBrowser from '$lib/components/ContentBrowser.svelte';
</script>

<ContentBrowser
	title={$t('feed.title')}
	subtitle={$t('feed.subtitle')}
	layout="discover"
	emptyIcon="spark"
	emptyText={$t('feed.empty')}
	searchPlaceholder={$t('search.placeholder')}
/>
