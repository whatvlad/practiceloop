import { describe, expect, it } from 'vitest';
import { algebraGroups } from './algebraGroups';

describe('algebra navigation', () => {
  it('groups the available topics and leaves planned topics unavailable', () => {
    expect(algebraGroups.map(group => group.title)).toEqual([
      'Matrices', 'Complex numbers', 'Polynomials', 'Eigenvalues and eigenvectors', 'Analytic geometry',
    ]);
    const items = algebraGroups.flatMap(group => group.items);
    expect(items.find(item => item.title === 'Matrix operations')?.topic).toBe('matrix-operations');
    expect(items.find(item => item.title === 'Diagonalization')?.topic).toBeUndefined();
    expect(items.map(item => item.topic)).not.toContain('algebraic-expressions');
    expect(items.map(item => item.topic)).not.toContain('binomial-theorem');
  });
});
