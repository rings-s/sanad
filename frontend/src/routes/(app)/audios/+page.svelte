<script>
	import { t } from '$lib/stores/locale.js';
	import ContentBrowser from '$lib/components/ContentBrowser.svelte';
</script>

<ContentBrowser
	title={$t('audios.title')}
	subtitle={$t('audios.subtitle')}
	layout="listen"
	type="audio"
	emptyIcon="headphones"
	emptyText={$t('audios.empty')}
	searchPlaceholder={$t('ui.searchPlaceholder')}
/>
