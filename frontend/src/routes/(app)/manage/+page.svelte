<script>
	import { t, dir } from '$lib/stores/locale.js';
	import { currentUser } from '$lib/stores/auth.js';
	import Icon from '$lib/components/Icon.svelte';

	const isSheikh = $derived($currentUser?.is_sheikh === true);

	/** @type {{ key: string, href: string, icon: string }[]} */
	const sections = $derived([
		{ key: 'content', href: '/manage/content', icon: 'notepad' },
		{ key: 'comments', href: '/manage/comments', icon: 'chat' },
		...(isSheikh
			? [
					{ key: 'daily', href: '/manage/daily', icon: 'sun' },
					{ key: 'taxonomy', href: '/manage/taxonomy', icon: 'layers' },
					{ key: 'users', href: '/manage/users', icon: 'user' }
				]
			: [])
	]);
</script>

<div class="gap-3 sm:grid-cols-2 grid">
	{#each sections as s (s.key)}
		<a
			href={s.href}
			class="card group gap-4 p-4 hover:bg-stone-50 dark:hover:bg-stone-800/60 flex items-center transition-colors"
		>
			<span
				class="h-11 w-11 rounded-xl bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 grid shrink-0 place-items-center"
			>
				<Icon name={s.icon} size={20} />
			</span>
			<span class="min-w-0 flex-1">
				<span class="text-sm font-semibold text-stone-900 dark:text-stone-50 block">
					{$t(`admin.tabs.${s.key}`)}
				</span>
				<span class="text-xs text-stone-500 dark:text-stone-400 block truncate">
					{$t(`admin.sectionDesc.${s.key}`)}
				</span>
			</span>
			<Icon
				name={$dir === 'rtl' ? 'arrowLeft' : 'arrowRight'}
				size={16}
				class="text-stone-300 group-hover:text-stone-500 dark:text-stone-600 shrink-0 transition-colors"
			/>
		</a>
	{/each}
</div>
