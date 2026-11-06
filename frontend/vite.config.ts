import { readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { loadEnv, type Plugin } from 'vite';
import { defineConfig } from 'vitest/config';
import { crawlerFiles, pagesHeaders, shellRobots, siteConfig, type SiteConfig } from './src/site.ts';

/**
 * robots.txt and sitemap.xml from the public route list and the approved site
 * URL (#38), plus the launch robots tag and `_headers` rules (#39).
 */
function crawlers(): Plugin {
  let site: SiteConfig = siteConfig(undefined, undefined);
  let outDir = 'dist';
  return {
    name: 'practiceloop-crawlers',
    apply: 'build',
    configResolved(config) {
      const env = loadEnv(config.mode, config.envDir || process.cwd(), 'VITE_');
      site = siteConfig(env.VITE_SITE_URL, env.VITE_SITE_INDEXABLE);
      outDir = resolve(config.root, config.build.outDir);
    },
    transformIndexHtml(html) {
      return html.replace('<meta name="robots" content="noindex, nofollow" />', `<meta name="robots" content="${shellRobots(site)}" />`);
    },
    generateBundle() {
      const files = crawlerFiles(site);
      this.emitFile({ type: 'asset', fileName: 'robots.txt', source: files.robots });
      if (files.sitemap) this.emitFile({ type: 'asset', fileName: 'sitemap.xml', source: files.sitemap });
    },
    // public/ is copied by now; rewrite its _headers for a launch build.
    closeBundle() {
      const file = join(outDir, '_headers');
      writeFileSync(file, pagesHeaders(readFileSync(file, 'utf8'), site));
    },
  };
}

export default defineConfig({
  plugins: [crawlers()],
  server: { proxy: {
    '/api': { target: 'http://127.0.0.1:8000', rewrite: path => path.replace(/^\/api/, '') },
    '/local-matrix-preview': { target: 'http://127.0.0.1:8011', rewrite: path => path.replace(/^\/local-matrix-preview/, '') },
  } },
  // Process CSS in tests so `?raw` imports return the stylesheet text.
  test: { css: true },
});
