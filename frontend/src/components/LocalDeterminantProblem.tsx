import { useRef, useState } from 'react';
import { parseAnswerInput } from '../data/answerInput';
import { parseVisual, type VisualSpec } from '../visual/spec';
import type { CheckResult, AnswerInputSpec, Difficulty, SolutionStep } from '../data/types';
import { ProblemCard } from './ProblemCard';

type Problem = { code: string; statement: string; answerInput?: AnswerInputSpec };

async function post(path: string, body: object): Promise<Record<string, unknown>> {
  const response = await fetch(`/local-matrix-preview/${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error('The local generator is unavailable.');
  return await response.json() as Record<string, unknown>;
}

export function LocalDeterminantProblem({ topic = 'determinants' }: { topic?: 'determinants' | 'inverse-matrices' | 'matrix-rank' | 'linear-systems' | 'complex-arithmetic' | 'complex-numbers' | 'complex-polar-form' | 'complex-conversion' | 'polynomial-division' | 'polynomial-roots' | 'polynomial-operations' | 'partial-fractions' | 'fundamental-theorem-algebra' }) {
  const complex = topic === 'complex-arithmetic';
  const polynomial = topic === 'polynomial-division';
  const roots = topic === 'polynomial-roots';
  const extra = ['polynomial-operations', 'partial-fractions', 'fundamental-theorem-algebra'].includes(topic);
  const fractions = topic === 'partial-fractions';
  const operations = topic === 'polynomial-operations';
  const conversion = topic === 'complex-conversion';
  const modulus = topic === 'complex-numbers';
  const polar = topic === 'complex-polar-form';
  const inverse = topic === 'inverse-matrices';
  const rank = topic === 'matrix-rank';
  const system = topic === 'linear-systems';
  const [level, setLevel] = useState<Difficulty>(1);
  const [size, setSize] = useState(2);
  const [operation, setOperation] = useState('multiply');
  const [modulusMode, setModulusMode] = useState('expression');
  const [direction, setDirection] = useState('alg-trig');
  const [polynomialMode, setPolynomialMode] = useState('division');
  const [polyOperation, setPolyOperation] = useState('add');
  const [polarMode, setPolarMode] = useState<'argument' | 'power' | 'root'>('argument');
  const [problemMode, setProblemMode] = useState(polarMode);
  const [columns, setColumns] = useState(2);
  const [problemLevel, setProblemLevel] = useState<Difficulty>(1);
  const [problem, setProblem] = useState<Problem | null>(null);
  const [answer, setAnswer] = useState('');
  const [result, setResult] = useState<CheckResult | null>(null);
  const [shownAnswer, setShownAnswer] = useState<string | null>(null);
  const [solution, setSolution] = useState<SolutionStep[] | null>(null);
  const [visual, setVisual] = useState<VisualSpec | undefined>();
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
    const data = await post('generate', extra ? { level, polynomialExtra: fractions ? 'fractions' : operations ? polyOperation : 'fundamental' } : roots ? { level, polynomialRoots: true } : polynomial ? { level, polynomialMode } : conversion ? { level, conversion: direction } : polar ? { level: 1, polarMode } : modulus ? { level, complexModulus: true, modulusMode } : complex ? { level, complexOperation: operation } : system ? { level, systemSize: size } : rank ? { level, rankDimensions: { rows: size, columns } } : inverse ? { level, inverseSize: size } : { level, determinantSize: size });
    const input = parseAnswerInput(data.answerInput);
    if (typeof data.code !== 'string' || typeof data.statement !== 'string' || (extra ? (fractions ? input?.kind !== 'tuple' : input !== undefined) : roots ? input?.kind !== 'finite_set' : polynomial ? (polynomialMode === 'division' ? input?.kind !== 'tuple' : input !== undefined) : conversion && direction.endsWith('-alg') ? input !== undefined : conversion ? input?.kind !== 'tuple' : !complex && !modulus && !polar && (!input || input.kind !== (inverse || system ? 'tuple' : 'formula')))) throw new Error('Invalid generated problem.');
    setProblem({ code: data.code, statement: data.statement, answerInput: input ?? undefined });
    setProblemLevel(polar ? ({ argument: 1, power: 2, root: 3 } as const)[polarMode] : level); setProblemMode(polarMode); setAnswer(''); setResult(null); setShownAnswer(null); setSolution(null); setVisual(undefined);
  }
  return <section className="pl-wrap pl-mb-6" aria-label={extra ? 'Polynomial exercises preview' : roots ? 'Polynomial roots preview' : polynomial ? 'Polynomial division preview' : conversion ? 'Complex forms conversion preview' : polar ? 'Complex polar form preview' : modulus ? 'Complex modulus preview' : complex ? 'Complex arithmetic preview' : system ? 'Systems of linear equations preview' : rank ? 'Matrix rank preview' : inverse ? 'Inverse matrix preview' : 'Determinant preview'}>
    <h2 className="pl-h-md">{fractions ? 'Partial fractions' : operations ? 'Polynomial operations' : extra ? 'Fundamental theorem of algebra' : roots ? 'Polynomial roots and factors' : polynomial ? 'Polynomial division and remainders' : conversion ? 'Converting complex forms' : polar ? 'Polar form, powers and roots' : modulus ? 'Modulus of a complex number' : complex ? 'Complex arithmetic' : system ? 'Systems of linear equations' : rank ? 'Matrix rank' : inverse ? 'Inverse matrices' : 'Determinants'}</h2>
    <p className="pl-small pl-muted">Local preview. Choose settings, then generate a problem.</p>
    <div className="pl-matrix-settings-top pl-matrix-settings">
      {!polar && <label className="pl-label">Difficulty<select className="pl-input" value={level} onChange={event => setLevel(Number(event.target.value) as Difficulty)}>
        <option value="1">Basic</option><option value="2">Intermediate</option><option value="3">Advanced</option>
      </select></label>}
      {operations ? <label className="pl-label">Operation<select className="pl-input" value={polyOperation} onChange={event => setPolyOperation(event.target.value)}><option value="add">Addition</option><option value="subtract">Subtraction</option><option value="multiply">Multiplication</option></select></label> : extra || roots ? null : polynomial ? <label className="pl-label">Exercise type<select className="pl-input" value={polynomialMode} onChange={event => setPolynomialMode(event.target.value)}><option value="division">Quotient and remainder</option><option value="remainder">Remainder theorem</option><option value="divisibility">Divisibility condition</option></select></label> : conversion ? <label className="pl-label">Conversion<select className="pl-input" value={direction} onChange={event => setDirection(event.target.value)}>
        <option value="alg-trig">Algebraic → trigonometric</option><option value="alg-exp">Algebraic → exponential</option><option value="trig-alg">Trigonometric → algebraic</option><option value="exp-alg">Exponential → algebraic</option>
      </select></label> : polar ? <label className="pl-label">Exercise type<select className="pl-input" value={polarMode} onChange={event => setPolarMode(event.target.value as typeof polarMode)}><option value="argument">Principal argument</option><option value="power">Powers (de Moivre)</option><option value="root">One root: smallest nonnegative argument</option></select></label> : modulus ? <label className="pl-label">Exercise type<select className="pl-input" value={modulusMode} onChange={event => setModulusMode(event.target.value)}><option value="expression">Modulus of an expression</option><option value="properties">Modulus properties</option><option value="geometry">Modulus as distance</option></select></label> : complex ? <label className="pl-label">Operation<select className="pl-input" value={operation} onChange={event => setOperation(event.target.value)}>
        <option value="multiply">Multiplication</option><option value="divide">Division</option>
      </select></label> : <label className="pl-label">{system ? 'Number of unknowns' : rank ? 'Rows' : 'Matrix size'}<select className="pl-input" value={size} onChange={event => setSize(Number(event.target.value))}>
        {[2, 3, 4, 5].map(n => <option key={n} value={n}>{rank || system ? n : `${n} × ${n}`}</option>)}
      </select></label>}
      {rank && <label className="pl-label">Columns<select className="pl-input" value={columns} onChange={event => setColumns(Number(event.target.value))}>{[2, 3, 4, 5].map(n => <option key={n} value={n}>{n}</option>)}</select></label>}
    </div>
    {error && <p role="alert">{error}</p>}
    {!problem && <button type="button" className="pl-btn pl-btn--secondary" disabled={busy} onClick={() => void run(next)}>Generate problem</button>}
    {problem && <ProblemCard difficultyScale={polar ? null : 3} topic={polar && problemMode === 'argument' ? 'complex-argument' : topic} difficulty={problemLevel} problemLatex={problem.statement} answerInput={problem.answerInput}
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
        setVisual(parseVisual(data.visual));
      })}
      onNext={() => void run(next)} answerLatex={shownAnswer} solution={solution} visual={visual} />}
  </section>;
}
