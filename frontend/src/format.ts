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
  return problemLatex.replace(/^\\text\{Calculate \}/, '').startsWith('\\int_');
}

/** What kind of answer the problem asks for. */
export type ProblemKind = 'indefinite' | 'definite' | 'double' | 'triple' | 'derivative' | 'partial' | 'numeric' | 'complex' | 'expression';

export function problemKind(topic: TopicSlug, problemLatex: string): ProblemKind {
  if (topic === 'algebraic-expressions') return 'numeric';
  if (topic === 'complex-arithmetic' || topic === 'complex-polar-form') return 'complex';
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
  if (['matrices', 'determinants', 'inverse-matrices', 'linear-systems', 'matrix-rank', 'binomial-theorem', 'eigenvalues', 'vectors', 'lines-and-planes', 'matrix-operations', 'complex-numbers', 'fundamental-theorem-algebra', 'combinations', 'functions-and-sequences', 'limits-and-continuity', 'series'].includes(topic)) return 'numeric';
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
    complex: 'Give the answer in the form a + bi.',
    expression: 'Solve the problem.',
  }[kind];
}

/** Separate the engine's text-and-math statements without changing saved records. */
export function displayProblem(topic: TopicSlug, problemLatex: string): { instruction: string; formula: string } {
  const division = problemLatex.match(/^\\text\{Find the (remainder|quotient) when \}(.+)\\text\{ is divided by \}(.+)\\text\{\.\}$/);
  if (division) {
    return {
      instruction: `Find the ${division[1]} when the polynomial is divided by the divisor.`,
      formula: `\\frac{${division[2].replace(/^P\(x\)=/, '')}}{${division[3]}}`,
    };
  }
  const unwrapped = problemLatex.replace(/^\\text\{Calculate \}(.+)\\text\{\.\}$/, '$1');
  if (topic === 'fundamental-theorem-algebra' && unwrapped.endsWith(': \\text{sum of the roots}')) {
    return { instruction: 'Find the sum of the roots.', formula: unwrapped.replace(/: \\text\{sum of the roots\}$/, '') };
  }
  if (topic === 'limits-and-continuity' && unwrapped.endsWith('\\text{ for continuity}')) {
    return { instruction: 'Find the value that makes the function continuous.', formula: unwrapped.replace(/\\text\{ for continuity\}$/, '') };
  }
  const generated = problemLatex.match(/^\\text\{(Calculate|Find|Differentiate|Simplify|Rationalize the denominator of|Decompose into partial fractions:) \}(.+)\\text\{\.\}$/);
  if (generated) {
    const formula = generated[2].replace(/\\text\{ for \}/, '\\quad ');
    const kind = problemKind(topic, formula);
    const instruction = topic === 'partial-fractions' ? 'Decompose into partial fractions.'
      : generated[1] === 'Calculate' || generated[1] === 'Find'
      ? leadText(kind)
      : `${generated[1].replace(/:$/, '').replace(/ of$/, '')}.`;
    return { instruction, formula };
  }
  // A worded exercise (#221) states its task before a colon and ends with one formula.
  const worded = problemLatex.match(/^\\text\{([^{}]+): \}(.+)\\text\{\.\}$/);
  if (worded) return { instruction: `${worded[1]}.`, formula: worded[2] };
  return { instruction: topic === 'partial-fractions' ? 'Decompose into partial fractions.' : leadText(problemKind(topic, problemLatex)), formula: problemLatex };
}

/**
 * ADR-005: the variables a partial-derivative answer may use. Every partial-v1
 * statement ends with its declared domain, `\quad(x, y \in \mathbb{R})` or
 * `\quad(r > 0,\ \theta \in \mathbb{R})`, so the names are read from there.
 * Other kinds keep the integration grammar (undefined).
 */
export function answerVariables(kind: ProblemKind, problemLatex: string): AnswerVariable[] | undefined {
  if (kind === 'complex') return ['i'];
  if (kind !== 'partial') return undefined;
  const start = problemLatex.lastIndexOf('\\quad(');
  if (start < 0) return undefined;
  const domain = problemLatex.slice(start + '\\quad('.length).replace(/\\mathbb\{R\}/g, '');
  const names = new Set(Array.from(domain.matchAll(/\\theta|[a-z]/g), match => match[0].replace('\\', '')));
  // The imaginary unit is never a partial-derivative variable; `\in` also contains an i.
  const found = ANSWER_VARIABLES.filter(name => name !== 'i' && names.has(name));
  return found.length ? found : undefined;
}

/** Suggested keypad variables do not change which answers the parser accepts. */
export function keypadVariables(kind: ProblemKind, problemLatex: string, topic: TopicSlug): AnswerVariable[] | undefined {
  if (kind === 'numeric' || kind === 'definite' || kind === 'double' || kind === 'triple') return [];
  if (kind === 'derivative') return ['x'];
  if (kind === 'complex') return ['i'];
  if (kind === 'expression') return topic === 'multivariable-functions' ? ['x', 'y'] : ['x'];
  return answerVariables(kind, problemLatex);
}
