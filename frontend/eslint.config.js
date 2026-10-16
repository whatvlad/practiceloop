import js from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  { ignores: ['dist/**', 'node_modules/**'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    // The temporary mock backend holds answers; only the data boundary may import it.
    files: ['src/**/*.{ts,tsx}'],
    ignores: ['src/data/api.ts', 'src/data/mock/**'],
    rules: {
      'no-restricted-imports': ['error', { patterns: [{ group: ['**/mock/*'], message: 'Import data through src/data/api.ts.' }] }],
    },
  },
);
