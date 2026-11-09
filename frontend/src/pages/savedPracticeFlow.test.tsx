// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { DashboardPage } from './DashboardPage';
import { PracticePage } from './PracticePage';
import { LocalRandomPractice } from '../components/LocalRandomPractice';
import { matrixOptionsFromSearch } from '../components/MatrixSettings';
import { modulusModeFromSearch } from '../components/ModulusSettings';
import { configurePracticeAuth, generateProblem, getProblem, resetPractice, revealSolution } from '../data/practice';
import type { PublicProblem } from '../data/types';
import type { AnswerInputSpec } from '../data/types';

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
const INTEGRALS = [
  { slug: 'basic-integrals', name: 'Basic integrals', area: 'mathematical-analysis', availableDifficulties: [1, 2] },
  { slug: 'substitution', name: 'Substitution', area: 'mathematical-analysis', availableDifficulties: [1] },
];
let catalogue: unknown;
const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const button = (label: string) => Array.from(element.querySelectorAll('button')).find(b => b.textContent?.includes(label))!;

it('persists and reuses random algebra settings for saved problems', async () => {
  localStorage.removeItem('practiceloop:algebra-random:student');
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'determinants', name: 'Determinants', area: 'algebra', availableDifficulties: [1, 2, 3] },
  ] };
  await act(async () => root.render(<LocalRandomPractice accountId="student" />));
  const topic = [...element.querySelectorAll('label')].find(label => label.textContent?.trim() === 'Determinants')!.querySelector('input')!;
  await act(async () => topic.click());
  const select = (name: string) => [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith(name))!.querySelector('select')!;
  await act(async () => { select('Difficulty').value = '2'; select('Difficulty').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => { select('Matrix size').value = '4'; select('Matrix size').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => button('Generate problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'determinants', difficulty: 2, squareSize: 4 });
  const params = new URLSearchParams(window.location.search);
  expect(params.get('mode')).toBe('algebra-random');
  await act(async () => root.render(<PracticePage id={params.get('id')} algebraRandomAccountId="student" />));
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'determinants', difficulty: 2, squareSize: 4 });
  localStorage.removeItem('practiceloop:algebra-random:student');
});

it('generates and continues polar powers without a difficulty selector', async () => {
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'complex-polar-form', name: 'Polar form', area: 'algebra', availableDifficulties: [1, 2, 3] },
  ] };
  await act(async () => root.render(<DashboardPage initialArea="algebra" initialTopic="complex-polar-form" />));
  const select = [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith('Exercise type'))!.querySelector('select')!;
  await act(async () => { select.value = 'power'; select.dispatchEvent(new Event('change', { bubbles: true })); });
  expect(element.textContent).not.toContain('Difficulty');
  await act(async () => button('Generate problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'complex-polar-form', difficulty: 2, exerciseMode: 'power' });
  await act(async () => root.render(<PracticePage id={new URLSearchParams(window.location.search).get('id')} />));
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'complex-polar-form', exerciseMode: 'power' });
});

it('uses local polynomial root exercises', async () => {
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'polynomial-roots', name: 'Roots and factors', area: 'algebra', availableDifficulties: [1, 2, 3] },
  ] };
  await act(async () => root.render(<DashboardPage initialArea="algebra" initialTopic="polynomial-roots" />));
  await act(async () => button('Generate problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'polynomial-roots', exerciseMode: 'roots' });
});

it('preserves complex conversion direction for the next saved problem', async () => {
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'complex-conversion', name: 'Converting complex forms', area: 'algebra', availableDifficulties: [1, 2, 3] },
  ] };
  await act(async () => root.render(<DashboardPage initialArea="algebra" initialTopic="complex-conversion" />));
  const select = [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith('Exercise type'))!.querySelector('select')!;
  await act(async () => { select.value = 'exp-alg'; select.dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => button('Generate problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'complex-conversion', exerciseMode: 'exp-alg' });
  await act(async () => root.render(<PracticePage id={new URLSearchParams(window.location.search).get('id')} />));
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'complex-conversion', exerciseMode: 'exp-alg' });
});

it('preserves complex exercise mode for the next saved problem', async () => {
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'complex-arithmetic', name: 'Complex arithmetic', area: 'algebra', availableDifficulties: [1, 2, 3] },
  ] };
  await act(async () => root.render(<DashboardPage initialArea="algebra" initialTopic="complex-arithmetic" />));
  const select = [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith('Exercise type'))!.querySelector('select')!;
  await act(async () => { select.value = 'divide'; select.dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => button('Generate problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'complex-arithmetic', exerciseMode: 'divide' });
  await act(async () => root.render(<PracticePage id={new URLSearchParams(window.location.search).get('id')} />));
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'complex-arithmetic', exerciseMode: 'divide' });
});

it('preserves determinant size for the next saved problem', async () => {
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'determinants', name: 'Determinants', area: 'algebra', availableDifficulties: [1, 2, 3] },
  ] };
  await act(async () => root.render(<DashboardPage initialArea="algebra" initialTopic="determinants" />));
  const select = [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith('Matrix size'))!.querySelector('select')!;
  await act(async () => { select.value = '4'; select.dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => button('Generate problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'determinants', squareSize: 4 });
  await act(async () => root.render(<PracticePage id={new URLSearchParams(window.location.search).get('id')} />));
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'determinants', squareSize: 4 });
});

it('generates and continues a custom matrix exercise', async () => {
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'matrix-operations', name: 'Matrix operations', area: 'algebra', availableDifficulties: [1, 2, 3] },
  ] };
  await act(async () => root.render(<DashboardPage initialArea="algebra" initialTopic="matrix-operations" />));
  await act(async () => element.querySelector<HTMLInputElement>('input[type="checkbox"]')!.click());
  const select = (name: string) => [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith(name))!.querySelector('select')!;
  await act(async () => { select('Operation').value = 'multiply'; select('Operation').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => { select('Columns of A').value = '3'; select('Columns of A').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => { select('Rows of B').value = '3'; select('Rows of B').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => { select('Columns of B').value = '4'; select('Columns of B').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => button('Generate problem').click());
  const dimensions = { operation: 'multiply', rowsA: 2, colsA: 3, rowsB: 3, colsB: 4 };
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ matrixDimensions: dimensions });
  await act(async () => root.render(<PracticePage id={new URLSearchParams(window.location.search).get('id')} />));
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ matrixDimensions: dimensions });
});

it('preserves rank dimensions when generating the next saved problem', async () => {
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'matrix-rank', name: 'Matrix rank', area: 'algebra', availableDifficulties: [1, 2, 3] },
  ] };
  await act(async () => root.render(<DashboardPage initialArea="algebra" initialTopic="matrix-rank" />));
  const select = (name: string) => [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith(name))!.querySelector('select')!;
  await act(async () => { select('Rows').value = '3'; select('Rows').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => { select('Columns').value = '5'; select('Columns').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => button('Generate problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'matrix-rank', rankDimensions: { rows: 3, columns: 5 } });
  await act(async () => root.render(<PracticePage id={new URLSearchParams(window.location.search).get('id')} />));
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'matrix-rank', rankDimensions: { rows: 3, columns: 5 } });
});

it('retains formula explanations provided with a revealed solution', async () => {
  const original = fetchMock.getMockImplementation()!;
  fetchMock.mockImplementation((url, options) => String(url).endsWith('/reveal-solution')
    ? Promise.resolve(response({ steps: [{ say: 'Use the distance formula.', latex: '|z|', rules: [
      { title: 'Modulus as distance', latex: '|z-z_0|=r', explanation: 'The locus is a circle.' },
    ] }] })) : original(url, options));
  const problem = await generateProblem('basic-integrals', 1);
  const solution = await revealSolution(problem.id);
  expect(solution.steps[0].rules?.[0].title).toBe('Modulus as distance');
});

it('retains determinant diagram data from the solution', async () => {
  const original = fetchMock.getMockImplementation()!;
  fetchMock.mockImplementation((url, options) => String(url).endsWith('/reveal-solution')
    ? Promise.resolve(response({ steps: [{ say: 'Expand.', latex: '1', determinantMatrix: [[1, 2], [3, 4]] }] })) : original(url, options));
  const problem = await generateProblem('basic-integrals', 1);
  expect((await revealSolution(problem.id)).steps[0].determinantMatrix).toEqual([[1, 2], [3, 4]]);
});

it('accepts detailed solutions for a five by five determinant', async () => {
  const original = fetchMock.getMockImplementation()!;
  fetchMock.mockImplementation((url, options) => String(url).endsWith('/reveal-solution')
    ? Promise.resolve(response({ steps: Array.from({ length: 44 }, (_, i) => ({ say: `Step ${i + 1}`, latex: '1' })) })) : original(url, options));
  const problem = await generateProblem('basic-integrals', 1);
  expect((await revealSolution(problem.id)).steps).toHaveLength(44);
});

it('generates and continues the chosen modulus exercise', async () => {
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'complex-numbers', name: 'Complex numbers', area: 'algebra', availableDifficulties: [1, 2, 3, 4, 5] },
  ] };
  await act(async () => root.render(<DashboardPage initialArea="algebra" initialTopic="complex-numbers" />));
  const select = [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith('Exercise type'))!.querySelector('select')!;
  await act(async () => { select.value = 'geometry'; select.dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => button('Generate problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'complex-numbers', difficulty: 1, modulusMode: 'geometry' });
  const params = new URLSearchParams(window.location.search);
  expect(modulusModeFromSearch(params)).toBe('geometry');
  // Opening from history has no settings in the URL; the server retains them.
  await act(async () => root.render(<PracticePage id={params.get('id')} />));
  expect(element.querySelector('[aria-label="Difficulty 1 of 3"]')).not.toBeNull();
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'complex-numbers', difficulty: 1, modulusMode: 'geometry' });
  expect(modulusModeFromSearch(new URLSearchParams(window.location.search))).toBe('geometry');
});

it('generates and continues matrix practice with the chosen operation and size', async () => {
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'matrix-operations', name: 'Matrix operations', area: 'algebra', availableDifficulties: [1, 2, 3] },
  ] };
  await act(async () => root.render(<DashboardPage initialArea="algebra" initialTopic="matrix-operations" />));
  const select = (name: string) => [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith(name))!.querySelector('select')!;
  await act(async () => { select('Operation').value = 'multiply'; select('Operation').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => { select('Matrix size').value = '3x3'; select('Matrix size').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => button('Generate problem').click());
  const options = { operation: 'multiply', size: '3x3' };
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'matrix-operations', difficulty: 1, matrixOptions: options });
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id')!;
  expect(matrixOptionsFromSearch(params)).toEqual(options);
  await act(async () => root.render(<PracticePage id={id} matrixOptions={matrixOptionsFromSearch(params)} />));
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'matrix-operations', difficulty: 1, matrixOptions: options });
  expect(matrixOptionsFromSearch(new URLSearchParams(window.location.search))).toEqual(options);
});

it('generates the next random problem from the saved selection', async () => {
  localStorage.setItem('practiceloop:random-selection:random-test', JSON.stringify({ substitution: 1 }));
  const first = await generateProblem('basic-integrals', 1, 'mathematical-analysis');
  await act(async () => root.render(<PracticePage id={first.id} randomAccountId="random-test" />));
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({ topic: 'substitution', difficulty: 1 });
  expect(window.location.search).toContain('mode=random');
  localStorage.removeItem('practiceloop:random-selection:random-test');
});

it('keeps operation and size for random matrix practice', async () => {
  catalogue = { areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }], items: [
    { slug: 'matrix-operations', name: 'Matrix operations', area: 'algebra', availableDifficulties: [1] },
  ] };
  localStorage.setItem('practiceloop:random-selection:matrix-test', JSON.stringify({ 'matrix-operations': 1 }));
  localStorage.setItem('practiceloop:random-matrix:matrix-test', JSON.stringify({ operation: 'multiply', size: '3x3' }));
  const first = await generateProblem('matrix-operations', 1, 'algebra');
  await act(async () => root.render(<PracticePage id={first.id} randomAccountId="matrix-test" />));
  await act(async () => button('Generate next problem').click());
  expect(calls.filter(call => call.path === '/api/problems').at(-1)?.body).toMatchObject({
    topic: 'matrix-operations', difficulty: 1, matrixOptions: { operation: 'multiply', size: '3x3' },
  });
  localStorage.removeItem('practiceloop:random-selection:matrix-test');
  localStorage.removeItem('practiceloop:random-matrix:matrix-test');
});

it('restores a probability topic in its own area after generation before catalogue loading', async () => {
  catalogue = { areas: [
    { slug: 'mathematical-analysis', name: 'Mathematical Analysis', mixed: null },
    { slug: 'probability-statistics', name: 'Probability and Statistics', mixed: null },
  ], items: [...INTEGRALS, { slug: 'probability-events', name: 'Events and counting', area: 'probability-statistics', availableDifficulties: [1,2,3,4,5] }] };
  await generateProblem('probability-events', 1, 'probability-statistics');
  await act(async () => root.render(<DashboardPage />));
  expect(element.textContent).toContain('Selected topic: Events and counting');
  expect(button('Generate problem').disabled).toBe(false);
});

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  resetPractice();
  configurePracticeAuth(async () => 'test-supabase-token');
  nextId = 0;
  saved.clear();
  calls.length = 0;
  catalogue = { areas: [{ slug: 'mathematical-analysis', name: 'Mathematical Analysis', mixed: null }], items: INTEGRALS };
  fetchMock.mockReset().mockImplementation(async (url, options) => {
    const path = String(url);
    const body = options?.body ? JSON.parse(String(options.body)) as Record<string, unknown> : null;
    calls.push({ path, body });
    expect(options?.headers).toHaveProperty('Authorization', 'Bearer test-supabase-token');
    if (path.endsWith('/topics')) return response(catalogue);
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

it('starts practice for the topic selected from the curriculum', async () => {
  await act(async () => root.render(<DashboardPage initialArea="mathematical-analysis" initialTopic="substitution" />));
  await act(async () => button('Generate problem').click());
  expect(calls.find(call => call.path === '/api/problems')?.body).toMatchObject({ topic: 'substitution', difficulty: 1 });
});

it('runs selection → saved generation → invalid/correct check → explicit reveals → next through the real data boundary', async () => {
  await act(async () => root.render(<DashboardPage />));
  // Levels the topic lacks are hidden, not disabled: basic integrals has 1-2 here.
  expect(button('Advanced')).toBeUndefined();
  // Topics the catalogue does not offer are not shown, and one area needs no area picker.
  expect(button('Integration by parts')).toBeUndefined();
  expect(element.textContent).not.toContain('Area');
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
  await act(async () => root.render(<DashboardPage key="substitution" initialArea="mathematical-analysis" initialTopic="substitution" />));
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

it.each([
  { kind: 'boolean', topic: 'hypothesis-tests', answer: 'false', selector: 'input[value=false]' },
  { kind: 'finite_set', topic: 'discrete-random-variables', answer: '{-1,2}', selector: '#answer-0' },
  { kind: 'interval', topic: 'confidence-intervals', answer: '(-inf,3/2]', selector: '#answer-1' },
] as const)('reopens a saved $kind answer through the real API decoder', async ({ kind, topic, answer, selector }) => {
  const spec: AnswerInputSpec = { kind, maxBytes: 256, ...(kind === 'finite_set' ? { maxItems: 8 } : {}) };
  saved.set('structured', { id: 'structured', topic, difficulty: 3, problemLatex: '\\text{Find the stated quantity.}',
    createdAt: '2026-11-03T00:00:00Z', lastAnswer: answer, lastResult: 'incorrect', attemptCount: 1,
    answerRevealed: false, solutionRevealed: false, answerInput: spec });
  resetPractice();
  await act(async () => root.render(<PracticePage id="structured" />));
  const field = element.querySelector<HTMLInputElement>(selector)!;
  expect(field).not.toBeNull();
  if (kind === 'boolean') expect(field.checked).toBe(true);
  else expect(field.value).toBe(kind === 'finite_set' ? '-1' : '3/2');
  expect((await getProblem('structured')).answerInput).toEqual(spec);
  await act(async () => button('Check answer').click());
  expect(calls.find(call => call.path.endsWith('/attempts'))?.body?.answer).toBe(answer);
  expect(calls.some(call => call.path.includes('reveal-'))).toBe(false);
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

it('uses the derivative topic selected from the tree', async () => {
  catalogue = {
    areas: [{ slug: 'mathematical-analysis', name: 'Mathematical Analysis', mixed: null }],
    items: [...INTEGRALS, { slug: 'derivatives', name: 'Derivatives', area: 'mathematical-analysis', availableDifficulties: [1, 2, 3] }],
  };
  await act(async () => root.render(<DashboardPage initialArea="mathematical-analysis" initialTopic="derivatives" />));
  expect(element.textContent).toContain('Selected topic: Derivatives');
  expect(button('Generate problem').disabled).toBe(false);
  expect(element.querySelectorAll('.pl-seg button')).toHaveLength(3);
  await act(async () => button('Medium').click());
  await act(async () => button('Generate problem').click());
  expect(calls.find(call => call.path === '/api/problems')?.body).toEqual({ topic: 'derivatives', difficulty: 3 });
});

it('sends Mathematical Analysis as the mixed-practice area', async () => {
  catalogue = {
    areas: [{ slug: 'mathematical-analysis', name: 'Mathematical Analysis', mixed: { availableDifficulties: [1, 2], weights: { 'basic-integrals': 1, substitution: 2 } } }],
    items: INTEGRALS,
  };
  await act(async () => root.render(<DashboardPage initialArea="mathematical-analysis" initialTopic="mixed" />));
  expect(element.querySelector('#mixed-weights')?.textContent).toContain('Basic integrals 33%, Substitution 67%');
  await act(async () => button('Generate problem').click());
  expect(calls.find(call => call.path === '/api/problems')?.body).toEqual({ topic: 'mixed', area: 'mathematical-analysis', difficulty: 1 });
});
