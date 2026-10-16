// TEMPORARY STUB for the backend equivalence check (PL-007, PL-008). It
// compares normalised text against a short list of accepted forms, so it
// recognises far fewer equivalent answers than the real symbolic check will.

import type { CheckResult } from '../types';

const ALLOWED = /^[a-z0-9+\-*/^().,|\s]*$/;
const OPERATOR_PAIR = /[+\-*/^]{2}/;
const TRAILING_OPERATOR = /[+\-*/^]$/;
const LEADING_OPERATOR = /^[+*/^]/;

/** Lower-cases, unifies symbols, drops spaces, `*` and a trailing `+ C`. */
export function normalise(input: string): string {
  return input
    .toLowerCase()
    .replace(/π/g, 'pi')
    .replace(/²/g, '^2')
    .replace(/³/g, '^3')
    .replace(/√/g, 'sqrt')
    .replace(/\s+/g, '')
    .replace(/\*/g, '')
    .replace(/\+c$/, '');
}

function balanced(text: string): boolean {
  let depth = 0;
  for (const ch of text) {
    if (ch === '(') depth += 1;
    if (ch === ')') {
      depth -= 1;
      if (depth < 0) return false;
    }
  }
  return depth === 0 && (text.match(/\|/g)?.length ?? 0) % 2 === 0;
}

export function isReadable(input: string): boolean {
  const text = input
    .trim()
    .toLowerCase()
    .replace(/[π²³√]/g, 'x')
    .replace(/\s+/g, '');
  return (
    text.length > 0 &&
    ALLOWED.test(text) &&
    balanced(text) &&
    !OPERATOR_PAIR.test(text) &&
    !TRAILING_OPERATOR.test(text) &&
    !LEADING_OPERATOR.test(text) &&
    !text.includes('()')
  );
}

export function check(input: string, accepted: readonly string[]): CheckResult {
  if (!isReadable(input)) return 'invalid';
  const value = normalise(input);
  return accepted.some((form) => normalise(form) === value) ? 'correct' : 'incorrect';
}
