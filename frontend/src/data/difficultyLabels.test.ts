import { expect, it } from 'vitest';
import { difficultyLabel } from './difficultyLabels';

it('shows three descriptive levels for matrix operations only', () => {
  expect([1, 2, 3].map(level => difficultyLabel('matrix-operations', level as 1 | 2 | 3))).toEqual(['Basic', 'Intermediate', 'Advanced']);
  expect(difficultyLabel('derivatives', 3)).toBe('Medium');
});
