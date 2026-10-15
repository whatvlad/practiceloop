import { describe, expect, it } from 'vitest';
import { renderMath } from './math';

describe('mathematical rendering boundary', () => {
  it('renders an integral with accessible MathML', () => {
    expect(renderMath('\\int x^2\\,dx')).toContain('<math');
  });
  it('does not produce an executable URL from a TeX command', () => {
    expect(renderMath('\\href{javascript:alert(1)}{click}')).not.toContain('href=');
  });
  it('rejects malformed expressions', () => {
    expect(() => renderMath('\\frac{')).toThrow();
  });
});
