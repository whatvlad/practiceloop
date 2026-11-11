import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Logo } from '../components/AppNav';
import { Button, ButtonLink } from '../components/Button';
import { DifficultyDots } from '../components/DifficultyScale';
import { ProblemStatement } from '../components/ProblemStatement';
import { lookupShare, type ShareLookup } from '../data/shares';
import { practiceCodeProblem, practiceSharedProblem } from '../data/api';
import { lookupProblemCode } from '../data/problemCodes';
import { problemTag } from '../data/topics';
import type { ShareUnavailable } from '../data/types';
import { navigate } from '../router';
import { useLoad } from '../useLoad';
import text from '../../../backend/app/content/en.json';

const UNAVAILABLE: Record<ShareUnavailable, { title: string; detail: string }> = {
  invalid: { title: 'That link or code is not valid.', detail: 'Check it for typos, or ask for a new one.' },
  not_found: { title: 'Nothing is shared under this link or code.', detail: 'Check it for typos, or ask for a new one.' },
  expired: { title: 'This shared problem has expired.', detail: 'Shares last 90 days. Ask for a new link.' },
  revoked: { title: 'This problem is no longer shared.', detail: 'Its owner stopped sharing it.' },
};

function CodeForm({ initial = '', permanent = false }: { initial?: string; permanent?: boolean }) {
  const [code, setCode] = useState(initial);
  function open(event: FormEvent) {
    event.preventDefault();
    if (code.trim()) navigate(permanent ? `/p/${encodeURIComponent(code.trim())}` : `/shared?code=${encodeURIComponent(code.trim())}`);
  }
  return (
    <form className="pl-stack pl-gap-3" onSubmit={open}>
      <label className="pl-field">
        <span className="pl-small pl-muted">{permanent ? 'Problem code' : 'Share code'}</span>
        <input className="pl-input" value={code} onChange={(event) => setCode(event.target.value)} placeholder={permanent ? 'CMB-1-0000000000000000-00' : 'K7M2-QX9P'} autoComplete="off" spellCheck={false} maxLength={permanent ? 128 : 32} />
      </label>
      <div>
        <Button type="submit" arrow disabled={!code.trim()}>Open problem</Button>
      </div>
    </form>
  );
}

type ShareRef = { token: string } | { code: string } | { problemCode: string };

function Result({ found, shareRef, signedIn, authLoading, inactive }: { found: ShareLookup; shareRef: ShareRef; signedIn: boolean; authLoading: boolean; inactive: boolean }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const pending = useRef(false);
  const active = useRef(true);
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);
  const permanent = 'problemCode' in shareRef;
  const path = 'problemCode' in shareRef ? `/p/${encodeURIComponent(shareRef.problemCode)}` : 'token' in shareRef ? `/s/${shareRef.token}` : `/shared?code=${encodeURIComponent(shareRef.code)}`;
  const signIn = `/login?next=${encodeURIComponent(path)}`;

  async function solve() {
    if (pending.current) return;
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      const problem = await ('problemCode' in shareRef ? practiceCodeProblem(shareRef.problemCode) : practiceSharedProblem(shareRef));
      if (active.current) navigate(`/practice?id=${encodeURIComponent(problem.id)}`);
    } catch (failure) {
      if (active.current) setError(failure instanceof Error ? failure.message : text.service_error);
    } finally {
      pending.current = false;
      if (active.current) setBusy(false);
    }
  }
  if ('unavailable' in found) {
    const { title, detail } = UNAVAILABLE[found.unavailable];
    return (
      <section className="pl-card pl-card--lg pl-stack pl-gap-4" aria-label={permanent ? 'Problem from code' : 'Shared problem'}>
        <h1 className="pl-h-lg pl-m-0">{permanent ? 'That problem code is not valid or is unknown.' : title}</h1>
        <p className="pl-muted pl-m-0">{permanent ? 'Check the code for typos and try again.' : detail}</p>
        <CodeForm permanent={permanent} />
      </section>
    );
  }
  const { topic, difficulty, problemLatex, promptVisual } = found.problem;
  return (
    <section className="pl-problem" aria-label={permanent ? 'Problem from code' : 'Shared problem'}>
      <h1 className="pl-sr-only">{permanent ? 'Problem from code' : 'Shared problem'}</h1>
      <div className="pl-problem-head">
        <div className="meta">
          <span className="pl-tag">{problemTag(topic)}</span>
          <span className="pl-small pl-muted">
            <DifficultyDots level={difficulty} />
          </span>
        </div>
        <span className="pl-label">{permanent ? 'Problem from code' : 'Shared problem'}</span>
      </div>
      <ProblemStatement topic={topic} problemLatex={problemLatex} promptVisual={promptVisual} />
      {inactive ? <p className="pl-h-lg" role="status">Coming soon</p> : <p className="pl-small pl-muted pl-m-0">Solve this problem with answer checking and a full solution. Your work is saved separately in your own history.</p>}
      {error && <p role="alert">{error}</p>}
      <div>
        {!inactive && (signedIn
          ? <Button onClick={() => void solve()} disabled={busy} aria-busy={busy} arrow>{busy ? 'Opening problem…' : 'Solve this problem'}</Button>
          : authLoading
            ? <Button disabled>Restoring your session…</Button>
            : <ButtonLink to={signIn} arrow>Sign in to solve this problem</ButtonLink>)}
      </div>
    </section>
  );
}

/** `/s/<token>` opens a shared link; `/shared` takes a code (#37). */
export function SharedProblemPage({ token, code, problemCode, signedIn = false, authLoading = false, inactive = false }: { token: string | null; code: string | null; problemCode?: string; signedIn?: boolean; authLoading?: boolean; inactive?: boolean }) {
  const ref: ShareRef | null = problemCode !== undefined ? { problemCode } : token !== null ? { token } : code !== null ? { code } : null;
  const referenceKey = `${token}:${code}:${problemCode}`;
  const found = useLoad(() => (ref ? 'problemCode' in ref ? lookupProblemCode(ref.problemCode) : lookupShare(ref) : Promise.resolve(null)), referenceKey);
  const returnPath = problemCode !== undefined ? `/p/${encodeURIComponent(problemCode)}` : token !== null ? `/s/${token}` : code !== null ? `/shared?code=${encodeURIComponent(code)}` : null;
  return (
    <div className="pl-page">
      <header className="pl-nav pl-nav--bare">
        <Logo />
        <ButtonLink to={signedIn ? '/dashboard' : returnPath ? `/login?next=${encodeURIComponent(returnPath)}` : '/login'} variant="secondary" size="sm" pill>{signedIn ? 'Dashboard' : 'Sign in'}</ButtonLink>
      </header>
      <main id="main" tabIndex={-1} className="pl-wrap pl-wrap--narrow pl-practice-main pl-stack pl-gap-5">
        {!ref && (
          <section className="pl-card pl-card--lg pl-stack pl-gap-4" aria-label="Open a shared problem">
            <h1 className="pl-h-lg pl-m-0">Open a shared problem</h1>
            <p className="pl-muted pl-m-0">Enter the code someone gave you.</p>
            <CodeForm />
          </section>
        )}
        {ref && found.status === 'loading' && <p role="status">{problemCode !== undefined ? 'Loading problem…' : 'Loading shared problem…'}</p>}
        {ref && found.status === 'ready' && found.data && <Result key={referenceKey} found={found.data} shareRef={ref} signedIn={signedIn} authLoading={authLoading} inactive={inactive} />}
        {ref && found.status === 'error' && (
          <section className="pl-card pl-card--lg pl-stack pl-gap-4" role="alert">
            <h1 className="pl-h-lg pl-m-0">{found.error instanceof Error ? found.error.message : text.service_error}</h1>
          </section>
        )}
      </main>
    </div>
  );
}
