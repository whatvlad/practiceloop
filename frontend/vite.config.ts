import { loadEnv, type Plugin } from 'vite';
import { defineConfig } from 'vitest/config';
import { crawlerFiles, siteConfig } from './src/site.ts';

/** robots.txt and sitemap.xml from the public route list and the approved site URL (#38). */
function crawlers(): Plugin {
  let env: Record<string, string> = {};
  return {
    name: 'practiceloop-crawlers',
    apply: 'build',
    configResolved(config) {
      env = loadEnv(config.mode, config.envDir || process.cwd(), 'VITE_');
    },
    generateBundle() {
      const files = crawlerFiles(siteConfig(env.VITE_SITE_URL, env.VITE_SITE_INDEXABLE));
      this.emitFile({ type: 'asset', fileName: 'robots.txt', source: files.robots });
      if (files.sitemap) this.emitFile({ type: 'asset', fileName: 'sitemap.xml', source: files.sitemap });
    },
  };
}

export default defineConfig({
  plugins: [crawlers()],
  server: { proxy: { '/api': { target: 'http://127.0.0.1:8000', rewrite: path => path.replace(/^\/api/, '') } } },
  // Process CSS in tests so `?raw` imports return the stylesheet text.
  test: { css: true },
});
