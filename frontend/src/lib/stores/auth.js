import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Only the non-sensitive user object is persisted in localStorage.
// The access token lives in memory only (cleared on page refresh).
// The refresh token lives in an HttpOnly cookie set by the backend — JS never touches it.
const USER_KEY = 'sanad_user';

function createAuthStore() {
	const { subscribe, set, update } = writable({
		user: null,
		token: null,   // access token — in-memory only
		loading: true,
	});

	return {
		subscribe,

		/**
		 * Called once from the root layout on mount.
		 * If a user object is cached in localStorage, restore it immediately for
		 * instant UI (optimistic hydration), then silently refresh the access token
		 * from the HttpOnly cookie via the /token/refresh/cookie/ endpoint.
		 */
		async init() {
			if (!browser) {
				set({ user: null, token: null, loading: false });
				return;
			}

			const raw = localStorage.getItem(USER_KEY);
			if (!raw) {
				set({ user: null, token: null, loading: false });
				return;
			}

			let user = null;
			try {
				user = JSON.parse(raw);
			} catch {
				localStorage.removeItem(USER_KEY);
				set({ user: null, token: null, loading: false });
				return;
			}

			// Show the user immediately while we validate the cookie.
			set({ user, token: null, loading: true });

			try {
				// Same-origin (proxied by hooks.server.js → first-party refresh cookie).
				const res = await fetch('/api/v1/auth/token/refresh/cookie/', {
					method: 'POST',
					credentials: 'include',
					headers: { 'Content-Type': 'application/json' },
				});

				if (res.ok) {
					const data = await res.json();
					// data.data.access is the new access token (Sanad envelope)
					const access = data?.data?.access ?? data?.access;
					set({ user, token: access ?? null, loading: false });
				} else {
					// Cookie is expired or absent — log the user out cleanly.
					localStorage.removeItem(USER_KEY);
					set({ user: null, token: null, loading: false });
				}
			} catch {
				// Network error during init — keep the user visible but mark token null.
				// The API client will retry on the next request.
				set({ user, token: null, loading: false });
			}
		},

		/**
		 * Persist a successful login.
		 * @param {object} user - The user object from the API.
		 * @param {string} access - The short-lived access token (in memory only).
		 * The refresh token is already set as an HttpOnly cookie by the backend.
		 */
		login(user, access) {
			if (browser) {
				localStorage.setItem(USER_KEY, JSON.stringify(user));
			}
			set({ user, token: access, loading: false });
		},

		logout() {
			if (browser) {
				localStorage.removeItem(USER_KEY);
			}
			set({ user: null, token: null, loading: false });
		},

		updateUser(user) {
			update((state) => {
				if (browser) localStorage.setItem(USER_KEY, JSON.stringify(user));
				return { ...state, user };
			});
		},

		updateToken(token) {
			update((state) => ({ ...state, token }));
		},
	};
}

export const auth = createAuthStore();

export const isAuthenticated = derived(auth, ($a) => !!$a.token && !$a.loading);

export const currentUser = derived(auth, ($a) => $a.user);

export const authLoading = derived(auth, ($a) => $a.loading);
