import { useState, type FormEvent } from 'react';
import { Logo } from '../components/AppNav';
import { Button, ButtonLink } from '../components/Button';
import { DifficultyDots } from '../components/DifficultyScale';
import { Tex } from '../components/Tex';
import { lookupShare, type ShareLookup } from '../data/shares';
import { topicName } from '../data/topics';
import type { ShareUnavailable } from '../data/types';
import { isDefinite } from '../format';
import { navigate } from '../router';
import { useLoad } from '../useLoad';
import text from '../../../backend/app/content/en.json';

const UNAVAILABLE: Record<ShareUnavailable, { title: string; detail: string }> = {
  invalid: { title: 'That link or code is not valid.', detail: 'Check it for typos, or ask for a new one.' },
  not_found: { title: 'Nothing is shared under this link or code.', detail: 'Check it for typos, or ask for a new one.' },
  expired: { title: 'This shared problem has expired.', detail: 'Shares last 90 days. Ask for a new link.' },
  revoked: { title: 'This problem is no longer shared.', detail: 'Its owner stopped sharing it.' },
};

function CodeForm({ initial = '' }: { initial?: string }) {
  const [code, setCode] = useState(initial);
  function open(event: FormEvent) {
    event.preventDefault();
    if (code.trim()) navigate(`/shared?code=${encodeURIComponent(code.trim())}`);
  }
  return (
    <form className="pl-stack pl-gap-3" onSubmit={open}>
      <label className="pl-field">
        <span className="pl-small pl-muted">Share code</span>
        <input className="pl-input" value={code} onChange={(event) => setCode(event.target.value)} placeholder="K7M2-QX9P" autoComplete="off" spellCheck={false} maxLength={32} />
      </label>
      <div>
        <Button type="submit" arrow disabled={!code.trim()}>Open problem</Button>
      </div>
    </form>
  );
}

function Result({ found }: { found: ShareLookup }) {
  if ('unavailable' in found) {
    const { title, detail } = UNAVAILABLE[found.unavailable];
    return (
      <section className="pl-card pl-card--lg pl-stack pl-gap-4" aria-label="Shared problem">
        <h1 className="pl-h-lg pl-m-0">{title}</h1>
        <p className="pl-muted pl-m-0">{detail}</p>
        <CodeForm />
      </section>
    );
  }
  const { topic, difficulty, problemLatex } = found.problem;
  return (
    <section className="pl-problem" aria-label="Shared problem">
      <div className="pl-problem-head">
        <div className="meta">
          <span className="pl-tag">Integration — {topicName(topic)}</span>
          <span className="pl-small pl-muted">
            <DifficultyDots level={difficulty} />
          </span>
        </div>
        <span className="pl-label">Shared problem</span>
      </div>
      <div className="pl-stack pl-gap-3">
        <p className="pl-lead">{isDefinite(problemLatex) ? text.calculate_definite : text.calculate}</p>
        <div className="pl-expr">
          <Tex latex={problemLatex} display />
        </div>
      </div>
      <p className="pl-small pl-muted pl-m-0">Work it out on paper, then practice problems like it with answer checking and full solutions.</p>
      <div>
        <ButtonLink to="/practice" arrow>Practice integrals</ButtonLink>
      </div>
    </section>
  );
}

/** `/s/<token>` opens a shared link; `/shared` takes a code (#37). */
export function SharedProblemPage({ token, code }: { token: string | null; code: string | null }) {
  const ref = token !== null ? { token } : code !== null ? { code } : null;
  const found = useLoad(() => (ref ? lookupShare(ref) : Promise.resolve(null)), `${token}:${code}`);
  return (
    <div className="pl-page">
      <header className="pl-nav pl-nav--bare">
        <Logo />
        <ButtonLink to="/login" variant="secondary" size="sm" pill>Sign in</ButtonLink>
      </header>
      <main id="main" tabIndex={-1} className="pl-wrap pl-wrap--narrow pl-practice-main pl-stack pl-gap-5">
        {!ref && (
          <section className="pl-card pl-card--lg pl-stack pl-gap-4" aria-label="Open a shared problem">
            <h1 className="pl-h-lg pl-m-0">Open a shared problem</h1>
            <p className="pl-muted pl-m-0">Enter the code someone gave you.</p>
            <CodeForm />
          </section>
        )}
        {ref && found.status === 'loading' && <p role="status">Loading shared problem…</p>}
        {ref && found.status === 'ready' && found.data && <Result found={found.data} />}
        {ref && found.status === 'error' && (
          <section className="pl-card pl-card--lg pl-stack pl-gap-4" role="alert">
            <h1 className="pl-h-lg pl-m-0">{found.error instanceof Error ? found.error.message : text.service_error}</h1>
          </section>
        )}
      </main>
    </div>
  );
}
