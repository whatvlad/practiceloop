import { describe, expect, it } from 'vitest';
import tokens from '../../../docs/design/system/tokens.json';
import css from './tokens.css?raw';

function block(selector: string): Record<string, string> {
  const start = css.indexOf(`${selector}{`);
  if (start < 0) throw new Error(`Missing ${selector} block`);
  const body = css.slice(start + selector.length + 1, css.indexOf('}', start));
  return Object.fromEntries(
    body
      .split(';')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const at = line.indexOf(':');
        return [line.slice(0, at).replace(/^--/, ''), line.slice(at + 1).trim()];
      }),
  );
}

const THEMES = {
  ink: ':root,[data-theme="ink"]',
  graphite: '[data-theme="graphite"]',
  paper: '[data-theme="paper"]',
} as const;

describe('design tokens', () => {
  for (const [theme, selector] of Object.entries(THEMES) as [keyof typeof THEMES, string][]) {
    it(`matches tokens.json for the ${theme} theme`, () => {
      const vars = block(selector);
      for (const token of [...tokens.color.tokens, ...tokens.shadow.tokens]) {
        expect(vars[token.name], token.name).toBe(token.value[theme]);
      }
    });
  }

  it('matches tokens.json for space, radius and type families', () => {
    const vars = block(':root');
    for (const token of [...tokens.spacing.tokens, ...tokens.radius.tokens]) {
      expect(vars[token.name], token.name).toBe(token.value);
    }
    for (const [name, value] of Object.entries(tokens.type.families)) {
      expect(vars[`font-${name}`], name).toBe(value);
    }
  });
});
