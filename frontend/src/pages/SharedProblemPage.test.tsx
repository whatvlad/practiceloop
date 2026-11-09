// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { SharedProblemPage } from './SharedProblemPage';
import { lookupShare, normalizeCode, shareCode, shareLink } from '../data/shares';
import { practiceCodeProblem, practiceSharedProblem } from '../data/api';
import { normalizeProblemCode } from '../data/problemCodes';

vi.mock('../data/api', () => ({ practiceSharedProblem: vi.fn(), practiceCodeProblem: vi.fn() }));

const TOKEN = 'A'.repeat(21) + '_' + 'b'.repeat(20) + '-';
const fetchMock = vi.fn<typeof fetch>();
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const failure = (code: string, status: number) => json({ error: { code, message: 'Server text', retryable: false } }, status);
let root: Root;
let element: HTMLDivElement;

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  fetchMock.mockReset();
  vi.mocked(practiceSharedProblem).mockReset();
  vi.mocked(practiceCodeProblem).mockReset();
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
  vi.stubGlobal('fetch', fetchMock);
  element = document.createElement('div');
  document.body.append(element);
  root = createRoot(element);
});

afterEach(async () => {
  await act(async () => root.unmount());
  element.remove();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

async function render(props: { token: string | null; code: string | null; problemCode?: string; signedIn?: boolean; authLoading?: boolean; inactive?: boolean }) {
  await act(async () => root.render(<SharedProblemPage {...props} />));
  await act(async () => {});
}

const PROBLEM_CODE = 'CMB-1-0000000000000000-32';

it('shows shared problems without offering a practice session when inactive', async () => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'combinations', difficulty: 1, problemLatex: '1' } }));
  await render({ token: null, code: null, problemCode: PROBLEM_CODE, signedIn: true, inactive: true });
  expect(element.textContent).toContain('Coming soon');
  expect(element.textContent).not.toContain('Solve this problem');
  expect(practiceCodeProblem).not.toHaveBeenCalled();
});

it('opens a permanent code anonymously and keeps its private fields out of the page', async () => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'combinations', difficulty: 1, problemLatex: '\\binom{5}{2}', answerLatex: 'PRIVATE', steps: ['PRIVATE'] } }));
  await render({ token: null, code: null, problemCode: PROBLEM_CODE.toLowerCase() });
  expect(fetchMock.mock.calls[0][0]).toBe(`/api/codes?code=${PROBLEM_CODE}`);
  expect(element.textContent).toContain('Problem from code');
  expect(element.innerHTML).not.toContain('PRIVATE');
  const next = new URL([...element.querySelectorAll('a')].find(a => a.textContent?.includes('Sign in to solve'))!.href).searchParams.get('next');
  expect(next).toBe(`/p/${PROBLEM_CODE.toLowerCase()}`);
});

it('saves the exact permanent code once and navigates to normal practice', async () => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'combinations', difficulty: 1, problemLatex: '1' } }));
  vi.mocked(practiceCodeProblem).mockResolvedValue({ id: 'code-copy' } as Awaited<ReturnType<typeof practiceCodeProblem>>);
  await render({ token: null, code: null, problemCode: PROBLEM_CODE, signedIn: true });
  const button = [...element.querySelectorAll('button')].find(b => b.textContent?.includes('Solve this problem'))!;
  await act(async () => { button.click(); button.click(); });
  expect(practiceCodeProblem).toHaveBeenCalledExactlyOnceWith(PROBLEM_CODE);
  expect(practiceSharedProblem).not.toHaveBeenCalled();
  expect(window.location.pathname + window.location.search).toBe('/practice?id=code-copy');
});

it('shows a clear invalid-code message and a problem-code form', async () => {
  fetchMock.mockResolvedValue(failure('problem_code_invalid', 400));
  await render({ token: null, code: null, problemCode: PROBLEM_CODE });
  expect(element.querySelector('h1')?.textContent).toContain('not valid or is unknown');
  expect(element.textContent).toContain('Problem code');
  expect(element.querySelector('.katex')).toBeNull();
});

it('normalizes case, whitespace and dashes without accepting URL fragments or non-ASCII', () => {
  expect(normalizeProblemCode(PROBLEM_CODE.toLowerCase().replaceAll('-', ' '))).toBe(PROBLEM_CODE);
  expect(normalizeProblemCode(PROBLEM_CODE.replaceAll('-', ''))).toBe(PROBLEM_CODE);
  expect(normalizeProblemCode('https://example.com')).toBeNull();
  expect(normalizeProblemCode('\u03c0')).toBeNull();
});

it('shows only the statement, topic and difficulty, even when the server sends more', async () => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'substitution', difficulty: 3, problemLatex: '\\int 2x\\cos(x^2)\\,dx',
    answerLatex: 'LEAKED-ANSWER', lastAttempt: { answer: 'LEAKED-ATTEMPT' }, id: 'LEAKED-ID' } }));
  await render({ token: TOKEN, code: null });
  const [url, options] = fetchMock.mock.calls[0];
  expect(String(url)).toBe(`/api/shares/${TOKEN}`);
  expect(options?.headers).not.toHaveProperty('Authorization');
  expect(options?.credentials).toBe('omit');
  expect(element.textContent).toContain('Integration — Substitution');
  expect(element.textContent).toContain('3/5');
  expect(element.querySelector('.katex')).not.toBeNull();
  expect(element.innerHTML).not.toMatch(/LEAKED/);
  expect(element.textContent).not.toMatch(/Show answer|Check answer/);
});

it('shows a numeric instruction for a shared combinations problem', async () => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'combinations', difficulty: 1, problemLatex: '\\binom{5}{2}' } }));
  await render({ token: TOKEN, code: null });
  expect(element.textContent).toContain('Calculate the value.');
  expect(element.textContent).not.toContain('Calculate the indefinite integral.');
});

it('places a shared radical instruction above its formula', async () => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'algebraic-expressions', difficulty: 1,
    problemLatex: '\\text{Simplify }2\\sqrt{3}-\\sqrt{27}\\text{.}' } }));
  await render({ token: TOKEN, code: null });
  expect(element.querySelector('.pl-lead')?.textContent).toContain('Simplify');
  expect(element.querySelector('.pl-expr')?.textContent).not.toContain('Simplify');
  expect(element.querySelector('.pl-expr .katex')).not.toBeNull();
});

it.each([{ token: TOKEN, code: null }, { token: null, code: 'k7m2-qx9p' }])('keeps the exact shared reference in the sign-in action', async props => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'basic-integrals', difficulty: 4, problemLatex: '\\int (x+2)^2\\,dx' } }));
  await render(props);
  const link = [...element.querySelectorAll('a')].find(a => a.textContent?.includes('Sign in to solve'))!;
  const next = new URL(link.href).searchParams.get('next');
  expect(next).toBe(props.token ? `/s/${TOKEN}` : '/shared?code=k7m2-qx9p');
  expect(practiceSharedProblem).not.toHaveBeenCalled();
});

it('opens the recipient copy once on duplicate clicks and never generates an unrelated problem', async () => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'partial-derivatives', difficulty: 5, problemLatex: 'f(x,y)=xy' } }));
  let finish!: (problem: Awaited<ReturnType<typeof practiceSharedProblem>>) => void;
  vi.mocked(practiceSharedProblem).mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  await render({ token: TOKEN, code: null, signedIn: true });
  const button = [...element.querySelectorAll('button')].find(b => b.textContent?.includes('Solve this problem'))!;
  await act(async () => { button.click(); button.click(); });
  expect(practiceSharedProblem).toHaveBeenCalledExactlyOnceWith({ token: TOKEN });
  expect(button.disabled).toBe(true);
  await act(async () => finish({ id: 'recipient-copy' } as Awaited<ReturnType<typeof practiceSharedProblem>>));
  expect(window.location.pathname + window.location.search).toBe('/practice?id=recipient-copy');
});

it('keeps the shared statement and offers a retry when copying fails', async () => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'basic-integrals', difficulty: 4, problemLatex: '\\int (x+2)^2\\,dx' } }));
  vi.mocked(practiceSharedProblem).mockRejectedValueOnce(new Error('This problem is no longer shared. Ask for a new link.'));
  await render({ token: null, code: 'K7M2QX9P', signedIn: true });
  const button = [...element.querySelectorAll('button')].find(b => b.textContent?.includes('Solve this problem'))!;
  await act(async () => button.click());
  expect(element.querySelector('[role="alert"]')?.textContent).toContain('no longer shared');
  expect(button.disabled).toBe(false);
  expect(element.querySelector('.katex')).not.toBeNull();
});

it('does not navigate on a late response after leaving the shared page', async () => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'basic-integrals', difficulty: 1, problemLatex: 'x' } }));
  let finish!: (problem: Awaited<ReturnType<typeof practiceSharedProblem>>) => void;
  vi.mocked(practiceSharedProblem).mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  await render({ token: TOKEN, code: null, signedIn: true });
  await act(async () => [...element.querySelectorAll('button')].find(b => b.textContent?.includes('Solve this problem'))!.click());
  await act(async () => root.render(<div>Another page</div>));
  window.history.replaceState(null, '', '/history');
  await act(async () => finish({ id: 'late-copy' } as Awaited<ReturnType<typeof practiceSharedProblem>>));
  expect(window.location.pathname).toBe('/history');
});

it.each([
  ['share_not_found', 404, 'Nothing is shared under this link or code.'],
  ['share_expired', 410, 'This shared problem has expired.'],
  ['share_revoked', 410, 'This problem is no longer shared.'],
  ['share_invalid', 400, 'That link or code is not valid.'],
])('turns %s into its own safe state', async (code, status, title) => {
  fetchMock.mockResolvedValue(failure(code, status));
  await render({ token: null, code: 'k7m2-qx9p' });
  expect(String(fetchMock.mock.calls[0][0])).toBe('/api/shares/code/K7M2QX9P');
  expect(element.querySelector('h1')?.textContent).toBe(title);
  expect(element.textContent).not.toContain('Server text');
});

it('rejects a malformed link or code without asking the server', async () => {
  await render({ token: 'short', code: null });
  expect(element.querySelector('h1')?.textContent).toBe('That link or code is not valid.');
  await render({ token: null, code: 'nope' });
  expect(element.querySelector('h1')?.textContent).toBe('That link or code is not valid.');
  expect(fetchMock).not.toHaveBeenCalled();
});

it('offers a code form when opened without one', async () => {
  await render({ token: null, code: null });
  expect(element.querySelector('h1')?.textContent).toBe('Open a shared problem');
  expect(element.querySelector('form input')).not.toBeNull();
  expect(fetchMock).not.toHaveBeenCalled();
});

it('says when lookups are busy and never treats an unknown error as a share state', async () => {
  fetchMock.mockResolvedValueOnce(failure('rate_limited', 429));
  await expect(lookupShare({ token: TOKEN })).rejects.toThrow(/Try again in a minute/);
  fetchMock.mockResolvedValueOnce(failure('constructor', 404));
  await expect(lookupShare({ token: TOKEN })).rejects.toThrow();
});

it('formats and normalizes codes like the API', () => {
  expect(shareCode('K7M2QX9P')).toBe('K7M2-QX9P');
  expect(normalizeCode(' o1il-0000 ')).toBe('01110000');
  expect(normalizeCode('K7M2QX9U')).toBeNull();
  expect(shareLink({ token: TOKEN, code: 'K7M2QX9P', expiresAt: '2027-01-18T00:00:00Z' }, 'https://example.test'))
    .toBe(`https://example.test/s/${TOKEN}`);
});
