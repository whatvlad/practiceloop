// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { LocalMatrixProblem } from './LocalMatrixProblem';

it('shows the practice actions and reveals a sample answer and solution', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div');
  document.body.append(host);
  const root = createRoot(host);
  let generation = 0;
  const spec = (size: number) => {
    const names = ['one', 'two', 'three'];
    const row = { kind: 'tuple', maxBytes: 256, labels: names.slice(0, size).map(name => `Column ${name}`), components: Array(size).fill({ kind: 'formula', maxBytes: 256 }) };
    return { kind: 'tuple', maxBytes: 256, labels: names.slice(0, size).map(name => `Matrix row ${name}`), components: Array(size).fill(row) };
  };
  vi.stubGlobal('fetch', vi.fn(async (path: string) => new Response(JSON.stringify(path.endsWith('/generate')
    ? { code: `test-${++generation}`, generatorVersion: 'matrix-sum-v1', statement: generation === 1 ? String.raw`\text{Add the matrices: }1+2\text{.}` : String.raw`\text{Subtract the matrices: }1-2\text{.}`, answerInput: spec(generation === 1 ? 2 : 3) }
    : { answerLatex: '3', steps: [{ say: 'Add corresponding entries.', latex: '3' }] }), { status: 200 })));
  await act(async () => root.render(<LocalMatrixProblem />));
  expect(fetch).not.toHaveBeenCalled();
  expect(host.querySelector('.pl-problem')).toBeNull();
  const button = (name: string) => [...host.querySelectorAll('button')].find(item => item.textContent?.includes(name))!;
  await act(async () => button('Generate problem').click());
  expect(host.querySelector('.pl-lead')?.textContent).toBe('Add the matrices.');
  expect(host.querySelector('.pl-expr')?.textContent).not.toContain('Add the matrices');
  for (const name of ['Check answer', 'Show answer', 'Show solution', 'Generate next problem']) expect(button(name)).toBeDefined();
  await act(async () => button('Show answer').click());
  expect(host.textContent).toContain('Answer');
  await act(async () => button('Show solution').click());
  expect(host.textContent).toContain('Add corresponding entries');
  const operation = [...host.querySelectorAll('label')].find(label => label.textContent?.startsWith('Operation'))!.querySelector('select')!;
  await act(async () => { operation.value = 'subtract'; operation.dispatchEvent(new Event('change', { bubbles: true })); });
  for (const labelText of ['Rows of A', 'Columns of A', 'Rows of B', 'Columns of B']) {
    const size = [...host.querySelectorAll('label')].find(label => label.textContent?.startsWith(labelText))!.querySelector('select')!;
    await act(async () => { size.value = '3'; size.dispatchEvent(new Event('change', { bubbles: true })); });
  }
  const rowsB = [...host.querySelectorAll('label')].find(label => label.textContent?.startsWith('Rows of B'))!.querySelector('select')!;
  await act(async () => { rowsB.value = '2'; rowsB.dispatchEvent(new Event('change', { bubbles: true })); });
  expect(host.textContent).toContain('both matrices must have the same dimensions');
  expect(button('Generate next problem').disabled).toBe(true);
  await act(async () => { rowsB.value = '3'; rowsB.dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => button('Generate next problem').click());
  const calls = vi.mocked(fetch).mock.calls;
  expect(JSON.parse(String(calls.at(-1)![1]?.body))).toEqual({ level: 1, dimensions: { operation: 'subtract', rowsA: 3, colsA: 3, rowsB: 3, colsB: 3 } });
  expect(host.textContent).not.toContain('Add corresponding entries');
  expect(host.querySelectorAll('.pl-matrix-grid input')).toHaveLength(9);
  expect(host.querySelector('.pl-lead')?.textContent).toBe('Subtract the matrices.');
  await act(async () => { operation.value = 'divide'; operation.dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => { rowsB.value = '2'; rowsB.dispatchEvent(new Event('change', { bubbles: true })); });
  expect(host.textContent).toContain('Division requires a square matrix B');
  expect(button('Generate next problem').disabled).toBe(true);
  await act(async () => root.unmount());
  vi.unstubAllGlobals();
  host.remove();
});
