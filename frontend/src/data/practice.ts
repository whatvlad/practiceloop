// Untracked preview: only public problems live in page memory. No mock fallback.
import text from '../../../backend/app/content/en.json';
import type { CheckResult, Difficulty, PublicProblem, RevealedAnswer, RevealedSolution, TopicSlug } from './types';

const base = (import.meta.env.VITE_API_BASE_URL ?? '/api').trim().replace(/\/+$/, '');
let token: Promise<string> | null = null;
let epoch = 0;
let problems: PublicProblem[] = [];
let selection: { topic: TopicSlug; difficulty: Difficulty } = { topic: 'basic-integrals', difficulty: 1 };
let generating: Promise<PublicProblem> | null = null;

export class NotFoundError extends Error {}

export function resetPractice(): void {
  epoch += 1;
  token = null;
  generating = null;
  problems = [];
  selection = { topic: 'basic-integrals', difficulty: 1 };
}

function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(text.service_error);
  return value as Record<string, unknown>;
}

async function request(path: string, body?: unknown, bearer?: string): Promise<Record<string, unknown>> {
  const started = epoch;
  let response: Response;
  try {
    response = await fetch(`${base}/preview${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(bearer ? { Authorization: `Bearer ${bearer}` } : {}) },
      body: JSON.stringify(body ?? {}),
      signal: AbortSignal.timeout(10000),
      cache: 'no-store',
    });
  } catch { throw new Error(text.service_error); }
  if (started !== epoch) throw new Error(text.expired);
  if (!response.ok) throw new Error(response.status === 401 || response.status === 409 ? text.expired : text.service_error);
  let data: unknown;
  try { data = await response.json(); } catch { throw new Error(text.service_error); }
  if (started !== epoch) throw new Error(text.expired);
  return object(data);
}

async function session(): Promise<string> {
  if (token) return token;
  const pending = request('/sessions').then(data => {
    if (typeof data.token !== 'string' || data.token.length < 32) throw new Error(text.service_error);
    return data.token;
  }).catch(error => { if (token === pending) token = null; throw error; });
  token = pending;
  return token;
}

function find(id: string): PublicProblem {
  const problem = problems.find(p => p.id === id);
  if (!problem) throw new NotFoundError(text.expired);
  return problem;
}

export async function listProblems(): Promise<PublicProblem[]> { return structuredClone(problems); }
export async function getProblem(id: string): Promise<PublicProblem> { return structuredClone(find(id)); }
export async function getLastSelection() { return { ...selection }; }
export async function getProfileCounts() {
  return { generated: problems.length, attempted: problems.filter(p => p.lastResult !== null).length,
    correct: problems.filter(p => p.lastResult === 'correct').length };
}

export function generateProblem(topic: TopicSlug, difficulty: Difficulty): Promise<PublicProblem> {
  if (!['basic-integrals', 'substitution'].includes(topic) || ![1, 2].includes(difficulty)) return Promise.reject(new Error(text.unsupported));
  if (generating) return generating;
  const started = epoch;
  const operation = (async () => {
    const data = await request('/problems', { topic, difficulty }, await session());
    if (started !== epoch) throw new Error(text.expired);
    if (typeof data.id !== 'string' || typeof data.problemLatex !== 'string' || typeof data.createdAt !== 'string'
        || data.topic !== topic || data.difficulty !== difficulty) throw new Error(text.service_error);
    // Explicit projection: even a malformed server response cannot cache private fields.
    const problem: PublicProblem = { id: data.id, topic, difficulty, problemLatex: data.problemLatex,
      createdAt: data.createdAt, answerRevealed: false, solutionRevealed: false, lastResult: null, lastAnswer: null };
    problems.unshift(problem);
    selection = { topic, difficulty };
    return structuredClone(problem);
  })();
  generating = operation;
  void operation.finally(() => { if (generating === operation) generating = null; }).catch(() => {});
  return operation;
}

export async function submitAttempt(id: string, answer: string): Promise<CheckResult> {
  const problem = find(id);
  const data = await request(`/problems/${encodeURIComponent(id)}/attempts`, { answer }, await session());
  if (data.result !== 'correct' && data.result !== 'incorrect' && data.result !== 'invalid') throw new Error(text.service_error);
  if (data.feedbackCode !== null && data.feedbackCode !== 'missing_constant') throw new Error(text.service_error);
  if (data.result !== 'invalid') {
    problem.lastResult = data.result;
    problem.lastAnswer = answer;
  }
  return data.feedbackCode === 'missing_constant' ? 'missing_constant' : data.result;
}

export async function revealAnswer(id: string): Promise<RevealedAnswer> {
  const problem = find(id);
  const data = await request(`/problems/${encodeURIComponent(id)}/reveal-answer`, {}, await session());
  if (typeof data.answerLatex !== 'string') throw new Error(text.service_error);
  problem.answerRevealed = true;
  return { answerLatex: data.answerLatex };
}

export async function revealSolution(id: string): Promise<RevealedSolution> {
  const problem = find(id);
  const data = await request(`/problems/${encodeURIComponent(id)}/reveal-solution`, {}, await session());
  if (!Array.isArray(data.steps) || data.steps.length > 20) throw new Error(text.service_error);
  const steps = data.steps.map((value: unknown) => {
    const step = object(value);
    if (typeof step.say !== 'string' || typeof step.latex !== 'string') throw new Error(text.service_error);
    return { say: step.say, latex: step.latex };
  });
  problem.solutionRevealed = true;
  return { steps };
}
