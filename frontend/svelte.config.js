import adapterCloudflare from '@sveltejs/adapter-cloudflare';
import adapterNode from '@sveltejs/adapter-node';

// Cloudflare Workers stays the default deploy target. Set ADAPTER=node (the Docker
// image does) to build a standalone Node SSR server instead — run with `node build`.
const useNode = process.env.ADAPTER === 'node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	compilerOptions: {
		// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
		runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
	},
	kit: { adapter: useNode ? adapterNode() : adapterCloudflare() }
};

export default config;
