// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { HistoryPage } from './HistoryPage';
import { ProfilePage } from './ProfilePage';
import * as api from '../data/api';
import type { ProblemPage, PublicProblem } from '../data/types';

vi.mock('../data/api', async original => ({ ...await original<typeof import('../data/api')>(), listProblemPage: vi.fn(), getProfileCounts: vi.fn(), createWorksheet: vi.fn(), downloadWorksheetPdf: vi.fn() }));
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

it('keeps saved history visible without exporting or selecting inactive problems', async () => {
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: [problem('one')], nextCursor: null });
  await act(async () => root.render(<HistoryPage inactive />));
  expect(element.textContent).toContain('Latest answer: x^2/2+C');
  expect(element.textContent).toContain('Saved problems are currently inactive');
  expect(element.querySelector('input[type="checkbox"]')).toBeNull();
  expect(api.createWorksheet).not.toHaveBeenCalled();
});

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

const many = (count: number, extra: Partial<PublicProblem> = {}) =>
  Array.from({ length: count }, (_, i) => ({ ...problem(`p${i}`), answerRevealed: false, ...extra }));
const boxes = () => Array.from(element.querySelectorAll<HTMLInputElement>('.pl-hcheck input'));
const chip = (label: string) => Array.from(element.querySelectorAll('.pl-chip')).find(b => b.textContent === label) as HTMLButtonElement;

it('labels each checkbox, keeps it outside the row link and counts the selection', async () => {
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: many(2), nextCursor: null });
  await act(async () => root.render(<HistoryPage />));
  const [first] = boxes();
  expect(first.getAttribute('aria-label')).toMatch(/^Select Basic integrals, level 2, /);
  expect(first.closest('a')).toBeNull();
  await act(async () => first.click());
  expect(first.checked).toBe(true);
  expect(element.querySelector('.pl-hexport-count')?.textContent).toBe('1 selected');
  expect(element.querySelector('.pl-hexport-count')?.getAttribute('aria-live')).toBe('polite');
  await act(async () => button('Select all').click());
  expect(boxes().every(b => b.checked)).toBe(true);
  expect(element.querySelector('.pl-hexport-count')?.textContent).toBe('2 selected');
  await act(async () => button('Clear').click());
  expect(boxes().some(b => b.checked)).toBe(false);
  expect(element.querySelector('.pl-hexport-count')?.textContent).toBe('');
});

it('selects only the rows under the current filter and stops at the 40-problem limit', async () => {
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: [...many(45), { ...problem('done'), answerRevealed: false, lastResult: 'incorrect' }], nextCursor: null });
  await act(async () => root.render(<HistoryPage />));
  await act(async () => chip('Incorrect').click());
  await act(async () => button('Select all').click());
  expect(element.querySelector('.pl-hexport-count')?.textContent).toBe('1 selected');
  await act(async () => chip('All').click());
  expect(element.querySelector('.pl-hexport-count')?.textContent).toBe('');
  await act(async () => button('Select all').click());
  expect(element.querySelector('.pl-hexport-count')?.textContent).toBe('40 selected · the limit is 40 problems per PDF');
  expect(element.textContent).toContain('Selected 40 problems: one PDF holds at most 40.');
  const unchecked = boxes().filter(b => !b.checked);
  expect(unchecked).toHaveLength(6);
  expect(unchecked.every(b => b.disabled)).toBe(true);
  await act(async () => boxes()[0].click());
  expect(boxes().filter(b => !b.checked).every(b => !b.disabled)).toBe(true);
});

it('asks the server for worksheet problems when that filter is chosen', async () => {
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: many(2), nextCursor: null });
  await act(async () => root.render(<HistoryPage />));
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: [{ ...problem('sheet'), worksheetId: 'w1' }], nextCursor: 'c2' });
  await act(async () => chip('From worksheets').click());
  expect(api.listProblemPage).toHaveBeenLastCalledWith({ cursor: null, worksheet: true });
  expect(element.querySelector('a[href*="id=sheet"]')).not.toBeNull();
  expect(element.querySelector('a[href*="id=p0"]')).toBeNull();
  expect(element.textContent).toContain('From a worksheet');
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: [], nextCursor: null });
  await act(async () => button('Load more problems').click());
  expect(api.listProblemPage).toHaveBeenLastCalledWith({ cursor: 'c2', worksheet: true });
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: many(1), nextCursor: null });
  await act(async () => chip('All').click());
  expect(api.listProblemPage).toHaveBeenLastCalledWith({ cursor: null });
  expect(element.querySelector('a[href*="id=sheet"]')).toBeNull();
});

const sheet = (problemIds: string[]) => ({ id: 'w1', problemIds,
  groups: [{ label: 'Basic integrals, level 2', topic: 'basic-integrals' as const, difficulty: 2 as const, requested: problemIds.length, count: problemIds.length }] });

it('exports the selection with the answer key and solutions by default, warns first and shows the reveal afterwards', async () => {
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: many(3), nextCursor: null });
  await act(async () => root.render(<HistoryPage />));
  expect(element.textContent).not.toContain('Answer revealed');
  await act(async () => { boxes()[0].click(); boxes()[2].click(); });
  const key = element.querySelector<HTMLInputElement>('.pl-hexport input[type="checkbox"]')!;
  expect(key.checked).toBe(true);
  expect(element.querySelector('.pl-hexport')?.textContent).toContain('marked as solution revealed');
  vi.mocked(api.createWorksheet).mockResolvedValueOnce(sheet(['p2', 'p0']));
  vi.mocked(api.downloadWorksheetPdf).mockResolvedValueOnce();
  await act(async () => button('Export PDF').click());
  expect(api.createWorksheet).toHaveBeenCalledWith({ source: 'history', problemIds: ['p0', 'p2'], paper: 'a4', columns: 1, answerKey: true, solutions: true });
  expect(api.downloadWorksheetPdf).toHaveBeenCalledWith('w1');
  expect(element.textContent).toContain('Downloaded a PDF with 2 problems.');
  expect(element.textContent?.match(/Answer revealed/g)).toHaveLength(2);
  expect(element.querySelector('a[href*="id=p1"]')?.textContent).not.toContain('Answer revealed');
  expect(boxes().some(b => b.checked)).toBe(false);
});

it('leaves reveals alone without the answer key and passes the page options', async () => {
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: many(1), nextCursor: null });
  await act(async () => root.render(<HistoryPage />));
  await act(async () => boxes()[0].click());
  const [key, solutions] = element.querySelectorAll<HTMLInputElement>('.pl-hexport input[type="checkbox"]');
  await act(async () => solutions.click());
  expect(element.querySelector('.pl-hexport')?.textContent).toContain('marked as answer revealed');
  await act(async () => key.click());
  expect(element.querySelector('.pl-hexport')?.textContent).toContain('stay unrevealed');
  await act(async () => chip('Letter').click());
  await act(async () => chip('Two columns').click());
  vi.mocked(api.createWorksheet).mockResolvedValueOnce(sheet(['p0']));
  vi.mocked(api.downloadWorksheetPdf).mockResolvedValueOnce();
  await act(async () => button('Export PDF').click());
  expect(api.createWorksheet).toHaveBeenCalledWith({ source: 'history', problemIds: ['p0'], paper: 'letter', columns: 2, answerKey: false, solutions: false });
  expect(element.textContent).not.toContain('Answer revealed');
  expect(element.textContent).toContain('Downloaded a PDF with 1 problem.');
});

it('keeps the selection when the worksheet fails and retries only the download when the PDF fails', async () => {
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: many(2), nextCursor: null });
  await act(async () => root.render(<HistoryPage />));
  await act(async () => boxes()[1].click());
  vi.mocked(api.createWorksheet).mockRejectedValueOnce(new Error('Some of these problems are no longer in your history.'));
  await act(async () => button('Export PDF').click());
  expect(element.querySelector('[role="alert"]')?.textContent).toContain('no longer in your history');
  expect(boxes()[1].checked).toBe(true);
  expect(button('Retry the download')).toBeUndefined();
  vi.mocked(api.createWorksheet).mockResolvedValueOnce(sheet(['p1']));
  vi.mocked(api.downloadWorksheetPdf).mockRejectedValueOnce(new Error('The PDF service is busy with another worksheet.'));
  await act(async () => button('Export PDF').click());
  expect(element.querySelector('[role="alert"]')?.textContent).toContain('busy');
  expect(element.textContent).toContain('Answer revealed');
  vi.mocked(api.downloadWorksheetPdf).mockResolvedValueOnce();
  await act(async () => button('Retry the download').click());
  expect(api.createWorksheet).toHaveBeenCalledTimes(2);
  expect(api.downloadWorksheetPdf).toHaveBeenCalledTimes(2);
  expect(element.querySelector('[role="alert"]')).toBeNull();
  expect(element.textContent).toContain('Downloaded a PDF with 1 problem.');
});
