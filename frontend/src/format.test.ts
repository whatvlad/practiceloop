import { describe, expect, it } from 'vitest';
import { mixedShares } from './data/topics';
import type { AvailableTopic, Difficulty } from './data/types';
import { formatWhen, isDefinite, statementKind } from './format';

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

describe('double integral statements', () => {
  it('are recognized by a region or by two iterated integrals', () => {
    expect(statementKind('\\iint_D \\left(3 x y\\right)\\,dA,\\quad D = [0,2]\\times[0,1]')).toBe('double');
    expect(statementKind('\\int_{0}^{\\frac{\\pi}{2}}\\int_{0}^{1} \\left(y\\right)\\,dy\\,dx')).toBe('double');
    expect(statementKind('\\int_{0}^{\\pi} \\left(\\sin{\\left(x \\right)}\\right)\\,dx')).toBe('definite');
    expect(statementKind('\\int \\left(x\\right)\\,dx')).toBe('indefinite');
  });
});

describe('mixed practice shares', () => {
  it('renormalize the published weights over the topics offered at a level', () => {
    const topics: AvailableTopic[] = [
      { slug: 'basic-integrals', name: 'Basic integrals', availableDifficulties: [1, 3] },
      { slug: 'substitution', name: 'Substitution', availableDifficulties: [1, 3] },
      { slug: 'integration-by-parts', name: 'Integration by parts', availableDifficulties: [3] },
    ];
    const mixed = { availableDifficulties: [1, 3] as Difficulty[], weights: { 'basic-integrals': 1, substitution: 2, 'integration-by-parts': 2 } };
    expect(mixedShares(topics, mixed, 1).map(share => [share.topic.slug, share.percent])).toEqual([['basic-integrals', 33], ['substitution', 67]]);
    expect(mixedShares(topics, mixed, 3).map(share => share.percent)).toEqual([20, 40, 40]);
  });
});
