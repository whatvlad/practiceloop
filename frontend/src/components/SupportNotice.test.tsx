// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it } from 'vitest';
import { SUPPORT_AFTER_SOLVED, recordSolved } from '../support';
import { SupportNotice } from './SupportNotice';

let element: HTMLDivElement;
let root: Root;
beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  localStorage.clear();
  element = document.createElement('div'); document.body.append(element);
  root = createRoot(element);
});
afterEach(async () => { await act(async () => root.unmount()); element.remove(); });

it('appears on the same page once enough problems are solved, and closes', async () => {
  await act(async () => root.render(<SupportNotice url="https://ko-fi.com/example" />));
  expect(element.textContent).toBe('');
  await act(async () => { for (let i = 0; i < SUPPORT_AFTER_SOLVED; i += 1) recordSolved(); });
  expect(element.querySelector('a')?.getAttribute('href')).toBe('https://ko-fi.com/example');
  const close = Array.from(element.querySelectorAll('button')).find((b) => b.textContent === 'Not now');
  await act(async () => close?.click());
  expect(element.textContent).toBe('');
});
