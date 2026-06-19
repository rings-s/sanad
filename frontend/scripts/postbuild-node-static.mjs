// Workaround for adapter-node + Vite 8 / Rolldown static-asset serving.
//
// adapter-node resolves its static dirs (`client`, `prerendered`) relative to
// `path.dirname(import.meta.url)` of the module holding the serve() code. With
// Vite 8 that code is emitted into a nested chunk (build/server/chunks/…), so it
// looks for `build/server/chunks/client` instead of `build/client` — every
// static file then 404s while SSR still works. Symlinking the dirs into the
// chunk folder makes sirv mount them. Relative links survive `COPY`/moves.
import { existsSync, rmSync, symlinkSync } from 'node:fs';
import { join } from 'node:path';

const chunksDir = 'build/server/chunks';

if (!existsSync(chunksDir)) {
	console.warn(`postbuild: ${chunksDir} not found — skipping static symlink fix`);
	process.exit(0);
}

for (const name of ['client', 'prerendered']) {
	if (!existsSync(`build/${name}`)) continue; // prerendered may not exist
	const link = join(chunksDir, name);
	try {
		rmSync(link, { force: true });
	} catch {
		/* not present */
	}
	symlinkSync(join('..', '..', name), link, 'dir');
	console.log(`postbuild: linked ${link} -> ../../${name}`);
}
