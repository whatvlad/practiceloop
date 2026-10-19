import type { CheckResult } from '../data/types';
import { CheckIcon, CrossIcon, WarningIcon } from './icons';
import { Tex } from './Tex';
import text from '../../../backend/app/content/en.json';

const RESULTS = {
  correct: {
    title: 'Correct',
    message: text.correct,
    Icon: CheckIcon,
  },
  incorrect: {
    title: 'Incorrect',
    message: text.incorrect,
    Icon: CrossIcon,
  },
  invalid: {
    title: 'Invalid expression',
    message: text.invalid,
    Icon: WarningIcon,
  },
  missing_constant: { title: 'Almost correct', message: text.missing_constant, Icon: WarningIcon },
} as const;

interface ResultBannerProps {
  state: CheckResult;
  message?: string;
  id?: string;
  /** Announce the result to assistive tech. Off for static demos. */
  live?: boolean;
}

/** One of the three checker results: a word, an icon and a colour, never colour alone. */
export function ResultBanner({ state, message, id, live = true }: ResultBannerProps) {
  const { title, message: fallback, Icon } = RESULTS[state];
  return (
    <div id={id} className={`pl-result pl-result--${state === 'missing_constant' ? 'invalid' : state} pl-fade`} role={live ? 'status' : undefined}>
      <Icon />
      <div>
        <b>{title}</b>
        <span>{message ?? fallback}</span>
      </div>
    </div>
  );
}

/** The revealed final answer. Neutral: information, not a verdict. */
export function RevealedAnswer({ latex }: { latex: string }) {
  return (
    <div className="pl-answer pl-fade">
      <div>
        <div className="pl-label pl-answer-label">Answer</div>
        <div className="v">
          <Tex latex={latex} />
        </div>
      </div>
    </div>
  );
}
