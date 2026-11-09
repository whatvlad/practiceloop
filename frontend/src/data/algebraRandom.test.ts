import { describe, expect, it } from 'vitest';
import { algebraRandomOptions, loadAlgebraRandom } from './algebraRandom';
import { initialLocalChoice } from './localRandom';

describe('saved algebra random practice', () => {
  it('retains chosen matrix dimensions', () => {
    const choice = { ...initialLocalChoice(), level: 2 as const, kinds: ['multiply'], rowsA: 2, colsA: 3, rowsB: 3, colsB: 4 };
    expect(algebraRandomOptions('matrix-operations', 'multiply', choice)).toMatchObject({ matrixDimensions: { operation: 'multiply', rowsA: 2, colsA: 3, rowsB: 3, colsB: 4 } });
  });
  it('maps conversion and polar modes to production settings', () => {
    expect(algebraRandomOptions('complex-conversion', 'alg-exp', initialLocalChoice())).toMatchObject({ exerciseMode: 'alg-exp' });
    expect(algebraRandomOptions('complex-polar-form', 'root', initialLocalChoice())).toMatchObject({ exerciseMode: 'root' });
  });
  it('ignores malformed saved choices', () => {
    const store = { getItem: () => JSON.stringify({ 'matrix-rank': null, nonsense: { kinds: [] } }) };
    Object.defineProperty(globalThis, 'localStorage', { value: store, configurable: true });
    expect(loadAlgebraRandom('account')).toEqual({});
  });
});
