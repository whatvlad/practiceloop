// @vitest-environment jsdom
import { act, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it } from 'vitest';
import { MatrixAnswerInput } from './MatrixAnswerInput';
import { StructuredAnswerInput } from './StructuredAnswerInput';
import type { ComputationalInputSpec } from '../data/types';

it('edits a selected matrix cell with the existing keypad', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div');
  document.body.append(host);
  const root = createRoot(host);
  function Example() {
    const [matrix, setMatrix] = useState([['', ''], ['', '']]);
    return <MatrixAnswerInput value={matrix} onChange={setMatrix} />;
  }
  await act(async () => root.render(<Example />));
  expect(host.querySelectorAll('input')).toHaveLength(4);
  expect(host.querySelector('[aria-label="Math keypad"]')).toBeNull();
  const field = host.querySelector<HTMLInputElement>('input[aria-label="Row 2, column 1"]')!;
  await act(async () => field.focus());
  const sqrt = host.querySelector<HTMLButtonElement>('button[aria-label="square root"]')!;
  await act(async () => sqrt.click());
  expect(field.value).toBe('sqrt()');
  expect(field.selectionStart).toBe(5);
  expect(host.querySelector<HTMLInputElement>('input[aria-label="Row 1, column 1"]')!.value).toBe('');
  await act(async () => root.unmount());
  host.remove();
});

it('uses the matrix editor for a matrix contract and serializes the answer', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div');
  document.body.append(host);
  const root = createRoot(host);
  const formula: ComputationalInputSpec = { kind: 'formula', maxBytes: 256, symbols: { theta: 'real' } };
  const row: ComputationalInputSpec = { kind: 'tuple', maxBytes: 256, labels: ['Column one', 'Column two'], components: [formula, formula] };
  const spec: ComputationalInputSpec = { kind: 'tuple', maxBytes: 256, labels: ['Matrix row one', 'Matrix row two'], components: [row, row] };
  function Example() {
    const [value, setValue] = useState('');
    return <><StructuredAnswerInput id="answer" spec={spec} value={value} onChange={setValue} /><output>{value}</output></>;
  }
  await act(async () => root.render(<Example />));
  const cell = host.querySelector<HTMLInputElement>('input[aria-label="Row 1, column 1"]')!;
  await act(async () => cell.focus());
  expect(host.querySelector('button[aria-label="theta"]')).not.toBeNull();
  await act(async () => host.querySelector<HTMLButtonElement>('button[aria-label="square root"]')!.click());
  expect(host.querySelector('output')!.textContent).toBe('((sqrt(););(;))');
  expect(host.querySelectorAll('input')).toHaveLength(4);
  await act(async () => root.unmount());
  host.remove();
});
