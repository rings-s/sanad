<script>
	import { t, locale } from '$lib/stores/locale.js';
	import { auth, currentUser } from '$lib/stores/auth.js';
	import { authApi } from '$lib/api/auth.js';
	import { goto } from '$app/navigation';
	import TopBar from '$lib/components/TopBar.svelte';
	import Icon from '$lib/components/Icon.svelte';

	let editing = $state(false);
	let saving = $state(false);
	let saveError = $state('');
	let saveSuccess = $state(false);

	let username = $state('');
	let bio = $state('');
	let nationality = $state('');
	let journalEnabled = $state(true);
	let avatarFile = $state(null);
	let avatarPreview = $state('');

	function initForm(user) {
		if (!user) return;
		username = user.username || '';
		bio = user.profile?.bio || '';
		nationality = user.profile?.nationality || '';
		journalEnabled = user.profile?.spiritual_journal_enabled ?? true;
		avatarPreview = user.profile?.avatar || '';
	}

	$effect(() => {
		if ($currentUser) initForm($currentUser);
	});

	function onAvatarChange(e) {
		const file = e.target.files?.[0];
		if (!file) return;
		avatarFile = file;
		avatarPreview = URL.createObjectURL(file);
	}

	async function saveProfile(e) {
		e.preventDefault();
		saving = true;
		saveError = '';
		saveSuccess = false;
		try {
			const fd = new FormData();
			fd.append('username', username);
			fd.append('profile.bio', bio);
			fd.append('profile.nationality', nationality);
			fd.append('profile.spiritual_journal_enabled', String(journalEnabled));
			if (avatarFile) fd.append('profile.avatar', avatarFile);
			const updated = await authApi.updateMe(fd);
			auth.updateUser(updated);
			saveSuccess = true;
			editing = false;
		} catch (err) {
			saveError = err.message || $t('ui.error');
		} finally {
			saving = false;
		}
	}

	async function handleLogout() {
		const { refreshToken } = $auth;
		try {
			if (refreshToken) await authApi.logout(refreshToken);
		} catch {}
		auth.logout();
		goto('/');
	}

	function joinedDate(user) {
		if (!user?.date_joined && !user?.profile?.created_at) return '';
		const d = new Date(user.date_joined || user.profile.created_at);
		return d.toLocaleDateString($locale === 'ar' ? 'ar-SA' : 'en-US', {
			year: 'numeric', month: 'long',
		});
	}

	const roleLabel = {
		user: 'profile.role.user',
		content_manager: 'profile.role.content_manager',
		sheikh: 'profile.role.sheikh',
	};
</script>

<svelte:head>
	<title>{$t('profile.title')} — {$t('app.name')}</title>
</svelte:head>

<TopBar title={$t('profile.title')} />

<div class="mx-auto w-full max-w-2xl px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
	{#if !$currentUser}
		<div class="space-y-4">
			<div class="shimmer w-20 h-20 rounded-full mx-auto"></div>
			<div class="shimmer h-5 w-32 rounded mx-auto"></div>
			<div class="shimmer h-4 w-48 rounded mx-auto"></div>
		</div>
	{:else}
		<!-- Profile header card -->
		<div class="card p-5 sm:p-6 mb-5">
			<div class="flex items-start gap-4">
				<!-- Avatar -->
				<div class="relative shrink-0">
					{#if avatarPreview || $currentUser.profile?.avatar}
						<img
							src={avatarPreview || $currentUser.profile.avatar}
							alt={$currentUser.username}
							class="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl object-cover"
						/>
					{:else}
						<div
							class="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl flex items-center justify-center
							       text-white text-2xl font-bold bg-gradient-to-br from-emerald-600 to-emerald-800"
						>
							{$currentUser.username?.charAt(0)?.toUpperCase() || '?'}
						</div>
					{/if}
				</div>

				<!-- Info -->
				<div class="flex-1 min-w-0">
					<h2 class="font-display text-lg sm:text-xl font-semibold tracking-tight truncate text-stone-900 dark:text-stone-50">
						{$currentUser.username || ''}
					</h2>
					<p class="text-sm truncate text-stone-400 dark:text-stone-500">{$currentUser.email}</p>

					{#if $currentUser.role}
						<span class="badge badge-accent mt-2 text-xs">
							{$t(roleLabel[$currentUser.role] || 'profile.role.user')}
						</span>
					{/if}
				</div>

				<!-- Edit button -->
				<button
					onclick={() => { editing = !editing; saveSuccess = false; saveError = ''; }}
					class="btn-ghost text-xs min-h-0 py-2 px-3 shrink-0"
				>
					<Icon name={editing ? 'x' : 'edit'} size={13} />
					<span class="hidden sm:inline">{editing ? $t('ui.cancel') : $t('profile.editProfile')}</span>
				</button>
			</div>

			{#if $currentUser.profile?.bio}
				<p class="text-sm mt-4 leading-relaxed text-stone-500 dark:text-stone-400">
					{$currentUser.profile.bio}
				</p>
			{/if}

			{#if $currentUser.profile?.nationality}
				<p class="flex items-center gap-1.5 text-xs mt-3 text-stone-400 dark:text-stone-500">
					<Icon name="globe" size={13} class="shrink-0" />
					{$currentUser.profile.nationality}
				</p>
			{/if}

			{#if joinedDate($currentUser)}
				<p class="text-xs mt-3 text-stone-400 dark:text-stone-500">
					{$t('profile.joinedOn')} {joinedDate($currentUser)}
				</p>
			{/if}
		</div>

		<!-- Edit form -->
		{#if editing}
			<div class="card p-5 sm:p-6 mb-5">
				{#if saveError}
					<div class="flex items-start gap-2 p-3 rounded-xl mb-4 text-sm
					            bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400
					            border border-red-200 dark:border-red-800/60"
					     role="alert">
						<Icon name="x" size={14} class="shrink-0 mt-0.5" />
						{saveError}
					</div>
				{/if}

				<form onsubmit={saveProfile}>
					<!-- Avatar upload -->
					<div class="mb-5">
						<label class="block text-sm font-medium mb-2 text-stone-700 dark:text-stone-300">
							{$locale === 'ar' ? 'الصورة الشخصية' : 'Profile picture'}
						</label>
						<div class="flex items-center gap-3">
							{#if avatarPreview}
								<img src={avatarPreview} alt="" class="w-12 h-12 rounded-xl object-cover" />
							{:else}
								<div class="w-12 h-12 rounded-xl flex items-center justify-center
								            text-white font-bold bg-gradient-to-br from-emerald-600 to-emerald-800">
									{$currentUser.username?.charAt(0)?.toUpperCase() || '?'}
								</div>
							{/if}
							<label class="btn-ghost text-xs cursor-pointer min-h-0 py-2.5">
								<Icon name="plus" size={13} />
								{$locale === 'ar' ? 'اختيار صورة' : 'Choose image'}
								<input type="file" accept="image/*" class="sr-only" onchange={onAvatarChange} />
							</label>
						</div>
					</div>

					<!-- Username -->
					<div class="mb-4">
						<label class="block text-sm font-medium mb-1.5 text-stone-700 dark:text-stone-300" for="edit-username">
							{$t('auth.username')}
						</label>
						<input id="edit-username" type="text" class="input-field" bind:value={username} />
					</div>

					<!-- Bio -->
					<div class="mb-4">
						<label class="block text-sm font-medium mb-1.5 text-stone-700 dark:text-stone-300" for="edit-bio">
							{$t('profile.bio')}
						</label>
						<textarea
							id="edit-bio"
							class="input-field resize-none"
							rows="3"
							placeholder={$t('profile.bioPlaceholder')}
							bind:value={bio}
						></textarea>
					</div>

					<!-- Nationality -->
					<div class="mb-4">
						<label class="block text-sm font-medium mb-1.5 text-stone-700 dark:text-stone-300" for="edit-nationality">
							{$t('profile.nationality')}
						</label>
						<input
							id="edit-nationality"
							type="text"
							maxlength="100"
							class="input-field"
							placeholder={$t('profile.nationalityPlaceholder')}
							bind:value={nationality}
						/>
					</div>

					<!-- Spiritual journal toggle -->
					<label class="flex items-center gap-3 mb-5 cursor-pointer">
						<div
							class="relative w-10 h-5 rounded-full transition-colors duration-200
							       {journalEnabled ? 'bg-emerald-600' : 'bg-stone-300 dark:bg-stone-600'}"
						>
							<div
								class="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200"
								style="transform: translateX({journalEnabled ? ($locale === 'ar' ? '-1.25rem' : '1.25rem') : '0.125rem'});"
							></div>
							<input type="checkbox" class="sr-only" bind:checked={journalEnabled} />
						</div>
						<span class="text-sm text-stone-500 dark:text-stone-400">{$t('profile.spiritualJournal')}</span>
					</label>

					<button type="submit" class="btn-primary w-full text-sm" disabled={saving} aria-busy={saving}>
						{#if saving}
							<span class="inline-block w-4 h-4 rounded-full border-2 border-white/30 border-t-white motion-safe:animate-spin" aria-hidden="true"></span>
						{/if}
						{$t('profile.saveChanges')}
					</button>
				</form>
			</div>
		{/if}

		<!-- Logout -->
		<div class="card p-2">
			<button
				onclick={handleLogout}
				class="flex items-center gap-2 text-sm w-full min-h-12 px-3 rounded-xl
				       text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20
				       transition-colors duration-150 focus-visible:ring-2 focus-visible:ring-red-400"
			>
				<Icon name="logout" size={16} />
				{$t('nav.logout')}
			</button>
		</div>
	{/if}
</div>
