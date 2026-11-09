import { useEffect, useRef, useState } from 'react';
import text from '../../../backend/app/content/en.json';
import { Button, ButtonLink } from '../components/Button';
import { DifficultyDots } from '../components/DifficultyScale';
import { AttemptStatus, HistoryList } from '../components/HistoryRow';
import { ProblemStatement } from '../components/ProblemStatement';
import { generateProblem, getLastSelection, getProfileCounts, listProblemPage } from '../data/api';
import { areaOf, topicName } from '../data/topics';
import type { PublicProblem } from '../data/types';
import { formatWhen } from '../format';
import { Link, navigate } from '../router';
import { useLoad } from '../useLoad';

const FEED = 5;

function LatestProblem({ problem, onNew, busy }: { problem: PublicProblem; onNew: () => void; busy: boolean }) {
  const solved = problem.lastResult === 'correct';
  return (
    <section className="pl-card pl-card--lg pl-home-latest" aria-labelledby="latest-title">
      <div className="pl-home-latest-head">
        <div>
          <h2 id="latest-title" className="pl-label pl-m-0">Last problem</h2>
          <p className="pl-h-md pl-m-0">{topicName(problem.topic)}</p>
        </div>
        <div className="pl-home-latest-meta">
          <DifficultyDots level={problem.difficulty} topic={problem.topic} total={problem.modulusMode ? 3 : 5} />
          <AttemptStatus result={problem.lastResult} />
          <time className="pl-small pl-subtle" dateTime={problem.createdAt}>{formatWhen(problem.createdAt)}</time>
        </div>
      </div>
      <Link className="pl-home-latest-expr" to={`/practice?id=${encodeURIComponent(problem.id)}`} aria-label={`Open the last problem in ${topicName(problem.topic)}`}>
        <ProblemStatement topic={problem.topic} problemLatex={problem.problemLatex} />
      </Link>
      <div className="pl-actions">
        <ButtonLink to={`/practice?id=${encodeURIComponent(problem.id)}`} arrow>{solved ? 'Open problem' : 'Continue solving'}</ButtonLink>
        <Button variant="secondary" onClick={onNew} disabled={busy} aria-busy={busy}>{busy ? 'Generating…' : 'New problem in this topic'}</Button>
      </div>
    </section>
  );
}

/** Signed-in home: the last problem in the centre, then a short activity feed; topics are in the sidebar. */
export function HomePage({ name }: { name: string }) {
  const [revision, setRevision] = useState(0);
  const recent = useLoad(async () => (await listProblemPage({ limit: FEED + 1 })).items, String(revision));
  const counts = useLoad(getProfileCounts, String(revision));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const pending = useRef(false);
  const active = useRef(true);
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);

  async function start(from?: PublicProblem) {
    if (pending.current) return;
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      const choice = from ? { topic: from.topic, difficulty: from.difficulty, area: areaOf(from.topic) } : await getLastSelection();
      const problem = await generateProblem(choice.topic, choice.difficulty, choice.area);
      if (active.current) navigate(`/practice?id=${encodeURIComponent(problem.id)}`);
    } catch (failure) {
      if (active.current) setError(failure instanceof Error ? failure.message : text.service_error);
    } finally {
      pending.current = false;
      if (active.current) setBusy(false);
    }
  }

  const items = recent.status === 'ready' ? recent.data : [];
  const [latest, ...feed] = items;
  const first = name.trim().split(/\s+/)[0];
  return (
    <main id="main" tabIndex={-1} className="pl-home">
      <div className="pl-home-main">
        <h1 className="pl-h-lg pl-home-title">{first ? `Welcome back, ${first}` : 'Welcome back'}</h1>
        {recent.status === 'loading' && <p role="status">Loading your practice…</p>}
        {recent.status === 'error' && <div role="alert" className="pl-card"><p className="pl-m-0">Your recent problems could not be loaded.</p><Button variant="secondary" onClick={() => setRevision(value => value + 1)}>Retry</Button></div>}
        {recent.status === 'ready' && (latest
          ? <LatestProblem problem={latest} onNew={() => void start(latest)} busy={busy} />
          : <section className="pl-card pl-card--lg pl-home-empty" aria-labelledby="empty-title">
              <h2 id="empty-title" className="pl-h-md pl-m-0">Generate your first problem</h2>
              <p className="pl-muted pl-m-0">Choose a topic on the left, or start with an integral.</p>
              <div className="pl-actions">
                <Button arrow onClick={() => void start()} disabled={busy} aria-busy={busy}>{busy ? 'Generating…' : 'Generate a problem'}</Button>
                <ButtonLink to="/random" variant="secondary">Random problems</ButtonLink>
              </div>
            </section>)}
        {error && <p className="pl-result pl-result--invalid" role="alert">{error}</p>}
        {feed.length > 0 && <section className="pl-home-feed" aria-labelledby="feed-title">
          <div className="pl-row pl-section-head">
            <h2 id="feed-title" className="pl-h-md pl-m-0">Recent activity</h2>
            <ButtonLink to="/history" variant="ghost" size="sm" arrow>All history</ButtonLink>
          </div>
          <HistoryList problems={feed.slice(0, FEED)} />
        </section>}
      </div>
      <aside className="pl-home-side" aria-label="Your progress">
        <h2 className="pl-label pl-m-0">Your progress</h2>
        {counts.status === 'ready' && <dl className="pl-home-stats">
          <div><dt>Generated</dt><dd>{counts.data.generated}</dd></div>
          <div><dt>Attempted</dt><dd>{counts.data.attempted}</dd></div>
          <div><dt>Correct</dt><dd>{counts.data.correct}</dd></div>
        </dl>}
        {counts.status === 'loading' && <p className="pl-small pl-muted" role="status">Loading…</p>}
        {counts.status === 'error' && <p className="pl-small pl-muted" role="alert">Statistics could not be loaded.</p>}
        <Link className="pl-small" to="/profile">Profile and settings</Link>
      </aside>
    </main>
  );
}
