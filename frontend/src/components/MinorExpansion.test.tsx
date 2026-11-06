// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it } from 'vitest';
import { MinorExpansion } from './MinorExpansion';

it('highlights the parent entries belonging to the selected minor', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  const matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]];
  await act(async () => root.render(<MinorExpansion expansion={{ matrix, row: 1, columns: [0, 2] }} />));
  const button = host.querySelector<HTMLButtonElement>('[aria-label="Minor: remove row 2, column 3"]')!;
  expect(button.querySelectorAll('.pl-minor-row')).toHaveLength(3);
  expect(host.querySelectorAll('.is-included')).toHaveLength(0);
  await act(async () => button.click());
  expect(button.getAttribute('aria-pressed')).toBe('true');
  expect(host.querySelectorAll('.is-included')).toHaveLength(9);
  expect(host.querySelectorAll('.is-excluded')).toHaveLength(7);
  expect(host.textContent).toContain('Row 2 and column 3 are removed');
  expect(host.querySelector('.pl-cofactor-signs .is-active')?.textContent).toBe('−');
  expect(host.textContent).toContain('The cofactor sign is −');
  expect(host.textContent).toContain('gives the coefficient -7');
  await act(async () => root.unmount()); host.remove();
});
