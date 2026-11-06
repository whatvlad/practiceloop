// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { PracticeSidebar } from './PracticeSidebar';
import { generateProblem } from '../data/api';
import type { PublicProblem } from '../data/types';

vi.mock('../data/api', () => ({
  getCatalogue: async () => ({
    areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }],
    topics: [{ slug: 'matrix-operations', name: 'Matrix operations', area: 'algebra', availableDifficulties: [1] }],
  }),
  generateProblem: vi.fn(),
}));

it('links available topics and marks unavailable algebra topics', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const element = document.createElement('div');
  document.body.append(element);
  const root = createRoot(element);
  await act(async () => root.render(<PracticeSidebar />));
  expect(element.querySelector('a[href="/dashboard?area=algebra&topic=matrix-operations"]')).not.toBeNull();
  expect(element.textContent).toContain('Diagonalization');
  expect(element.textContent).toContain('In develop');
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

it('requires a level for a randomly selected topic and remembers the selection', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  localStorage.clear();
  const element = document.createElement('div');
  document.body.append(element);
  const root = createRoot(element);
  await act(async () => root.render(<PracticeSidebar accountId="test-account" />));
  const random = [...element.querySelectorAll('button')].find(button => button.textContent === 'Random problems')!;
  await act(async () => random.click());
  const checkbox = [...element.querySelectorAll('label')].find(label => label.textContent?.includes('Matrix operations'))!.querySelector('input')!;
  await act(async () => checkbox.click());
  const generate = [...element.querySelectorAll('button')].find(button => button.textContent === 'Generate random problem')!;
  expect(generate.disabled).toBe(true);
  const level = element.querySelector('select')!;
  await act(async () => { level.value = '1'; level.dispatchEvent(new Event('change', { bubbles: true })); });
  const settings = (name: string) => [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith(name))!.querySelector('select')!;
  await act(async () => { settings('Operation').value = 'multiply'; settings('Operation').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => { settings('Matrix size').value = '3x3'; settings('Matrix size').dispatchEvent(new Event('change', { bubbles: true })); });
  expect(generate.disabled).toBe(false);
  expect(JSON.parse(localStorage.getItem('practiceloop:random-selection:test-account')!)).toEqual({ 'matrix-operations': 1 });
  vi.mocked(generateProblem).mockResolvedValueOnce({ id: 'random-1' } as PublicProblem);
  const scroll = vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
  await act(async () => generate.click());
  expect(generateProblem).toHaveBeenCalledWith('matrix-operations', 1, 'algebra', { operation: 'multiply', size: '3x3' });
  expect(window.location.search).toContain('mode=random');
  window.history.replaceState(null, '', '/');
  scroll.mockRestore();
  await act(async () => root.unmount());
  element.remove();
});
