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

/** What kind of answer the problem asks for. */
export type ProblemKind = 'indefinite' | 'definite' | 'double' | 'triple' | 'derivative' | 'partial' | 'numeric' | 'expression';

export function problemKind(topic: TopicSlug, problemLatex: string): ProblemKind {
  if (topic === 'algebraic-expressions') return 'numeric';
  if (topic === 'polynomial-division' && problemLatex.startsWith('\\text{Find the remainder when ')) return 'numeric';
  if (topic === 'partial-derivatives') return 'partial';
  if (topic === 'derivatives') return 'derivative';
  // A double integral's answer is also one exact number (#99).
  if (topic === 'double-integrals') return 'double';
  if (topic === 'triple-integrals') return 'triple';
  if (topic === 'improper-integrals') return 'definite';
  if (['basic-integrals', 'substitution', 'integration-by-parts', 'rational-functions', 'trigonometric-integrals', 'definite-integrals'].includes(topic)) {
    return isDefinite(problemLatex) ? 'definite' : 'indefinite';
  }
  if (['matrices', 'complex-numbers', 'fundamental-theorem-algebra', 'combinations', 'functions-and-sequences', 'limits-and-continuity', 'series'].includes(topic)) return 'numeric';
  return 'expression';
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
    numeric: 'Calculate the value.',
    expression: 'Solve the problem.',
  }[kind];
}

/**
 * ADR-005: the variables a partial-derivative answer may use. Every partial-v1
 * statement ends with its declared domain, `\quad(x, y \in \mathbb{R})` or
 * `\quad(r > 0,\ \theta \in \mathbb{R})`, so the names are read from there.
 * Other kinds keep the integration grammar (undefined).
 */
export function answerVariables(kind: ProblemKind, problemLatex: string): AnswerVariable[] | undefined {
  if (kind !== 'partial') return undefined;
  const start = problemLatex.lastIndexOf('\\quad(');
  if (start < 0) return undefined;
  const domain = problemLatex.slice(start + '\\quad('.length).replace(/\\mathbb\{R\}/g, '');
  const names = new Set(Array.from(domain.matchAll(/\\theta|[a-z]/g), match => match[0].replace('\\', '')));
  const found = ANSWER_VARIABLES.filter(name => names.has(name));
  return found.length ? found : undefined;
}

/** Suggested keypad variables do not change which answers the parser accepts. */
export function keypadVariables(kind: ProblemKind, problemLatex: string, topic: TopicSlug): AnswerVariable[] | undefined {
  if (kind === 'numeric' || kind === 'definite' || kind === 'double' || kind === 'triple') return [];
  if (kind === 'derivative') return ['x'];
  if (kind === 'expression') return topic === 'multivariable-functions' ? ['x', 'y'] : ['x'];
  return answerVariables(kind, problemLatex);
}
