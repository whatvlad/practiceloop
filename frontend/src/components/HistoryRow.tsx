import type { PublicProblem } from '../data/types';
import { topicName } from '../data/topics';
import { formatWhen } from '../format';
import { Link } from '../router';
import { DifficultyDots } from './DifficultyScale';
import { CheckIcon, ChevronIcon, CrossIcon, DashIcon } from './icons';
import { Tex } from './Tex';

export function AttemptStatus({ result }: { result: PublicProblem['lastResult'] }) {
  if (result === 'correct')
    return (
      <span className="pl-status pl-status--correct">
        <CheckIcon />
        Correct
      </span>
    );
  if (result === 'incorrect' || result === 'missing_constant')
    return (
      <span className="pl-status pl-status--incorrect">
        <CrossIcon />
        Incorrect
      </span>
    );
  if (result === 'invalid') return <span className="pl-status pl-status--none">Invalid expression</span>;
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
        {problem.promptVisual && <p className="pl-small pl-subtle">{problem.promptVisual.description}</p>}
      </div>
      <div>
        <div>{topicName(problem.topic)}</div>
        <time className="pl-small pl-subtle" dateTime={problem.createdAt} title={new Date(problem.createdAt).toLocaleString()}>{formatWhen(problem.createdAt)}</time>
        {problem.lastAnswer !== null && <div className="pl-small pl-subtle pl-history-answer">Latest answer: <code>{problem.lastAnswer}</code></div>}
      </div>
      <div className="pl-small pl-muted">
        <DifficultyDots level={problem.difficulty} />
      </div>
      <div>
        <AttemptStatus result={problem.lastResult} />
        {problem.attemptCount !== undefined && <div className="pl-small pl-subtle">{problem.attemptCount} {problem.attemptCount === 1 ? 'attempt' : 'attempts'}</div>}
        {problem.answerRevealed && <div className="pl-small pl-subtle">Answer revealed</div>}
        {problem.solutionRevealed && <div className="pl-small pl-subtle">Solution viewed</div>}
        {problem.worksheetId && <div className="pl-small pl-subtle">From a worksheet</div>}
      </div>
      <ChevronIcon className="go" />
    </Link>
  );
}

/** Row checkboxes for the History export (#118); the dashboard list has none. */
export interface RowSelection {
  selected: ReadonlySet<string>;
  /** True when the selection is full, so unselected rows cannot be added. */
  full: boolean;
  onToggle: (id: string) => void;
}

/** The checkbox sits beside the row's link, so ticking it never opens the problem. */
function SelectableRow({ problem, selection }: { problem: PublicProblem; selection: RowSelection }) {
  const checked = selection.selected.has(problem.id);
  return (
    <div className={`pl-hitem${checked ? ' is-selected' : ''}`}>
      <label className="pl-hcheck">
        <input
          type="checkbox"
          checked={checked}
          disabled={!checked && selection.full}
          onChange={() => selection.onToggle(problem.id)}
          aria-label={`Select ${topicName(problem.topic)}, level ${problem.difficulty}, ${formatWhen(problem.createdAt)}`}
        />
      </label>
      <HistoryRow problem={problem} />
    </div>
  );
}

interface HistoryListProps {
  problems: readonly PublicProblem[];
  /** Column headings; the dashboard's short list leaves them out. */
  header?: boolean;
  selection?: RowSelection;
}

export function HistoryList({ problems, header = false, selection }: HistoryListProps) {
  return (
    <div className={`pl-hlist${selection ? ' pl-hlist--select' : ''}`}>
      {header && (
        <div className="pl-hhead" aria-hidden="true">
          {selection && <span />}
          <span className="pl-label">Problem</span>
          <span className="pl-label">Topic</span>
          <span className="pl-label">Level</span>
          <span className="pl-label">Result</span>
          <span />
        </div>
      )}
      {problems.map((problem) =>
        selection ? (
          <SelectableRow key={problem.id} problem={problem} selection={selection} />
        ) : (
          <HistoryRow key={problem.id} problem={problem} />
        ),
      )}
    </div>
  );
}
