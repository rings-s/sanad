import { browser } from '$app/environment';
import { get } from 'svelte/store';
import { auth } from '../stores/auth.js';

const BASE_URL = (browser && import.meta.env.VITE_API_URL) || 'http://localhost:8000';

/**
 * Unwrap the Sanad API envelope.
 *
 * Backend wraps every response as:
 *   { success: true, data: <payload> }              (single resource)
 *   { success: true, data: [...], meta: { ... } }   (paginated list)
 *
 * Non-enveloped responses (e.g. raw SimpleJWT refresh) are returned as-is.
 */
function unwrap(body) {
	if (body && typeof body === 'object' && 'success' in body && 'data' in body) {
		if (body.meta) return { results: body.data, meta: body.meta };
		return body.data;
	}
	return body;
}

/**
 * Silently refresh the access token using the HttpOnly refresh cookie.
 * Returns true on success, false if the cookie is absent/expired.
 */
async function tryRefresh() {
	try {
		const res = await fetch(`${BASE_URL}/api/v1/auth/token/refresh/cookie/`, {
			method: 'POST',
			credentials: 'include',
			headers: { 'Content-Type': 'application/json' },
		});
		if (res.ok) {
			const data = await res.json();
			const access = data?.data?.access ?? data?.access;
			if (access) {
				auth.updateToken(access);
				return true;
			}
		}
		return false;
	} catch {
		return false;
	}
}

async function request(endpoint, options = {}, retry = true) {
	const { token } = get(auth);

	const headers = { 'Content-Type': 'application/json', ...options.headers };
	if (token) headers['Authorization'] = `Bearer ${token}`;

	const res = await fetch(`${BASE_URL}${endpoint}`, {
		...options,
		headers,
		credentials: 'include',
	});

	if (res.status === 401 && retry && browser) {
		const refreshed = await tryRefresh();
		if (refreshed) return request(endpoint, options, false);
		auth.logout();
		if (browser) window.location.href = '/login';
		throw new ApiError(401, { error: { code: 'AUTHENTICATION_REQUIRED', message: 'Session expired' } });
	}

	return res;
}

export const client = {
	async get(endpoint) {
		const res = await request(endpoint);
		if (!res.ok) throw new ApiError(res.status, await safeJson(res));
		return unwrap(await res.json());
	},

	async post(endpoint, body) {
		const res = await request(endpoint, { method: 'POST', body: JSON.stringify(body) });
		if (!res.ok) throw new ApiError(res.status, await safeJson(res));
		return unwrap(await res.json());
	},

	async patch(endpoint, body) {
		const res = await request(endpoint, { method: 'PATCH', body: JSON.stringify(body) });
		if (!res.ok) throw new ApiError(res.status, await safeJson(res));
		return unwrap(await res.json());
	},

	async put(endpoint, body) {
		const res = await request(endpoint, { method: 'PUT', body: JSON.stringify(body) });
		if (!res.ok) throw new ApiError(res.status, await safeJson(res));
		return unwrap(await res.json());
	},

	async delete(endpoint) {
		const res = await request(endpoint, { method: 'DELETE' });
		if (!res.ok) throw new ApiError(res.status, await safeJson(res));
		return res.status === 204 ? null : unwrap(await res.json());
	},

	async postForm(endpoint, formData) {
		const res = await requestForm(endpoint, 'POST', formData);
		if (!res.ok) throw new ApiError(res.status, await safeJson(res));
		return unwrap(await res.json());
	},

	async patchForm(endpoint, formData) {
		const res = await requestForm(endpoint, 'PATCH', formData);
		if (!res.ok) throw new ApiError(res.status, await safeJson(res));
		return unwrap(await res.json());
	},
};

async function requestForm(endpoint, method, formData) {
	const { token } = get(auth);
	const headers = {};
	if (token) headers['Authorization'] = `Bearer ${token}`;
	return fetch(`${BASE_URL}${endpoint}`, { method, headers, body: formData, credentials: 'include' });
}

async function safeJson(res) {
	try {
		return await res.json();
	} catch {
		return { error: { message: res.statusText } };
	}
}

export class ApiError extends Error {
	constructor(status, data) {
		super(data?.error?.message || data?.detail || `HTTP ${status}`);
		this.status = status;
		this.data = data;
	}
}

/**
 * Normalize an error into a `{ <field>: message }` map for form display.
 * Understands the Sanad error envelope: { success:false, error:{ code, message, details } }.
 */
export function extractErrors(error) {
	if (!(error instanceof ApiError)) return { non_field: error.message };
	const d = error.data;
	if (!d) return { non_field: `Error ${error.status}` };

	const err = d.error ?? d;
	const result = {};

	const details = err.details;
	if (details && typeof details === 'object') {
		for (const [key, val] of Object.entries(details)) {
			result[key] = Array.isArray(val) ? val[0] : String(val);
		}
	}

	if (Object.keys(result).length === 0) {
		result.non_field = err.message || (typeof d === 'string' ? d : `Error ${error.status}`);
	}
	return result;
}
