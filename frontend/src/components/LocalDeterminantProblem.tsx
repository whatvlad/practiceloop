import { useRef, useState } from 'react';
import { parseAnswerInput } from '../data/answerInput';
import type { CheckResult, ComputationalInputSpec, Difficulty, SolutionStep } from '../data/types';
import { ProblemCard } from './ProblemCard';

type Problem = { code: string; statement: string; answerInput: ComputationalInputSpec };

async function post(path: string, body: object): Promise<Record<string, unknown>> {
  const response = await fetch(`/local-matrix-preview/${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error('The local generator is unavailable.');
  return await response.json() as Record<string, unknown>;
}

export function LocalDeterminantProblem({ topic = 'determinants' }: { topic?: 'determinants' | 'inverse-matrices' }) {
  const inverse = topic === 'inverse-matrices';
  const [level, setLevel] = useState<Difficulty>(1);
  const [size, setSize] = useState(2);
  const [problemLevel, setProblemLevel] = useState<Difficulty>(1);
  const [problem, setProblem] = useState<Problem | null>(null);
  const [answer, setAnswer] = useState('');
  const [result, setResult] = useState<CheckResult | null>(null);
  const [shownAnswer, setShownAnswer] = useState<string | null>(null);
  const [solution, setSolution] = useState<SolutionStep[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const pending = useRef(false);
  async function run(action: () => Promise<void>) {
    if (pending.current) return;
    pending.current = true; setBusy(true); setError('');
    try { await action(); }
    catch (failure) { setError(failure instanceof Error ? failure.message : 'The local generator is unavailable.'); }
    finally { pending.current = false; setBusy(false); }
  }
  async function next() {
    const data = await post('generate', inverse ? { level, inverseSize: size } : { level, determinantSize: size });
    const input = parseAnswerInput(data.answerInput);
    if (typeof data.code !== 'string' || typeof data.statement !== 'string' || !input || input.kind !== (inverse ? 'tuple' : 'formula')) throw new Error('Invalid generated problem.');
    setProblem({ code: data.code, statement: data.statement, answerInput: input });
    setProblemLevel(level); setAnswer(''); setResult(null); setShownAnswer(null); setSolution(null);
  }
  return <section className="pl-wrap pl-mb-6" aria-label={inverse ? 'Inverse matrix preview' : 'Determinant preview'}>
    <h2 className="pl-h-md">{inverse ? 'Inverse matrices' : 'Determinants'}</h2>
    <p className="pl-small pl-muted">Local preview. Choose settings, then generate a problem.</p>
    <div className="pl-matrix-settings-top pl-matrix-settings">
      <label className="pl-label">Difficulty<select className="pl-input" value={level} onChange={event => setLevel(Number(event.target.value) as Difficulty)}>
        <option value="1">Basic</option><option value="2">Intermediate</option><option value="3">Advanced</option>
      </select></label>
      <label className="pl-label">Matrix size<select className="pl-input" value={size} onChange={event => setSize(Number(event.target.value))}>
        {[2, 3, 4, 5].map(n => <option key={n} value={n}>{n} × {n}</option>)}
      </select></label>
    </div>
    {error && <p role="alert">{error}</p>}
    {!problem && <button type="button" className="pl-btn pl-btn--secondary" disabled={busy} onClick={() => void run(next)}>Generate problem</button>}
    {problem && <ProblemCard topic={topic} difficulty={problemLevel} problemLatex={problem.statement} answerInput={problem.answerInput}
      answer={answer} onAnswerChange={value => { setAnswer(value); setResult(null); }} result={result} busy={busy}
      onCheck={() => void run(async () => {
        const data = await post('check', { code: problem.code, answer });
        if (data.result !== 'correct' && data.result !== 'incorrect' && data.result !== 'invalid') throw new Error('Could not check the answer.');
        setResult(data.result);
      })}
      onShowAnswer={() => void run(async () => {
        const data = await post('reveal-answer', { code: problem.code });
        if (typeof data.answerLatex !== 'string') throw new Error('Invalid answer.');
        setShownAnswer(data.answerLatex);
      })}
      onShowSolution={() => void run(async () => {
        const data = await post('reveal-solution', { code: problem.code });
        if (!Array.isArray(data.steps)) throw new Error('Invalid solution.');
        setSolution(data.steps as SolutionStep[]);
      })}
      onNext={() => void run(next)} answerLatex={shownAnswer} solution={solution} />}
  </section>;
}
