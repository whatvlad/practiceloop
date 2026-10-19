// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { HistoryPage } from './HistoryPage';
import { ProfilePage } from './ProfilePage';
import * as api from '../data/api';
import type { ProblemPage, PublicProblem } from '../data/types';

vi.mock('../data/api', async original => ({ ...await original<typeof import('../data/api')>(), listProblemPage: vi.fn(), getProfileCounts: vi.fn() }));
const problem = (id: string): PublicProblem => ({ id, saved: true, topic: 'basic-integrals', difficulty: 2,
  problemLatex: '\\int x\\,dx', createdAt: '2026-10-19T00:00:00Z', answerRevealed: true,
  solutionRevealed: true, attemptCount: 3, lastAnswer: 'x^2/2+C', lastResult: 'correct' });
let root: Root;
let element: HTMLDivElement;
const button = (label: string) => Array.from(element.querySelectorAll('button')).find(b => b.textContent?.includes(label))!;
beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  vi.resetAllMocks();
  element = document.createElement('div');
  document.body.append(element);
  root = createRoot(element);
});
afterEach(async () => { await act(async () => root.unmount()); element.remove(); });

it('shows persisted metadata, keeps the first page on error and retries the same cursor once for duplicate clicks', async () => {
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: [problem('one')], nextCursor: 'cursor-1' });
  await act(async () => root.render(<HistoryPage />));
  expect(element.textContent).toContain('3 attempts');
  expect(element.textContent).toContain('Latest answer: x^2/2+C');
  expect(element.textContent).toContain('Solution viewed');
  expect(element.querySelector('time')?.dateTime).toBe('2026-10-19T00:00:00Z');
  let reject!: (error: Error) => void;
  vi.mocked(api.listProblemPage).mockImplementationOnce(() => new Promise((_resolve, fail) => { reject = fail; }));
  await act(async () => { button('Load more problems').click(); button('Load more problems').click(); });
  expect(api.listProblemPage).toHaveBeenCalledTimes(2);
  await act(async () => reject(new Error('Temporary failure.')));
  expect(element.querySelector('a[href*="id=one"]')).not.toBeNull();
  expect(element.querySelector('[role="alert"]')?.textContent).toContain('Temporary failure');
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: [problem('two')], nextCursor: null });
  await act(async () => button('Retry loading history').click());
  expect(api.listProblemPage).toHaveBeenLastCalledWith({ cursor: 'cursor-1' });
  expect(element.querySelector('a[href*="id=two"]')).not.toBeNull();
  expect(element.textContent).toContain('2 of 2 loaded');
  expect(button('Load more problems')).toBeUndefined();
});

it('shows loading, retries the first page and distinguishes empty history', async () => {
  let finish!: (value: ProblemPage) => void;
  vi.mocked(api.listProblemPage).mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  await act(async () => root.render(<HistoryPage />));
  expect(element.querySelector('[role="status"]')?.textContent).toBe('Loading history…');
  await act(async () => finish({ items: [], nextCursor: null }));
  expect(element.textContent).toContain('No saved problems yet');
});

it('ignores a pending history page after the account view is replaced', async () => {
  let old!: (value: ProblemPage) => void;
  vi.mocked(api.listProblemPage).mockImplementationOnce(() => new Promise(resolve => { old = resolve; }));
  await act(async () => root.render(<HistoryPage key="alice" />));
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: [problem('bob')], nextCursor: null });
  await act(async () => root.render(<HistoryPage key="bob" />));
  await act(async () => old({ items: [problem('alice')], nextCursor: null }));
  expect(element.querySelector('a[href*="id=bob"]')).not.toBeNull();
  expect(element.querySelector('a[href*="id=alice"]')).toBeNull();
});

it('shows an error rather than invented zero profile counts, then loads real totals on retry', async () => {
  vi.mocked(api.getProfileCounts).mockRejectedValueOnce(new Error('Database unavailable'));
  await act(async () => root.render(<ProfilePage account={{ id: 'one', name: 'Ada', email: 'ada@example.invalid', provider: 'Google' }} onLogOut={() => {}} />));
  expect(element.querySelector('[role="alert"]')).not.toBeNull();
  expect(element.querySelector('.pl-stat')).toBeNull();
  vi.mocked(api.getProfileCounts).mockResolvedValueOnce({ generated: 123, attempted: 45, correct: 20 });
  await act(async () => button('Retry loading statistics').click());
  expect(element.textContent).toContain('123');
  expect(element.textContent).toContain('45');
  expect(element.textContent).not.toContain('Your statistics could not be loaded.');
});
