// @vitest-environment jsdom
import { act, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it } from 'vitest';
import { StructuredAnswerInput } from './StructuredAnswerInput';
import type { ComputationalInputSpec } from '../data/types';

it('edits the three vector coordinates compactly and keeps their exact order', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const formula = { kind: 'formula', maxBytes: 256 } as const;
  const spec: ComputationalInputSpec = { kind: 'tuple', maxBytes: 256, components: [formula, formula, formula], labels: ['x component', 'y component', 'z component'] };
  function Form() {
    const [value, setValue] = useState('');
    return <><StructuredAnswerInput id="answer" spec={spec} value={value} onChange={setValue} /><output>{value}</output></>;
  }
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  try {
    await act(async () => root.render(<Form />));
    const inputs = [...host.querySelectorAll<HTMLInputElement>('input')];
    expect(inputs).toHaveLength(3);
    expect(inputs.map(input => input.getAttribute('aria-label'))).toEqual(['x component', 'y component', 'z component']);
    for (const [input, value] of inputs.map((input, index) => [input, ['1/2', 'sqrt(3)', '-2'][index]] as const)) {
      await act(async () => { Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, value); input.dispatchEvent(new Event('input', { bubbles: true })); });
    }
    expect(host.querySelector('output')?.textContent).toBe('(1/2;sqrt(3);-2)');
    expect(host.textContent).toContain('Reads as');
    expect((host.textContent?.match(/Use exact/g) ?? [])).toHaveLength(1);
  } finally { await act(async () => root.unmount()); host.remove(); }
});

it('presents an unordered vector pair as two compact coordinate editors', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const formula = { kind: 'formula', maxBytes: 256 } as const;
  const vector: ComputationalInputSpec = { kind: 'tuple', maxBytes: 256, components: [formula, formula, formula], labels: ['x coordinate', 'y coordinate', 'z coordinate'] };
  const spec: ComputationalInputSpec = { kind: 'tuple', maxBytes: 256, components: [vector, vector], labels: ['Vector one', 'Vector two'] };
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  function Form() {
    const [value, setValue] = useState('');
    return <><StructuredAnswerInput id="pair" spec={spec} value={value} onChange={setValue} /><output>{value}</output></>;
  }
  try {
    await act(async () => root.render(<Form />));
    expect(host.querySelectorAll('.pl-vector-grid')).toHaveLength(2);
    expect(host.querySelectorAll('input')).toHaveLength(6);
    expect(host.textContent).toContain('either order');
    expect(host.textContent).not.toContain('Keep the displayed order');
    const inputs = [...host.querySelectorAll<HTMLInputElement>('input')];
    for (const [index, input] of inputs.entries()) {
      await act(async () => { Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, String(index)); input.dispatchEvent(new Event('input', { bubbles: true })); });
    }
    expect(host.querySelector('output')?.textContent).toBe('((0;1;2);(3;4;5))');
  } finally { await act(async () => root.unmount()); host.remove(); }
});
