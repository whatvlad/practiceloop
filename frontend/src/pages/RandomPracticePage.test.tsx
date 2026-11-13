// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { RandomPracticePage } from './RandomPracticePage';
import { generateProblem } from '../data/api';
import type { PublicProblem } from '../data/types';

vi.mock('../data/api', () => ({
  getCatalogue: async () => ({
    areas: [{ slug: 'algebra', name: 'Algebra', mixed: null }],
    topics: [
      { slug: 'matrix-operations', name: 'Matrix operations', area: 'algebra', availableDifficulties: [1] },
      { slug: 'vectors', name: 'Vectors', area: 'algebra', availableDifficulties: [1, 2, 3, 4, 5] },
      { slug: 'lines-and-planes', name: 'Lines and planes', area: 'algebra', availableDifficulties: [1, 2, 3, 4, 5] },
    ],
  }),
  generateProblem: vi.fn(),
}));

it('requires a level for a randomly selected topic and remembers the selection', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  localStorage.clear();
  const element = document.createElement('div');
  document.body.append(element);
  const root = createRoot(element);
  await act(async () => root.render(<RandomPracticePage accountId="test-account" />));
  const button = (text: string) => [...element.querySelectorAll('button')].find(item => item.textContent === text)!;
  await act(async () => button('Matrix operations').click());
  expect(button('Matrix operations').getAttribute('aria-pressed')).toBe('true');
  expect(button('Generate random problem').disabled).toBe(true);
  expect(element.textContent).toContain('choose a level for each');
  await act(async () => button('Basic').click());
  const settings = (name: string) => [...element.querySelectorAll('label')].find(label => label.textContent?.startsWith(name))!.querySelector('select')!;
  await act(async () => { settings('Operation').value = 'multiply'; settings('Operation').dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => { settings('Matrix size').value = '3x3'; settings('Matrix size').dispatchEvent(new Event('change', { bubbles: true })); });
  expect(button('Generate random problem').disabled).toBe(false);
  expect(JSON.parse(localStorage.getItem('practiceloop:random-selection:test-account')!)).toEqual({ 'matrix-operations': 1 });
  vi.mocked(generateProblem).mockResolvedValueOnce({ id: 'random-1' } as PublicProblem);
  const scroll = vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
  await act(async () => button('Generate random problem').click());
  expect(generateProblem).toHaveBeenCalledWith('matrix-operations', 1, 'algebra', { operation: 'multiply', size: '3x3' });
  expect(window.location.search).toContain('mode=random');
  window.history.replaceState(null, '', '/');
  scroll.mockRestore();
  await act(async () => root.unmount());
  element.remove();
});

it('selects and clears a whole group', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  localStorage.clear();
  const element = document.createElement('div');
  document.body.append(element);
  const root = createRoot(element);
  await act(async () => root.render(<RandomPracticePage accountId="group-account" />));
  const button = (text: string) => [...element.querySelectorAll('button')].find(item => item.textContent === text)!;
  await act(async () => button('Select all').click());
  expect(element.textContent).toContain('1 topic selected');
  await act(async () => button('Clear group').click());
  expect(element.textContent).toContain('No topics selected.');
  await act(async () => root.unmount());
  element.remove();
});

it('offers each canonical geometry topic once with three current levels', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  localStorage.clear();
  const element = document.createElement('div'); document.body.append(element);
  const root = createRoot(element);
  await act(async () => root.render(<RandomPracticePage accountId="geometry-random" />));
  for (const title of ['Vectors, areas and volumes', 'Lines and planes']) {
    const toggles = [...element.querySelectorAll<HTMLButtonElement>('button')].filter(button => button.textContent === title);
    expect(toggles).toHaveLength(1);
    await act(async () => toggles[0].click());
    const levels = element.querySelector(`[aria-label="Level for ${title}"]`)!;
    expect(levels.querySelectorAll('button')).toHaveLength(3);
  }
  await act(async () => root.unmount()); element.remove();
});
