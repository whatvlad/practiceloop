// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it } from 'vitest';
import { DeterminantDiagram } from './DeterminantDiagram';

it('draws the correct number of diagonals and repeats columns only for Sarrus', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  await act(async () => root.render(<DeterminantDiagram matrix={[[1, 2], [3, 4]]} />));
  expect(host.querySelectorAll('.pl-det-line-plus')).toHaveLength(1);
  expect(host.querySelectorAll('.pl-det-line-minus')).toHaveLength(1);
  expect(host.querySelectorAll('text')).toHaveLength(4);
  await act(async () => root.render(<DeterminantDiagram matrix={[[1, 2, 3], [4, 5, 6], [7, 8, 9]]} />));
  expect(host.querySelectorAll('.pl-det-line-plus')).toHaveLength(3);
  expect(host.querySelectorAll('.pl-det-line-minus')).toHaveLength(3);
  expect(host.querySelectorAll('.pl-det-repeat')).toHaveLength(6);
  await act(async () => root.unmount()); host.remove();
});
