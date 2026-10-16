import { defineConfig } from 'vitest/config';

export default defineConfig({
  // Process CSS in tests so `?raw` imports return the stylesheet text.
  test: { css: true },
});
