// @vitest-environment jsdom
import { act, useState } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { ComputationalInputSpec } from '../data/types';
import { StructuredAnswerInput } from './StructuredAnswerInput';

let root: Root; let element: HTMLDivElement;
const tuple: ComputationalInputSpec = { kind: 'tuple', maxBytes: 256,
  components: [{ kind: 'formula', maxBytes: 256 }, { kind: 'real_set', maxBytes: 256, maxItems: 8 }], labels: ['Value', 'Domain'] };
const enter = vi.fn();
function Harness({ spec = tuple, initial = '' }: { spec?: ComputationalInputSpec; initial?: string }) {
  const [value, setValue] = useState(initial);
  return <><StructuredAnswerInput id="answer" spec={spec} value={value} onChange={setValue} onEnter={enter} /><output>{value}</output></>;
}
beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  element = document.createElement('div'); document.body.append(element); root = createRoot(element); enter.mockClear();
});
afterEach(() => { act(() => root.unmount()); element.remove(); });
function change(input: HTMLInputElement, value: string) {
  act(() => { Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, value); input.dispatchEvent(new Event('input', { bubbles: true })); });
}

it('reopens complete ordered results with named fields and submits unchanged notation', () => {
  act(() => root.render(<Harness initial={'(sqrt(2);R\\{0})'} />));
  const fields = element.querySelectorAll<HTMLInputElement>('input[type=text], input:not([type])');
  expect([...element.querySelectorAll('legend')].map(x => x.textContent)).toEqual(['Your answer', 'Value', 'Domain']);
  expect([...fields].map(x => x.value)).toEqual(['sqrt(2)', 'R\\{0}']);
  change(fields[0], '1/2');
  expect(element.querySelector('output')!.textContent).toBe('(1/2;R\\{0})');
  act(() => fields[0].dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })));
  expect(enter).toHaveBeenCalledTimes(1);
});

it('preserves malformed historical input until an explicit edit', () => {
  act(() => root.render(<Harness initial="(1,2)" />));
  expect(element.querySelector<HTMLInputElement>('#answer')!.value).toBe('(1,2)');
  expect(element.querySelector('output')!.textContent).toBe('(1,2)');
  change(element.querySelector<HTMLInputElement>('#answer')!, '(1;{})');
  expect(element.querySelector('output')!.textContent).toBe('(1;{})');
});

it('offers server-declared named categories without preselecting an answer', () => {
  act(() => root.render(<Harness spec={{ kind: 'category', maxBytes: 256, choices: ['absolute', 'conditional', 'divergent'] }} />));
  const radios = element.querySelectorAll<HTMLInputElement>('input[type=radio]');
  expect([...radios].every(x => !x.checked)).toBe(true);
  act(() => radios[1].click());
  expect(element.querySelector('output')!.textContent).toBe('conditional');
});
