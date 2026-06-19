<script>
	let { type = 'post', count = 3 } = $props();
</script>

{#each Array(count) as _, i}
	{#if type === 'video'}
		<div class="card overflow-hidden" aria-hidden="true">
			<div class="shimmer w-full aspect-video"></div>
			<div class="p-4 space-y-3">
				<div class="shimmer h-5 w-14 rounded-full"></div>
				<div class="space-y-1.5">
					<div class="shimmer h-4 w-full rounded-lg"></div>
					<div class="shimmer h-4 w-3/4 rounded-lg"></div>
				</div>
			</div>
		</div>

	{:else if type === 'audio'}
		<div class="card flex items-center gap-4 p-4" aria-hidden="true">
			<div class="shimmer w-12 h-12 rounded-2xl shrink-0"></div>
			<div class="flex-1 space-y-2">
				<div class="shimmer h-4 w-3/4 rounded-lg"></div>
				<div class="shimmer h-3 w-1/2 rounded-lg"></div>
			</div>
			<div class="shimmer w-7 h-7 rounded-xl shrink-0"></div>
		</div>

	{:else}
		<div class="card p-5 space-y-4" aria-hidden="true">
			<!-- Pill badges -->
			<div class="flex items-center gap-2">
				<div class="shimmer h-5 w-16 rounded-full"></div>
				<div class="shimmer h-5 w-20 rounded-full"></div>
			</div>
			<!-- Text lines -->
			<div class="space-y-2">
				<div class="shimmer h-4 w-full rounded-lg"></div>
				<div class="shimmer h-4 w-5/6 rounded-lg"></div>
			</div>
			<!-- Body text lines -->
			<div class="space-y-1.5">
				<div class="shimmer h-3 w-full rounded-lg"></div>
				<div class="shimmer h-3 w-4/5 rounded-lg"></div>
				<div class="shimmer h-3 w-3/4 rounded-lg"></div>
			</div>
			<!-- Footer -->
			<div class="flex items-center justify-between pt-3 border-t border-stone-100 dark:border-stone-800">
				<div class="flex items-center gap-2">
					<div class="shimmer w-6 h-6 rounded-full"></div>
					<div class="shimmer h-3 w-20 rounded-lg"></div>
				</div>
				<div class="shimmer h-3 w-16 rounded-lg"></div>
			</div>
		</div>
	{/if}
{/each}
