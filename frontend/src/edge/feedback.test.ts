import { describe, expect, it, vi } from 'vitest';
import { checkFeedback, FEEDBACK_TO, handleFeedback } from './feedback';

const valid = { name: 'Ada', email: 'ada@example.com', topic: 'General', message: 'The integral answer looks wrong.', website: '', elapsed: 8000 };
const post = (body: unknown, headers: Record<string, string> = {}) => new Request('https://mathloop.pages.dev/api/feedback', {
  method: 'POST', headers: { 'content-type': 'application/json', origin: 'https://mathloop.pages.dev', ...headers }, body: JSON.stringify(body),
});
const resend = () => vi.fn<typeof fetch>(async () => new Response('{"id":"1"}', { status: 200 }));

describe('checkFeedback', () => {
  it('accepts a complete message and trims it', () => {
    expect(checkFeedback({ ...valid, name: '  Ada ' })).toEqual({ ok: true, value: valid });
  });
  it.each([
    [{ name: '' }, 'Enter your name.'],
    [{ email: 'not-an-email' }, 'Enter a valid email address, so we can reply.'],
    [{ topic: 'Spam' }, 'Choose a topic from the list.'],
    [{ message: 'short' }, 'Write a message of at least 10 characters.'],
    [{ message: 'x'.repeat(4001) }, 'Keep your message under 4000 characters.'],
  ])('rejects %o', (change, error) => {
    expect(checkFeedback({ ...valid, ...change })).toEqual({ ok: false, error });
  });
});

describe('handleFeedback', () => {
  it('emails the support mailbox with a reply-to of the sender', async () => {
    const fetchImpl = resend();
    const response = await handleFeedback(post(valid), 'key', fetchImpl);
    expect(response.status).toBe(200);
    const [url, init] = fetchImpl.mock.calls[0];
    expect(url).toBe('https://api.resend.com/emails');
    expect((init!.headers as Record<string, string>).authorization).toBe('Bearer key');
    const sent = JSON.parse(String(init!.body));
    expect(sent.to).toEqual([FEEDBACK_TO]);
    expect(sent.reply_to).toBe('ada@example.com');
    expect(sent.text).toContain('The integral answer looks wrong.');
  });

  it.each([{ website: 'https://spam.example' }, { elapsed: 500 }])('answers bots like people but sends nothing: %o', async change => {
    const fetchImpl = resend();
    expect((await handleFeedback(post({ ...valid, ...change }), 'key', fetchImpl)).status).toBe(200);
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it('refuses other sites, other methods, non-JSON and oversized bodies', async () => {
    const fetchImpl = resend();
    expect((await handleFeedback(post(valid, { origin: 'https://evil.example' }), 'key', fetchImpl)).status).toBe(403);
    expect((await handleFeedback(new Request('https://mathloop.pages.dev/api/feedback'), 'key', fetchImpl)).status).toBe(405);
    expect((await handleFeedback(post(valid, { 'content-type': 'text/plain' }), 'key', fetchImpl)).status).toBe(415);
    expect((await handleFeedback(post({ ...valid, message: 'x'.repeat(20000) }), 'key', fetchImpl)).status).toBe(413);
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it('says when the mail key is missing or the provider fails', async () => {
    const missing = await handleFeedback(post(valid), undefined, resend());
    expect(missing.status).toBe(503);
    expect(await missing.json()).toMatchObject({ code: 'not_configured' });
    const failing = vi.fn<typeof fetch>(async () => new Response('no', { status: 500 }));
    expect((await handleFeedback(post(valid), 'key', failing)).status).toBe(502);
  });
});
