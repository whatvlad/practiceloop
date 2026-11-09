// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it } from 'vitest';
import { SupportPage } from './SupportPage';

let element: HTMLDivElement;
let root: Root;
beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  element = document.createElement('div'); document.body.append(element);
  root = createRoot(element);
});
afterEach(async () => { await act(async () => root.unmount()); element.remove(); });

it('loads the Ko-fi panel only after the visitor asks for it', async () => {
  await act(async () => root.render(<SupportPage url="https://ko-fi.com/mathloop" />));
  expect(element.querySelector('iframe')).toBeNull();
  const show = Array.from(element.querySelectorAll('button')).find((b) => b.textContent === 'Show the donation form');
  await act(async () => show?.click());
  const frame = element.querySelector('iframe');
  expect(frame?.getAttribute('src')).toBe('https://ko-fi.com/mathloop/?hidefeed=true&widget=true&embed=true&preview=true');
  expect(frame?.getAttribute('allow')).toBe('payment');
});

it('shows no form without a support page', async () => {
  await act(async () => root.render(<SupportPage url="" />));
  expect(element.querySelector('button, iframe')).toBeNull();
});
