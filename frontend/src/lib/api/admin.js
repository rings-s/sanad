import { client } from './client.js';

/** Build a query string from defined params. */
function q(params) {
	const p = new URLSearchParams();
	for (const [k, v] of Object.entries(params))
		if (v !== undefined && v !== null && v !== '') p.set(k, v);
	const s = p.toString();
	return s ? `?${s}` : '';
}

/**
 * Sheikh-only admin client. Talks to the in-app admin API (/api/v1/admin/…)
 * and the Sheikh-scoped content endpoints. All of these 401/403 for non-Sheikh
 * users — the UI also hides them, but the server is the real gate.
 */
export const adminApi = {
	// ── Content (all types, including drafts + archived) ───────────────────────
	// The caller sets the scope: Sheikh passes { scope: 'all' } to see every
	// author's drafts + archived items; a content manager passes { mine: 1 } to
	// manage their own non-archived content. The server enforces both gates.
	listContent: (params = {}) => client.get(`/api/v1/content/${q(params)}`),
	getContent: (id) => client.get(`/api/v1/content/${id}/`),
	createContent: (formData) => client.postForm('/api/v1/content/', formData),
	updateContent: (id, formData) => client.patchForm(`/api/v1/content/${id}/`, formData),
	deleteContent: (id) => client.delete(`/api/v1/content/${id}/`), // soft-delete (archive)
	restoreContent: (id) => client.patch(`/api/v1/content/${id}/`, { is_archived: false }),

	// ── Categories ─────────────────────────────────────────────────────────────
	listCategories: () => client.get('/api/v1/admin/categories/?page_size=100'),
	createCategory: (body) => client.post('/api/v1/admin/categories/', body),
	updateCategory: (slug, body) => client.patch(`/api/v1/admin/categories/${slug}/`, body),
	deleteCategory: (slug) => client.delete(`/api/v1/admin/categories/${slug}/`),

	// ── Subcategories ──────────────────────────────────────────────────────────
	listSubcategories: (category) =>
		client.get(`/api/v1/admin/subcategories/${q({ category, page_size: 100 })}`),
	createSubcategory: (body) => client.post('/api/v1/admin/subcategories/', body),
	updateSubcategory: (slug, body) => client.patch(`/api/v1/admin/subcategories/${slug}/`, body),
	deleteSubcategory: (slug) => client.delete(`/api/v1/admin/subcategories/${slug}/`),

	// ── Tags ────────────────────────────────────────────────────────────────────
	listTags: () => client.get('/api/v1/admin/tags/?page_size=100'),
	createTag: (body) => client.post('/api/v1/admin/tags/', body),
	updateTag: (slug, body) => client.patch(`/api/v1/admin/tags/${slug}/`, body),
	deleteTag: (slug) => client.delete(`/api/v1/admin/tags/${slug}/`),

	// ── Daily guidance ──────────────────────────────────────────────────────────
	listDaily: (params = {}) => client.get(`/api/v1/admin/daily/${q(params)}`),
	createDaily: (body) => client.post('/api/v1/admin/daily/', body),
	updateDaily: (id, body) => client.patch(`/api/v1/admin/daily/${id}/`, body),
	deleteDaily: (id) => client.delete(`/api/v1/admin/daily/${id}/`),

	// ── Comments (full moderation) ──────────────────────────────────────────────
	listComments: (params = {}) => client.get(`/api/v1/admin/comments/${q(params)}`),
	approveComment: (uid) => client.post(`/api/v1/comments/${uid}/approve/`, {}),
	rejectComment: (uid) => client.post(`/api/v1/comments/${uid}/reject/`, {}),
	deleteComment: (uid) => client.delete(`/api/v1/comments/${uid}/`),

	// ── Users ────────────────────────────────────────────────────────────────────
	listUsers: (params = {}) => client.get(`/api/v1/admin/users/${q(params)}`),
	updateUser: (id, body) => client.patch(`/api/v1/admin/users/${id}/`, body)
};
