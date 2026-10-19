import { defineConfig } from 'vitest/config';

export default defineConfig({
  server: { proxy: { '/api': { target: 'http://127.0.0.1:8000', rewrite: path => path.replace(/^\/api/, '') } } },
  // Process CSS in tests so `?raw` imports return the stylesheet text.
  test: { css: true },
});
