import { DIFFICULTIES } from '../data/topics';
import type { Difficulty } from '../data/types';

interface DifficultyScaleProps {
  selected: Difficulty;
  onSelect: (level: Difficulty) => void;
  labelledBy?: string;
  available?: readonly Difficulty[];
}

/** Segmented five-level picker, used where the learner chooses. */
export function DifficultyScale({ selected, onSelect, labelledBy, available }: DifficultyScaleProps) {
  return (
    <div className="pl-seg" role="group" aria-label={labelledBy ? undefined : 'Difficulty'} aria-labelledby={labelledBy}>
      {DIFFICULTIES.map(({ level, name }) => (
        <button key={level} type="button" aria-pressed={level === selected} disabled={available !== undefined && !available.includes(level)} title={available !== undefined && !available.includes(level) ? 'Not available yet' : undefined} onClick={() => onSelect(level)}>
          <span className="n">{level}</span>
          <span className="t">{name}</span>
        </button>
      ))}
    </div>
  );
}

/** Compact indicator wherever a problem's difficulty is shown; always with "n/5". */
export function DifficultyDots({ level }: { level: Difficulty }) {
  return (
    <>
      <span className="pl-dots" role="img" aria-label={`Difficulty ${level} of 5`}>
        {DIFFICULTIES.map((d) => (
          <i key={d.level} className={d.level <= level ? 'on' : undefined} />
        ))}
      </span>
      <span aria-hidden="true">{'\u00a0'}{level}/5</span>
    </>
  );
}
