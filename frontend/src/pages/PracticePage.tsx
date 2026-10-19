import { useEffect, useRef, useState } from 'react';
import text from '../../../backend/app/content/en.json';
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
  const answerRevision = useRef(0);
  const [result, setResult] = useState<CheckResult | null>(problem.lastResult);
  const [answerLatex, setAnswerLatex] = useState<string | null>(null);
  const [solution, setSolution] = useState<SolutionStep[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const pending = useRef(false);
  const active = useRef(true);
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);

  // A reopened problem shows what was already revealed for it.
  useEffect(() => {
    let current = true;
    const failed = () => { if (current) setError(text.service_error); };
    if (problem.answerRevealed) void revealAnswer(problem.id).then((r) => { if (current) setAnswerLatex(r.answerLatex); }).catch(failed);
    if (problem.solutionRevealed) void revealSolution(problem.id).then((r) => { if (current) setSolution(r.steps); }).catch(failed);
    return () => { current = false; };
  }, [problem]);

  async function run(task: () => Promise<void>) {
    if (pending.current) return;
    pending.current = true;
    setError('');
    setBusy(true);
    try {
      await task();
    } catch (failure) {
      if (active.current) setError(failure instanceof Error ? failure.message : text.service_error);
    } finally {
      pending.current = false;
      if (active.current) setBusy(false);
    }
  }

  return (
    <>
    {error && <p role="alert">{error}</p>}
    <ProblemCard
      topic={problem.topic}
      difficulty={problem.difficulty}
      problemLatex={problem.problemLatex}
      headLabel={problem.saved ? 'Saved to your account' : 'Temporary practice'}
      answer={answer}
      onAnswerChange={(value) => { answerRevision.current += 1; setAnswer(value); setResult(null); }}
      result={result}
      busy={busy}
      onCheck={() => run(async () => {
        const revision = answerRevision.current;
        const checked = await submitAttempt(problem.id, answer);
        if (active.current && revision === answerRevision.current) setResult(checked);
      })}
      onShowAnswer={() => run(async () => { const revealed = await revealAnswer(problem.id); if (active.current) setAnswerLatex(revealed.answerLatex); })}
      onShowSolution={() => run(async () => { const revealed = await revealSolution(problem.id); if (active.current) setSolution(revealed.steps); })}
      onNext={() =>
        run(async () => {
          const next = await generateProblem(problem.topic, problem.difficulty);
          if (active.current) navigate(practiceUrl(next.id));
        })
      }
      answerLatex={answerLatex}
      solution={solution}
    />
    </>
  );
}

export function PracticePage({ id }: { id: string | null }) {
  const [startError, setStartError] = useState(false);
  useEffect(() => {
    let current = true;
    setStartError(false);
    if (!id) void latestOrNewId().then((latest) => { if (current) navigate(practiceUrl(latest), { replace: true }); }).catch(() => { if (current) setStartError(true); });
    return () => { current = false; };
  }, [id]);
  const problem = useLoad(() => (id ? getProblem(id) : new Promise<never>(() => {})), id ?? '');

  return (
    <main className="pl-wrap pl-wrap--narrow pl-practice-main">
      {problem.status === 'ready' && <PracticeSession key={problem.data.id} problem={problem.data} />}
      {!startError && problem.status === 'loading' && <p role="status">Loading problem…</p>}
      {(startError || problem.status === 'error') && (
        <section className="pl-card pl-card--lg pl-stack pl-gap-4">
          <h1 className="pl-h-lg">
            {problem.status === 'error' && problem.error instanceof NotFoundError ? 'That problem is not in your history.' : text.service_error}
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
