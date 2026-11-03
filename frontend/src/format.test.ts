import { describe, expect, it } from 'vitest';
import { mixedShares } from './data/topics';
import type { AvailableTopic, Difficulty, TopicSlug } from './data/types';
import { answerVariables, formatWhen, isDefinite, keypadVariables, leadText, problemKind } from './format';
import text from '../../backend/app/content/en.json';

it('offers x for polynomial quotient problems', () => {
  const statement = '\\text{Find the quotient when }x^{2}+1\\text{ is divided by }x-1\\text{.}';
  const kind = problemKind('polynomial-division', statement);
  expect(kind).toBe('expression');
  expect(keypadVariables(kind, statement, 'polynomial-division')).toEqual(['x']);
});

it('declares the imaginary unit for complex-number answers (#221)', () => {
  const kind = problemKind('complex-arithmetic', '\\text{Calculate }(1+i)(2-i)\\text{.}');
  expect(kind).toBe('complex');
  expect(answerVariables(kind, '')).toEqual(['i']);
  expect(keypadVariables(kind, '', 'complex-arithmetic')).toEqual(['i']);
  expect(problemKind('complex-polar-form', '')).toBe('complex');
});

it('never reads the i of \\in as a partial-derivative variable', () => {
  expect(answerVariables('partial', 'f(x,y)\\quad(x, y \\in \\mathbb{R})')).toEqual(['x', 'y']);
});

it('uses a numeric answer for a polynomial remainder', () => {
  expect(problemKind('polynomial-division', '\\text{Find the remainder when }P(x)=x^2')).toBe('numeric');
});

it('uses a numeric answer without variable keys for radical exercises', () => {
  const kind = problemKind('algebraic-expressions', '');
  expect(kind).toBe('numeric');
  expect(keypadVariables(kind, '', 'algebraic-expressions')).toEqual([]);
});

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

  it('recognizes generated definite integrals even when the instruction is included', () => {
    expect(problemKind('basic-integrals', '\\text{Calculate }\\int_{0}^{1}x\\,dx\\text{.}')).toBe('definite');
  });
});

describe('double integral statements', () => {
  it('are one exact number with their own lead text', () => {
    expect(problemKind('double-integrals', '\\int_{0}^{1}\\int_{0}^{x} \\left(y\\right)\\,dy\\,dx')).toBe('double');
    expect(problemKind('double-integrals', '\\iint_D \\left(3 x y\\right)\\,dA')).toBe('double');
    expect(leadText('double')).toBe('Calculate the double integral.');
  });
});

describe('triple integral statements', () => {
  it('are one exact number with their own lead text', () => {
    expect(problemKind('triple-integrals', '\\int_{0}^{2}\\int_{0}^{2 - x}\\int_{0}^{2 - x - y} \\left(x\\right)\\,dz\\,dy\\,dx')).toBe('triple');
    expect(problemKind('triple-integrals', '\\iiint_E \\left(x y z\\right)\\,dV')).toBe('triple');
    expect(leadText('triple')).toBe('Calculate the triple integral.');
  });
});

describe('mixed practice shares', () => {
  it('renormalize the published weights over the topics offered at a level', () => {
    const topics: AvailableTopic[] = [
      { slug: 'basic-integrals', name: 'Basic integrals', area: 'mathematical-analysis', availableDifficulties: [1, 3] },
      { slug: 'substitution', name: 'Substitution', area: 'mathematical-analysis', availableDifficulties: [1, 3] },
      { slug: 'integration-by-parts', name: 'Integration by parts', area: 'mathematical-analysis', availableDifficulties: [3] },
    ];
    const mixed = { availableDifficulties: [1, 3] as Difficulty[], weights: { 'basic-integrals': 1, substitution: 2, 'integration-by-parts': 2 } };
    expect(mixedShares(topics, mixed, 1).map(share => [share.topic.slug, share.percent])).toEqual([['basic-integrals', 33], ['substitution', 67]]);
    expect(mixedShares(topics, mixed, 3).map(share => share.percent)).toEqual([20, 40, 40]);
  });
});

describe('problem kinds', () => {
  it.each<TopicSlug>([
    'matrices', 'complex-numbers', 'fundamental-theorem-algebra', 'combinations',
    'series',
  ])('does not describe %s as an integral', topic => {
    expect(problemKind(topic, 'x')).toBe('numeric');
    expect(leadText('numeric')).toBe('Calculate the value.');
    expect(keypadVariables('numeric', 'x', topic)).toEqual([]);
    expect(answerVariables('numeric', 'x')).toBeUndefined();
  });

  it.each<TopicSlug>(['partial-fractions', 'multivariable-functions', 'differential-equations', 'functions-and-sequences', 'limits-and-continuity', 'differential-calculus'])(
    'uses a general expression instruction for %s', topic => {
      expect(problemKind(topic, 'x')).toBe('expression');
      expect(leadText('expression')).toBe('Solve the problem.');
    },
  );

  it('allows the variables of expression problems without an integration constant', () => {
    expect(keypadVariables('expression', '', 'partial-fractions')).toEqual(['x']);
    expect(keypadVariables('expression', '', 'multivariable-functions')).toEqual(['x', 'y']);
    expect(keypadVariables('expression', '', 'differential-equations')).toEqual(['x']);
    expect(keypadVariables('derivative', '', 'derivatives')).toEqual(['x']);
    expect(keypadVariables('definite', '', 'definite-integrals')).toEqual([]);
  });

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
