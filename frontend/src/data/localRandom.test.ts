import { describe, expect, it } from 'vitest';
import { chooseLocalRandom, initialLocalChoice, localRandomError, localRandomRequest } from './localRandom';

describe('local random practice', () => {
  it('chooses topics before kinds, so topic chance does not depend on kind count', () => {
    const selection = {
      'complex-arithmetic': { ...initialLocalChoice(), level: 1 as const, kinds: ['multiply', 'divide'] },
      'matrix-rank': { ...initialLocalChoice(), level: 2 as const, kinds: ['default'] },
    };
    expect(chooseLocalRandom(selection, () => 0.49).topic).toBe('complex-arithmetic');
    expect(chooseLocalRandom(selection, () => 0.51).topic).toBe('matrix-rank');
  });
  it('retains selected matrix dimensions and refuses incompatible configurations', () => {
    const choice = { ...initialLocalChoice(), level: 1 as const, kinds: ['multiply'], rowsA: 2, colsA: 3, rowsB: 3, colsB: 4 };
    expect(localRandomError('matrix-operations', choice)).toBeNull();
    expect(localRandomRequest('matrix-operations', 'multiply', choice)).toEqual({ level: 1, dimensions: { operation: 'multiply', rowsA: 2, colsA: 3, rowsB: 3, colsB: 4 } });
    expect(localRandomError('matrix-operations', { ...choice, rowsB: 2 })).not.toBeNull();
  });
  it('lets polar exercise types be selected without a fictional difficulty', () => {
    const choice = { ...initialLocalChoice(), kinds: ['root'] };
    expect(localRandomError('complex-polar-form', choice)).toBeNull();
    expect(localRandomRequest('complex-polar-form', 'root', choice)).toEqual({ level: 1, polarMode: 'root' });
  });
});

it('offers the redesigned modulus types and excludes the retired exercises', async () => {
  const { LOCAL_RANDOM_TOPICS } = await import('./localRandom');
  expect(LOCAL_RANDOM_TOPICS.find(topic => topic.id === 'complex-numbers')?.kinds).toEqual(['expression', 'properties', 'geometry']);
  expect(LOCAL_RANDOM_TOPICS.find(topic => topic.id === 'complex-arithmetic')?.kinds).toEqual(['multiply', 'divide']);
  expect(LOCAL_RANDOM_TOPICS.find(topic => topic.id === 'complex-conversion')?.kinds).toEqual(['alg-trig', 'alg-exp', 'trig-alg', 'exp-alg']);
  const ids: readonly string[] = LOCAL_RANDOM_TOPICS.map(topic => topic.id);
  expect(ids).not.toContain('polynomial-operations');
  expect(ids).not.toContain('fundamental-theorem-algebra');
  expect(localRandomRequest('complex-numbers', 'geometry', { ...initialLocalChoice(), level: 2 })).toEqual({ level: 2, complexModulus: true, modulusMode: 'geometry' });
});

it('offers only local topics and maps every available kind to one exercise request', async () => {
  const { LOCAL_RANDOM_TOPICS, localRandomError, localRandomRequest, initialLocalChoice } = await import('./localRandom');
  for (const topic of LOCAL_RANDOM_TOPICS) for (const kind of topic.kinds) {
    const choice = { ...initialLocalChoice(), level: 2 as const, kinds: [kind] };
    expect(localRandomError(topic.id, choice)).toBeNull();
    expect(Object.keys(localRandomRequest(topic.id, kind, choice)).length).toBe(topic.id === 'complex-numbers' ? 3 : 2);
  }
});
