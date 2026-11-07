import { DIFFICULTIES } from '../data/topics';
import type { Difficulty } from '../data/types';
import { difficultyLabel } from '../data/difficultyLabels';

interface DifficultyScaleProps {
  selected: Difficulty;
  onSelect: (level: Difficulty) => void;
  labelledBy?: string;
  available?: readonly Difficulty[];
  /** The levels the chosen topic has; the others are hidden rather than disabled. */
  shown?: readonly Difficulty[];
  topic?: string;
}

/** Segmented level picker (up to five), used where the learner chooses. */
export function DifficultyScale({ selected, onSelect, labelledBy, available, shown, topic = '' }: DifficultyScaleProps) {
  const levels = shown?.length ? DIFFICULTIES.filter(({ level }) => shown.includes(level)) : DIFFICULTIES;
  return (
    <div className="pl-seg" role="group" aria-label={labelledBy ? undefined : 'Difficulty'} aria-labelledby={labelledBy}>
      {levels.map(({ level, name }) => (
        <button key={level} type="button" aria-pressed={level === selected} disabled={available !== undefined && !available.includes(level)} title={available !== undefined && !available.includes(level) ? 'Not available yet' : undefined} onClick={() => onSelect(level)}>
          {topic !== 'matrix-operations' && <span className="n">{level}</span>}
          <span className="t">{topic ? difficultyLabel(topic, level) : name}</span>
        </button>
      ))}
    </div>
  );
}

/** Compact indicator wherever a problem's difficulty is shown; always with "n/5". */
export function DifficultyDots({ level, topic, total = 5 }: { level: Difficulty; topic?: string; total?: 3 | 5 }) {
  if (total === 5 && topic === 'matrix-operations' && level <= 3) return <span>{difficultyLabel(topic, level)}</span>;
  return (
    <>
      <span className="pl-dots" role="img" aria-label={`Difficulty ${level} of ${total}`}>
        {DIFFICULTIES.filter(d => d.level <= total).map((d) => (
          <i key={d.level} className={d.level <= level ? 'on' : undefined} />
        ))}
      </span>
      <span aria-hidden="true">{'\u00a0'}{level}/{total}</span>
    </>
  );
}
