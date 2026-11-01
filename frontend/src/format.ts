import text from '../../backend/app/content/en.json';
import { ANSWER_VARIABLES, type AnswerVariable } from './answerSyntax';
import type { TopicSlug } from './data/types';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function startOfDay(date: Date): number {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
}

/** History timestamps: "Today, 14:20", "Yesterday", "12 Oct", "12 Oct 2025". */
export function formatWhen(iso: string, now: Date = new Date()): string {
  const date = new Date(iso);
  const days = Math.round((startOfDay(now) - startOfDay(date)) / 86_400_000);
  if (days === 0) {
    const time = `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    return `Today, ${time}`;
  }
  if (days === 1) return 'Yesterday';
  const day = `${date.getDate()} ${MONTHS[date.getMonth()]}`;
  return date.getFullYear() === now.getFullYear() ? day : `${day} ${date.getFullYear()}`;
}

/** Definite statements start with bounds, `\int_{a}^{b}`; their answer is a number with no `+ C`. */
export function isDefinite(problemLatex: string): boolean {
  return problemLatex.startsWith('\\int_');
}

/**
 * What a statement asks for: an antiderivative + C, one exact number, f'(x), a partial
 * (ADR-005), or, for every other Algebra and Analysis topic, a general exact answer (#202).
 */
export type ProblemKind = 'indefinite' | 'definite' | 'double' | 'triple' | 'derivative' | 'partial' | 'general';

// Single-integral topics: a statement with bounds is definite, any other is indefinite.
const INTEGRAL_TOPICS: ReadonlySet<TopicSlug> = new Set<TopicSlug>([
  'basic-integrals',
  'substitution',
  'integration-by-parts',
  'rational-functions',
  'trigonometric-integrals',
  'definite-integrals',
  'improper-integrals',
]);

export function problemKind(topic: TopicSlug, problemLatex: string): ProblemKind {
  if (topic === 'partial-derivatives') return 'partial';
  if (topic === 'derivatives') return 'derivative';
  // A double integral's answer is also one exact number (#99).
  if (topic === 'double-integrals') return 'double';
  if (topic === 'triple-integrals') return 'triple';
  if (!INTEGRAL_TOPICS.has(topic)) return 'general';
  return isDefinite(problemLatex) ? 'definite' : 'indefinite';
}

/** The instruction above a statement. */
export function leadText(kind: ProblemKind): string {
  return {
    indefinite: text.calculate,
    definite: text.calculate_definite,
    double: text.calculate_double,
    triple: text.calculate_triple,
    derivative: text.calculate_derivative,
    partial: text.calculate_partial,
    general: text.calculate_general,
  }[kind];
}

// #202: the variables a general answer uses. Every other general topic answers with a number.
const GENERAL_VARIABLES: Partial<Record<TopicSlug, AnswerVariable[]>> = {
  'partial-fractions': ['x'],
  'differential-equations': ['x'],
  'multivariable-functions': ['x', 'y'],
};

/**
 * ADR-005: the variables a partial-derivative answer may use. Every partial-v1
 * statement ends with its declared domain, `\quad(x, y \in \mathbb{R})` or
 * `\quad(r > 0,\ \theta \in \mathbb{R})`, so the names are read from there.
 * A general answer uses its topic's variables, none for a number, and so has no +C.
 * Integrals and derivatives keep the integration grammar (undefined).
 */
export function answerVariables(kind: ProblemKind, problemLatex: string, topic?: TopicSlug): AnswerVariable[] | undefined {
  if (kind === 'general') return (topic && GENERAL_VARIABLES[topic]) || [];
  if (kind !== 'partial') return undefined;
  const start = problemLatex.lastIndexOf('\\quad(');
  if (start < 0) return undefined;
  const domain = problemLatex.slice(start + '\\quad('.length).replace(/\\mathbb\{R\}/g, '');
  const names = new Set(Array.from(domain.matchAll(/\\theta|[a-z]/g), match => match[0].replace('\\', '')));
  const found = ANSWER_VARIABLES.filter(name => names.has(name));
  return found.length ? found : undefined;
}
