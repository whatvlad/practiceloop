import { useEffect, useState } from 'react';
import { ButtonLink } from '../components/Button';
import { ProblemCard } from '../components/ProblemCard';
import {
  NotFoundError,
  generateProblem,
  getLastSelection,
  getProblem,
  listProblems,
  revealAnswer,
  revealSolution,
  submitAttempt,
} from '../data/api';
import type { CheckResult, PublicProblem, SolutionStep } from '../data/types';
import { navigate } from '../router';
import { useLoad } from '../useLoad';

/** Opens the most recent problem, or generates one when history is empty. */
async function latestOrNewId(): Promise<string> {
  const [latest] = await listProblems();
  if (latest) return latest.id;
  const { topic, difficulty } = await getLastSelection();
  return (await generateProblem(topic, difficulty)).id;
}

function practiceUrl(id: string): string {
  return `/practice?id=${encodeURIComponent(id)}`;
}

function PracticeSession({ problem }: { problem: PublicProblem }) {
  const [answer, setAnswer] = useState(problem.lastAnswer ?? '');
  const [result, setResult] = useState<CheckResult | null>(problem.lastResult);
  const [answerLatex, setAnswerLatex] = useState<string | null>(null);
  const [solution, setSolution] = useState<SolutionStep[] | null>(null);
  const [busy, setBusy] = useState(false);

  // A reopened problem shows what was already revealed for it.
  useEffect(() => {
    if (problem.answerRevealed) void revealAnswer(problem.id).then((r) => setAnswerLatex(r.answerLatex));
    if (problem.solutionRevealed) void revealSolution(problem.id).then((r) => setSolution(r.steps));
  }, [problem]);

  async function run(task: () => Promise<void>) {
    setBusy(true);
    try {
      await task();
    } finally {
      setBusy(false);
    }
  }

  return (
    <ProblemCard
      topic={problem.topic}
      difficulty={problem.difficulty}
      problemLatex={problem.problemLatex}
      headLabel="Saved to history"
      answer={answer}
      onAnswerChange={setAnswer}
      result={result}
      busy={busy}
      onCheck={() => run(async () => setResult(await submitAttempt(problem.id, answer)))}
      onShowAnswer={() => run(async () => setAnswerLatex((await revealAnswer(problem.id)).answerLatex))}
      onShowSolution={() => run(async () => setSolution((await revealSolution(problem.id)).steps))}
      onNext={() =>
        run(async () => navigate(practiceUrl((await generateProblem(problem.topic, problem.difficulty)).id)))
      }
      answerLatex={answerLatex}
      solution={solution}
    />
  );
}

export function PracticePage({ id }: { id: string | null }) {
  useEffect(() => {
    if (!id) void latestOrNewId().then((latest) => navigate(practiceUrl(latest), { replace: true }));
  }, [id]);
  const problem = useLoad(() => (id ? getProblem(id) : new Promise<never>(() => {})), id ?? '');

  return (
    <main className="pl-wrap pl-wrap--narrow pl-practice-main">
      {problem.status === 'ready' && <PracticeSession key={problem.data.id} problem={problem.data} />}
      {problem.status === 'error' && (
        <section className="pl-card pl-card--lg pl-stack pl-gap-4">
          <h1 className="pl-h-lg">
            {problem.error instanceof NotFoundError ? 'That problem is not in your history.' : 'Something went wrong.'}
          </h1>
          <p className="pl-muted pl-m-0">Start a new problem from the dashboard.</p>
          <div>
            <ButtonLink to="/dashboard" arrow>
              Go to dashboard
            </ButtonLink>
          </div>
        </section>
      )}
    </main>
  );
}
