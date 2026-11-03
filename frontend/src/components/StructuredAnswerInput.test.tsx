// @vitest-environment jsdom
import { act, useState } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { AnswerInputSpec } from '../data/types';
import { StructuredAnswerInput } from './StructuredAnswerInput';

vi.mock('mathlive', () => ({}));
let root: Root; let element: HTMLDivElement;
function Harness({ kind, initial = '' }: { kind: AnswerInputSpec['kind']; initial?: string }) {
  const [value, setValue] = useState(initial);
  return <><StructuredAnswerInput id="answer" spec={{ kind, maxBytes: 256, ...(kind === 'finite_set' ? { maxItems: 8 } : {}) }} value={value} onChange={setValue} /><output>{value}</output></>;
}
beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  element = document.createElement('div'); document.body.append(element); root = createRoot(element);
});
afterEach(() => { act(() => root.unmount()); element.remove(); });
function click(node: Element) { act(() => node.dispatchEvent(new MouseEvent('click', { bubbles: true }))); }
function change(node: HTMLInputElement | HTMLSelectElement, value: string) {
  const prototype = node instanceof HTMLSelectElement ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
  act(() => { Object.getOwnPropertyDescriptor(prototype, 'value')!.set!.call(node, value); node.dispatchEvent(new Event(node instanceof HTMLSelectElement ? 'change' : 'input', { bubbles: true })); });
}
const wire = () => element.querySelector('output')!.textContent;
it('starts boolean input unselected and preserves reopened false', () => {
  act(() => root.render(<Harness kind="boolean" />));
  const radios = element.querySelectorAll<HTMLInputElement>('input[type=radio]');
  expect([...radios].every(radio => !radio.checked)).toBe(true);
  click(radios[1]); expect(wire()).toBe('false');
  act(() => root.render(<Harness key="reopened" kind="boolean" initial="false" />));
  expect(element.querySelector<HTMLInputElement>('input[value=false]')!.checked).toBe(true);
});
it('keeps unfinished function text while adding/removing set entries', () => {
  act(() => root.render(<Harness kind="finite_set" />));
  change(element.querySelector<HTMLInputElement>('#answer-0')!, 'sqrt(');
  expect(element.querySelector<HTMLInputElement>('#answer-0')!.value).toBe('sqrt(');
  change(element.querySelector<HTMLInputElement>('#answer-0')!, 'sqrt(2)');
  click([...element.querySelectorAll('button')].find(button => button.textContent === 'Add entry')!);
  change(element.querySelector<HTMLInputElement>('#answer-1')!, '1/2');
  expect(wire()).toBe('{sqrt(2),1/2}');
  click([...element.querySelectorAll('button')].find(button => button.textContent === 'Remove entry 1')!);
  expect(wire()).toBe('{1/2}');
  click([...element.querySelectorAll('button')].find(button => button.textContent === 'Empty set')!);
  expect(wire()).toBe('{}');
});
it('serializes open infinite bounds and reopens the exact endpoints', () => {
  act(() => root.render(<Harness kind="interval" initial="[1/3,2]" />));
  expect(element.querySelector<HTMLInputElement>('#answer-0')!.value).toBe('1/3');
  const selects = element.querySelectorAll<HTMLSelectElement>('select');
  change(selects[0], 'unbounded'); expect(wire()).toBe('(-inf,2]');
  expect(selects[1].disabled).toBe(true);
  const checkbox = element.querySelector<HTMLInputElement>('input[type=checkbox]')!;
  click(checkbox); change(element.querySelector<HTMLInputElement>('#answer')!, '(0,3/2]');
  expect(wire()).toBe('(0,3/2]');
  click(checkbox); expect(element.querySelector<HTMLInputElement>('#answer-1')!.value).toBe('3/2');
});

it('preserves whitespace and infinity notation in reopened answers until an edit', () => {
  act(() => root.render(<Harness kind="interval" initial=" [1/3,∞) " />));
  expect(element.querySelectorAll<HTMLSelectElement>('select')[2].value).toBe('unbounded');
  expect(wire()).toBe(' [1/3,∞) ');
  act(() => root.render(<Harness key="bool" kind="boolean" initial=" false " />));
  expect(element.querySelector<HTMLInputElement>('input[value=false]')!.checked).toBe(true);
  expect(wire()).toBe(' false ');
});

it('reopens an invalid saved interval as its original text instead of fabricated endpoints', () => {
  act(() => root.render(<Harness kind="interval" initial="999999" />));
  expect(element.querySelector<HTMLInputElement>('#answer')!.value).toBe('999999');
  expect(element.querySelector('#answer-0')).toBeNull();
  expect(wire()).toBe('999999');
});

it('keeps interval endpoint fields visible while a function is unfinished', () => {
  act(() => root.render(<Harness kind="interval" initial="[0,2]" />));
  change(element.querySelector<HTMLInputElement>('#answer-0')!, 'sqrt(');
  expect(element.querySelector<HTMLInputElement>('#answer-0')!.value).toBe('sqrt(');
  expect(element.querySelector<HTMLInputElement>('#answer-1')!.value).toBe('2');
  expect(element.querySelector<HTMLInputElement>('input[type=checkbox]')!.checked).toBe(false);
  change(element.querySelector<HTMLInputElement>('#answer-0')!, 'sqrt(2)');
  expect(wire()).toBe('[sqrt(2),2]');
});
