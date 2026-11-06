import { useEffect, useRef, useState } from 'react';
import text from '../../../backend/app/content/en.json';
import { Button, ButtonLink } from '../components/Button';
import { ProblemCard } from '../components/ProblemCard';
import { ReportProblem } from '../components/ReportProblem';
import { ShareControls } from '../components/ShareControls';
import { WorksheetBuilder } from '../components/WorksheetBuilder';
import { initialMatrixOptions, matrixOptionsQuery, matrixOptionsValid } from '../components/MatrixSettings';
import {
  NotFoundError,
  generateProblem,
  getCatalogue,
  getLastSelection,
  openProblem,
  openDemo,
  listProblemPage,
  revealAnswer,
  revealSolution,
  submitAttempt,
} from '../data/api';
import { areaOf } from '../data/topics';
import { eligibleRandomChoices, loadRandomMatrixOptions, loadRandomSelection, pickRandomChoice } from '../data/randomPractice';
import type { CheckResult, FeedbackCode, MatrixOptions, OpenedProblem, RevealedSolution } from '../data/types';
import { navigate } from '../router';
import { useLoad } from '../useLoad';

/** Opens the most recent problem, or generates one when history is empty. */
async function latestOrNewId(): Promise<string> {
  const { items: [latest] } = await listProblemPage({ limit: 1 });
  if (latest) return latest.id;
  const { topic, difficulty, area } = await getLastSelection();
  return (await generateProblem(topic, difficulty, area)).id;
}

function practiceUrl(id: string, random = false, options?: MatrixOptions): string {
  return `/practice?id=${encodeURIComponent(id)}${random ? '&mode=random' : ''}${options ? matrixOptionsQuery(options) : ''}`;
}

function PracticeSession({ opened, randomAccountId, matrixOptions }: { opened: OpenedProblem; randomAccountId?: string; matrixOptions?: MatrixOptions }) {
  const { problem } = opened;
  const [answer, setAnswer] = useState(problem.lastAnswer ?? '');
  const answerRevision = useRef(0);
  const [result, setResult] = useState<CheckResult | null>(problem.lastResult);
  const [feedback, setFeedback] = useState<FeedbackCode | null>(problem.lastFeedback ?? null);
  const [answerLatex, setAnswerLatex] = useState<string | null>(opened.answer?.answerLatex ?? null);
  const [solution, setSolution] = useState<RevealedSolution | null>(opened.solution ?? null);
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
      answerInput={problem.answerInput}
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
      onShowSolution={() => run(async () => { const revealed = await revealSolution(problem.id); if (active.current) setSolution(revealed); })}
      onNext={() =>
        run(async () => {
          if (problem.saved === false) { navigate('/login'); return; }
          if (randomAccountId) {
            const catalogue = await getCatalogue();
            const choices = eligibleRandomChoices(loadRandomSelection(randomAccountId), catalogue.topics);
            if (!choices) throw new Error('Select available topics and a level for each before generating the next problem.');
            const choice = pickRandomChoice(choices);
            const storedOptions = loadRandomMatrixOptions(randomAccountId);
            const options = choice.topic === 'matrix-operations'
              ? storedOptions && matrixOptionsValid(choice.difficulty, storedOptions) ? storedOptions : initialMatrixOptions(choice.difficulty)
              : undefined;
            const next = options ? await generateProblem(choice.topic, choice.difficulty, choice.area, options)
              : await generateProblem(choice.topic, choice.difficulty, choice.area);
            if (active.current) navigate(practiceUrl(next.id, true));
            return;
          }
          // Mixed practice draws within one area, the one this problem's topic belongs to.
          const options = problem.topic === 'matrix-operations' ? matrixOptions : undefined;
          const selectedTopic = problem.mixed ? 'mixed' : problem.topic;
          const next = options ? await generateProblem(selectedTopic, problem.difficulty, areaOf(problem.topic), options)
            : await generateProblem(selectedTopic, problem.difficulty, areaOf(problem.topic));
          if (active.current) navigate(practiceUrl(next.id, false, options));
        })
      }
      nextLabel={problem.saved === false ? 'Sign in for more practice' : 'Generate next problem'}
      answerLatex={answerLatex}
      solution={solution?.steps}
      visual={solution?.visual}
    />
    {problem.saved && <ShareControls problemId={problem.id} initial={opened.share ?? null} />}
    {problem.saved && <ReportProblem problemId={problem.id} />}
    {problem.saved && <WorksheetBuilder start={{ area: areaOf(problem.topic), topic: problem.mixed ? 'mixed' : problem.topic, difficulty: problem.difficulty }} />}
    </>
  );
}

export function PracticePage({ id, demo = false, randomAccountId, matrixOptions }: { id: string | null; demo?: boolean; randomAccountId?: string; matrixOptions?: MatrixOptions }) {
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
    <main id="main" tabIndex={-1} className="pl-wrap pl-wrap--narrow pl-practice-main">
      {!(startError || problem.status === 'error') && <h1 className="pl-sr-only">Practice problem</h1>}
      {problem.status === 'ready' && <PracticeSession key={problem.data.problem.id} opened={problem.data} randomAccountId={randomAccountId} matrixOptions={matrixOptions} />}
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
