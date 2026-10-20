// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

const report = vi.hoisted(() => vi.fn());
vi.mock('../data/api', () => ({ reportProblem: report }));

import { ReportProblem } from './ReportProblem';

let root: Root;
let element: HTMLDivElement;

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  report.mockReset();
  element = document.createElement('div');
  document.body.append(element);
  root = createRoot(element);
});
afterEach(async () => {
  await act(async () => root.unmount());
  element.remove();
});

function button(label: string): HTMLButtonElement {
  return [...element.querySelectorAll('button')].find((b) => b.textContent === label)!;
}

async function openForm() {
  await act(async () => root.render(<ReportProblem problemId="p1" />));
  await act(async () => button('Report a problem').click());
}

it('sends one report with a labelled category and comment, and blocks a double submit', async () => {
  let finish: () => void = () => {};
  report.mockImplementation(() => new Promise<void>((resolve) => { finish = resolve; }));
  await openForm();
  expect(button('Send report').disabled).toBe(true);
  const radio = element.querySelector<HTMLInputElement>('input[value="solution"]')!;
  expect(radio.closest('label')?.textContent).toContain('The answer or solution is wrong');
  await act(async () => radio.click());
  const comment = element.querySelector('textarea')!;
  expect(comment.closest('label')?.textContent).toContain('Comment');
  expect(comment.maxLength).toBe(500);
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')!.set!.call(comment, 'step 2');
    comment.dispatchEvent(new Event('input', { bubbles: true }));
  });
  const form = element.querySelector('form')!;
  await act(async () => { form.requestSubmit(); form.requestSubmit(); });
  expect(report).toHaveBeenCalledTimes(1);
  expect(report).toHaveBeenCalledWith('p1', 'solution', 'step 2');
  expect(button('Sending…').disabled).toBe(true);
  await act(async () => finish());
  expect(element.querySelector('[role="status"]')?.textContent).toBe('Thanks, your report was sent.');
  expect(element.querySelector('form')).toBeNull();
});

it('shows a safe error and keeps the form open', async () => {
  report.mockRejectedValue(new Error('You are going a bit fast. Wait a moment and try again.'));
  await openForm();
  await act(async () => element.querySelector<HTMLInputElement>('input[value="other"]')!.click());
  await act(async () => element.querySelector('form')!.requestSubmit());
  expect(element.querySelector('[role="alert"]')?.textContent).toBe('You are going a bit fast. Wait a moment and try again.');
  expect(element.querySelector('form')).not.toBeNull();
  expect(button('Send report').disabled).toBe(false);
});
