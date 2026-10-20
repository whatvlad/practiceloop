// Shared problems (#37): anyone with a link or code may look one up, signed in or not.
// No Authorization header is sent, and only the statement, topic and difficulty are kept.
import text from '../../../backend/app/content/en.json';
import { TOPICS } from './topics';
import type { Difficulty, ProblemShare, SharedProblem, ShareUnavailable, TopicSlug } from './types';

const base = (import.meta.env.VITE_API_BASE_URL ?? '/api').trim().replace(/\/+$/, '');
const APP_BASE = import.meta.env.BASE_URL.replace(/\/$/, '');
const TOKEN = /^[A-Za-z0-9_-]{43}$/;
const CONFUSABLE: Record<string, string> = { O: '0', I: '1', L: '1' };

const UNAVAILABLE: Record<string, ShareUnavailable> = {
  share_invalid: 'invalid',
  share_not_found: 'not_found',
  share_expired: 'expired',
  share_revoked: 'revoked',
};

export type ShareLookup = { problem: SharedProblem } | { unavailable: ShareUnavailable };

/** The address a recipient opens; tokens are URL-safe already. */
export function shareLink(share: ProblemShare, origin = window.location.origin): string {
  return `${origin}${APP_BASE}/s/${share.token}`;
}

/** `K7M2QX9P` reads as `K7M2-QX9P`. */
export function shareCode(code: string): string {
  return `${code.slice(0, 4)}-${code.slice(4)}`;
}

/** What the API would accept from a typed code, or null; mirrors app.services.shares. */
export function normalizeCode(value: string): string | null {
  const code = value.replace(/[\s-]/g, '').toUpperCase().replace(/[OIL]/g, c => CONFUSABLE[c]);
  return /^[0-9A-HJKMNP-TV-Z]{8}$/.test(code) ? code : null;
}

export async function lookupShare(ref: { token: string } | { code: string }): Promise<ShareLookup> {
  let path: string;
  if ('token' in ref) {
    if (!TOKEN.test(ref.token)) return { unavailable: 'invalid' };
    path = `/shares/${ref.token}`;
  } else {
    const code = normalizeCode(ref.code);
    if (!code) return { unavailable: 'invalid' };
    path = `/shares/code/${code}`;
  }
  let response: Response;
  try {
    response = await fetch(`${base}${path}`, { headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(10000), cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer' });
  } catch { throw new Error(text.service_error); }
  let data: unknown;
  try { data = await response.json(); } catch { throw new Error(text.service_error); }
  if (!response.ok) {
    if (response.status === 429) throw new Error('Too many people are opening shared problems right now. Try again in a minute.');
    const code = (data as { error?: { code?: unknown } } | null)?.error?.code;
    const state = typeof code === 'string' && Object.hasOwn(UNAVAILABLE, code) ? UNAVAILABLE[code] : undefined;
    if (state) return { unavailable: state };
    throw new Error(text.service_error);
  }
  const problem = (data as { problem?: Record<string, unknown> } | null)?.problem;
  if (!problem || typeof problem.problemLatex !== 'string' || !TOPICS.some(t => t.slug === problem.topic)
    || ![1, 2, 3, 4, 5].includes(problem.difficulty as number)) throw new Error(text.service_error);
  // Explicit projection: even a malformed response cannot carry more into the page.
  return { problem: { topic: problem.topic as TopicSlug, difficulty: problem.difficulty as Difficulty, problemLatex: problem.problemLatex } };
}
