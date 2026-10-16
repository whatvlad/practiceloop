import type { PublicProblem } from '../data/types';
import { topicName } from '../data/topics';
import { formatWhen } from '../format';
import { Link } from '../router';
import { DifficultyDots } from './DifficultyScale';
import { CheckIcon, ChevronIcon, CrossIcon, DashIcon } from './icons';
import { Tex } from './Tex';

function AttemptStatus({ result }: { result: PublicProblem['lastResult'] }) {
  if (result === 'correct')
    return (
      <span className="pl-status pl-status--correct">
        <CheckIcon />
        Correct
      </span>
    );
  if (result === 'incorrect')
    return (
      <span className="pl-status pl-status--incorrect">
        <CrossIcon />
        Incorrect
      </span>
    );
  return (
    <span className="pl-status pl-status--none">
      <DashIcon />
      Not attempted
    </span>
  );
}

/** One generated problem; the whole row reopens it in the practice view. */
export function HistoryRow({ problem }: { problem: PublicProblem }) {
  return (
    <Link className="pl-hrow" to={`/practice?id=${encodeURIComponent(problem.id)}`}>
      <div className="m">
        <Tex latex={problem.problemLatex} />
      </div>
      <div>
        <div>{topicName(problem.topic)}</div>
        <div className="pl-small pl-subtle">{formatWhen(problem.createdAt)}</div>
      </div>
      <div className="pl-small pl-muted">
        <DifficultyDots level={problem.difficulty} />
      </div>
      <div>
        <AttemptStatus result={problem.lastResult} />
        {problem.answerRevealed && <div className="pl-small pl-subtle">Answer revealed</div>}
        {problem.solutionRevealed && <div className="pl-small pl-subtle">Solution viewed</div>}
      </div>
      <ChevronIcon className="go" />
    </Link>
  );
}

interface HistoryListProps {
  problems: readonly PublicProblem[];
  /** Column headings; the dashboard's short list leaves them out. */
  header?: boolean;
}

export function HistoryList({ problems, header = false }: HistoryListProps) {
  return (
    <div className="pl-hlist">
      {header && (
        <div className="pl-hhead" aria-hidden="true">
          <span className="pl-label">Problem</span>
          <span className="pl-label">Topic</span>
          <span className="pl-label">Level</span>
          <span className="pl-label">Result</span>
          <span />
        </div>
      )}
      {problems.map((problem) => (
        <HistoryRow key={problem.id} problem={problem} />
      ))}
    </div>
  );
}
