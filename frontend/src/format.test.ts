import { describe, expect, it } from 'vitest';
import { mixedShares } from './data/topics';
import type { AvailableTopic, Difficulty } from './data/types';
import { answerVariables, formatWhen, isDefinite, leadText, problemKind } from './format';
import text from '../../backend/app/content/en.json';

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
  it('are one exact number with their own lead text', () => {
    expect(problemKind('double-integrals', '\\int_{0}^{1}\\int_{0}^{x} \\left(y\\right)\\,dy\\,dx')).toBe('double');
    expect(problemKind('double-integrals', '\\iint_D \\left(3 x y\\right)\\,dA')).toBe('double');
    expect(leadText('double')).toBe('Calculate the double integral.');
  });
});

describe('mixed practice shares', () => {
  it('renormalize the published weights over the topics offered at a level', () => {
    const topics: AvailableTopic[] = [
      { slug: 'basic-integrals', name: 'Basic integrals', area: 'integrals', availableDifficulties: [1, 3] },
      { slug: 'substitution', name: 'Substitution', area: 'integrals', availableDifficulties: [1, 3] },
      { slug: 'integration-by-parts', name: 'Integration by parts', area: 'integrals', availableDifficulties: [3] },
    ];
    const mixed = { availableDifficulties: [1, 3] as Difficulty[], weights: { 'basic-integrals': 1, substitution: 2, 'integration-by-parts': 2 } };
    expect(mixedShares(topics, mixed, 1).map(share => [share.topic.slug, share.percent])).toEqual([['basic-integrals', 33], ['substitution', 67]]);
    expect(mixedShares(topics, mixed, 3).map(share => share.percent)).toEqual([20, 40, 40]);
  });
});

describe('problem kinds', () => {
  it('asks for a partial derivative in the partial-derivatives topic only', () => {
    expect(problemKind('partial-derivatives', '\\frac{\\partial}{\\partial x}')).toBe('partial');
    expect(problemKind('derivatives', '\\frac{d}{dx}')).toBe('derivative');
    expect(leadText('partial')).toBe(text.calculate_partial);
  });

  it('reads the declared answer variables from a partial statement', () => {
    const polar = 'f = 3 x y,\\quad x = r \\cos{\\left(\\theta \\right)}:\\quad \\frac{\\partial f}{\\partial \\theta}'
      + '\\quad(r > 0,\\ \\theta \\in \\mathbb{R})';
    expect(answerVariables('partial', polar)).toEqual(['r', 'theta']);
    expect(answerVariables('partial', '\\frac{\\partial}{\\partial x}\\left(x y\\right)\\quad(y > 0,\\ x \\in \\mathbb{R})'))
      .toEqual(['x', 'y']);
    expect(answerVariables('partial', 'f\\quad(r > 0,\\ \\theta, z \\in \\mathbb{R})')).toEqual(['z', 'r', 'theta']);
    expect(answerVariables('derivative', '\\frac{d}{dx} x\\quad(x > 0)')).toBeUndefined();
  });
});
