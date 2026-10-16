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

export type Difficulty = 1 | 2 | 3 | 4 | 5;

/** The three outcomes the checker can return, and no others. */
export type CheckResult = 'correct' | 'incorrect' | 'invalid';

/** Latest recorded attempt. Invalid expressions are not recorded as attempts. */
export type AttemptResult = 'correct' | 'incorrect' | null;

export interface PublicProblem {
  id: string;
  topic: TopicSlug;
  difficulty: Difficulty;
  problemLatex: string;
  createdAt: string;
  answerRevealed: boolean;
  solutionRevealed: boolean;
  lastResult: AttemptResult;
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

export interface Account {
  name: string;
  email: string;
  provider: 'Google';
}

export interface ProfileCounts {
  generated: number;
  attempted: number;
  correct: number;
}
