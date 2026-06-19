// Barrel exports for $lib
export { auth, isAuthenticated, currentUser, authLoading } from './stores/auth.js';
export { locale, t, dir, setLocale, toggleLocale } from './stores/locale.js';
export { client, ApiError, extractErrors } from './api/client.js';
export { default as ShareMenu } from './components/ShareMenu.svelte';
export {
	SHARE_TARGETS,
	buildShareUrl,
	intentUrl,
	openShareWindow,
	copyToClipboard
} from './share/share.js';
