import type { CheckResult, Difficulty, SolutionStep, TopicSlug } from '../data/types';
import { topicName } from '../data/topics';
import { AnswerInput } from './AnswerInput';
import { Button } from './Button';
import { DifficultyDots } from './DifficultyScale';
import { ResultBanner, RevealedAnswer } from './ResultBanner';
import { SolutionSteps } from './SolutionSteps';
import { Tex } from './Tex';

interface ProblemCardProps {
  topic: TopicSlug;
  difficulty: Difficulty;
  problemLatex: string;
  /** Eyebrow at the top right, e.g. "Saved to history". */
  headLabel?: string;
  answer: string;
  onAnswerChange: (value: string) => void;
  result: CheckResult | null;
  /** A request is in flight; buttons wait for it. */
  busy?: boolean;
  onCheck: () => void;
  onShowAnswer: () => void;
  onShowSolution: () => void;
  onNext: () => void;
  /** Present only after the backend returns it for Show Answer. */
  answerLatex?: string | null;
  /** Present only after the backend returns it for Show Solution. */
  solution?: readonly SolutionStep[] | null;
}

/** The one lifted surface: a problem, its answer field and every action on it. */
export function ProblemCard({
  topic,
  difficulty,
  problemLatex,
  headLabel,
  answer,
  onAnswerChange,
  result,
  busy = false,
  onCheck,
  onShowAnswer,
  onShowSolution,
  onNext,
  answerLatex,
  solution,
}: ProblemCardProps) {
  const solved = result === 'correct';
  return (
    <section className="pl-problem" aria-label="Problem">
      <div className="pl-problem-head">
        <div className="meta">
          <span className="pl-tag">Integration — {topicName(topic)}</span>
          <span className="pl-small pl-muted">
            <DifficultyDots level={difficulty} />
          </span>
        </div>
        {headLabel && <span className="pl-label">{headLabel}</span>}
      </div>
      <div className="pl-stack pl-gap-3">
        <p className="pl-lead">Calculate:</p>
        <div className="pl-expr">
          <Tex latex={problemLatex} display />
        </div>
      </div>
      <AnswerInput
        id="answer"
        value={answer}
        onChange={onAnswerChange}
        state={result}
        placeholder="e.g. x^2/2 + C"
        describedBy={result ? 'answer-result' : undefined}
        onEnter={solved || busy ? undefined : onCheck}
        hint={
          <>
            Type notation like <code>sqrt(3)</code>, <code>pi/4 + 2</code>, <code>e^2</code>. Press Enter to check.
          </>
        }
      />
      <div className="pl-result-slot" role="status">{result && <ResultBanner id="answer-result" state={result} live={false} />}</div>
      <Button size="lg" block onClick={onCheck} disabled={solved || busy}>
        Check answer
      </Button>
      <div className="pl-actions">
        <Button variant="secondary" onClick={onShowAnswer} disabled={busy}>
          Show answer
        </Button>
        <Button variant="secondary" onClick={onShowSolution} disabled={busy}>
          Show solution
        </Button>
        <span className="pl-spacer" />
        <Button variant={solved ? 'primary' : 'ghost'} arrow onClick={onNext} disabled={busy}>
          Generate next problem
        </Button>
      </div>
      {answerLatex && <RevealedAnswer latex={answerLatex} />}
      {solution && <SolutionSteps steps={solution} />}
    </section>
  );
}
