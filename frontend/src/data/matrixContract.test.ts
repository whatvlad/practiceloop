import { expect, it } from 'vitest';
import { matrixDimensions, parseMatrixAnswer, serializeMatrixAnswer } from './matrixContract';
import type { ComputationalInputSpec } from './types';
import { parseAnswerInput } from './answerInput';

const formula: ComputationalInputSpec = { kind: 'formula', maxBytes: 256 };
const row: ComputationalInputSpec = { kind: 'tuple', maxBytes: 256, labels: ['Column one', 'Column two'], components: [formula, formula] };
const matrix: ComputationalInputSpec = { kind: 'tuple', maxBytes: 256, labels: ['Matrix row one', 'Matrix row two'], components: [row, row] };

it('recognizes only the explicit public matrix contract and preserves values', () => {
  expect(matrixDimensions(matrix)).toEqual([2, 2]);
  expect(matrixDimensions({ ...matrix, labels: ['Other', 'Matrix row two'] })).toBeNull();
  expect(parseMatrixAnswer('', 2, 2)).toEqual([['', ''], ['', '']]);
  expect(parseMatrixAnswer('((1/2;sqrt(3));(sin(x);-4))', 2, 2)).toEqual([['1/2', 'sqrt(3)'], ['sin(x)', '-4']]);
  expect(parseMatrixAnswer('((1;2))', 2, 2)).toBeNull();
  expect(serializeMatrixAnswer([['1/2', ''], ['2', '3']])).toBe('((1/2;);(2;3))');
});

it('accepts a bounded 5 × 5 matrix input contract', () => {
  const names = ['one', 'two', 'three', 'four', 'five'];
  const matrixRow = { kind: 'tuple', maxBytes: 256, labels: names.map(n => `Column ${n}`), components: names.map(() => formula) };
  const spec = { kind: 'tuple', maxBytes: 256, labels: names.map(n => `Matrix row ${n}`), components: names.map(() => matrixRow) };
  const parsed = parseAnswerInput(spec) as ComputationalInputSpec;
  expect(matrixDimensions(parsed)).toEqual([5, 5]);
  expect(() => parseAnswerInput({ ...spec, labels: names.map(() => 'Other') })).toThrow();
});
