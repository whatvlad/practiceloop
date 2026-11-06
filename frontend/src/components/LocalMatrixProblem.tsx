import { useRef, useState } from 'react';
import { parseAnswerInput } from '../data/answerInput';
import type { CheckResult, ComputationalInputSpec, Difficulty, SolutionStep } from '../data/types';
import { ProblemCard } from './ProblemCard';

type Dimensions = { operation: 'add' | 'subtract' | 'multiply' | 'divide'; rowsA: number; colsA: number; rowsB: number; colsB: number };
const initialDimensions: Dimensions = { operation: 'add', rowsA: 2, colsA: 2, rowsB: 2, colsB: 2 };

interface PreviewProblem { code: string; statement: string; generatorVersion: string; answerInput: ComputationalInputSpec }

async function post(path: string, body: object): Promise<Record<string, unknown>> {
  const response = await fetch(`/local-matrix-preview/${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error('The local generator is unavailable.');
  return await response.json() as Record<string, unknown>;
}

async function generate(level: Difficulty, dimensions: Dimensions): Promise<PreviewProblem> {
  const data = await post('generate', { level, dimensions });
  const answerInput = parseAnswerInput(data.answerInput);
  if (typeof data.code !== 'string' || typeof data.statement !== 'string' || typeof data.generatorVersion !== 'string'
      || !answerInput || answerInput.kind !== 'tuple') throw new Error('The local generator returned an invalid problem.');
  return { code: data.code, statement: data.statement, generatorVersion: data.generatorVersion, answerInput };
}

/** Local-only preview: problems and checks come from the real Python generators. */
export function LocalMatrixProblem() {
  const [level, setLevel] = useState<Difficulty>(1);
  const [options, setOptions] = useState<Dimensions>(initialDimensions);
  const compatible = options.operation === 'divide' ? options.colsA === options.rowsB && options.rowsB === options.colsB
    : options.operation === 'multiply' ? options.colsA === options.rowsB : options.rowsA === options.rowsB && options.colsA === options.colsB;
  const [problemLevel, setProblemLevel] = useState<Difficulty>(1);
  const [problem, setProblem] = useState<PreviewProblem | null>(null);
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
    const nextProblem = await generate(level, options);
    setProblem(nextProblem); setProblemLevel(level); setAnswer(''); setResult(null); setShownAnswer(null); setSolution(null);
  }
  return <section className="pl-wrap pl-mb-6" aria-label="Local generator preview">
    <p className="pl-small pl-muted">Local generator preview. Integers, fractions and sin(θ)/cos(θ) are supported; no answers are saved.</p>
    <div className="pl-matrix-settings"><div className="pl-matrix-settings-top">
    <label className="pl-label">Difficulty <select className="pl-input" value={level} onChange={event => setLevel(Number(event.target.value) as Difficulty)}>
      <option value="1">Basic</option><option value="2">Intermediate</option><option value="3">Advanced</option>
    </select></label>
    <label className="pl-label">Operation <select className="pl-input" value={options.operation} onChange={event => setOptions({ ...options, operation: event.target.value as Dimensions['operation'] })}>
      <option value="add">Addition</option><option value="subtract">Subtraction</option><option value="multiply">Multiplication</option><option value="divide">Division</option>
    </select></label>
    </div>
    {([['rowsA', 'colsA'], ['rowsB', 'colsB']] as const).map((keys, index) => <div className="pl-matrix-dimensions" key={index}>
      {keys.map(key => <label className="pl-label" key={key}>{({ rowsA: 'Rows of A', colsA: 'Columns of A', rowsB: 'Rows of B', colsB: 'Columns of B' })[key]}
      <select className="pl-input" value={options[key]} onChange={event => setOptions({ ...options, [key]: Number(event.target.value) })}>{[1, 2, 3, 4, 5].map(size => <option key={size} value={size}>{size}</option>)}</select>
      </label>)}
    </div>)}
    </div>
    {!compatible && <p role="alert">{options.operation === 'divide' ? 'Division requires a square matrix B and columns of A equal to rows of B.' : options.operation === 'multiply' ? 'Multiplication is impossible: columns of A must equal rows of B.' : 'This operation is impossible: both matrices must have the same dimensions.'}</p>}
    {error && <p role="alert">{error}</p>}
    {!problem && <button type="button" className="pl-btn pl-btn--secondary" disabled={busy || !compatible} onClick={() => void run(next)}>Generate problem</button>}
    {problem && <>
      <ProblemCard answerInput={problem.answerInput} topic="matrix-operations" difficulty={problemLevel} problemLatex={problem.statement}
        answer={answer} onAnswerChange={value => { setAnswer(value); setResult(null); }} result={result} busy={busy}
        onCheck={() => void run(async () => {
          const data = await post('check', { code: problem.code, answer });
          if (data.result !== 'correct' && data.result !== 'incorrect' && data.result !== 'invalid') throw new Error('Could not check the answer.');
          setResult(data.result);
        })}
        onShowAnswer={() => void run(async () => {
          const data = await post('reveal-answer', { code: problem.code });
          if (typeof data.answerLatex !== 'string') throw new Error('Invalid preview answer.');
          setShownAnswer(data.answerLatex);
        })}
        onShowSolution={() => void run(async () => {
          const data = await post('reveal-solution', { code: problem.code });
          if (!Array.isArray(data.steps)) throw new Error('Invalid preview solution.');
          setSolution(data.steps as SolutionStep[]);
        })}
        onNext={() => void run(next)} nextDisabled={!compatible} answerLatex={shownAnswer} solution={solution} />
    </>}
  </section>;
}
