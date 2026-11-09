// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { FeedbackPage } from './FeedbackPage';

function setValue(element: HTMLInputElement | HTMLTextAreaElement, value: string) {
  const setter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), 'value')!.set!;
  setter.call(element, value);
  element.dispatchEvent(new Event('input', { bubbles: true }));
}

async function mount(fetchImpl: typeof fetch) {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const element = document.createElement('div');
  document.body.append(element);
  const root = createRoot(element);
  await act(async () => root.render(<FeedbackPage name="Ada" email="ada@example.com" fetchImpl={fetchImpl} />));
  return { element, unmount: async () => { await act(async () => root.unmount()); element.remove(); } };
}

it('validates in the browser, posts the form and thanks the sender', async () => {
  const now = vi.spyOn(Date, 'now').mockReturnValue(1_000_000);
  const fetchImpl = vi.fn<typeof fetch>(async () => new Response('{"ok":true}', { status: 200 }));
  const { element, unmount } = await mount(fetchImpl);
  const form = element.querySelector('form')!;
  await act(async () => form.requestSubmit());
  expect(element.querySelector('[role="alert"]')?.textContent).toBe('Write a message of at least 10 characters.');
  expect(fetchImpl).not.toHaveBeenCalled();
  await act(async () => setValue(element.querySelector('textarea')!, 'The answer to problem 3 looks wrong.'));
  now.mockReturnValue(1_010_000);
  await act(async () => form.requestSubmit());
  const body = JSON.parse(String(fetchImpl.mock.calls[0][1]!.body));
  expect(body).toMatchObject({ name: 'Ada', email: 'ada@example.com', topic: 'General', website: '', elapsed: 10_000 });
  expect(element.textContent).toContain('Thank you, your message was sent');
  now.mockRestore();
  await unmount();
});

it('points to the mailbox while the form is not connected', async () => {
  const fetchImpl = vi.fn<typeof fetch>(async () => new Response('{"code":"not_configured"}', { status: 503 }));
  const { element, unmount } = await mount(fetchImpl);
  await act(async () => setValue(element.querySelector('textarea')!, 'A long enough message.'));
  await act(async () => element.querySelector('form')!.requestSubmit());
  expect(element.querySelector('[role="alert"]')?.textContent).toContain('practiceloop.support@gmail.com');
  await unmount();
});
