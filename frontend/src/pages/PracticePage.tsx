import { useEffect, useRef, useState } from 'react';
import text from '../../../backend/app/content/en.json';
import { Button, ButtonLink } from '../components/Button';
import { ProblemCard } from '../components/ProblemCard';
import {
  NotFoundError,
  generateProblem,
  getLastSelection,
  openProblem,
  openDemo,
  listProblemPage,
  revealAnswer,
  revealSolution,
  submitAttempt,
} from '../data/api';
import type { CheckResult, FeedbackCode, OpenedProblem, SolutionStep } from '../data/types';
import { navigate } from '../router';
import { useLoad } from '../useLoad';

/** Opens the most recent problem, or generates one when history is empty. */
async function latestOrNewId(): Promise<string> {
  const { items: [latest] } = await listProblemPage({ limit: 1 });
  if (latest) return latest.id;
  const { topic, difficulty } = await getLastSelection();
  return (await generateProblem(topic, difficulty)).id;
}

function practiceUrl(id: string): string {
  return `/practice?id=${encodeURIComponent(id)}`;
}

function PracticeSession({ opened }: { opened: OpenedProblem }) {
  const { problem } = opened;
  const [answer, setAnswer] = useState(problem.lastAnswer ?? '');
  const answerRevision = useRef(0);
  const [result, setResult] = useState<CheckResult | null>(problem.lastResult);
  const [feedback, setFeedback] = useState<FeedbackCode | null>(problem.lastFeedback ?? null);
  const [answerLatex, setAnswerLatex] = useState<string | null>(opened.answer?.answerLatex ?? null);
  const [solution, setSolution] = useState<SolutionStep[] | null>(opened.solution?.steps ?? null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const pending = useRef(false);
  const active = useRef(true);
  const [startedAt] = useState(() => Date.now());
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);

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
      mixed={problem.mixed === true}
      headLabel={problem.saved ? 'Saved to your account' : 'Temporary practice'}
      answer={answer}
      onAnswerChange={(value) => { answerRevision.current += 1; setAnswer(value); setResult(null); }}
      result={result}
      feedback={feedback}
      busy={busy}
      onCheck={() => run(async () => {
        const revision = answerRevision.current;
        const checked = await submitAttempt(problem.id, answer, Math.min(86400000, Math.max(0, Date.now() - startedAt)));
        if (active.current && revision === answerRevision.current) { setResult(checked.result); setFeedback(checked.feedback); }
      })}
      onShowAnswer={() => run(async () => { const revealed = await revealAnswer(problem.id); if (active.current) setAnswerLatex(revealed.answerLatex); })}
      onShowSolution={() => run(async () => { const revealed = await revealSolution(problem.id); if (active.current) setSolution(revealed.steps); })}
      onNext={() =>
        run(async () => {
          if (problem.saved === false) { navigate('/login'); return; }
          const next = await generateProblem(problem.mixed ? 'mixed' : problem.topic, problem.difficulty);
          if (active.current) navigate(practiceUrl(next.id));
        })
      }
      nextLabel={problem.saved === false ? 'Sign in for more practice' : 'Generate next problem'}
      answerLatex={answerLatex}
      solution={solution}
    />
    </>
  );
}

export function PracticePage({ id, demo = false }: { id: string | null; demo?: boolean }) {
  const [revision, setRevision] = useState(0);
  const [startError, setStartError] = useState(false);
  useEffect(() => {
    let current = true;
    setStartError(false);
    if (!id && !demo) void latestOrNewId().then((latest) => { if (current) navigate(practiceUrl(latest), { replace: true }); }).catch(() => { if (current) setStartError(true); });
    return () => { current = false; };
  }, [id, revision, demo]);
  const problem = useLoad(() => (demo ? openDemo() : id ? openProblem(id) : new Promise<never>(() => {})), `${demo}:${id ?? ''}:${revision}`);

  return (
    <main className="pl-wrap pl-wrap--narrow pl-practice-main">
      {problem.status === 'ready' && <PracticeSession key={problem.data.problem.id} opened={problem.data} />}
      {!startError && problem.status === 'loading' && <p role="status">Loading problem…</p>}
      {(startError || problem.status === 'error') && (
        <section className="pl-card pl-card--lg pl-stack pl-gap-4">
          <h1 className="pl-h-lg">
            {problem.status === 'error' && problem.error instanceof NotFoundError ? 'That problem is not in your history.' : text.service_error}
          </h1>
          <p className="pl-muted pl-m-0">{demo ? 'Retry the demo or sign in to save your practice.' : 'Start a new problem from the dashboard.'}</p>
          <div>
            {!(problem.status === 'error' && problem.error instanceof NotFoundError) && <Button variant="secondary" onClick={() => setRevision(value => value + 1)}>Retry loading problem</Button>}
            <ButtonLink to={demo ? '/login' : '/dashboard'} arrow>
              {demo ? 'Sign in with Google' : 'Go to dashboard'}
            </ButtonLink>
          </div>
        </section>
      )}
    </main>
  );
}
