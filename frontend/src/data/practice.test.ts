import { beforeEach, afterEach, expect, it, vi } from 'vitest';
import * as practice from './practice';

const fetchMock = vi.fn<typeof fetch>();
const publicProblem = { id: 'problem-1', topic: 'basic-integrals', difficulty: 1, problemLatex: '\\int x\\,dx', createdAt: '2026-10-19T00:00:00Z' };
const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
beforeEach(() => { practice.resetPractice(); practice.configurePracticeAuth(async () => null); fetchMock.mockReset(); vi.stubGlobal('fetch', fetchMock); });
afterEach(() => vi.unstubAllGlobals());

async function generate() {
  fetchMock.mockResolvedValueOnce(response({ token: 'a'.repeat(43) }));
  fetchMock.mockResolvedValueOnce(response(publicProblem));
  return practice.generateProblem('basic-integrals', 1);
}

it('calls the real boundary once for duplicate clicks and starts with an empty history', async () => {
  expect(await practice.listProblems()).toEqual([]);
  fetchMock.mockResolvedValueOnce(response({ token: 'a'.repeat(43) }));
  fetchMock.mockResolvedValueOnce(response({ ...publicProblem, answer: 'PRIVATE', record: { seed: 1 } }));
  const one = practice.generateProblem('basic-integrals', 1);
  const two = practice.generateProblem('basic-integrals', 1);
  expect(one).toBe(two);
  const problem = await one;
  expect(fetchMock).toHaveBeenCalledTimes(2);
  expect(fetchMock.mock.calls[1][0]).toMatch(/\/preview\/problems$/);
  expect(fetchMock.mock.calls[1][1]?.headers).toHaveProperty('Authorization', `Bearer ${'a'.repeat(43)}`);
  expect(JSON.stringify(problem)).not.toMatch(/PRIVATE|seed|record/);
  expect(await practice.getProfileCounts()).toEqual({ generated: 1, attempted: 0, correct: 0 });
});

it('keeps missing-constant feedback separate and reveals only on explicit requests', async () => {
  const problem = await generate();
  fetchMock.mockResolvedValueOnce(response({ result: 'incorrect', feedbackCode: 'missing_constant' }));
  expect(await practice.submitAttempt(problem.id, 'x^2/2')).toBe('missing_constant');
  fetchMock.mockResolvedValueOnce(response({ answerLatex: 'x^2/2+C' }));
  expect(await practice.revealAnswer(problem.id)).toEqual({ answerLatex: 'x^2/2+C' });
  fetchMock.mockResolvedValueOnce(response({ steps: [{ say: 'Integrate.', latex: 'x^2/2+C', private: true }] }));
  expect(await practice.revealSolution(problem.id)).toEqual({ steps: [{ say: 'Integrate.', latex: 'x^2/2+C' }] });
  expect(JSON.stringify(await practice.getProblem(problem.id))).not.toContain('answerLatex');
});

it('does not turn network failures into incorrect answers or fallback demos', async () => {
  const problem = await generate();
  fetchMock.mockResolvedValueOnce(response({}, 503));
  await expect(practice.submitAttempt(problem.id, 'x')).rejects.toThrow('Try again');
  expect((await practice.getProblem(problem.id)).lastResult).toBeNull();
  fetchMock.mockRejectedValueOnce(new TypeError('Network error'));
  await expect(practice.generateProblem('basic-integrals', 1)).rejects.toThrow('Try again');
  expect(await practice.listProblems()).toHaveLength(1);
});

it('rejects unsupported cells before networking and clears public state on identity changes', async () => {
  await expect(practice.generateProblem('integration-by-parts', 1)).rejects.toThrow('available');
  await expect(practice.generateProblem('substitution', 3)).rejects.toThrow('available');
  expect(fetchMock).not.toHaveBeenCalled();
  const problem = await generate();
  practice.resetPractice();
  expect(await practice.listProblems()).toEqual([]);
  await expect(practice.getProblem(problem.id)).rejects.toBeInstanceOf(practice.NotFoundError);
});

it('discards a response from the previous identity', async () => {
  fetchMock.mockResolvedValueOnce(response({ token: 'a'.repeat(43) }));
  let finish!: (value: Response) => void;
  fetchMock.mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  const pending = practice.generateProblem('basic-integrals', 1);
  await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  practice.resetPractice();
  finish(response(publicProblem));
  await expect(pending).rejects.toThrow('expired');
  expect(await practice.listProblems()).toEqual([]);
});

it('rejects malformed check and solution payloads without marking a result', async () => {
  const problem = await generate();
  fetchMock.mockResolvedValueOnce(response({ result: 'correct', feedbackCode: 'secret' }));
  await expect(practice.submitAttempt(problem.id, 'x')).rejects.toThrow();
  fetchMock.mockResolvedValueOnce(response({ steps: [{ say: 42, latex: 'x' }] }));
  await expect(practice.revealSolution(problem.id)).rejects.toThrow();
  expect((await practice.getProblem(problem.id)).lastResult).toBeNull();
});

async function savedProblem() {
  practice.configurePracticeAuth(async () => 'supabase-access-token');
  fetchMock.mockResolvedValueOnce(response({ problem: { ...publicProblem, answerRevealed: false,
    solutionRevealed: false, lastAttempt: null, answerLatex: 'PRIVATE', generator: 'PRIVATE' } }, 201));
  return practice.generateProblem('basic-integrals', 1);
}

it('uses saved DTOs and a Supabase bearer without creating a preview session or caching private fields', async () => {
  const problem = await savedProblem();
  expect(problem.saved).toBe(true);
  expect(fetchMock).toHaveBeenCalledTimes(1);
  expect(fetchMock.mock.calls[0][0]).toBe('/api/problems');
  expect(fetchMock.mock.calls[0][1]?.headers).toMatchObject({ Authorization: 'Bearer supabase-access-token' });
  expect(JSON.stringify(await practice.getProblem(problem.id))).not.toContain('PRIVATE');
  fetchMock.mockResolvedValueOnce(response({ attempt: { result: 'invalid', feedbackCode: null } }, 201));
  expect(await practice.submitAttempt(problem.id, 'sin(')).toBe('invalid');
  expect((await practice.getProblem(problem.id)).lastResult).toBe('invalid');
  fetchMock.mockResolvedValueOnce(response({ attempt: { result: 'incorrect', feedbackCode: 'missing_constant' } }, 201));
  expect(await practice.submitAttempt(problem.id, 'x^2/2')).toBe('missing_constant');
  expect((await practice.getProblem(problem.id)).lastResult).toBe('missing_constant');
  fetchMock.mockResolvedValueOnce(response({ steps: [{ say: 'Integrate.', latex: 'x^2/2+C' }] }));
  await practice.revealSolution(problem.id);
  expect(await practice.getProblem(problem.id)).toMatchObject({ answerRevealed: true, solutionRevealed: true });
  expect(JSON.stringify(await practice.getProblem(problem.id))).not.toContain('steps');
});

it('reuses the generation key after a lost response but makes a new key for the next deliberate problem', async () => {
  practice.configurePracticeAuth(async () => 'access-token');
  fetchMock.mockRejectedValueOnce(new TypeError('Network failed after commit'));
  await expect(practice.generateProblem('basic-integrals', 1)).rejects.toThrow();
  const firstKey = (fetchMock.mock.calls[0][1]?.headers as Record<string, string>)['Idempotency-Key'];
  expect(firstKey).toMatch(/^[0-9a-f-]{14}4[0-9a-f-]{21}$/);
  fetchMock.mockResolvedValueOnce(response({ problem: publicProblem }, 201));
  await practice.generateProblem('basic-integrals', 1);
  expect(fetchMock.mock.calls[1][1]?.headers).toHaveProperty('Idempotency-Key', firstKey);
  fetchMock.mockResolvedValueOnce(response({ problem: { ...publicProblem, id: 'two' } }, 201));
  await practice.generateProblem('basic-integrals', 1);
  expect((fetchMock.mock.calls[2][1]?.headers as Record<string, string>)['Idempotency-Key']).not.toBe(firstKey);
  expect((await practice.getProblem('two')).id).toBe('two');
});

it('deduplicates attempts and retains their key on retry with a refreshed access token', async () => {
  const problem = await savedProblem();
  let fail!: (reason: Error) => void;
  fetchMock.mockImplementationOnce(() => new Promise((_resolve, reject) => { fail = reject; }));
  const one = practice.submitAttempt(problem.id, 'x+C');
  const two = practice.submitAttempt(problem.id, 'x+C');
  expect(one).toBe(two);
  await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  fail(new Error('lost response'));
  await expect(one).rejects.toThrow();
  const headers = fetchMock.mock.calls[1][1]?.headers as Record<string, string>;
  practice.configurePracticeAuth(async () => 'refreshed-token');
  fetchMock.mockResolvedValueOnce(response({ attempt: { result: 'correct', feedbackCode: null } }, 201));
  expect(await practice.submitAttempt(problem.id, 'x+C')).toBe('correct');
  expect(fetchMock.mock.calls[2][1]?.headers).toMatchObject({ 'Idempotency-Key': headers['Idempotency-Key'], Authorization: 'Bearer refreshed-token' });
});

it('loads supported topic cells from the API, including future higher levels', async () => {
  practice.configurePracticeAuth(async () => 'access-token');
  fetchMock.mockResolvedValueOnce(response({ items: [{ slug: 'basic-integrals', name: 'Basic integrals', availableDifficulties: [1, 2, 3, 4, 5] }] }));
  expect((await practice.getTopics())[0].availableDifficulties).toEqual([1, 2, 3, 4, 5]);
  expect(fetchMock.mock.calls[0][0]).toBe('/api/topics');
  expect(fetchMock.mock.calls[0][1]?.method).toBe('GET');
  fetchMock.mockResolvedValueOnce(response({ problem: { ...publicProblem, difficulty: 5 } }, 201));
  expect((await practice.generateProblem('basic-integrals', 5)).difficulty).toBe(5);
});

it('does not fall back to preview when the account token cannot be obtained', async () => {
  practice.configurePracticeAuth(async () => { throw new Error('Please sign in again.'); });
  await expect(practice.generateProblem('basic-integrals', 1)).rejects.toThrow('sign in again');
  expect(fetchMock).not.toHaveBeenCalled();
});

it('honors Retry-After and keeps rate-limit, authentication and server errors out of verdict state', async () => {
  const problem = await savedProblem();
  const clock = vi.spyOn(Date, 'now').mockReturnValue(1000);
  try {
    fetchMock.mockResolvedValueOnce(new Response('{}', { status: 429, headers: { 'Retry-After': '3' } }));
    await expect(practice.submitAttempt(problem.id, 'x')).rejects.toThrow('Wait');
    await expect(practice.submitAttempt(problem.id, 'x')).rejects.toThrow('wait');
    expect(fetchMock).toHaveBeenCalledTimes(2);
    clock.mockReturnValue(4000);
    fetchMock.mockResolvedValueOnce(response({ error: { message: 'PRIVATE exception' } }, 503));
    await expect(practice.submitAttempt(problem.id, 'x')).rejects.toThrow('Try again');
    fetchMock.mockResolvedValueOnce(response({}, 401));
    await expect(practice.submitAttempt(problem.id, 'x')).rejects.toThrow('sign in again');
    expect((await practice.getProblem(problem.id)).lastResult).toBeNull();
  } finally { clock.mockRestore(); }
});

it('drops saved responses and credentials that finish after an identity change', async () => {
  const problem = await savedProblem();
  let finish!: (value: Response) => void;
  fetchMock.mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  const pending = practice.submitAttempt(problem.id, 'x');
  await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  practice.resetPractice();
  finish(response({ attempt: { result: 'correct', feedbackCode: null } }));
  await expect(pending).rejects.toThrow('expired');
  practice.configurePracticeAuth(async () => null);
  expect(await practice.listProblems()).toEqual([]);
  let credential!: (value: string) => void;
  practice.configurePracticeAuth(() => new Promise(resolve => { credential = resolve; }));
  const next = practice.generateProblem('basic-integrals', 1);
  practice.resetPractice();
  credential('old-account-token');
  await expect(next).rejects.toThrow('expired');
  expect(fetchMock).toHaveBeenCalledTimes(2);
});

const storedProblem = { ...publicProblem, answerRevealed: false, solutionRevealed: false, attemptCount: 2,
  lastAttempt: { answer: 'x^2/2', result: 'incorrect', feedbackCode: 'missing_constant' } };

it('reads paginated persisted history and keeps reveal payloads out of shared problem state', async () => {
  practice.configurePracticeAuth(async () => 'access-token');
  fetchMock.mockResolvedValueOnce(response({ items: [{ ...storedProblem, answer: 'PRIVATE', solution: 'PRIVATE', generator: 'PRIVATE' }], nextCursor: 'next-page' }));
  const page = await practice.listProblemPage({ limit: 1 });
  expect(page.nextCursor).toBe('next-page');
  expect(page.items[0]).toMatchObject({ attemptCount: 2, lastResult: 'missing_constant', lastAnswer: 'x^2/2' });
  expect(JSON.stringify(page)).not.toContain('PRIVATE');
  fetchMock.mockResolvedValueOnce(response({ items: [], nextCursor: null }));
  await practice.listProblemPage({ limit: 1, cursor: page.nextCursor });
  expect(fetchMock.mock.calls[1][0]).toBe('/api/problems?limit=1&cursor=next-page');
});

it('reopens persisted state after a reload with previously authorized reveals and no POST', async () => {
  practice.configurePracticeAuth(async () => 'access-token');
  fetchMock.mockResolvedValueOnce(response({ problem: { ...storedProblem, answerRevealed: true, solutionRevealed: true },
    answer: { answerLatex: 'x^2/2+C', generator: 'PRIVATE' }, solution: { steps: [{ say: 'Integrate.', latex: 'x^2/2+C' }] } }));
  const opened = await practice.openProblem(publicProblem.id);
  expect(opened.answer).toEqual({ answerLatex: 'x^2/2+C' });
  expect(opened.solution?.steps).toHaveLength(1);
  expect(opened.problem.lastResult).toBe('missing_constant');
  expect(fetchMock.mock.calls[0][1]?.method).toBe('GET');
  expect(JSON.stringify(await practice.getProblem(publicProblem.id))).not.toMatch(/answerLatex|steps|PRIVATE/);
});

it('ignores unsolicited reveals on an unrevealed problem and takes profile counts from the server', async () => {
  practice.configurePracticeAuth(async () => 'access-token');
  fetchMock.mockResolvedValueOnce(response({ problem: storedProblem, answer: { answerLatex: 'PRIVATE' }, solution: { steps: [] } }));
  const opened = await practice.openProblem(publicProblem.id);
  expect(opened.answer).toBeUndefined();
  expect(opened.solution).toBeUndefined();
  fetchMock.mockResolvedValueOnce(response({ counts: { generated: 100, attempted: 70, correct: 40 } }));
  expect(await practice.getProfileCounts()).toEqual({ generated: 100, attempted: 70, correct: 40 });
  expect(fetchMock.mock.calls[1][0]).toBe('/api/profile');
});

it('rejects a looping page cursor, duplicate page IDs and inconsistent profile counts', async () => {
  practice.configurePracticeAuth(async () => 'access-token');
  fetchMock.mockResolvedValueOnce(response({ items: [storedProblem], nextCursor: 'loop' }));
  await expect(practice.listProblemPage({ cursor: 'loop' })).rejects.toThrow();
  fetchMock.mockResolvedValueOnce(response({ items: [storedProblem, storedProblem], nextCursor: null }));
  await expect(practice.listProblemPage()).rejects.toThrow();
  fetchMock.mockResolvedValueOnce(response({ counts: { generated: 1, attempted: 0, correct: 1 } }));
  await expect(practice.getProfileCounts()).rejects.toThrow();
});

it('discards a read that finishes after switching accounts and never caches its problem', async () => {
  practice.configurePracticeAuth(async () => 'old-token');
  let finish!: (value: Response) => void;
  fetchMock.mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  const pending = practice.listProblemPage();
  await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  practice.resetPractice();
  practice.configurePracticeAuth(async () => null);
  finish(response({ items: [storedProblem], nextCursor: null }));
  await expect(pending).rejects.toThrow('expired');
  expect(await practice.listProblems()).toEqual([]);
});
