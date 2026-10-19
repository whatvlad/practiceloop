// Saved account practice and an isolated, untracked guest preview. Public cache only.
import text from '../../../backend/app/content/en.json';
import { TOPICS } from './topics';
import type { AvailableTopic, CheckResult, Difficulty, PublicProblem, RevealedAnswer, RevealedSolution, TopicSlug } from './types';

const base = (import.meta.env.VITE_API_BASE_URL ?? '/api').trim().replace(/\/+$/, '');
let token: Promise<string> | null = null;
let epoch = 0;
let problems: PublicProblem[] = [];
let selection: { topic: TopicSlug; difficulty: Difficulty } = { topic: 'basic-integrals', difficulty: 1 };
let generating: Promise<PublicProblem> | null = null;
let accessToken: () => Promise<string | null> = async () => null;
const keys = new Map<string, string>();
const pending = new Map<string, Promise<unknown>>();
const correctProblems = new Set<string>();
let retryAfter = 0;

export function configurePracticeAuth(provider: () => Promise<string | null>): void { accessToken = provider; }

export class NotFoundError extends Error {}

export function resetPractice(): void {
  epoch += 1;
  token = null;
  generating = null;
  problems = [];
  selection = { topic: 'basic-integrals', difficulty: 1 };
  keys.clear();
  pending.clear();
  correctProblems.clear();
  retryAfter = 0;
}

function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(text.service_error);
  return value as Record<string, unknown>;
}

async function request(path: string, body: unknown, bearer: string | null, saved: boolean, operation?: string): Promise<Record<string, unknown>> {
  const started = epoch;
  if (Date.now() < retryAfter) throw new Error('Please wait a moment before trying again.');
  const key = saved && operation ? keys.get(operation) ?? crypto.randomUUID() : undefined;
  if (key && operation) keys.set(operation, key);
  let response: Response;
  try {
    response = await fetch(`${base}${saved ? '' : '/preview'}${path}`, {
      method: body === undefined ? 'GET' : 'POST',
      headers: { 'Content-Type': 'application/json', ...(bearer ? { Authorization: `Bearer ${bearer}` } : {}),
        ...(key ? { 'Idempotency-Key': key } : {}) },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(10000),
      cache: 'no-store',
    });
  } catch { throw new Error(text.service_error); }
  if (started !== epoch) throw new Error(text.expired);
  if (!response.ok) {
    const delay = Number(response.headers.get('Retry-After'));
    if (Number.isFinite(delay) && delay > 0) retryAfter = Date.now() + delay * 1000;
    // Do not display raw error bodies or exception text from upstream services.
    if (response.status === 401) throw new Error(saved ? 'Please sign in again to continue saved practice.' : text.expired);
    if (response.status === 404) throw new NotFoundError('That problem is not available.');
    if (response.status === 422) {
      if (operation) keys.delete(operation);
      throw new Error('Check your selection or answer and try again.');
    }
    if (response.status === 429) throw new Error('You are going a bit fast. Wait a moment and try again.');
    throw new Error(text.service_error);
  }
  let data: unknown;
  try { data = await response.json(); } catch { throw new Error(text.service_error); }
  if (started !== epoch) throw new Error(text.expired);
  return object(data);
}

async function credentials(): Promise<{ bearer: string; saved: boolean }> {
  const started = epoch;
  const bearer = await accessToken();
  if (started !== epoch) throw new Error(text.expired);
  return { bearer: bearer ?? '', saved: bearer !== null };
}

async function authorize(started: number, saved: boolean, bearer: string): Promise<string> {
  const result = saved ? bearer : await session();
  if (started !== epoch) throw new Error(text.expired);
  return result;
}

function once<T>(name: string, task: () => Promise<T>): Promise<T> {
  const existing = pending.get(name);
  if (existing) return existing as Promise<T>;
  const operation = task();
  pending.set(name, operation);
  void operation.finally(() => { if (pending.get(name) === operation) pending.delete(name); }).catch(() => {});
  return operation;
}

async function session(): Promise<string> {
  if (token) return token;
  const pending = request('/sessions', {}, null, false).then(data => {
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
    correct: correctProblems.size };
}

export async function getTopics(): Promise<AvailableTopic[]> {
  const started = epoch;
  const bearer = await accessToken();
  if (started !== epoch) throw new Error(text.expired);
  if (!bearer) return TOPICS.slice(0, 2).map(topic => ({ ...topic, availableDifficulties: [1, 2] }));
  const data = await request('/topics', undefined, bearer, true);
  if (started !== epoch) throw new Error(text.expired);
  if (!Array.isArray(data.items)) throw new Error(text.service_error);
  const seen = new Set<string>();
  return data.items.map((value: unknown) => {
    const item = object(value);
    const topic = TOPICS.find(t => t.slug === item.slug);
    if (!topic || seen.has(topic.slug) || !Array.isArray(item.availableDifficulties)
      || item.availableDifficulties.some(level => ![1, 2, 3, 4, 5].includes(level))) throw new Error(text.service_error);
    seen.add(topic.slug);
    return { ...topic, availableDifficulties: [...new Set(item.availableDifficulties)] as Difficulty[] };
  });
}

export function generateProblem(topic: TopicSlug, difficulty: Difficulty): Promise<PublicProblem> {
  if (!TOPICS.some(t => t.slug === topic) || ![1, 2, 3, 4, 5].includes(difficulty)) return Promise.reject(new Error(text.unsupported));
  if (generating) return generating;
  const started = epoch;
  const operation = (async () => {
    const { bearer, saved } = await credentials();
    if (!saved && (!['basic-integrals', 'substitution'].includes(topic) || ![1, 2].includes(difficulty))) throw new Error(text.unsupported);
    const operation = `generate:${topic}:${difficulty}`;
    const authorized = await authorize(started, saved, bearer);
    const response = await request('/problems', { topic, difficulty }, authorized, saved, operation);
    const data = saved ? object(response.problem) : response;
    if (started !== epoch) throw new Error(text.expired);
    if (typeof data.id !== 'string' || typeof data.problemLatex !== 'string' || typeof data.createdAt !== 'string'
        || data.topic !== topic || data.difficulty !== difficulty) throw new Error(text.service_error);
    // Explicit projection: even a malformed server response cannot cache private fields.
    const problem: PublicProblem = { saved, id: data.id, topic, difficulty, problemLatex: data.problemLatex,
      createdAt: data.createdAt, answerRevealed: false, solutionRevealed: false, lastResult: null, lastAnswer: null };
    problems.unshift(problem);
    selection = { topic, difficulty };
    keys.delete(operation);
    return structuredClone(problem);
  })();
  generating = operation;
  void operation.finally(() => { if (generating === operation) generating = null; }).catch(() => {});
  return operation;
}

export function submitAttempt(id: string, answer: string): Promise<CheckResult> {
  return once(`attempt:${id}:${answer}`, async () => {
    const problem = find(id);
    const started = epoch;
    const { bearer, saved } = await credentials();
    const operation = `attempt:${id}:${answer}`;
    const authorized = await authorize(started, saved, bearer);
    const response = await request(`/problems/${encodeURIComponent(id)}/attempts`, { answer }, authorized, saved, operation);
    if (started !== epoch) throw new Error(text.expired);
    const data = saved ? object(response.attempt) : response;
    if (data.result !== 'correct' && data.result !== 'incorrect' && data.result !== 'invalid') throw new Error(text.service_error);
    if (data.feedbackCode !== null && data.feedbackCode !== 'missing_constant') throw new Error(text.service_error);
    if (data.feedbackCode === 'missing_constant' && data.result !== 'incorrect') throw new Error(text.service_error);
    if (data.result === 'correct') correctProblems.add(id);
    if (data.result !== 'invalid' || saved) {
      problem.lastResult = data.feedbackCode === 'missing_constant' ? 'missing_constant' : data.result;
      problem.lastAnswer = answer;
    }
    keys.delete(operation);
    return data.feedbackCode === 'missing_constant' ? 'missing_constant' : data.result;
  });
}

export function revealAnswer(id: string): Promise<RevealedAnswer> {
  return once(`answer:${id}`, async () => {
    const problem = find(id);
    const started = epoch;
    const { bearer, saved } = await credentials();
    const authorized = await authorize(started, saved, bearer);
    const data = await request(`/problems/${encodeURIComponent(id)}/reveal-answer`, {}, authorized, saved);
    if (started !== epoch) throw new Error(text.expired);
    if (typeof data.answerLatex !== 'string') throw new Error(text.service_error);
    problem.answerRevealed = true;
    return { answerLatex: data.answerLatex };
  });
}

export function revealSolution(id: string): Promise<RevealedSolution> {
  return once(`solution:${id}`, async () => {
    const problem = find(id);
    const started = epoch;
    const { bearer, saved } = await credentials();
    const authorized = await authorize(started, saved, bearer);
    const data = await request(`/problems/${encodeURIComponent(id)}/reveal-solution`, {}, authorized, saved);
    if (started !== epoch) throw new Error(text.expired);
    if (!Array.isArray(data.steps) || data.steps.length > 20) throw new Error(text.service_error);
    const steps = data.steps.map((value: unknown) => {
      const step = object(value);
      if (typeof step.say !== 'string' || typeof step.latex !== 'string') throw new Error(text.service_error);
      return { say: step.say, latex: step.latex };
    });
    problem.solutionRevealed = true;
    if (saved) problem.answerRevealed = true;
    return { steps };
  });
}
