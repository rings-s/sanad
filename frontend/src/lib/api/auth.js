import { client } from './client.js';

export const authApi = {
	register: (email, username, password) =>
		client.post('/api/v1/auth/register/', { email, username, password }),

	login: (email, password) =>
		client.post('/api/v1/auth/login/', { email, password }),

	/**
	 * OAuth2 Authorization Code + PKCE flow.
	 * Called from the /auth/google/callback page after Google redirects back.
	 *
	 * @param {string} code - The authorization code from Google.
	 * @param {string} redirectUri - Must exactly match the Google Cloud Console registration
	 *   and the value used to build the authorization URL: http://localhost:5173/auth/google/callback
	 * @param {string} codeVerifier - The PKCE code_verifier stored in sessionStorage.
	 */
	googleCallback: (code, redirectUri, codeVerifier) =>
		client.post('/api/v1/auth/google/callback/', {
			code,
			redirect_uri: redirectUri,
			code_verifier: codeVerifier,
		}),

	/** Legacy GSI popup flow — kept for backward compat. */
	googleAuth: (id_token) =>
		client.post('/api/v1/auth/google/', { id_token }),

	refresh: () =>
		client.post('/api/v1/auth/token/refresh/cookie/', {}),

	/**
	 * Log out.
	 * The HttpOnly refresh cookie is cleared by the backend. No body needed.
	 * (The backend also accepts refresh in body — we don't have it in memory.)
	 */
	logout: () =>
		client.post('/api/v1/auth/logout/', {}),

	me: () =>
		client.get('/api/v1/auth/me/'),

	updateMe: (formData) =>
		client.patchForm('/api/v1/auth/me/', formData),

	// Password reset
	requestPasswordReset: (email) =>
		client.post('/api/v1/auth/password/reset/', { email }),

	confirmPasswordReset: (uid, token, new_password) =>
		client.post('/api/v1/auth/password/reset/confirm/', { uid, token, new_password }),

	// Email verification
	verifyEmail: (token) =>
		client.post('/api/v1/auth/email/verify/', { token }),

	resendVerification: () =>
		client.post('/api/v1/auth/email/verify/resend/', {}),
};

/**
 * Build the Google OAuth2 authorization URL.
 * The redirect_uri is the GOOGLE_REDIRECT_URI constant — it must match exactly
 * what is registered in Google Cloud Console.
 *
 * @param {string} state - Cryptographic random value for CSRF protection.
 * @param {string} codeChallenge - Base64url-encoded SHA-256 of the code_verifier.
 */
export function buildGoogleAuthUrl(state, codeChallenge) {
	const params = new URLSearchParams({
		client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
		redirect_uri: GOOGLE_REDIRECT_URI,
		response_type: 'code',
		scope: 'openid email profile',
		state,
		code_challenge: codeChallenge,
		code_challenge_method: 'S256',
		access_type: 'offline',
		prompt: 'select_account',
	});
	return `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
}

/** The exact redirect_uri registered in Google Cloud Console. */
export const GOOGLE_REDIRECT_URI =
	import.meta.env.VITE_GOOGLE_REDIRECT_URI || 'http://localhost:5173/auth/google/callback/';
