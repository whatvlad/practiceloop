// Saved account practice and an isolated, untracked guest preview. Public cache only.
import text from '../../../backend/app/content/en.json';
import { normalizeCode } from './shares';
import { normalizeProblemCode } from './problemCodes';
import { parseVisual } from '../visual/spec';
import { AREAS, areaOf, isTopicSlug, listedArea, rememberTopics } from './topics';
import { FEEDBACK_CODES } from './types';
import { parseAnswerInput } from './answerInput';
import type { ModulusMode } from '../components/ModulusSettings';
import type { MatrixDimensions } from './types';
import type { AreaSlug, AvailableArea, AvailableTopic, Catalogue, CheckOutcome, Difficulty, LearningStatistics, MatrixOptions, OmissionMetric, OpenedProblem, ProblemPage, ProblemShare, ProfileCounts, PublicProblem, ReportCategory, RevealedAnswer, RevealedSolution, PracticeTopic, TopicSlug, WorksheetCapacity } from './types';

const base = (import.meta.env.VITE_API_BASE_URL ?? '/api').trim().replace(/\/+$/, '');
let token: Promise<string> | null = null;
let epoch = 0;
let problems: PublicProblem[] = [];
export interface Selection { topic: PracticeTopic; difficulty: Difficulty; area: AreaSlug }
const FIRST: Selection = { topic: 'basic-integrals', difficulty: 1, area: 'mathematical-analysis' };
let selection: Selection = { ...FIRST };
let generating: Promise<PublicProblem> | null = null;
let accessToken: () => Promise<string | null> = async () => null;
const keys = new Map<string, string>();
const elapsed = new Map<string, number>();
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
  selection = { ...FIRST };
  keys.clear();
  elapsed.clear();
  pending.clear();
  correctProblems.clear();
  retryAfter = 0;
}

// #190: an old problem of a topic that moved to the new engine can be read but not checked.
const ARCHIVED = 'This problem is archived, so answers can no longer be checked. Its answer and solution are still available.';

/** The error envelope's code only; its message is never shown. */
async function errorCode(response: Response): Promise<string | null> {
  try {
    const body: unknown = await response.json();
    const error = body && typeof body === 'object' ? (body as { error?: { code?: unknown } }).error : undefined;
    return typeof error?.code === 'string' ? error.code : null;
  } catch { return null; }
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
    if (response.status === 410) throw new NotFoundError('This problem is no longer shared. Ask for a new link.');
    if (response.status === 422) {
      if (operation) keys.delete(operation);
      throw new Error('Check your selection or answer and try again.');
    }
    if (response.status === 429) throw new Error('You are going a bit fast. Wait a moment and try again.');
    if (response.status === 409 && await errorCode(response) === 'problem_archived') {
      if (operation) keys.delete(operation);
      throw new Error(ARCHIVED);
    }
    throw new Error(text.service_error);
  }
  let data: unknown;
  try { data = await response.json(); } catch { throw new Error(text.service_error); }
  if (started !== epoch) throw new Error(text.expired);
  return object(data);
}

/** The account's bearer for routes guests cannot use (#116 worksheets), with the epoch it belongs to. */
export async function accountSession(guestMessage: string): Promise<{ bearer: string; started: number }> {
  const started = epoch;
  const { bearer, saved } = await credentials();
  if (!saved) throw new Error(guestMessage);
  return { bearer, started };
}

/** False once the signed-in identity changed after `started`. */
export function sessionCurrent(started: number): boolean { return started === epoch; }

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

function verdict(data: Record<string, unknown>): CheckOutcome {
  if (data.result !== 'correct' && data.result !== 'incorrect' && data.result !== 'invalid') throw new Error(text.service_error);
  if (data.feedbackCode !== null && typeof data.feedbackCode !== 'string') throw new Error(text.service_error);
  if (data.feedbackCode !== null && data.result !== 'incorrect') throw new Error(text.service_error);
  if (data.feedbackCode === 'missing_constant') return { result: 'missing_constant', feedback: null };
  // A code this build does not know yet falls back to the general hint.
  const feedback = FEEDBACK_CODES.find(code => code === data.feedbackCode) ?? null;
  return { result: data.result, feedback };
}

function publicProblem(value: unknown): PublicProblem {
  const data = object(value);
  if (data.exerciseMode !== undefined && !(data.topic === 'complex-arithmetic' ? ['multiply', 'divide'] : data.topic === 'polynomial-division' ? ['division', 'remainder', 'divisibility'] : data.topic === 'complex-conversion' ? ['alg-trig', 'alg-exp', 'trig-alg', 'exp-alg'] : data.topic === 'polynomial-roots' ? ['roots'] : data.topic === 'partial-fractions' ? ['fractions'] : data.topic === 'complex-polar-form' ? ['argument', 'power', 'root'] : []).includes(data.exerciseMode as string)) throw new Error(text.service_error);
  if (data.squareSize !== undefined && (!['determinants', 'inverse-matrices', 'linear-systems'].includes(data.topic as string) || ![2, 3, 4, 5].includes(data.squareSize as number))) throw new Error(text.service_error);
  const matrixDimensions = data.matrixDimensions === undefined ? undefined : object(data.matrixDimensions);
  if (matrixDimensions && (data.topic !== 'matrix-operations' || !['add', 'subtract', 'multiply', 'divide'].includes(matrixDimensions.operation as string) || !['rowsA', 'colsA', 'rowsB', 'colsB'].every(k => [1, 2, 3, 4, 5].includes(matrixDimensions[k] as number)))) throw new Error(text.service_error);
  const dimensions = data.rankDimensions === undefined ? undefined : object(data.rankDimensions);
  if (dimensions && (data.topic !== 'matrix-rank' || ![2, 3, 4, 5].includes(dimensions.rows as number) || ![2, 3, 4, 5].includes(dimensions.columns as number))) throw new Error(text.service_error);
  if (typeof data.id !== 'string' || typeof data.problemLatex !== 'string' || typeof data.createdAt !== 'string'
    || !isTopicSlug(data.topic) || ![1, 2, 3, 4, 5].includes(data.difficulty as number)
    || typeof data.answerRevealed !== 'boolean' || typeof data.solutionRevealed !== 'boolean'
    || !Number.isSafeInteger(data.attemptCount) || (data.attemptCount as number) < 0
    || (data.worksheetId !== undefined && data.worksheetId !== null && typeof data.worksheetId !== 'string')
    || (data.modulusMode !== undefined && (data.topic !== 'complex-numbers' || !['expression', 'properties', 'geometry'].includes(data.modulusMode as string)))) throw new Error(text.service_error);
  const last = data.lastAttempt === null ? null : object(data.lastAttempt);
  if (last && typeof last.answer !== 'string') throw new Error(text.service_error);
  return { saved: true, id: data.id, topic: data.topic as TopicSlug, difficulty: data.difficulty as Difficulty,
    problemLatex: data.problemLatex, createdAt: data.createdAt, answerRevealed: data.answerRevealed,
    solutionRevealed: data.solutionRevealed, attemptCount: data.attemptCount as number,
    lastResult: last ? verdict(last).result : null, lastFeedback: last ? verdict(last).feedback : null,
    lastAnswer: last ? last.answer as string : null, worksheetId: (data.worksheetId as string | null | undefined) ?? null,
    ...(data.answerInput === undefined ? {} : { answerInput: parseAnswerInput(data.answerInput) }),
    ...(data.modulusMode === undefined ? {} : { modulusMode: data.modulusMode as ModulusMode }),
    ...(dimensions ? { rankDimensions: { rows: dimensions.rows as number, columns: dimensions.columns as number } } : {}),
    ...(matrixDimensions ? { matrixDimensions: { operation: matrixDimensions.operation as MatrixDimensions['operation'], rowsA: matrixDimensions.rowsA as number, colsA: matrixDimensions.colsA as number, rowsB: matrixDimensions.rowsB as number, colsB: matrixDimensions.colsB as number } } : {}),
    ...(data.squareSize === undefined ? {} : { squareSize: data.squareSize as number }),
    ...(data.exerciseMode === undefined ? {} : { exerciseMode: data.exerciseMode as PublicProblem['exerciseMode'] }) };
}

function cache(problem: PublicProblem): PublicProblem {
  const existing = problems.find(p => p.id === problem.id);
  if (existing) { Object.assign(existing, problem); return existing; }
  problems.push(problem);
  return problem;
}

function solution(data: Record<string, unknown>): RevealedSolution {
  if (!Array.isArray(data.steps) || data.steps.length > 128) throw new Error(text.service_error);
  const steps = data.steps.map((value: unknown) => {
    const step = object(value);
    if (typeof step.say !== 'string' || typeof step.latex !== 'string') throw new Error(text.service_error);
    if (step.rules !== undefined && (!Array.isArray(step.rules) || step.rules.length > 4)) throw new Error(text.service_error);
    const rules = (step.rules as unknown[] | undefined)?.map(value => {
      const rule = object(value);
      if (typeof rule.title !== 'string' || rule.title.length > 120
        || typeof rule.latex !== 'string' || rule.latex.length > 2000
        || typeof rule.explanation !== 'string' || rule.explanation.length > 1000) throw new Error(text.service_error);
      return { title: rule.title, latex: rule.latex, explanation: rule.explanation };
    });
    const matrix = (value: unknown): number[][] => {
      if (!Array.isArray(value) || value.length < 2 || value.length > 5 || value.some(row => !Array.isArray(row) || row.length !== value.length || row.some((n: unknown) => !Number.isSafeInteger(n) || Math.abs(n as number) > 1e8))) throw new Error(text.service_error);
      return value as number[][];
    };
    const determinantMatrix = step.determinantMatrix === undefined ? undefined : matrix(step.determinantMatrix);
    let minorExpansion: { matrix: number[][]; row: number; columns: number[] } | undefined;
    if (step.minorExpansion !== undefined) {
      const source = object(step.minorExpansion); const m = matrix(source.matrix);
      if (!Number.isInteger(source.row) || (source.row as number) < 0 || (source.row as number) >= m.length || !Array.isArray(source.columns) || source.columns.some(col => !Number.isInteger(col) || col < 0 || col >= m.length)) throw new Error(text.service_error);
      minorExpansion = { matrix: m, row: source.row as number, columns: source.columns as number[] };
    }
    return { say: step.say, latex: step.latex, ...(rules ? { rules } : {}), ...(determinantMatrix ? { determinantMatrix } : {}), ...(minorExpansion ? { minorExpansion } : {}) };
  });
  // A visual this build cannot read is left out; the steps never depend on it.
  const visual = parseVisual(data.visual);
  return visual ? { steps, visual } : { steps };
}

const SHARE_TOKEN = /^[A-Za-z0-9_-]{43}$/;
const SHARE_CODE = /^[0-9A-HJKMNP-TV-Z]{8}$/;

function problemShare(value: unknown): ProblemShare {
  const data = object(value);
  if (typeof data.token !== 'string' || !SHARE_TOKEN.test(data.token) || typeof data.code !== 'string'
    || !SHARE_CODE.test(data.code) || typeof data.expiresAt !== 'string' || Number.isNaN(Date.parse(data.expiresAt))) throw new Error(text.service_error);
  return { token: data.token, code: data.code, expiresAt: data.expiresAt };
}

/** The problem's live share, or a new one; only saved problems can be shared (#37). */
export function shareProblem(id: string): Promise<ProblemShare> {
  return once(`share:${id}`, async () => {
    const started = epoch;
    const { bearer, saved } = await credentials();
    if (!saved) throw new Error('Sign in to share a problem.');
    const data = await request(`/problems/${encodeURIComponent(id)}/share`, {}, bearer, true);
    if (started !== epoch) throw new Error(text.expired);
    return problemShare(data.share);
  });
}

/** Ends the link and the code at once. */
export function stopSharing(id: string): Promise<void> {
  return once(`unshare:${id}`, async () => {
    const started = epoch;
    const { bearer, saved } = await credentials();
    if (!saved) throw new Error('Sign in to share a problem.');
    const data = await request(`/problems/${encodeURIComponent(id)}/share/revoke`, {}, bearer, true);
    if (started !== epoch) throw new Error(text.expired);
    if (data.share !== null) throw new Error(text.service_error);
  });
}

/** Start this exact shared exercise; retries reuse the same recipient-owned copy. */
export function practiceSharedProblem(ref: { token: string } | { code: string }): Promise<PublicProblem> {
  const body = 'token' in ref ? { token: ref.token } : { code: normalizeCode(ref.code) };
  if (('token' in ref && !SHARE_TOKEN.test(ref.token)) || ('code' in ref && !body.code)) {
    return Promise.reject(new Error('That link or code is not valid.'));
  }
  const operation = `practice-share:${JSON.stringify(body)}`;
  return once(operation, async () => {
    const started = epoch;
    const { bearer, saved } = await credentials();
    if (!saved) throw new Error('Sign in to solve this problem.');
    const data = await request('/shares/practice', body, bearer, true, operation);
    if (started !== epoch) throw new Error(text.expired);
    return structuredClone(cache(publicProblem(data.problem)));
  });
}

/** Save a separate exercise from a permanent code, with normal private reveals. */
export function practiceCodeProblem(value: string): Promise<PublicProblem> {
  const code = normalizeProblemCode(value);
  if (!code) return Promise.reject(new Error('That problem code is not valid.'));
  const operation = `practice-code:${code}`;
  return once(operation, async () => {
    const started = epoch;
    const { bearer, saved } = await credentials();
    if (!saved) throw new Error('Sign in to solve this problem.');
    const data = await request('/codes/practice', { code }, bearer, true, operation);
    if (started !== epoch) throw new Error(text.expired);
    return structuredClone(cache(publicProblem(data.problem)));
  });
}

/** #38: one report per call; categories mirror app.api.reports. */
export function reportProblem(id: string, category: ReportCategory, comment: string): Promise<void> {
  return once(`report:${id}`, async () => {
    const started = epoch;
    const { bearer, saved } = await credentials();
    if (!saved) throw new Error('Sign in to report a problem.');
    const trimmed = comment.trim();
    const data = await request(`/problems/${encodeURIComponent(id)}/report`,
      { category, ...(trimmed ? { comment: trimmed.slice(0, 500) } : {}) }, bearer, true);
    if (started !== epoch) throw new Error(text.expired);
    if (object(data.report).category !== category) throw new Error(text.service_error);
  });
}

/** One history page; `worksheet` keeps only problems a generated worksheet created (ADR-007). */
export async function listProblemPage({ limit = 20, cursor = null, worksheet = false }: { limit?: number; cursor?: string | null; worksheet?: boolean } = {}): Promise<ProblemPage> {
  if (!Number.isInteger(limit) || limit < 1 || limit > 50) throw new Error(text.service_error);
  const started = epoch;
  const { bearer, saved } = await credentials();
  if (!saved) {
    const offset = cursor === null ? 0 : Number(cursor);
    if (!Number.isSafeInteger(offset) || offset < 0) throw new Error(text.service_error);
    const local = worksheet ? problems.filter(p => p.worksheetId) : problems;
    return { items: structuredClone(local.slice(offset, offset + limit)),
      nextCursor: offset + limit < local.length ? String(offset + limit) : null };
  }
  const query = new URLSearchParams({ limit: String(limit) });
  if (cursor !== null) query.set('cursor', cursor);
  if (worksheet) query.set('worksheet', 'true');
  const data = await request(`/problems?${query}`, undefined, bearer, true);
  if (started !== epoch) throw new Error(text.expired);
  if (!Array.isArray(data.items) || data.items.length > limit
    || (data.nextCursor !== null && (typeof data.nextCursor !== 'string' || !data.nextCursor || data.nextCursor === cursor))) throw new Error(text.service_error);
  const items = data.items.map(publicProblem);
  if (new Set(items.map(p => p.id)).size !== items.length || (!items.length && data.nextCursor)) throw new Error(text.service_error);
  items.forEach(cache);
  return { items, nextCursor: data.nextCursor as string | null };
}

/** Convenience read of the most recent history page. */
export async function listProblems(): Promise<PublicProblem[]> { return (await listProblemPage()).items; }

export async function openDemo(): Promise<OpenedProblem> {
  const demo = problems.find(problem => problem.saved === false) ?? await generateProblem('basic-integrals', 1);
  return openProblem(demo.id);
}

export async function openProblem(id: string): Promise<OpenedProblem> {
  const started = epoch;
  const { bearer, saved } = await credentials();
  if (!saved) {
    const problem = structuredClone(find(id));
    return { problem, ...(problem.answerRevealed ? { answer: await revealAnswer(id) } : {}),
      ...(problem.solutionRevealed ? { solution: await revealSolution(id) } : {}) };
  }
  const data = await request(`/problems/${encodeURIComponent(id)}`, undefined, bearer, true);
  if (started !== epoch) throw new Error(text.expired);
  const problem = publicProblem(data.problem);
  if (problem.id !== id) throw new Error(text.service_error);
  const result: OpenedProblem = { problem };
  if (problem.answerRevealed) {
    const answer = object(data.answer);
    if (typeof answer.answerLatex !== 'string') throw new Error(text.service_error);
    result.answer = { answerLatex: answer.answerLatex };
  }
  if (problem.solutionRevealed) result.solution = solution(object(data.solution));
  result.share = data.share === null || data.share === undefined ? null : problemShare(data.share);
  // The cache keeps session-only flags such as `mixed` that the server does not store.
  result.problem = structuredClone(cache(problem));
  return result;
}

/** Public cache lookup for an already active problem, otherwise open it from the server. */
export async function getProblem(id: string): Promise<PublicProblem> {
  const local = problems.find(p => p.id === id);
  return local ? structuredClone(local) : (await openProblem(id)).problem;
}
export async function getLastSelection() { return { ...selection }; }
export async function getProfileCounts(): Promise<ProfileCounts> {
  const started = epoch;
  const { bearer, saved } = await credentials();
  if (saved) {
    const data = await once('profile-read', () => request('/profile', undefined, bearer, true));
    if (started !== epoch) throw new Error(text.expired);
    const counts = object(data.counts);
    const values = [counts.generated, counts.attempted, counts.correct];
    if (values.some(value => !Number.isSafeInteger(value) || (value as number) < 0)
      || (counts.correct as number) > (counts.attempted as number) || (counts.attempted as number) > (counts.generated as number)) throw new Error(text.service_error);
    return { generated: counts.generated as number, attempted: counts.attempted as number, correct: counts.correct as number };
  }
  return { generated: problems.length, attempted: problems.filter(p => p.lastResult !== null).length,
    correct: correctProblems.size };
}

const LEVELS = [1, 2, 3, 4, 5];

function difficulties(value: unknown): Difficulty[] {
  if (!Array.isArray(value) || value.some(level => !LEVELS.includes(level))) throw new Error(text.service_error);
  return [...new Set(value)] as Difficulty[];
}

/** ADR-007 decision 4: distinct records per level; absent when the API does not publish it. */
function capacity(value: unknown, levels: readonly Difficulty[]): WorksheetCapacity | undefined {
  if (value === undefined || value === null) return undefined;
  const data = object(value);
  const result: WorksheetCapacity = {};
  for (const [key, count] of Object.entries(data)) {
    const level = Number(key) as Difficulty;
    if (!levels.includes(level) || !Number.isSafeInteger(count) || (count as number) < 0) throw new Error(text.service_error);
    result[level] = count as number;
  }
  return result;
}

function mixedPractice(value: unknown, area: AreaSlug, topics: readonly AvailableTopic[]): AvailableArea['mixed'] {
  if (value === null) return null;
  const data = object(value);
  const weights = object(data.weights);
  if (Object.entries(weights).some(([slug, weight]) => !topics.some(t => t.slug === slug && t.area === area)
    || !Number.isSafeInteger(weight) || (weight as number) <= 0)) throw new Error(text.service_error);
  const availableDifficulties = difficulties(data.availableDifficulties);
  const worksheetCapacity = capacity(data.worksheetCapacity, availableDifficulties);
  return { availableDifficulties, weights: weights as Record<TopicSlug, number>, ...(worksheetCapacity ? { worksheetCapacity } : {}) };
}

export async function getTopics(): Promise<AvailableTopic[]> {
  return (await getCatalogue()).topics;
}

// The guest preview serves only these cells (see generateProblem); the API lists the rest.
const PREVIEW_TOPICS: readonly AvailableTopic[] = [
  { slug: 'basic-integrals', name: 'Basic integrals', area: 'mathematical-analysis', availableDifficulties: [1, 2] },
  { slug: 'substitution', name: 'Substitution', area: 'mathematical-analysis', availableDifficulties: [1, 2] },
];

/** #191: the topic list is the API's; this build has no copy of its own. */
export async function getCatalogue(): Promise<Catalogue> {
  const started = epoch;
  const bearer = await accessToken();
  if (started !== epoch) throw new Error(text.expired);
  if (!bearer) {
    rememberTopics(PREVIEW_TOPICS);
    return { areas: [{ ...AREAS.find(area => area.slug === FIRST.area)!, mixed: null }], topics: structuredClone([...PREVIEW_TOPICS]) };
  }
  const data = await request('/topics', undefined, bearer, true);
  if (started !== epoch) throw new Error(text.expired);
  if (!Array.isArray(data.items) || !Array.isArray(data.areas)) throw new Error(text.service_error);
  const seen = new Set<string>();
  const topics: AvailableTopic[] = data.items.map((value: unknown) => {
    const item = object(value);
    const area = AREAS.find(a => a.slug === item.area);
    if (!isTopicSlug(item.slug) || seen.has(item.slug) || typeof item.name !== 'string' || !item.name.trim()
      || item.name.length > 80 || !area || !Array.isArray(item.availableDifficulties)
      || item.availableDifficulties.some(level => ![1, 2, 3, 4, 5].includes(level))) throw new Error(text.service_error);
    seen.add(item.slug);
    const availableDifficulties = [...new Set(item.availableDifficulties)] as Difficulty[];
    const worksheetCapacity = capacity(item.worksheetCapacity, availableDifficulties);
    return { slug: item.slug, name: item.name, area: area.slug, availableDifficulties, ...(worksheetCapacity ? { worksheetCapacity } : {}) };
  });
  const areas = data.areas.map((value: unknown) => {
    const item = object(value);
    const area = AREAS.find(a => a.slug === item.slug);
    if (!area) throw new Error(text.service_error);
    return { ...area, mixed: mixedPractice(item.mixed, area.slug, topics) };
  });
  if (new Set(areas.map(a => a.slug)).size !== areas.length
    || topics.some(t => !areas.some(a => a.slug === t.area))) throw new Error(text.service_error);
  rememberTopics(topics);
  return { areas, topics };
}

/** `area` picks the area mixed practice draws from; a topic carries its own area. */
export function generateProblem(topic: PracticeTopic, difficulty: Difficulty, area: AreaSlug = 'mathematical-analysis', matrixOptions?: MatrixOptions, modulusMode?: ModulusMode, rankDimensions?: { rows: number; columns: number }, matrixDimensions?: MatrixDimensions, squareSize?: number, exerciseMode?: PublicProblem['exerciseMode']): Promise<PublicProblem> {
  const mixed = topic === 'mixed';
  if ((!mixed && !isTopicSlug(topic)) || ![1, 2, 3, 4, 5].includes(difficulty)
    || !AREAS.some(a => a.slug === area) || (matrixOptions && topic !== 'matrix-operations')
    || (modulusMode && (topic !== 'complex-numbers' || difficulty > 3 || !['expression', 'properties', 'geometry'].includes(modulusMode)))
    || (rankDimensions && (topic !== 'matrix-rank' || difficulty > 3 || ![2, 3, 4, 5].includes(rankDimensions.rows) || ![2, 3, 4, 5].includes(rankDimensions.columns)))
    || (matrixDimensions && (topic !== 'matrix-operations' || difficulty > 3 || !!matrixOptions))
    || (squareSize !== undefined && (!['determinants', 'inverse-matrices', 'linear-systems'].includes(topic) || difficulty > 3 || ![2, 3, 4, 5].includes(squareSize)))
    || (exerciseMode && (difficulty > 3 || !(topic === 'complex-arithmetic' ? ['multiply', 'divide'] : topic === 'polynomial-division' ? ['division', 'remainder', 'divisibility'] : topic === 'complex-conversion' ? ['alg-trig', 'alg-exp', 'trig-alg', 'exp-alg'] : topic === 'polynomial-roots' ? ['roots'] : topic === 'partial-fractions' ? ['fractions'] : topic === 'complex-polar-form' ? ['argument', 'power', 'root'] : []).includes(exerciseMode)))) return Promise.reject(new Error(text.unsupported));
  const drawFrom = mixed ? area : areaOf(topic);
  if (generating) return generating;
  const started = epoch;
  const operation = (async () => {
    const { bearer, saved } = await credentials();
    if (!saved && (mixed || !PREVIEW_TOPICS.some(t => t.slug === topic && t.availableDifficulties.includes(difficulty)))) throw new Error(text.unsupported);
    const operation = (mixed ? `generate:mixed:${drawFrom}:${difficulty}` : `generate:${topic}:${difficulty}`)
      + (matrixOptions ? `:${matrixOptions.operation}:${matrixOptions.size}` : '') + (modulusMode ? `:${modulusMode}` : '') + (rankDimensions ? `:${rankDimensions.rows}:${rankDimensions.columns}` : '') + (matrixDimensions ? `:${JSON.stringify(matrixDimensions)}` : '') + (squareSize ? `:${squareSize}` : '') + (exerciseMode ? `:${exerciseMode}` : '');
    const authorized = await authorize(started, saved, bearer);
    const body = mixed ? { topic, area: drawFrom, difficulty } : { topic, difficulty, ...(matrixOptions ? { matrixOptions } : {}), ...(modulusMode ? { modulusMode } : {}), ...(rankDimensions ? { rankDimensions } : {}), ...(matrixDimensions ? { matrixDimensions } : {}), ...(squareSize ? { squareSize } : {}), ...(exerciseMode ? { exerciseMode } : {}) };
    const response = await request('/problems', body, authorized, saved, operation);
    const data = saved ? object(response.problem) : response;
    if (started !== epoch) throw new Error(text.expired);
    if (typeof data.id !== 'string' || typeof data.problemLatex !== 'string' || typeof data.createdAt !== 'string'
        || (mixed ? !isTopicSlug(data.topic) || listedArea(data.topic) !== drawFrom : data.topic !== topic)
        || data.difficulty !== difficulty) throw new Error(text.service_error);
    // Explicit projection: even a malformed server response cannot cache private fields.
    const problem: PublicProblem = { saved, id: data.id, topic: data.topic as TopicSlug, difficulty,
      problemLatex: data.problemLatex, createdAt: data.createdAt, answerRevealed: false, solutionRevealed: false,
      lastResult: null, lastAnswer: null, ...(mixed ? { mixed: true } : {}),
      ...(data.answerInput === undefined ? {} : { answerInput: parseAnswerInput(data.answerInput) }),
      ...(modulusMode ? { modulusMode } : {}), ...(rankDimensions ? { rankDimensions } : {}), ...(matrixDimensions ? { matrixDimensions } : {}), ...(squareSize ? { squareSize } : {}), ...(exerciseMode ? { exerciseMode } : {}) };
    problems.unshift(problem);
    selection = { topic, difficulty, area: drawFrom };
    keys.delete(operation);
    return structuredClone(problem);
  })();
  generating = operation;
  void operation.finally(() => { if (generating === operation) generating = null; }).catch(() => {});
  return operation;
}

export function submitAttempt(id: string, answer: string, elapsedMs?: number): Promise<CheckOutcome> {
  return once(`attempt:${id}:${answer}`, async () => {
    const problem = find(id);
    const started = epoch;
    const { bearer, saved } = await credentials();
    const operation = `attempt:${id}:${answer}`;
    if (elapsedMs !== undefined && !elapsed.has(operation)) elapsed.set(operation, elapsedMs);
    const authorized = await authorize(started, saved, bearer);
    const response = await request(`/problems/${encodeURIComponent(id)}/attempts`, { answer, ...(saved && elapsed.has(operation) ? { elapsedMs: elapsed.get(operation) } : {}) }, authorized, saved, operation);
    if (started !== epoch) throw new Error(text.expired);
    const data = saved ? object(response.attempt) : response;
    const checked = verdict(data);
    if (data.result === 'correct') correctProblems.add(id);
    if (data.result !== 'invalid' || saved) {
      problem.lastResult = checked.result;
      problem.lastFeedback = checked.feedback;
      problem.lastAnswer = answer;
      problem.attemptCount = (problem.attemptCount ?? 0) + 1;
    }
    keys.delete(operation);
    elapsed.delete(operation);
    return checked;
  });
}

async function accountRequest(path: string, body?: unknown) {
  const { bearer, saved } = await credentials();
  if (!saved) throw new Error('Sign in to view your account.');
  if (path === '/profile' && body === undefined) return once('profile-read', () => request(path, body, bearer, true));
  return request(path, body, bearer, true);
}

export async function getDisplayName(): Promise<string | null> {
  const data = await accountRequest('/profile');
  const account = object(data.account);
  if (account.name !== null && typeof account.name !== 'string') throw new Error(text.service_error);
  return account.name as string | null;
}

export async function saveDisplayName(name: string): Promise<void> {
  await accountRequest('/profile', { name: name.trim() || null });
}

export async function deleteAccount(): Promise<void> {
  const data = await accountRequest('/account/delete', { confirmation: 'DELETE' });
  if (data.deleted !== true) throw new Error(text.service_error);
  resetPractice();
}

function omissionMetric(value: unknown): OmissionMetric {
  const data = object(value);
  if (!Number.isSafeInteger(data.checkedAttempts) || !Number.isSafeInteger(data.omitted)
    || (data.omitted as number) < 0 || (data.checkedAttempts as number) < (data.omitted as number)
    || (data.checkedAttempts === 0 ? data.rate !== null : typeof data.rate !== 'number'
      || Math.abs(data.rate - (data.omitted as number) / (data.checkedAttempts as number)) > 1e-9)) throw new Error(text.service_error);
  return { checkedAttempts: data.checkedAttempts as number, omitted: data.omitted as number, rate: data.rate as number | null };
}

export async function getLearningStatistics(): Promise<LearningStatistics> {
  const data = await accountRequest('/statistics');
  if (!Array.isArray(data.byTopicDifficulty) || !Array.isArray(data.weekly) || data.weekly.length !== 8) throw new Error(text.service_error);
  return { ...omissionMetric(data), byTopicDifficulty: data.byTopicDifficulty.map(value => {
    const item = object(value);
    if (!isTopicSlug(item.topic) || ![1, 2, 3, 4, 5].includes(item.difficulty as number)) throw new Error(text.service_error);
    return { ...omissionMetric(item), topic: item.topic as TopicSlug, difficulty: item.difficulty as Difficulty };
  }), weekly: data.weekly.map(value => {
    const item = object(value);
    if (typeof item.week !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(item.week)) throw new Error(text.service_error);
    return { ...omissionMetric(item), week: item.week };
  }) };
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
    const revealed = solution(data);
    problem.solutionRevealed = true;
    if (saved) problem.answerRevealed = true;
    return revealed;
  });
}
