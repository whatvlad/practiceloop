// Public shapes the UI works with. None of them carries an expected answer,
// a solution or generator data: those arrive only from the reveal calls.

export type TopicSlug =
  | 'basic-integrals'
  | 'substitution'
  | 'integration-by-parts'
  | 'rational-functions'
  | 'trigonometric-integrals';

export interface Topic {
  slug: TopicSlug;
  name: string;
}

export interface AvailableTopic extends Topic {
  availableDifficulties: Difficulty[];
}

export type Difficulty = 1 | 2 | 3 | 4 | 5;

/** Three API outcomes plus a display state for the missing_constant feedback code. */
export type CheckResult = 'correct' | 'incorrect' | 'invalid' | 'missing_constant';

/** A declared mistake the checker matched unambiguously (#36); null means a general hint. */
export const FEEDBACK_CODES = [
  'power_rule', 'trig_sign', 'chain_factor', 'log_absolute', 'split_product', 'parts_sign',
  'cycle_factor', 'partial_fraction_sign', 'definite_not_evaluated', 'bounds_reversed', 'definite_constant',
] as const;
export type FeedbackCode = (typeof FEEDBACK_CODES)[number];

export interface CheckOutcome {
  result: CheckResult;
  feedback: FeedbackCode | null;
}

/** Saved practice records invalid expressions too; preview does not. */
export type AttemptResult = CheckResult | null;

export interface PublicProblem {
  attemptCount?: number;
  saved?: boolean;
  id: string;
  topic: TopicSlug;
  difficulty: Difficulty;
  problemLatex: string;
  createdAt: string;
  answerRevealed: boolean;
  solutionRevealed: boolean;
  lastResult: AttemptResult;
  lastFeedback?: FeedbackCode | null;
  lastAnswer: string | null;
}

export interface RevealedAnswer {
  answerLatex: string;
}

export interface SolutionStep {
  say: string;
  latex: string;
}

export interface RevealedSolution {
  steps: SolutionStep[];
}

/** Only the active reopened card receives previously authorized reveal payloads. */
export interface OpenedProblem {
  problem: PublicProblem;
  answer?: RevealedAnswer;
  solution?: RevealedSolution;
}

export interface ProblemPage {
  items: PublicProblem[];
  nextCursor: string | null;
}

export interface Account {
  id: string;
  name: string;
  email: string;
  provider: 'Google';
}

export interface ProfileCounts {
  generated: number;
  attempted: number;
  correct: number;
}

export interface OmissionMetric {
  checkedAttempts: number;
  omitted: number;
  rate: number | null;
}

export interface LearningStatistics extends OmissionMetric {
  byTopicDifficulty: (OmissionMetric & { topic: TopicSlug; difficulty: Difficulty })[];
  weekly: (OmissionMetric & { week: string })[];
}
