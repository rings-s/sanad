<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { auth, isAuthenticated, authLoading } from '$lib/stores/auth.js';
	import SideNav from '$lib/components/SideNav.svelte';
	import BottomNav from '$lib/components/BottomNav.svelte';

	let { children } = $props();

	const COLLAPSE_KEY = 'sanad_sidebar_collapsed';

	let sideCollapsed = $state(browser && localStorage.getItem(COLLAPSE_KEY) === '1');

	$effect(() => {
		if (browser) localStorage.setItem(COLLAPSE_KEY, sideCollapsed ? '1' : '0');
	});

	onMount(() => {
		const unsub = auth.subscribe(($a) => {
			if (!$a.loading && !$a.token) goto('/login');
		});
		return unsub;
	});
</script>

{#if $authLoading}
	<!-- ── Full-screen auth loading spinner ────────────────────────────────── -->
	<div class="min-h-dvh flex items-center justify-center bg-stone-50 dark:bg-stone-950"
	     aria-live="polite" aria-label="Loading">
		<div class="flex flex-col items-center gap-4">
			<div class="w-10 h-10 rounded-full border-2 border-stone-200 dark:border-stone-800
			            border-t-emerald-600 dark:border-t-emerald-500
			            motion-safe:animate-spin">
			</div>
			<p class="text-sm text-stone-400 dark:text-stone-500">Loading…</p>
		</div>
	</div>

{:else if $isAuthenticated}
	<div class="flex bg-stone-50 dark:bg-stone-950 min-h-dvh">
		<!-- Sidebar — desktop -->
		<SideNav bind:collapsed={sideCollapsed} />

		<!-- Main column -->
		<div
			class="app-main flex-1 flex flex-col min-w-0"
			style="--sidebar-w: {sideCollapsed ? '64px' : '220px'};"
		>
			<main class="flex-1 pb-[calc(4.5rem+env(safe-area-inset-bottom))] md:pb-0">
				{@render children()}
			</main>
		</div>

		<!-- Bottom nav — mobile -->
		<BottomNav />
	</div>
{/if}
