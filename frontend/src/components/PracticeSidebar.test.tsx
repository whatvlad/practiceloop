// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { PracticeSidebar } from './PracticeSidebar';

vi.mock('../data/api', () => ({
  getCatalogue: async () => ({
    areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }],
    topics: [{ slug: 'matrix-operations', name: 'Matrix operations', area: 'algebra', availableDifficulties: [1] }],
  }),
}));

it('links available topics and marks unavailable algebra topics', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const element = document.createElement('div');
  document.body.append(element);
  const root = createRoot(element);
  await act(async () => root.render(<PracticeSidebar />));
  expect(element.querySelector('a[href="/dashboard?area=algebra&topic=matrix-operations"]')).not.toBeNull();
  expect(element.textContent).toContain('Diagonalization');
  expect(element.textContent).toContain('Coming soon');
  expect(element.querySelector('a[href*="algebraic-expressions"]')).toBeNull();
  await act(async () => root.unmount());
  element.remove();
});

it('opens the determinant topic in local preview without navigating away', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const element = document.createElement('div'); document.body.append(element);
  const root = createRoot(element);
  const select = vi.fn();
  await act(async () => root.render(<PracticeSidebar preview={{
    areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }],
    topics: [{ slug: 'determinants', name: 'Determinants', area: 'algebra', availableDifficulties: [1, 2, 3] }],
  }} onPreviewTopic={select} />));
  const button = [...element.querySelectorAll('button')].find(item => item.textContent === 'Determinants')!;
  await act(async () => button.click());
  expect(select).toHaveBeenCalledWith('determinants');
  await act(async () => root.unmount()); element.remove();
});
