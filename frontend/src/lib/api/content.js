import { client } from './client.js';

function q(params) {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(params))
        if (v !== undefined && v !== null && v !== '') p.set(k, v);
    const s = p.toString();
    return s ? `?${s}` : '';
}

export const contentApi = {
    // ── Content ────────────────────────────────────────────────────────────────
    list: (params = {}) => client.get(`/api/v1/content/${q(params)}`),
    get:  (id)          => client.get(`/api/v1/content/${id}/`),

    // ── Engagement ────────────────────────────────────────────────────────────
    save:         (id) => client.post('/api/v1/saves/', { content_id: id }),
    unsave:       (id) => client.delete(`/api/v1/saves/${id}/`),
    markComplete: (id) => client.post('/api/v1/progress/', { content_id: id }),
    mySaves: (params = {}) => client.get(`/api/v1/saves/${q(params)}`),

    // ── Comments ──────────────────────────────────────────────────────────────
    getComments: (id)        => client.get(`/api/v1/comments/${q({ content_id: id })}`),
    addComment:  (id, text)  => client.post('/api/v1/comments/', { content_id: id, text }),

    // ── Moderation ─────────────────────────────────────────────────────────────
    pendingComments: () => client.get('/api/v1/comments/pending/'),
    approveComment:  (uid) => client.post(`/api/v1/comments/${uid}/approve/`, {}),
    rejectComment:   (uid) => client.post(`/api/v1/comments/${uid}/reject/`, {}),

    // ── Discovery ─────────────────────────────────────────────────────────────
    daily:  ()             => client.get('/api/v1/daily/'),
    search: (term, type)   => client.get(`/api/v1/search/${q({ q: term, type: type || 'all' })}`),

    // ── Taxonomy ──────────────────────────────────────────────────────────────
    categories: ()      => client.get('/api/v1/categories/'),
    category:   (slug)  => client.get(`/api/v1/categories/${slug}/`),
    tags:       ()      => client.get('/api/v1/tags/'),

    // ── YouTube ───────────────────────────────────────────────────────────────
    /** Fetch YouTube video metadata (title, description, duration, thumbnail). */
    youtubeMetadata: (url) => client.get(`/api/v1/content/youtube-metadata/${q({ url })}`),

    /** Create new content. */
    create: (payload) => client.post('/api/v1/content/', payload),
};
