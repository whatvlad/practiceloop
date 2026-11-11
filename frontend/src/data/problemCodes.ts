// Permanent problem codes (#198). The server checks the checksum and rebuilds privately.
import text from '../../../backend/app/content/en.json';
import { parsePromptVisual } from '../visual/spec';
import { parseAnswerInput } from './answerInput';
import { parseVisual } from '../visual/spec';
import { isTopicSlug } from './topics';
import type { ShareLookup } from './shares';
import type { Difficulty, TopicSlug } from './types';

const base = (import.meta.env.VITE_API_BASE_URL ?? '/api').trim().replace(/\/+$/, '');

export function normalizeProblemCode(value: string): string | null {
  if (value.length > 128 || [...value].some(c => c.charCodeAt(0) > 127)) return null;
  const match = /^([A-Z]{2,8})([1-9][0-9]{0,3})([0-9]{16})([0-9]{2})$/.exec(value.replace(/[\s-]/g, '').toUpperCase());
  return match ? `${match[1]}-${match[2]}-${match[3]}-${match[4]}` : null;
}

export async function lookupProblemCode(value: string): Promise<ShareLookup> {
  const code = normalizeProblemCode(value);
  if (!code) return { unavailable: 'invalid' };
  let response: Response;
  try {
    response = await fetch(`${base}/codes?code=${encodeURIComponent(code)}`, {
      headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(10000),
      cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer',
    });
  } catch { throw new Error(text.service_error); }
  let data: unknown;
  try { data = await response.json(); } catch { throw new Error(text.service_error); }
  if (!response.ok) {
    if (response.status === 400 && (data as { error?: { code?: unknown } } | null)?.error?.code === 'problem_code_invalid') return { unavailable: 'invalid' };
    if (response.status === 429) throw new Error('Too many problems are being opened right now. Try again in a minute.');
    throw new Error(text.service_error);
  }
  const problem = (data as { problem?: Record<string, unknown> } | null)?.problem;
  if (!problem || typeof problem.problemLatex !== 'string' || !isTopicSlug(problem.topic)
    || ![1, 2, 3, 4, 5].includes(problem.difficulty as number)) throw new Error(text.service_error);
  const statementVisual = parseVisual(problem.statementVisual);
  const promptVisual = parsePromptVisual(problem.promptVisual);
  return { problem: { topic: problem.topic as TopicSlug, difficulty: problem.difficulty as Difficulty, problemLatex: problem.problemLatex,
    ...(promptVisual ? { promptVisual } : {}),
    ...(problem.selfReview === true ? { selfReview: true } : {}),
    ...(statementVisual ? { statementVisual } : {}),
    ...(problem.answerInput === undefined ? {} : { answerInput: parseAnswerInput(problem.answerInput) }) } };
}
