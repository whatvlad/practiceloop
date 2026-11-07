import type { Difficulty } from './types';

export const LOCAL_RANDOM_TOPICS = [
  { id: 'matrix-operations', label: 'Matrix operations', kinds: ['add', 'subtract', 'multiply', 'divide'] },
  { id: 'determinants', label: 'Determinants', kinds: ['default'] },
  { id: 'inverse-matrices', label: 'Inverse matrices', kinds: ['default'] },
  { id: 'matrix-rank', label: 'Matrix rank', kinds: ['default'] },
  { id: 'linear-systems', label: 'Systems of linear equations', kinds: ['default'] },
  { id: 'complex-arithmetic', label: 'Complex arithmetic', kinds: ['multiply', 'divide'] },
  { id: 'complex-numbers', label: 'Modulus', kinds: ['expression', 'properties', 'geometry'] },
  { id: 'complex-conversion', label: 'Converting complex forms', kinds: ['alg-trig', 'alg-exp', 'trig-alg', 'exp-alg'] },
  { id: 'complex-polar-form', label: 'Polar form, powers and roots', kinds: ['argument', 'power', 'root'] },
  { id: 'polynomial-division', label: 'Division, remainders and divisibility', kinds: ['division', 'remainder', 'divisibility'] },
  { id: 'polynomial-roots', label: 'Roots and factors', kinds: ['default'] },
  { id: 'partial-fractions', label: 'Partial fractions', kinds: ['default'] },
] as const;

export type LocalChoice = { level: Difficulty | null; kinds: string[]; size: number; columns: number; rowsA: number; colsA: number; rowsB: number; colsB: number };
export type LocalSelection = Record<string, LocalChoice>;
export const initialLocalChoice = (): LocalChoice => ({ level: null, kinds: [], size: 2, columns: 2, rowsA: 2, colsA: 2, rowsB: 2, colsB: 2 });
const finiteSize = (n: number, min = 1) => Number.isInteger(n) && n >= min && n <= 5;

export function localRandomError(topic: string, choice: LocalChoice): string | null {
  const definition = LOCAL_RANDOM_TOPICS.find(item => item.id === topic);
  if (!definition) return 'Unknown topic.';
  if (topic !== 'complex-polar-form' && ![1, 2, 3].includes(choice.level ?? 0)) return 'Choose a difficulty.';
  if (!choice.kinds.length || choice.kinds.some(kind => !(definition.kinds as readonly string[]).includes(kind))) return 'Choose at least one exercise type.';
  if (!finiteSize(choice.size, 2) || !finiteSize(choice.columns, 2)) return 'Choose valid dimensions.';
  if (topic === 'matrix-operations') {
    const { rowsA, colsA, rowsB, colsB } = choice;
    if (![rowsA, colsA, rowsB, colsB].every(n => finiteSize(n))) return 'Choose valid dimensions.';
    if (choice.kinds.some(kind => kind === 'divide' ? colsA !== rowsB || rowsB !== colsB : kind === 'multiply' ? colsA !== rowsB : rowsA !== rowsB || colsA !== colsB)) return 'The selected operations require compatible dimensions.';
  }
  return null;
}

export function localRandomRequest(topic: string, kind: string, choice: LocalChoice): Record<string, unknown> {
  const level = choice.level ?? 1;
  switch (topic) {
    case 'matrix-operations': return { level, dimensions: { operation: kind, rowsA: choice.rowsA, colsA: choice.colsA, rowsB: choice.rowsB, colsB: choice.colsB } };
    case 'determinants': return { level, determinantSize: choice.size };
    case 'inverse-matrices': return { level, inverseSize: choice.size };
    case 'matrix-rank': return { level, rankDimensions: { rows: choice.size, columns: choice.columns } };
    case 'linear-systems': return { level, systemSize: choice.size };
    case 'complex-arithmetic': return { level, complexOperation: kind };
    case 'complex-numbers': return { level, complexModulus: true, modulusMode: kind };
    case 'complex-conversion': return { level, conversion: kind };
    case 'complex-polar-form': return { level: 1, polarMode: kind };
    case 'polynomial-division': return { level, polynomialMode: kind };
    case 'polynomial-roots': return { level, polynomialRoots: true };
    case 'partial-fractions': return { level, polynomialExtra: 'fractions' };
    default: throw new Error('Unknown topic.');
  }
}

export function chooseLocalRandom(selection: LocalSelection, random = Math.random) {
  const entries = Object.entries(selection);
  if (!entries.length) throw new Error('Select at least one topic.');
  for (const [topic, choice] of entries) {
    const error = localRandomError(topic, choice);
    if (error) throw new Error(`${LOCAL_RANDOM_TOPICS.find(item => item.id === topic)?.label ?? topic}: ${error}`);
  }
  const [topic, choice] = entries[Math.floor(random() * entries.length)];
  const kind = choice.kinds[Math.floor(random() * choice.kinds.length)];
  return { topic, kind, level: choice.level ?? 1, body: localRandomRequest(topic, kind, choice) };
}
