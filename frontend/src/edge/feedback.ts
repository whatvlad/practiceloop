// Feedback form backend, run as a Cloudflare Pages Function (functions/api/feedback.ts).
// It emails the support mailbox through Resend; the key is the RESEND_API_KEY Pages secret.
// Without a verified domain Resend only delivers to the account owner's address, so the
// Resend account must belong to the support mailbox.

export const FEEDBACK_TO = 'practiceloop.support@gmail.com';
const FROM = 'MathLoop feedback <onboarding@resend.dev>';
export const LIMITS = { name: 80, email: 254, topic: 60, message: 4000 } as const;
/** A person needs a few seconds to fill the form; bots usually post at once. */
export const MIN_FILL_MS = 3000;
const MAX_BODY = 16_000;
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const TOPICS = ['General', 'A problem or answer is wrong', 'Something does not work', 'Idea or request'] as const;

export interface FeedbackInput {
  name: string;
  email: string;
  topic: string;
  message: string;
  /** Honeypot: hidden from people, so only bots fill it. */
  website: string;
  /** Milliseconds the form was open before sending. */
  elapsed: number;
}

export type FeedbackCheck = { ok: true; value: FeedbackInput } | { ok: false; error: string };

function text(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

/** Shared by the form and the function, so both reject the same input. */
export function checkFeedback(raw: unknown): FeedbackCheck {
  const data = (raw && typeof raw === 'object' ? raw : {}) as Record<string, unknown>;
  const value: FeedbackInput = {
    name: text(data.name),
    email: text(data.email),
    topic: text(data.topic) || 'General',
    message: text(data.message),
    website: text(data.website),
    elapsed: typeof data.elapsed === 'number' && Number.isFinite(data.elapsed) ? data.elapsed : 0,
  };
  if (!value.name) return { ok: false, error: 'Enter your name.' };
  if (value.name.length > LIMITS.name) return { ok: false, error: `Keep your name under ${LIMITS.name} characters.` };
  if (!EMAIL.test(value.email) || value.email.length > LIMITS.email) return { ok: false, error: 'Enter a valid email address, so we can reply.' };
  if (!(TOPICS as readonly string[]).includes(value.topic)) return { ok: false, error: 'Choose a topic from the list.' };
  if (value.message.length < 10) return { ok: false, error: 'Write a message of at least 10 characters.' };
  if (value.message.length > LIMITS.message) return { ok: false, error: `Keep your message under ${LIMITS.message} characters.` };
  return { ok: true, value };
}

function json(status: number, body: Record<string, unknown>): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
}

/** Handles POST /api/feedback: same-origin JSON only, honeypot and timing checks, then one email. */
export async function handleFeedback(request: Request, apiKey: string | undefined, fetchImpl: typeof fetch = fetch): Promise<Response> {
  if (request.method !== 'POST') return json(405, { error: 'Use POST.' });
  const origin = request.headers.get('origin');
  if (origin && origin !== new URL(request.url).origin) return json(403, { error: 'Cross-site requests are not accepted.' });
  if (!(request.headers.get('content-type') ?? '').startsWith('application/json')) return json(415, { error: 'Send JSON.' });
  const body = await request.text();
  if (body.length > MAX_BODY) return json(413, { error: 'The message is too long.' });
  let raw: unknown;
  try { raw = JSON.parse(body); } catch { return json(400, { error: 'The form data could not be read.' }); }
  const checked = checkFeedback(raw);
  if (!checked.ok) return json(400, { error: checked.error });
  const { value } = checked;
  // Bots get the same answer as people, so they learn nothing; nothing is sent.
  if (value.website || value.elapsed < MIN_FILL_MS) return json(200, { ok: true });
  if (!apiKey) return json(503, { error: 'Feedback is not set up yet.', code: 'not_configured' });

  const lines = [
    `Name: ${value.name}`,
    `Email: ${value.email}`,
    `Topic: ${value.topic}`,
    `Page: ${request.headers.get('referer') ?? 'unknown'}`,
    '',
    value.message,
  ];
  try {
    const sent = await fetchImpl('https://api.resend.com/emails', {
      method: 'POST',
      headers: { authorization: `Bearer ${apiKey}`, 'content-type': 'application/json' },
      body: JSON.stringify({
        from: FROM,
        to: [FEEDBACK_TO],
        reply_to: value.email,
        subject: `[MathLoop] ${value.topic}: ${value.name}`.slice(0, 150),
        text: lines.join('\n'),
      }),
    });
    if (!sent.ok) return json(502, { error: 'The message could not be sent. Try again later.' });
  } catch {
    return json(502, { error: 'The message could not be sent. Try again later.' });
  }
  return json(200, { ok: true });
}
