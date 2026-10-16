import { useState } from 'react';
import { ButtonLink } from '../components/Button';
import { HistoryList } from '../components/HistoryRow';
import { Chips } from '../components/TopicChips';
import { listProblems } from '../data/api';
import type { PublicProblem } from '../data/types';
import { useLoad } from '../useLoad';

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
    case 'incorrect':
      return problem.lastResult === filter;
    case 'none':
      return problem.lastResult === null;
    case 'revealed':
      return problem.answerRevealed || problem.solutionRevealed;
  }
}

export function HistoryPage() {
  const problems = useLoad(listProblems);
  const [filter, setFilter] = useState<Filter>('all');
  const all = problems.status === 'ready' ? problems.data : [];
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
      {problems.status === 'ready' && (
        <>
          {shown.length > 0 ? (
            <HistoryList problems={shown} header />
          ) : (
            <p className="pl-muted">No problems match this filter.</p>
          )}
          <p className="pl-small pl-subtle pl-mt-4">
            Showing {shown.length} of {all.length} problems · Select any row to reopen it.
          </p>
        </>
      )}
    </main>
  );
}
