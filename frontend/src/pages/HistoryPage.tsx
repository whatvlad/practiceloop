import { useCallback, useEffect, useRef, useState } from 'react';
import { Button, ButtonLink } from '../components/Button';
import { HistoryList } from '../components/HistoryRow';
import { Chips } from '../components/TopicChips';
import { listProblemPage } from '../data/api';
import type { PublicProblem } from '../data/types';
import text from '../../../backend/app/content/en.json';

type Filter = 'all' | 'correct' | 'incorrect' | 'none' | 'revealed';

const FILTERS: readonly { value: Filter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'correct', label: 'Correct' },
  { value: 'incorrect', label: 'Incorrect' },
  { value: 'none', label: 'Not attempted' },
  { value: 'revealed', label: 'Revealed' },
];

function matches(problem: PublicProblem, filter: Filter): boolean {
  switch (filter) {
    case 'all':
      return true;
    case 'correct':
      return problem.lastResult === filter;
    case 'incorrect':
      return problem.lastResult === 'incorrect' || problem.lastResult === 'missing_constant';
    case 'none':
      return problem.lastResult === null;
    case 'revealed':
      return problem.answerRevealed || problem.solutionRevealed;
  }
}

export function HistoryPage() {
  const [all, setAll] = useState<PublicProblem[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const active = useRef(true);
  const pending = useRef(false);
  const failedCursor = useRef<string | null>(null);
  const load = useCallback(async (cursor: string | null) => {
    if (pending.current) return;
    pending.current = true;
    failedCursor.current = cursor;
    setBusy(true);
    setError('');
    try {
      const page = await listProblemPage({ cursor });
      if (!active.current) return;
      setAll(previous => cursor === null ? page.items : [...previous, ...page.items.filter(p => !previous.some(old => old.id === p.id))]);
      setNextCursor(page.nextCursor);
      setLoaded(true);
    } catch (failure) {
      if (active.current) setError(failure instanceof Error ? failure.message : text.service_error);
    } finally {
      pending.current = false;
      if (active.current) setBusy(false);
    }
  }, []);
  useEffect(() => {
    active.current = true;
    void load(null);
    return () => { active.current = false; };
  }, [load]);
  const [filter, setFilter] = useState<Filter>('all');
  const shown = all.filter((p) => matches(p, filter));

  return (
    <main className="pl-wrap pl-app-main">
      <div className="pl-label">History</div>
      <div className="pl-row pl-title-row">
        <h1 className="pl-display-md">
          Every problem, <em>saved.</em>
        </h1>
        <ButtonLink to="/dashboard" arrow>
          New problem
        </ButtonLink>
      </div>
      <div className="pl-mb-5">
        <Chips options={FILTERS} selected={filter} onSelect={setFilter} label="Filter by result" />
      </div>
      {busy && <p role="status">Loading history…</p>}
      {error && <div role="alert"><p>{error}</p><Button variant="secondary" onClick={() => void load(failedCursor.current)} disabled={busy}>Retry loading history</Button></div>}
      {loaded && (
        <>
          {shown.length > 0 ? (
            <HistoryList problems={shown} header />
          ) : (
            <p className="pl-muted">{all.length === 0 ? 'No saved problems yet. Generate your first problem from the dashboard.' : 'No loaded problems match this filter.'}</p>
          )}
          <p className="pl-small pl-subtle pl-mt-4">
            Showing {shown.length} of {all.length} loaded problems · Select any row to reopen it.
          </p>
          {nextCursor && <Button variant="secondary" onClick={() => void load(nextCursor)} disabled={busy}>Load more problems</Button>}
          {nextCursor && filter !== 'all' && <p className="pl-small pl-muted">Load more to include older problems in this filter.</p>}
        </>
      )}
    </main>
  );
}
