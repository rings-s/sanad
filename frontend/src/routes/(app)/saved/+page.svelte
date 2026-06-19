<script>
	import { t } from '$lib/stores/locale.js';
	import { contentApi } from '$lib/api/content.js';
	import ContentBrowser from '$lib/components/ContentBrowser.svelte';

	// Saved rows arrive hydrated as { public_id, content: {...}, created_at };
	// flatten to the content shape the cards expect, keeping the save id/date.
	const mapSaves = (rows) =>
		rows.map((s) => ({ ...s.content, _saved_at: s.created_at, _saved_id: s.public_id }));
</script>

<ContentBrowser
	title={$t('saved.title')}
	subtitle={$t('saved.subtitle')}
	layout="discover"
	emptyIcon="bookmark"
	emptyText={$t('saved.empty')}
	searchPlaceholder={$t('ui.searchPlaceholder')}
	fetcher={(p) => contentApi.mySaves(p)}
	mapResults={mapSaves}
	clientFilter
/>
