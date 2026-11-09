// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, expect, it, vi } from 'vitest';
import { HomePage } from './HomePage';
import * as api from '../data/api';
import type { PublicProblem } from '../data/types';

vi.mock('../data/api', () => ({
  listProblemPage: vi.fn(),
  getProfileCounts: vi.fn(async () => ({ generated: 3, attempted: 2, correct: 1 })),
  getLastSelection: vi.fn(async () => ({ topic: 'basic-integrals', difficulty: 1, area: 'mathematical-analysis' })),
  generateProblem: vi.fn(),
}));

function problem(id: string, extra: Partial<PublicProblem> = {}): PublicProblem {
  return { id, topic: 'basic-integrals', difficulty: 2, problemLatex: '\\int x\\,dx', createdAt: '2026-11-08T10:00:00Z', answerRevealed: false, solutionRevealed: false, lastResult: null, lastAnswer: null, ...extra };
}

let root: ReturnType<typeof createRoot> | null = null;
const element = document.createElement('div');
afterEach(async () => { await act(async () => root?.unmount()); element.remove(); window.history.replaceState(null, '', '/'); });

async function render() {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  document.body.append(element);
  root = createRoot(element);
  await act(async () => root!.render(<HomePage name="Ada Lovelace" />));
}

it('shows the last problem first, then a short activity feed and progress', async () => {
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: [problem('latest'), problem('older', { lastResult: 'correct' })], nextCursor: null });
  await render();
  expect(element.querySelector('h1')?.textContent).toBe('Welcome back, Ada');
  const latest = element.querySelector('section[aria-labelledby="latest-title"]')!;
  expect(latest.querySelector('a[href="/practice?id=latest"]')).not.toBeNull();
  expect(latest.textContent).toContain('Continue solving');
  const feed = element.querySelector('section[aria-labelledby="feed-title"]')!;
  expect(feed.querySelector('a[href="/practice?id=older"]')).not.toBeNull();
  expect(feed.querySelector('a[href="/practice?id=latest"]')).toBeNull();
  expect(element.querySelector('.pl-home-stats')?.textContent).toContain('Generated3');
});

it('offers to generate a first problem when the history is empty', async () => {
  vi.mocked(api.listProblemPage).mockResolvedValueOnce({ items: [], nextCursor: null });
  vi.mocked(api.generateProblem).mockResolvedValueOnce(problem('first'));
  const scroll = vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
  await render();
  expect(element.textContent).toContain('Generate your first problem');
  expect(element.querySelector('section[aria-labelledby="feed-title"]')).toBeNull();
  const generate = [...element.querySelectorAll('button')].find(button => button.textContent === 'Generate a problem')!;
  await act(async () => generate.click());
  expect(api.generateProblem).toHaveBeenCalledWith('basic-integrals', 1, 'mathematical-analysis');
  expect(window.location.search).toBe('?id=first');
  scroll.mockRestore();
});
