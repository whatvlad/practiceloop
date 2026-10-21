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

export type StatementKind = 'indefinite' | 'definite' | 'double';

/** Double integrals (#99) show `\iint_D` over a region or two iterated `\int_{a}^{b}`. */
export function statementKind(problemLatex: string): StatementKind {
  if (problemLatex.startsWith('\\iint') || /^\\int_\{.*?\}\^\{.*?\}\s*\\int_/.test(problemLatex)) return 'double';
  return isDefinite(problemLatex) ? 'definite' : 'indefinite';
}

/** The instruction above a statement, from the shared catalogue. */
export const LEAD_KEYS = { indefinite: 'calculate', definite: 'calculate_definite', double: 'calculate_double' } as const;
