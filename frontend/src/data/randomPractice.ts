import type { AreaSlug, AvailableTopic, Difficulty, MatrixOptions } from './types';

export type RandomSelection = Record<string, Difficulty | null>;
export interface RandomChoice { topic: string; difficulty: Difficulty; area: AreaSlug }

/** Require every selection to remain available and have an explicit level. */
export function eligibleRandomChoices(selection: RandomSelection, topics: readonly AvailableTopic[]): RandomChoice[] | null {
  const entries = Object.entries(selection);
  if (!entries.length) return null;
  const choices: RandomChoice[] = [];
  for (const [slug, level] of entries) {
    const topic = topics.find(item => item.slug === slug);
    if (!topic || level === null || !topic.availableDifficulties.includes(level)) return null;
    choices.push({ topic: slug, difficulty: level, area: topic.area });
  }
  return choices;
}

export function pickRandomChoice(choices: readonly RandomChoice[], random: () => number = Math.random): RandomChoice {
  if (!choices.length) throw new Error('Select at least one topic.');
  return choices[Math.floor(random() * choices.length)];
}

const storageKey = (accountId: string) => `practiceloop:random-selection:${accountId}`;

export function loadRandomSelection(accountId: string): RandomSelection {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(storageKey(accountId)) ?? '{}');
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {};
    return Object.fromEntries(Object.entries(parsed).filter(([slug, level]) =>
      /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug) && (level === null || [1, 2, 3, 4, 5].includes(level as number))));
  } catch { return {}; }
}

export function saveRandomSelection(accountId: string, selection: RandomSelection): void {
  try { localStorage.setItem(storageKey(accountId), JSON.stringify(selection)); } catch { /* Storage may be disabled. */ }
}

const matrixStorageKey = (accountId: string) => `practiceloop:random-matrix:${accountId}`;

export function loadRandomMatrixOptions(accountId: string): MatrixOptions | undefined {
  try {
    const value: unknown = JSON.parse(localStorage.getItem(matrixStorageKey(accountId)) ?? 'null');
    if (!value || typeof value !== 'object') return undefined;
    const data = value as Record<string, unknown>;
    if (!['add', 'subtract', 'multiply', 'mixed'].includes(String(data.operation))
        || !['2x2', '3x3', 'rectangular'].includes(String(data.size))) return undefined;
    return { operation: data.operation as MatrixOptions['operation'], size: data.size as MatrixOptions['size'] };
  } catch { return undefined; }
}

export function saveRandomMatrixOptions(accountId: string, options: MatrixOptions): void {
  try { localStorage.setItem(matrixStorageKey(accountId), JSON.stringify(options)); } catch { /* Storage may be disabled. */ }
}
