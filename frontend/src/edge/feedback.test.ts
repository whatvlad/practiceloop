import { describe, expect, it, vi } from 'vitest';
import { checkFeedback, FEEDBACK_TO, handleFeedback } from './feedback';

const valid = { name: 'Ada', topic: 'General', message: 'The integral answer looks wrong.', website: '', elapsed: 8000 };
const env = { RESEND_API_KEY: 'key', SUPABASE_URL: 'https://project.supabase.co/', SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_x' };
const post = (body: unknown, headers: Record<string, string> = {}) => new Request('https://mathloop.pages.dev/api/feedback', {
  method: 'POST',
  headers: { 'content-type': 'application/json', origin: 'https://mathloop.pages.dev', authorization: 'Bearer token-1', ...headers },
  body: JSON.stringify(body),
});
/** Supabase answers the token check with the account; Resend accepts the email. */
const services = (user: Response = new Response('{"email":"ada@example.com"}', { status: 200 })) => vi.fn<typeof fetch>(async input =>
  String(input).endsWith('/auth/v1/user') ? user.clone() : new Response('{"id":"1"}', { status: 200 }));

describe('checkFeedback', () => {
  it('accepts a complete message and trims it', () => {
    expect(checkFeedback({ ...valid, name: '  Ada ' })).toEqual({ ok: true, value: valid });
  });
  it.each([
    [{ name: '' }, 'Enter your name.'],
    [{ topic: 'Spam' }, 'Choose a topic from the list.'],
    [{ message: 'short' }, 'Write a message of at least 10 characters.'],
    [{ message: 'x'.repeat(4001) }, 'Keep your message under 4000 characters.'],
  ])('rejects %o', (change, error) => {
    expect(checkFeedback({ ...valid, ...change })).toEqual({ ok: false, error });
  });
});

describe('handleFeedback', () => {
  it('replies to the signed-in account, never to an address in the form', async () => {
    const fetchImpl = services();
    const response = await handleFeedback(post({ ...valid, email: 'someone-else@example.com' }), env, fetchImpl);
    expect(response.status).toBe(200);
    const [userUrl, userInit] = fetchImpl.mock.calls[0];
    expect(userUrl).toBe('https://project.supabase.co/auth/v1/user');
    expect((userInit!.headers as Record<string, string>).authorization).toBe('Bearer token-1');
    const [url, init] = fetchImpl.mock.calls[1];
    expect(url).toBe('https://api.resend.com/emails');
    expect((init!.headers as Record<string, string>).authorization).toBe('Bearer key');
    const sent = JSON.parse(String(init!.body));
    expect(sent.to).toEqual([FEEDBACK_TO]);
    expect(sent.reply_to).toBe('ada@example.com');
    expect(sent.text).toContain('Account: ada@example.com');
    expect(sent.text).not.toContain('someone-else');
  });

  it('refuses guests and expired sessions', async () => {
    const fetchImpl = services(new Response('{}', { status: 401 }));
    const guest = await handleFeedback(post(valid, { authorization: '' }), env, fetchImpl);
    expect(guest.status).toBe(401);
    expect(fetchImpl).not.toHaveBeenCalled();
    expect((await handleFeedback(post(valid), env, fetchImpl)).status).toBe(401);
    expect(fetchImpl.mock.calls.some(([url]) => String(url).includes('resend'))).toBe(false);
  });

  it.each([{ website: 'https://spam.example' }, { elapsed: 500 }])('answers bots like people but sends nothing: %o', async change => {
    const fetchImpl = services();
    expect((await handleFeedback(post({ ...valid, ...change }), env, fetchImpl)).status).toBe(200);
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it('refuses other sites, other methods, non-JSON and oversized bodies', async () => {
    const fetchImpl = services();
    expect((await handleFeedback(post(valid, { origin: 'https://evil.example' }), env, fetchImpl)).status).toBe(403);
    expect((await handleFeedback(new Request('https://mathloop.pages.dev/api/feedback'), env, fetchImpl)).status).toBe(405);
    expect((await handleFeedback(post(valid, { 'content-type': 'text/plain' }), env, fetchImpl)).status).toBe(415);
    expect((await handleFeedback(post({ ...valid, message: 'x'.repeat(20000) }), env, fetchImpl)).status).toBe(413);
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it('says when the mail key is missing or the provider fails', async () => {
    const missing = await handleFeedback(post(valid), { ...env, RESEND_API_KEY: undefined }, services());
    expect(missing.status).toBe(503);
    expect(await missing.json()).toMatchObject({ code: 'not_configured' });
    const failing = vi.fn<typeof fetch>(async input => String(input).endsWith('/auth/v1/user')
      ? new Response('{"email":"ada@example.com"}') : new Response('no', { status: 500 }));
    expect((await handleFeedback(post(valid), env, failing)).status).toBe(502);
  });
});
