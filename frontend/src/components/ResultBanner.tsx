import type { CheckResult } from '../data/types';
import { CheckIcon, CrossIcon, WarningIcon } from './icons';
import { Tex } from './Tex';

const RESULTS = {
  correct: {
    title: 'Correct',
    message: 'Your answer is mathematically equivalent to the solution.',
    Icon: CheckIcon,
  },
  incorrect: {
    title: 'Incorrect',
    message: 'That is not equivalent to the correct answer. Try again, or reveal it.',
    Icon: CrossIcon,
  },
  invalid: {
    title: 'Invalid expression',
    message: 'We could not read that. Check your brackets and operators.',
    Icon: WarningIcon,
  },
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
    <div id={id} className={`pl-result pl-result--${state} pl-fade`} role={live ? 'status' : undefined}>
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
