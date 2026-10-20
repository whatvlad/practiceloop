// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { DashboardPage } from './DashboardPage';
import { PracticePage } from './PracticePage';
import { configurePracticeAuth, getProblem, resetPractice } from '../data/practice';
import type { PublicProblem } from '../data/types';

// Keep the real answer input, syntax preview and keyboard handlers; only skip
// the dynamically loaded native math editor, which needs an actual browser.
vi.mock('../components/FormulaField', () => ({ useMathLive: () => null, usesPhoneKeyboard: () => false }));

let root: Root;
let element: HTMLDivElement;
let nextId: number;
const saved = new Map<string, PublicProblem>();
const calls: { path: string; body: Record<string, unknown> | null }[] = [];
const fetchMock = vi.fn<typeof fetch>();
const SHARE_TOKEN = 'S'.repeat(43);
const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const button = (label: string) => Array.from(element.querySelectorAll('button')).find(b => b.textContent?.includes(label))!;

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  resetPractice();
  configurePracticeAuth(async () => 'test-supabase-token');
  nextId = 0;
  saved.clear();
  calls.length = 0;
  fetchMock.mockReset().mockImplementation(async (url, options) => {
    const path = String(url);
    const body = options?.body ? JSON.parse(String(options.body)) as Record<string, unknown> : null;
    calls.push({ path, body });
    expect(options?.headers).toHaveProperty('Authorization', 'Bearer test-supabase-token');
    if (path.endsWith('/topics')) return response({ items: [
      { slug: 'basic-integrals', name: 'Basic integrals', availableDifficulties: [1, 2] },
      { slug: 'substitution', name: 'Substitution', availableDifficulties: [1] },
    ] });
    const dto = (problem: PublicProblem) => ({ ...problem, attemptCount: problem.attemptCount ?? 0,
      lastAttempt: problem.lastAnswer === null ? null : { answer: problem.lastAnswer,
        result: problem.lastResult, feedbackCode: null } });
    if (path === '/api/profile') return response({ counts: { generated: saved.size, attempted: 0, correct: 0 } });
    if (path.startsWith('/api/problems?')) return response({ items: [...saved.values()].map(dto), nextCursor: null });
    if (options?.method === 'GET' && path.startsWith('/api/problems/')) {
      const problem = saved.get(path.split('/').at(-1)!)!;
      return response({ problem: dto(problem), ...(problem.answerRevealed ? { answer: { answerLatex: 'x^2/2+C' } } : {}),
        ...(problem.solutionRevealed ? { solution: { steps: [{ say: 'Previously revealed step.', latex: 'x^2/2+C' }] } } : {}) });
    }
    if (path.endsWith('/share')) return response({ share: { token: SHARE_TOKEN, code: 'K7M2QX9P', expiresAt: '2027-01-18T12:00:00Z' } }, 201);
    if (path.endsWith('/share/revoke')) return response({ share: null });
    if (path.endsWith('/attempts')) return response({ attempt: { result: body?.answer === 'x^2/2+C' ? 'correct' : 'invalid', feedbackCode: null } }, 201);
    if (path.endsWith('/reveal-answer')) return response({ answerLatex: 'x^2/2+C' });
    if (path.endsWith('/reveal-solution')) return response({ steps: [{ say: 'Apply the power rule.', latex: 'x^2/2+C' }] });
    if (path === '/api/problems') {
      const problem = { id: `problem-${++nextId}`, ...body, problemLatex: '\\int x\\,dx',
        createdAt: '2026-10-19T00:00:00Z', answerRevealed: false, solutionRevealed: false,
        lastResult: null, lastAnswer: null } as PublicProblem;
      saved.set(problem.id, problem);
      return response({ problem: { ...problem, lastAttempt: null } }, 201);
    }
    throw new Error('Unexpected route');
  });
  vi.stubGlobal('fetch', fetchMock);
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
  window.history.replaceState(null, '', '/dashboard');
  element = document.createElement('div');
  document.body.append(element);
  root = createRoot(element);
});

afterEach(async () => {
  await act(async () => root.unmount());
  element.remove();
  resetPractice();
  configurePracticeAuth(async () => null);
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

async function typeAnswer(value: string) {
  const input = element.querySelector<HTMLInputElement>('#answer')!;
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, value);
    input.dispatchEvent(new Event('input', { bubbles: true }));
  });
}

it('runs selection → saved generation → invalid/correct check → explicit reveals → next through the real data boundary', async () => {
  await act(async () => root.render(<DashboardPage />));
  // Levels the topic lacks are hidden, not disabled: basic integrals has 1-2 here.
  expect(button('Advanced')).toBeUndefined();
  expect(button('Integration by parts').disabled).toBe(true);
  expect(element.querySelectorAll('.pl-seg button')).toHaveLength(2);
  await act(async () => { button('Generate problem').click(); button('Generate problem').click(); });
  expect(calls.filter(call => call.path === '/api/problems')).toHaveLength(1);
  const id = new URLSearchParams(window.location.search).get('id')!;
  await act(async () => root.render(<PracticePage key={id} id={id} />));
  expect(element.textContent).toContain('Saved to your account');
  expect(element.querySelector('.katex-mathml')).not.toBeNull();
  expect(calls.some(call => call.path.includes('reveal-'))).toBe(false);
  await typeAnswer('sin(');
  await act(async () => button('Check answer').click());
  expect(element.textContent).toContain('Check your brackets');
  await typeAnswer('x^2/2+C');
  await act(async () => element.querySelector('#answer')!.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })));
  expect(element.textContent).toContain('mathematically equivalent');
  expect(button('Check answer').disabled).toBe(true);
  await act(async () => button('Show answer').click());
  await act(async () => button('Show solution').click());
  expect(element.textContent).toContain('Apply the power rule');
  expect(await getProblem(id)).toMatchObject({ answerRevealed: true, solutionRevealed: true });
  await act(async () => button('Generate next problem').click());
  const next = new URLSearchParams(window.location.search).get('id')!;
  expect(next).not.toBe(id);
  await act(async () => root.render(<PracticePage key={next} id={next} />));
  expect(element.querySelector<HTMLInputElement>('#answer')!.value).toBe('');
  expect(element.textContent).not.toContain('Apply the power rule');
});

it('uses topic-specific availability and retries a failed catalogue without generating a problem', async () => {
  fetchMock.mockResolvedValueOnce(response({}, 503));
  await act(async () => root.render(<DashboardPage />));
  expect(button('Generate problem').disabled).toBe(true);
  expect(element.querySelector('[role="alert"]')).not.toBeNull();
  await act(async () => button('Retry loading topics').click());
  expect(button('Generate problem').disabled).toBe(false);
  await act(async () => button('Easy').click());
  await act(async () => button('Substitution').click());
  // Substitution has only level 1 here: level 2 is hidden and the choice moves to 1.
  expect(button('Easy')).toBeUndefined();
  expect(button('1Basic').getAttribute('aria-pressed')).toBe('true');
  expect(button('Generate problem').disabled).toBe(false);
  expect(element.textContent).not.toContain('Choose an available option');
  await act(async () => button('Generate problem').click());
  expect(calls.find(call => call.path === '/api/problems')?.body).toEqual({ topic: 'substitution', difficulty: 1 });
});

it('discards a check verdict after the answer changes while the request is pending', async () => {
  await act(async () => root.render(<DashboardPage />));
  await act(async () => button('Generate problem').click());
  await act(async () => root.render(<PracticePage id="problem-1" />));
  await typeAnswer('x^2/2+C');
  let finish!: (value: Response) => void;
  fetchMock.mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  await act(async () => button('Check answer').click());
  await typeAnswer('x');
  await act(async () => finish(response({ attempt: { result: 'correct', feedbackCode: null } })));
  expect(element.textContent).not.toContain('mathematically equivalent');
  expect(button('Check answer').disabled).toBe(false);
});

it('restores an old problem after clearing browser practice state without making reveal writes', async () => {
  saved.set('old', { id: 'old', topic: 'basic-integrals', difficulty: 2, problemLatex: '\\int x\\,dx',
    createdAt: '2026-10-19T00:00:00Z', lastAnswer: 'x^2/2+C', lastResult: 'correct', attemptCount: 2,
    answerRevealed: true, solutionRevealed: true });
  resetPractice();
  await act(async () => root.render(<PracticePage id="old" />));
  expect(element.querySelector<HTMLInputElement>('#answer')!.value).toBe('x^2/2+C');
  expect(element.textContent).toContain('Previously revealed step');
  expect(element.textContent).toContain('mathematically equivalent');
  expect(calls).toHaveLength(1);
  expect(calls[0]).toEqual({ path: '/api/problems/old', body: null });
});

it('shares a saved problem by link and code and stops sharing it (#37)', async () => {
  await act(async () => root.render(<DashboardPage />));
  await act(async () => button('Generate problem').click());
  await act(async () => root.render(<PracticePage id="problem-1" />));
  expect(element.textContent).toContain('Your answers, results and solutions stay private');
  await act(async () => button('Share problem').click());
  expect(calls.at(-1)?.path).toBe('/api/problems/problem-1/share');
  expect(element.querySelector<HTMLInputElement>('.pl-share-link')!.value).toBe(`${window.location.origin}/s/${SHARE_TOKEN}`);
  expect(element.textContent).toContain('K7M2-QX9P');
  expect(element.textContent).toContain('18 Jan 2027');
  await act(async () => button('Stop sharing').click());
  expect(calls.at(-1)?.path).toBe('/api/problems/problem-1/share/revoke');
  expect(element.querySelector('.pl-share-link')).toBeNull();
  expect(button('Share problem')).toBeDefined();
});
