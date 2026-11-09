// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { FeedbackPage } from './FeedbackPage';

vi.mock('../data/api', () => ({ feedbackToken: async () => null }));

function setValue(element: HTMLInputElement | HTMLTextAreaElement, value: string) {
  const setter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), 'value')!.set!;
  setter.call(element, value);
  element.dispatchEvent(new Event('input', { bubbles: true }));
}

async function mount(fetchImpl: typeof fetch, token: string | null = 'token-1') {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const element = document.createElement('div');
  document.body.append(element);
  const root = createRoot(element);
  await act(async () => root.render(<FeedbackPage name="Ada" email="ada@example.com" fetchImpl={fetchImpl} getToken={async () => token} />));
  return { element, unmount: async () => { await act(async () => root.unmount()); element.remove(); } };
}

it('shows the account email, validates, posts with the session token and thanks the sender', async () => {
  const now = vi.spyOn(Date, 'now').mockReturnValue(1_000_000);
  const fetchImpl = vi.fn<typeof fetch>(async () => new Response('{"ok":true}', { status: 200 }));
  const { element, unmount } = await mount(fetchImpl);
  expect(element.textContent).toContain('ada@example.com');
  expect(element.querySelector('input[name="email"]')).toBeNull();
  const form = element.querySelector('form')!;
  await act(async () => form.requestSubmit());
  expect(element.querySelector('[role="alert"]')?.textContent).toBe('Write a message of at least 10 characters.');
  expect(fetchImpl).not.toHaveBeenCalled();
  await act(async () => setValue(element.querySelector('textarea')!, 'The answer to problem 3 looks wrong.'));
  now.mockReturnValue(1_010_000);
  await act(async () => form.requestSubmit());
  const init = fetchImpl.mock.calls[0][1]!;
  expect((init.headers as Record<string, string>).authorization).toBe('Bearer token-1');
  expect(JSON.parse(String(init.body))).toMatchObject({ name: 'Ada', topic: 'General', website: '', elapsed: 10_000 });
  expect(element.textContent).toContain('Thank you, your message was sent');
  now.mockRestore();
  await unmount();
});

it('asks to sign in again without a session, and points to the mailbox while the form is not connected', async () => {
  const fetchImpl = vi.fn<typeof fetch>(async () => new Response('{"code":"not_configured"}', { status: 503 }));
  const guest = await mount(fetchImpl, null);
  await act(async () => setValue(guest.element.querySelector('textarea')!, 'A long enough message.'));
  await act(async () => guest.element.querySelector('form')!.requestSubmit());
  expect(guest.element.querySelector('[role="alert"]')?.textContent).toBe('Sign in again to send feedback.');
  expect(fetchImpl).not.toHaveBeenCalled();
  await guest.unmount();
  const learner = await mount(fetchImpl);
  await act(async () => setValue(learner.element.querySelector('textarea')!, 'A long enough message.'));
  await act(async () => learner.element.querySelector('form')!.requestSubmit());
  expect(learner.element.querySelector('[role="alert"]')?.textContent).toContain('practiceloop.support@gmail.com');
  await learner.unmount();
});
