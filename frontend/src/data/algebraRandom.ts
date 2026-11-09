import { generateProblem } from './practice';
import { chooseLocalRandom, initialLocalChoice, LOCAL_RANDOM_TOPICS, type LocalChoice, type LocalSelection } from './localRandom';
import type { MatrixDimensions, PublicProblem } from './types';
import type { ModulusMode } from '../components/ModulusSettings';

const key = (accountId: string) => `practiceloop:algebra-random:${accountId}`;

export function loadAlgebraRandom(accountId: string): LocalSelection {
  try {
    const data: unknown = JSON.parse(localStorage.getItem(key(accountId)) ?? '{}');
    if (!data || typeof data !== 'object' || Array.isArray(data)) return {};
    const result: LocalSelection = {};
    for (const [topic, value] of Object.entries(data)) {
      const definition = LOCAL_RANDOM_TOPICS.find(item => item.id === topic);
      if (!definition || !value || typeof value !== 'object' || Array.isArray(value)) continue;
      const raw = value as Partial<LocalChoice>; const choice = initialLocalChoice();
      choice.level = raw.level && [1, 2, 3].includes(raw.level) ? raw.level : null;
      choice.kinds = Array.isArray(raw.kinds) ? raw.kinds.filter(kind => (definition.kinds as readonly string[]).includes(kind)) : [];
      for (const dimension of ['size', 'columns', 'rowsA', 'colsA', 'rowsB', 'colsB'] as const) {
        const candidate = raw[dimension];
        if (typeof candidate === 'number' && Number.isInteger(candidate) && candidate >= 1 && candidate <= 5) choice[dimension] = candidate;
      }
      result[topic] = choice;
    }
    return result;
  } catch { return {}; }
}

export function saveAlgebraRandom(accountId: string, selection: LocalSelection): void {
  localStorage.setItem(key(accountId), JSON.stringify(selection));
}

export function algebraRandomOptions(topic: string, kind: string, choice: LocalChoice): {
  matrixDimensions?: MatrixDimensions; rankDimensions?: { rows: number; columns: number };
  squareSize?: number; modulusMode?: ModulusMode; exerciseMode?: PublicProblem['exerciseMode'];
} {
  if (topic === 'matrix-operations') return { matrixDimensions: { operation: kind as MatrixDimensions['operation'], rowsA: choice.rowsA, colsA: choice.colsA, rowsB: choice.rowsB, colsB: choice.colsB } };
  if (topic === 'matrix-rank') return { rankDimensions: { rows: choice.size, columns: choice.columns } };
  if (['determinants', 'inverse-matrices', 'linear-systems'].includes(topic)) return { squareSize: choice.size };
  if (topic === 'complex-numbers') return { modulusMode: kind as ModulusMode };
  const exerciseMode = topic === 'polynomial-roots' ? 'roots' : topic === 'partial-fractions' ? 'fractions' : kind;
  return { exerciseMode: exerciseMode as PublicProblem['exerciseMode'] };
}

export async function generateAlgebraRandom(selection: LocalSelection): Promise<PublicProblem> {
  const { topic, kind, level } = chooseLocalRandom(selection);
  const options = algebraRandomOptions(topic, kind, selection[topic]);
  const chosenLevel = topic === 'complex-polar-form' ? ({ argument: 1, power: 2, root: 3 } as const)[kind as 'argument' | 'power' | 'root'] : level;
  return generateProblem(topic, chosenLevel, 'algebra', undefined, options.modulusMode, options.rankDimensions, options.matrixDimensions, options.squareSize, options.exerciseMode);
}
