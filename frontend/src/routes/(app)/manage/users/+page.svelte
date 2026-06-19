<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { currentUser } from '$lib/stores/auth.js';
	import AdminUsersPanel from '$lib/components/admin/AdminUsersPanel.svelte';

	// User administration is Sheikh-only. The layout blocks non-creators; this
	// sends content managers back to the hub. The backend rejects them regardless.
	const isSheikh = $derived($currentUser?.is_sheikh === true);

	onMount(() => {
		if ($currentUser && !$currentUser.is_sheikh) goto('/manage');
	});
</script>

{#if isSheikh}
	<AdminUsersPanel />
{/if}
