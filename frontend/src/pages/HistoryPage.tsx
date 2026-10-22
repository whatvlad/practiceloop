import { useCallback, useEffect, useRef, useState } from 'react';
import { Button, ButtonLink } from '../components/Button';
import { HistoryList } from '../components/HistoryRow';
import { Chips } from '../components/TopicChips';
import { listProblemPage } from '../data/api';
import type { PublicProblem } from '../data/types';
import { HistoryExport, MAX_EXPORT } from './HistoryExport';
import text from '../../../backend/app/content/en.json';

type Filter = 'all' | 'correct' | 'incorrect' | 'none' | 'revealed' | 'worksheet';

const FILTERS: readonly { value: Filter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'correct', label: 'Correct' },
  { value: 'incorrect', label: 'Incorrect' },
  { value: 'none', label: 'Not attempted' },
  { value: 'revealed', label: 'Revealed' },
  { value: 'worksheet', label: 'From worksheets' },
];

function matches(problem: PublicProblem, filter: Filter): boolean {
  switch (filter) {
    case 'all':
    case 'worksheet':
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
  const [filter, setFilter] = useState<Filter>('all');
  const [selected, setSelected] = useState<ReadonlySet<string>>(() => new Set());
  const [limitNote, setLimitNote] = useState('');
  const active = useRef(true);
  const pending = useRef(false);
  const failedCursor = useRef<string | null>(null);
  // The worksheet filter is a server query (#116), so switching to or from it reloads.
  const worksheet = filter === 'worksheet';
  const request = useRef(0);
  const load = useCallback(async (cursor: string | null, fromWorksheets: boolean) => {
    if (pending.current && cursor !== null) return;
    const mine = ++request.current;
    pending.current = true;
    failedCursor.current = cursor;
    setBusy(true);
    setError('');
    try {
      const page = await listProblemPage(fromWorksheets ? { cursor, worksheet: true } : { cursor });
      if (!active.current || mine !== request.current) return;
      setAll(previous => cursor === null ? page.items : [...previous, ...page.items.filter(p => !previous.some(old => old.id === p.id))]);
      setNextCursor(page.nextCursor);
      setLoaded(true);
    } catch (failure) {
      if (active.current && mine === request.current) setError(failure instanceof Error ? failure.message : text.service_error);
    } finally {
      if (mine === request.current) {
        pending.current = false;
        if (active.current) setBusy(false);
      }
    }
  }, []);
  useEffect(() => {
    active.current = true;
    void load(null, worksheet);
    return () => { active.current = false; };
  }, [load, worksheet]);
  const shown = all.filter((p) => matches(p, filter));

  function changeFilter(next: Filter) {
    if (next === filter) return;
    // A selection is made under one filter; a new filter starts a new one.
    setSelected(new Set());
    setLimitNote('');
    if ((next === 'worksheet') !== worksheet) {
      setAll([]);
      setNextCursor(null);
      setLoaded(false);
    }
    setFilter(next);
  }
  function toggle(id: string) {
    setLimitNote('');
    setSelected(previous => {
      const next = new Set(previous);
      if (next.has(id)) next.delete(id);
      else if (next.size < MAX_EXPORT) next.add(id);
      return next;
    });
  }
  function selectAll() {
    const next = new Set(selected);
    const missing = shown.filter(p => !next.has(p.id));
    for (const problem of missing) {
      if (next.size >= MAX_EXPORT) break;
      next.add(problem.id);
    }
    setSelected(next);
    setLimitNote(next.size < selected.size + missing.length ? `Selected ${next.size} problems: one PDF holds at most ${MAX_EXPORT}.` : '');
  }
  function clear() {
    setSelected(new Set());
    setLimitNote('');
  }
  function exported(ids: readonly string[], revealed: boolean) {
    if (revealed) setAll(previous => previous.map(p => ids.includes(p.id) ? { ...p, answerRevealed: true } : p));
    clear();
  }
  const allShownSelected = shown.length > 0 && shown.every(p => selected.has(p.id));

  return (
    <main id="main" tabIndex={-1} className="pl-wrap pl-app-main">
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
        <Chips options={FILTERS} selected={filter} onSelect={changeFilter} label="Filter by result" />
      </div>
      {busy && <p role="status">Loading history…</p>}
      {error && <div role="alert"><p>{error}</p><Button variant="secondary" onClick={() => void load(failedCursor.current, worksheet)} disabled={busy}>Retry loading history</Button></div>}
      {loaded && (
        <>
          {shown.length > 0 && (
            <div className="pl-hselect" role="group" aria-label="Select problems">
              <Button variant="secondary" size="sm" onClick={selectAll} disabled={allShownSelected || selected.size >= MAX_EXPORT}>
                Select all
              </Button>
              <Button variant="ghost" size="sm" onClick={clear} disabled={selected.size === 0}>
                Clear
              </Button>
              <span className="pl-small pl-muted">Tick problems to print them as a PDF.</span>
            </div>
          )}
          <HistoryExport selected={[...selected]} limitNote={limitNote} onExported={exported} />
          {shown.length > 0 ? (
            <HistoryList problems={shown} header selection={{ selected, full: selected.size >= MAX_EXPORT, onToggle: toggle }} />
          ) : (
            <p className="pl-muted">{all.length === 0
              ? worksheet ? 'No problems from worksheets yet. Print a worksheet from the practice page.' : 'No saved problems yet. Generate your first problem from the dashboard.'
              : 'No loaded problems match this filter.'}</p>
          )}
          <p className="pl-small pl-subtle pl-mt-4">
            Showing {shown.length} of {all.length} loaded problems · Select any row to reopen it.
          </p>
          {nextCursor && <Button variant="secondary" onClick={() => void load(nextCursor, worksheet)} disabled={busy}>Load more problems</Button>}
          {nextCursor && filter !== 'all' && !worksheet && <p className="pl-small pl-muted">Load more to include older problems in this filter.</p>}
        </>
      )}
    </main>
  );
}
