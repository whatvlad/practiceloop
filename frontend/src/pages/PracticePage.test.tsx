// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { beforeEach, afterEach, expect, it, vi } from 'vitest';
import { PracticePage } from './PracticePage';
import * as api from '../data/api';

vi.mock('../data/api', () => ({
  NotFoundError: class extends Error {},
  openProblem: vi.fn(async () => ({ problem: { id: 'one', topic: 'basic-integrals', difficulty: 1,
    problemLatex: '\\int x\\,dx', createdAt: '', answerRevealed: false, solutionRevealed: false,
    lastResult: null, lastAnswer: null } })),
  getLastSelection: vi.fn(), listProblemPage: vi.fn(), generateProblem: vi.fn(),
  revealAnswer: vi.fn(), revealSolution: vi.fn(), submitAttempt: vi.fn(),
}));
vi.mock('../components/AnswerInput', () => ({ AnswerInput: () => <input aria-label="answer" /> }));
let element: HTMLDivElement;
let root: Root;
beforeEach(async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  vi.clearAllMocks();
  element = document.createElement('div'); document.body.append(element);
  root = createRoot(element);
  await act(async () => root.render(<PracticePage id="one" />));
});
afterEach(async () => { await act(async () => root.unmount()); element.remove(); });
const button = (label: string) => Array.from(element.querySelectorAll('button')).find(b => b.textContent?.includes(label))!;

it('disables all actions during a request and catches failures without an incorrect verdict', async () => {
  let fail!: (reason: Error) => void;
  vi.mocked(api.submitAttempt).mockImplementationOnce(() => new Promise((_resolve, reject) => { fail = reject; }));
  await act(async () => { button('Check answer').click(); button('Check answer').click(); });
  expect(api.submitAttempt).toHaveBeenCalledTimes(1);
  expect(button('Generate next problem').disabled).toBe(true);
  await act(async () => fail(new Error('Try again shortly.')));
  expect(element.querySelector('[role="alert"]')?.textContent).toContain('Try again');
  expect(element.textContent).not.toContain('Incorrect');
  expect(button('Generate next problem').disabled).toBe(false);
});

it('shows the dedicated missing-constant message and does not prefetch solutions', async () => {
  expect(api.revealAnswer).not.toHaveBeenCalled();
  expect(api.revealSolution).not.toHaveBeenCalled();
  vi.mocked(api.submitAttempt).mockResolvedValueOnce('missing_constant');
  await act(async () => button('Check answer').click());
  expect(element.textContent).toContain('Add an arbitrary integration constant');
  expect(button('Check answer').disabled).toBe(false);
});
