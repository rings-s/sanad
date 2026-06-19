import { describe, it, expect, vi, beforeEach } from 'vitest';
import { page } from '@vitest/browser/context';
import { render } from 'vitest-browser-svelte';

// Mock the Django-backed content API so tests never hit the network.
vi.mock('$lib/api/content.js', () => ({
	contentApi: {
		youtubeMetadata: vi.fn(),
		create: vi.fn()
	}
}));

import CreateVideoForm from './CreateVideoForm.svelte';
import { contentApi } from '$lib/api/content.js';
import { setLocale } from '$lib/stores/locale.js';

const VALID_URL = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
const META = {
	video_id: 'dQw4w9WgXcQ',
	title: 'A Trusted Lecture',
	description: 'Beneficial reminder.',
	thumbnail_url: 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
	duration_seconds: 754,
	channel_title: 'Sanad'
};

beforeEach(() => {
	vi.clearAllMocks();
	setLocale('en'); // deterministic strings regardless of browser locale
});

describe('CreateVideoForm', () => {
	it('rejects non-YouTube input without calling the API (error prevention)', async () => {
		render(CreateVideoForm, { debounceMs: 0 });

		await page.getByLabelText('YouTube URL').fill('just some text');

		await expect.element(page.getByText('That doesn’t look like a YouTube link.')).toBeVisible();
		expect(contentApi.youtubeMetadata).not.toHaveBeenCalled();
	});

	it('links the URL label to its input for accessibility', async () => {
		render(CreateVideoForm, { debounceMs: 0 });
		const input = page.getByLabelText('YouTube URL');
		await expect.element(input).toHaveAttribute('id', 'yt-url');
	});

	it('shows the skeleton loading state while fetching metadata', async () => {
		let resolve;
		contentApi.youtubeMetadata.mockImplementation(
			() => new Promise((r) => (resolve = r))
		);
		render(CreateVideoForm, { debounceMs: 0 });

		await page.getByLabelText('YouTube URL').fill(VALID_URL);

		await vi.waitFor(() => expect(contentApi.youtubeMetadata).toHaveBeenCalledWith(VALID_URL));
		await vi.waitFor(() =>
			expect(document.querySelector('[aria-busy="true"]')).not.toBeNull()
		);

		resolve(META); // let it settle so the pending promise doesn't dangle
		await vi.waitFor(() => expect(document.querySelector('[aria-busy="true"]')).toBeNull());
	});

	it('renders the play-preview card once metadata resolves', async () => {
		contentApi.youtubeMetadata.mockResolvedValue(META);
		render(CreateVideoForm, { debounceMs: 0 });

		await page.getByLabelText('YouTube URL').fill(VALID_URL);

		await expect.element(page.getByRole('heading', { name: META.title })).toBeVisible();
		// Title field is revealed and pre-filled from the fetched metadata.
		await expect.element(page.getByLabelText(/Title/)).toHaveValue(META.title);
		// Play button comes from the reused YouTubeEmbed component.
		await expect.element(page.getByRole('button', { name: 'Play video' })).toBeVisible();
	});

	it('surfaces a retryable error when the fetch fails', async () => {
		contentApi.youtubeMetadata.mockRejectedValue(new Error('boom'));
		render(CreateVideoForm, { debounceMs: 0 });

		await page.getByLabelText('YouTube URL').fill(VALID_URL);

		await expect.element(page.getByRole('button', { name: 'Retry' })).toBeVisible();
	});

	it('submits the correct payload to contentApi.create', async () => {
		contentApi.youtubeMetadata.mockResolvedValue(META);
		contentApi.create.mockResolvedValue({});
		render(CreateVideoForm, { debounceMs: 0 });

		await page.getByLabelText('YouTube URL').fill(VALID_URL);
		await expect.element(page.getByRole('button', { name: 'Publish Video' })).toBeVisible();
		await page.getByRole('button', { name: 'Publish Video' }).click();

		await vi.waitFor(() =>
			expect(contentApi.create).toHaveBeenCalledWith(
				expect.objectContaining({
					type: 'video',
					youtube_url: VALID_URL,
					title: META.title,
					duration_seconds: META.duration_seconds,
					is_published: true
				})
			)
		);
		await expect.element(page.getByText('Video created!')).toBeVisible();
	});

	it('gives the submit button a 48px-minimum touch target', async () => {
		contentApi.youtubeMetadata.mockResolvedValue(META);
		render(CreateVideoForm, { debounceMs: 0 });

		await page.getByLabelText('YouTube URL').fill(VALID_URL);
		const btn = page.getByRole('button', { name: 'Publish Video' });
		await expect.element(btn).toBeVisible();
		expect(btn.element().getBoundingClientRect().height).toBeGreaterThanOrEqual(48);
	});
});
