import { describe, expect, it } from 'vitest';
import { formatWhen, isDefinite } from './format';

const NOW = new Date(2026, 9, 16, 15, 0);

describe('history timestamps', () => {
  it('formats today, yesterday and older dates', () => {
    expect(formatWhen(new Date(2026, 9, 16, 14, 20).toISOString(), NOW)).toBe('Today, 14:20');
    expect(formatWhen(new Date(2026, 9, 15, 9, 5).toISOString(), NOW)).toBe('Yesterday');
    expect(formatWhen(new Date(2026, 9, 12, 9, 5).toISOString(), NOW)).toBe('12 Oct');
    expect(formatWhen(new Date(2025, 0, 3).toISOString(), NOW)).toBe('3 Jan 2025');
  });
});

describe('definite statements', () => {
  it('are recognized by their bounds', () => {
    expect(isDefinite('\\int_{0}^{\\pi} \\left(\\sin{\\left(x \\right)}\\right)\\,dx')).toBe(true);
    expect(isDefinite('\\int \\left(x\\right)\\,dx\\quad(x\\in\\mathbb{R})')).toBe(false);
  });
});
