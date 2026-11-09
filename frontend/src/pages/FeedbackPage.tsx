import { useRef, useState, type FormEvent } from 'react';
import { Button } from '../components/Button';
import { checkFeedback, LIMITS, TOPICS } from '../edge/feedback';
import { CONTACT_EMAIL } from '../legal';
import { Link } from '../router';

const ENDPOINT = `${import.meta.env.BASE_URL.replace(/\/$/, '')}/api/feedback`;

/** The feedback form; /api/feedback (a Pages Function) emails it to the support mailbox. */
export function FeedbackPage({ name: initialName = '', email: initialEmail = '', fetchImpl = fetch }: { name?: string; email?: string; fetchImpl?: typeof fetch }) {
  const [name, setName] = useState(initialName);
  const [email, setEmail] = useState(initialEmail);
  const [topic, setTopic] = useState<string>(TOPICS[0]);
  const [message, setMessage] = useState('');
  const [website, setWebsite] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);
  const [openedAt] = useState(() => Date.now());
  const pending = useRef(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (pending.current) return;
    const payload = { name, email, topic, message, website, elapsed: Date.now() - openedAt };
    const checked = checkFeedback(payload);
    if (!checked.ok) { setError(checked.error); return; }
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      const response = await fetchImpl(ENDPOINT, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) });
      const body = await response.json().catch(() => ({})) as { error?: string; code?: string };
      if (response.ok) setSent(true);
      else if (body.code === 'not_configured') setError(`The form is not connected yet. Please write to ${CONTACT_EMAIL}.`);
      else setError(body.error ?? `The message could not be sent. Please write to ${CONTACT_EMAIL}.`);
    } catch {
      setError(`The message could not be sent. Check your connection, or write to ${CONTACT_EMAIL}.`);
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }

  return (
    <main id="main" tabIndex={-1} className="pl-wrap pl-wrap--narrow pl-app-main">
      <h1 className="pl-display-md pl-page-title">Feedback</h1>
      {sent ? (
        <section className="pl-card pl-card--lg pl-stack pl-gap-4" role="status">
          <h2 className="pl-h-md pl-m-0">Thank you, your message was sent</h2>
          <p className="pl-muted pl-m-0">We will reply to {email}.</p>
          <div><Button variant="secondary" onClick={() => { setSent(false); setMessage(''); }}>Send another message</Button></div>
        </section>
      ) : (
        <form className="pl-card pl-card--lg pl-feedback" onSubmit={submit} noValidate>
          <p className="pl-muted pl-m-0">Report a wrong answer or a bug, or suggest an idea. We reply by email.</p>
          <div className="pl-feedback-row">
            <label className="pl-field">Name
              <input className="pl-input pl-input--text" name="name" autoComplete="name" maxLength={LIMITS.name} value={name} onChange={e => setName(e.target.value)} disabled={busy} required />
            </label>
            <label className="pl-field">Email
              <input className="pl-input pl-input--text" type="email" name="email" autoComplete="email" maxLength={LIMITS.email} value={email} onChange={e => setEmail(e.target.value)} disabled={busy} required />
            </label>
          </div>
          <label className="pl-field">Topic
            <select className="pl-select" name="topic" value={topic} onChange={e => setTopic(e.target.value)} disabled={busy}>
              {TOPICS.map(item => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label className="pl-field">Message
            <textarea className="pl-input pl-input--text pl-feedback-message" name="message" rows={7} maxLength={LIMITS.message} value={message} onChange={e => setMessage(e.target.value)} disabled={busy} required aria-describedby="feedback-count" />
          </label>
          <p id="feedback-count" className="pl-small pl-subtle pl-m-0">{message.length} / {LIMITS.message}</p>
          {/* Honeypot: off-screen and skipped by keyboard and screen readers, so only bots fill it. */}
          <div className="pl-feedback-trap" aria-hidden="true">
            <label>Website <input name="website" tabIndex={-1} autoComplete="off" value={website} onChange={e => setWebsite(e.target.value)} /></label>
          </div>
          {error && <p className="pl-result pl-result--invalid pl-m-0" role="alert">{error}</p>}
          <div className="pl-actions">
            <Button type="submit" arrow disabled={busy} aria-busy={busy}>{busy ? 'Sending…' : 'Send message'}</Button>
            <span className="pl-small pl-muted">Your name and email are used only to answer you. See <Link to="/privacy">Privacy</Link>.</span>
          </div>
        </form>
      )}
    </main>
  );
}
