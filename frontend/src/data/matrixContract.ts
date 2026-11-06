import { splitComputationalParts } from '../answerSyntax';
import type { ComputationalInputSpec } from './types';

const names = ['one', 'two', 'three', 'four', 'five'];

/** Distinguish matrix tuples from other ordered computational answers. */
export function matrixDimensions(spec: ComputationalInputSpec): [number, number] | null {
  if (spec.kind !== 'tuple' || !spec.components || !spec.labels || spec.components.length < 1 || spec.components.length > 5) return null;
  const columns = spec.components[0].components?.length ?? 0;
  if (columns < 1 || columns > 5) return null;
  if (spec.components.some((row, i) => spec.labels![i] !== `Matrix row ${names[i]}` || row.kind !== 'tuple'
    || row.components?.length !== columns || row.labels?.length !== columns
    || row.components.some((cell, j) => cell.kind !== 'formula' || row.labels![j] !== `Column ${names[j]}`))) return null;
  return [spec.components.length, columns];
}

export function parseMatrixAnswer(value: string, rows: number, columns: number): string[][] | null {
  if (!value.trim()) return Array.from({ length: rows }, () => Array<string>(columns).fill(''));
  try {
    const text = value.trim();
    if (!text.startsWith('(') || !text.endsWith(')')) return null;
    const parts = splitComputationalParts(text.slice(1, -1), ';');
    if (parts.length !== rows) return null;
    const matrix = parts.map(part => {
      const row = part.trim();
      return row.startsWith('(') && row.endsWith(')') ? splitComputationalParts(row.slice(1, -1), ';') : [];
    });
    return matrix.every(row => row.length === columns) ? matrix : null;
  } catch { return null; }
}

export function serializeMatrixAnswer(matrix: string[][]): string {
  return `(${matrix.map(row => `(${row.join(';')})`).join(';')})`;
}
