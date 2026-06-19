<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { currentUser } from '$lib/stores/auth.js';
	import AdminDailyPanel from '$lib/components/admin/AdminDailyPanel.svelte';

	// Daily guidance is Sheikh-only. The layout already blocks non-creators; this
	// sends content managers back to the hub. The backend rejects them regardless.
	const isSheikh = $derived($currentUser?.is_sheikh === true);

	onMount(() => {
		if ($currentUser && !$currentUser.is_sheikh) goto('/manage');
	});
</script>

{#if isSheikh}
	<AdminDailyPanel />
{/if}
