import { beforeEach, afterEach, expect, it, vi } from 'vitest';
import * as practice from './practice';

const fetchMock = vi.fn<typeof fetch>();
const publicProblem = { id: 'problem-1', topic: 'basic-integrals', difficulty: 1, problemLatex: '\\int x\\,dx', createdAt: '2026-10-19T00:00:00Z' };
const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
beforeEach(() => { practice.resetPractice(); fetchMock.mockReset(); vi.stubGlobal('fetch', fetchMock); });
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
