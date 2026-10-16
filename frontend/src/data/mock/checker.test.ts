import { describe, expect, it } from 'vitest';
import { check, isReadable } from './checker';

const ACCEPTED = ['sin(x^2)'];

describe('mock checker stand-in', () => {
  it('accepts spacing, case, * and a trailing + C', () => {
    expect(check('sin(x^2) + C', ACCEPTED)).toBe('correct');
    expect(check('SIN(x^2)', ACCEPTED)).toBe('correct');
    expect(check('sin(x²)+c', ACCEPTED)).toBe('correct');
  });
  it('marks a readable but different answer incorrect', () => {
    expect(check('cos(x^2) + C', ACCEPTED)).toBe('incorrect');
  });
  it('returns invalid for unreadable input', () => {
    for (const input of ['', '   ', 'sin(x^2', '3pi +* 2', 'x^2 +', '*x', 'x$', '()', '|x']) {
      expect(isReadable(input), input).toBe(false);
      expect(check(input, ACCEPTED), input).toBe('invalid');
    }
  });
  it('reads the notation shown in the hint', () => {
    for (const input of ['3pi', '3*pi', '3π', '3/5', 'sqrt(3)', '√3', 'e^2', 'pi/4 + 2', '-x']) {
      expect(isReadable(input), input).toBe(true);
    }
  });
});
