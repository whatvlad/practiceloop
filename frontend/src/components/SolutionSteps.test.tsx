// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it } from 'vitest';
import { SolutionSteps } from './SolutionSteps';

it('shows the original matrix first and opens explanations only on request', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  await act(async () => root.render(<SolutionSteps matrixStatement={String.raw`\begin{pmatrix}1&2\\3&4\end{pmatrix}`}
    steps={[{ say: 'Add the entries.', latex: '1+2=3' }, { say: 'Final result.', latex: '3' }]} />));
  const items = host.querySelectorAll('li');
  expect(items).toHaveLength(3);
  expect(items[0].querySelector('details')).toBeNull();
  const detail = items[1].querySelector('details')!;
  expect(detail.open).toBe(false);
  detail.open = true;
  expect(detail.open).toBe(true);
  expect(detail.textContent).toContain('Add the entries.');
  await act(async () => root.unmount()); host.remove();
});

it('shows the selected row and column calculation for a numeric matrix product', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  const statement = String.raw`\begin{pmatrix}2&0&3\\1&4&-1\end{pmatrix}\cdot\begin{pmatrix}1&2\\3&5\\1&1\end{pmatrix}`;
  await act(async () => root.render(<SolutionSteps matrixStatement={statement} steps={[
    { say: 'Check the dimensions.', latex: String.raw`(2\times3)(3\times2)=2\times2` },
    { say: 'Multiply each row by each column.', latex: String.raw`\begin{pmatrix}(2)\cdot(1)\end{pmatrix}` },
    { say: 'Write the result.', latex: String.raw`\begin{pmatrix}5&7\\12&21\end{pmatrix}` },
  ]} />));
  const steps = host.querySelectorAll('li');
  expect(steps).toHaveLength(4);
  expect(steps[0].querySelector('.pl-product-grid')).toBeNull();
  expect(steps[1].textContent).toContain('Check the dimensions.');
  expect(steps[2].querySelector('.pl-product-grid')).not.toBeNull();
  expect(steps[2].textContent).toContain('Multiply the matrices');
  expect(steps[3].textContent).toContain('Write the result.');
  const arrows = [...host.querySelectorAll('.pl-product-arrow')];
  expect(arrows).toHaveLength(3);
  expect(arrows.every(arrow => arrow.hasAttribute('marker-start') && arrow.hasAttribute('marker-end'))).toBe(true);
  const firstArrowEnd = arrows[0].getAttribute('x2');
  const first = host.querySelector<HTMLButtonElement>('[aria-label="Result row 1, column 1: 5"]')!;
  expect(first.getAttribute('aria-pressed')).toBe('true');
  const second = host.querySelector<HTMLButtonElement>('[aria-label="Result row 2, column 2: 21"]')!;
  await act(async () => second.click());
  expect(second.getAttribute('aria-pressed')).toBe('true');
  expect(arrows[0].getAttribute('x2')).not.toBe(firstArrowEnd);
  expect(host.querySelector('.pl-product-formula')?.textContent).toContain('21');
  await act(async () => root.unmount()); host.remove();
});

it('shows the multiplication diagram after the inverse in division', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  const a = String.raw`\begin{pmatrix}1&2\\3&4\end{pmatrix}`;
  const b = String.raw`\begin{pmatrix}1&1\\0&1\end{pmatrix}`;
  const inverse = String.raw`\begin{pmatrix}1&-1\\0&1\end{pmatrix}`;
  await act(async () => root.render(<SolutionSteps matrixStatement={`${a}:${b}`} steps={[
    { say: 'Dimensions', latex: String.raw`2\times2` },
    { say: 'Inverse', latex: String.raw`B^{-1}=` + inverse },
    { say: 'Rewrite', latex: String.raw`A:B=A\cdot B^{-1}=` + a + String.raw`\cdot` + inverse },
    { say: 'Multiply', latex: String.raw`\begin{pmatrix}(1)\cdot(1)\end{pmatrix}` },
    { say: 'Result', latex: a },
  ]} />));
  const items = host.querySelectorAll('li');
  expect(items[3].textContent).toContain('Rewrite');
  expect(items[4].querySelector('.pl-product-grid')).not.toBeNull();
  expect(items[4].querySelector('[aria-label="Result row 1, column 2: 1"]')).not.toBeNull();
  await act(async () => root.unmount()); host.remove();
});

it('keeps the row operation and augmented matrix on separate scrollable lines', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  const operation = String.raw`R_{2}\leftarrow \frac{R_{2}}{-1}\quad \left[\begin{array}{cc|cc}1&2&1&0\\0&1&-2&1\end{array}\right]`;
  await act(async () => root.render(<SolutionSteps matrixStatement="A:B" steps={[{ say: 'Divide the row.', latex: operation }]} />));
  const lines = host.querySelectorAll('.pl-solution-detail .m');
  expect(lines).toHaveLength(2);
  expect(lines[0].querySelector('.katex')).not.toBeNull();
  expect(lines[1].querySelector('.katex')).not.toBeNull();
  expect(lines[0].textContent).not.toContain('array');
  expect(host.textContent).toContain('Modified row');
  expect(host.textContent).not.toContain('Reference row');
  expect([...lines[1].querySelectorAll<HTMLElement>('[style]')].some(item => item.style.color === 'rgb(101, 223, 145)')).toBe(true);
  await act(async () => root.unmount()); host.remove();
});

it('highlights both rows used in an elimination and labels them', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  const operation = String.raw`R_{2}\leftarrow R_{2}-(3)R_{1}\quad \left[\begin{array}{cc|cc}1&2&1&0\\0&1&-3&1\end{array}\right]`;
  await act(async () => root.render(<SolutionSteps matrixStatement="A" steps={[{ say: 'Eliminate an entry.', latex: operation }]} />));
  const matrix = host.querySelectorAll('.pl-solution-detail .m')[1];
  const colors = [...matrix.querySelectorAll<HTMLElement>('[style]')].map(element => element.style.color);
  expect(colors).toContain('rgb(101, 223, 145)');
  expect(colors).toContain('rgb(95, 168, 255)');
  expect(host.textContent).toContain('Modified row');
  expect(host.textContent).toContain('Reference row');
  await act(async () => root.unmount()); host.remove();
});

it('labels both highlighted rows when rows are exchanged', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  const operation = String.raw`R_{1}\leftrightarrow R_{2}\quad \left[\begin{array}{cc|cc}0&1&0&1\\1&0&1&0\end{array}\right]`;
  await act(async () => root.render(<SolutionSteps matrixStatement="A" steps={[{ say: 'Exchange rows.', latex: operation }]} />));
  expect(host.textContent).toContain('Exchanged row');
  expect(host.textContent).toContain('Other exchanged row');
  await act(async () => root.unmount()); host.remove();
});

it('shows a diagonal diagram alongside the determinant calculation', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  await act(async () => root.render(<SolutionSteps matrixStatement="A" colorEntries={false} steps={[
    { say: 'Sarrus rule', latex: '1+2+3', determinantMatrix: [[1, 2, 3], [4, 5, 6], [7, 8, 9]] },
  ]} />));
  expect(host.querySelectorAll('.pl-det-line')).toHaveLength(6);
  expect(host.querySelector('details')?.textContent).toContain('Sarrus rule');
  await act(async () => root.unmount()); host.remove();
});

it('renders colored calculation groups for the determinant', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  await act(async () => root.render(<SolutionSteps matrixStatement="A" colorEntries={false} steps={[
    { say: 'Multiply diagonals', latex: String.raw`\color{#f17baa}{(2)\cdot(4)}-\color{#759bff}{(3)\cdot(1)}` },
  ]} />));
  const colors = [...host.querySelectorAll<HTMLElement>('[style]')].map(element => element.style.color);
  expect(colors).toContain('rgb(241, 123, 170)');
  expect(colors).toContain('rgb(117, 155, 255)');
  await act(async () => root.unmount()); host.remove();
});

it('opens a used formula and its explanation from the calculation step', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  await act(async () => root.render(<SolutionSteps steps={[
    { say: 'Write the original problem.', latex: 'x^2-1' },
    { say: 'Multiply the divisor.', latex: 'x(x+1)=x^2+x', rules: [
      { title: 'Distributive law', latex: 'a(b+c)=ab+ac', explanation: 'Multiply each term.' },
    ] },
  ]} />));
  expect(host.querySelectorAll('details')).toHaveLength(1);
  const details = host.querySelector('details')!;
  expect(details.open).toBe(false);
  await act(async () => details.querySelector('summary')!.click());
  expect(details.open).toBe(true);
  expect(details.textContent).toContain('Distributive law');
  expect(details.textContent).toContain('Multiply each term.');
  expect(details.querySelectorAll('.katex').length).toBe(2);
  await act(async () => root.unmount()); host.remove();
});
