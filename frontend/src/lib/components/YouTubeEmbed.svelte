<script>
    /**
     * Lazy YouTube embed — shows a thumbnail until the user clicks play.
     * @property {string} url        Any YouTube URL (watch, youtu.be, embed, shorts).
     * @property {string} [title]    Accessible title for the player.
     * @property {string} [thumbnail] Optional high-res poster (e.g. from the YouTube
     *                                Data API). Falls back to the always-present
     *                                hqdefault image if omitted or it fails to load.
     */
    let { url, title = 'Video', thumbnail = '' } = $props();

    function extractId(u) {
        if (!u) return '';
        const m = u.match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([A-Za-z0-9_-]{11})/);
        return m ? m[1] : '';
    }

    const id = $derived(extractId(url));
    let posterError = $state(false);
    const fallbackThumb = $derived(id ? `https://i.ytimg.com/vi/${id}/hqdefault.jpg` : '');
    const thumb = $derived(!posterError && thumbnail ? thumbnail : fallbackThumb);
    let playing = $state(false);
</script>

{#if id}
    <div class="relative w-full aspect-video overflow-hidden rounded-2xl bg-black">
        {#if playing}
            <iframe
                src="https://www.youtube-nocookie.com/embed/{id}?autoplay=1&rel=0"
                {title}
                class="absolute inset-0 w-full h-full border-0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
            ></iframe>
        {:else}
            <button
                onclick={() => (playing = true)}
                class="absolute inset-0 w-full h-full group"
                aria-label="Play video"
            >
                <img
                    src={thumb}
                    alt={title}
                    class="w-full h-full object-cover"
                    loading="lazy"
                    onerror={() => (posterError = true)}
                />
                <div class="absolute inset-0 flex items-center justify-center bg-black/30 group-hover:bg-black/40 transition-colors">
                    <div class="w-16 h-16 rounded-full bg-white/95 flex items-center justify-center shadow-xl transition-transform group-hover:scale-110">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" class="text-stone-900 translate-x-0.5">
                            <path d="M5 3l14 9-14 9V3z"/>
                        </svg>
                    </div>
                </div>
            </button>
        {/if}
    </div>
{:else}
    <div class="w-full aspect-video rounded-2xl flex items-center justify-center
                bg-stone-100 dark:bg-stone-800">
        <span class="text-sm text-stone-400 dark:text-stone-500">No video</span>
    </div>
{/if}
