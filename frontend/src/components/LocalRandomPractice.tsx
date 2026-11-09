import { useRef, useState } from 'react';
import { parseAnswerInput } from '../data/answerInput';
import { chooseLocalRandom, initialLocalChoice, LOCAL_RANDOM_TOPICS, localRandomError, type LocalChoice, type LocalSelection } from '../data/localRandom';
import type { AnswerInputSpec, CheckResult, Difficulty, SolutionStep } from '../data/types';
import { parseVisual, type VisualSpec } from '../visual/spec';
import { ProblemCard } from './ProblemCard';
import { generateAlgebraRandom, loadAlgebraRandom, saveAlgebraRandom } from '../data/algebraRandom';
import { navigate } from '../router';

const STORAGE = 'practiceloop:local-random:v1';
function load(): LocalSelection {
  try {
    const data: unknown = JSON.parse(localStorage.getItem(STORAGE) ?? '{}');
    if (!data || typeof data !== 'object' || Array.isArray(data)) return {};
    return Object.fromEntries(Object.entries(data).filter(([topic, choice]) =>
      LOCAL_RANDOM_TOPICS.some(item => item.id === topic) && choice && typeof choice === 'object' && !Array.isArray(choice))
      .map(([topic, choice]) => {
        const available = LOCAL_RANDOM_TOPICS.find(item => item.id === topic)!;
        const oldKinds = Array.isArray((choice as LocalChoice).kinds) ? (choice as LocalChoice).kinds : [];
        const kinds = oldKinds.map(kind => topic === 'complex-numbers' && kind === 'default' ? 'expression' : kind).filter(kind => (available.kinds as readonly string[]).includes(kind));
        return [topic, { ...initialLocalChoice(), ...choice as LocalChoice, kinds }];
      }));
  } catch { return {}; }
}
async function post(path: string, body: object): Promise<Record<string, unknown>> {
  const response = await fetch(`/local-matrix-preview/${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!response.ok) throw new Error('The local generator is unavailable.');
  return await response.json() as Record<string, unknown>;
}
type Draw = { topic: string; kind: string; level: Difficulty; code: string; statement: string; input?: AnswerInputSpec };
const LABELS: Record<string, string> = { default: 'Available exercise', add: 'Addition', subtract: 'Subtraction', multiply: 'Multiplication', divide: 'Division', expression: 'Modulus of an expression', properties: 'Modulus properties', geometry: 'Modulus as distance', argument: 'Principal argument', power: 'Powers', root: 'One root', division: 'Quotient and remainder', remainder: 'Remainder theorem', divisibility: 'Divisibility condition', 'alg-trig': 'Algebraic → trigonometric', 'alg-exp': 'Algebraic → exponential', 'trig-alg': 'Trigonometric → algebraic', 'exp-alg': 'Exponential → algebraic' };

export function LocalRandomPractice({ accountId }: { accountId?: string } = {}) {
  const [selection, setSelection] = useState<LocalSelection>(() => accountId ? loadAlgebraRandom(accountId) : load());
  const [problem, setProblem] = useState<Draw | null>(null);
  const [configOpen, setConfigOpen] = useState(true);
  const [answer, setAnswer] = useState('');
  const [result, setResult] = useState<CheckResult | null>(null);
  const [shown, setShown] = useState<string | null>(null);
  const [solution, setSolution] = useState<SolutionStep[] | null>(null);
  const [visual, setVisual] = useState<VisualSpec | undefined>();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  function save(next: LocalSelection) { setSelection(next); try { if (accountId) saveAlgebraRandom(accountId, next); else localStorage.setItem(STORAGE, JSON.stringify(next)); } catch { setError('Could not save the selection on this device.'); } }
  function update(topic: string, patch: Partial<LocalChoice>) { save({ ...selection, [topic]: { ...selection[topic], ...patch } }); }
  async function run(action: () => Promise<void>) {
    if (pending.current) return;
    pending.current = true; setBusy(true); setError('');
    try { await action(); } catch (failure) { setError(failure instanceof Error ? failure.message : 'Unable to generate the problem.'); }
    finally { pending.current = false; setBusy(false); }
  }
  async function next() {
    if (accountId) {
      const generated = await generateAlgebraRandom(selection);
      navigate(`/practice?id=${encodeURIComponent(generated.id)}&mode=algebra-random`);
      return;
    }
    const picked = chooseLocalRandom(selection);
    const data = await post('generate', picked.body);
    if (typeof data.code !== 'string' || typeof data.statement !== 'string') throw new Error('Invalid generated problem.');
    const input = parseAnswerInput(data.answerInput);
    setProblem({ ...picked, code: data.code, statement: data.statement, input });
    setConfigOpen(false);
    setAnswer(''); setResult(null); setShown(null); setSolution(null); setVisual(undefined);
  }
  const sizeSelect = (topic: string, choice: LocalChoice, key: 'size' | 'columns' | 'rowsA' | 'colsA' | 'rowsB' | 'colsB', label: string, min = 1) =>
    <label className="pl-label" key={key}>{label}<select className="pl-input" value={choice[key]} onChange={event => update(topic, { [key]: Number(event.target.value) })}>{[1, 2, 3, 4, 5].filter(n => n >= min).map(n => <option key={n} value={n}>{n}</option>)}</select></label>;
  return <section className="pl-wrap pl-mb-6" aria-label={accountId ? 'Random algebra practice' : 'Local random practice'}>
    <h2 className="pl-h-md">Random problems</h2><p className="pl-small pl-muted">Choose topics, their levels and exercise types. Each topic has an equal chance.</p>
    <details className="pl-local-random-config" open={configOpen} onToggle={event => setConfigOpen(event.currentTarget.open)}>
    <summary>Choose topics and settings ({Object.keys(selection).length} selected)</summary>
    <div className="pl-local-random-list">{LOCAL_RANDOM_TOPICS.map(item => {
      const choice = selection[item.id]; const issue = choice ? localRandomError(item.id, choice) : null;
      return <div className="pl-local-random-topic" key={item.id}>
        <label className="pl-vis-toggle"><input type="checkbox" checked={!!choice} onChange={event => {
          if (event.target.checked) save({ ...selection, [item.id]: { ...initialLocalChoice(), kinds: item.kinds.length === 1 ? [item.kinds[0]] : [] } });
          else { const next = { ...selection }; delete next[item.id]; save(next); }
        }} />{item.label}</label>
        {choice && <div className="pl-local-random-settings">
          {item.id !== 'complex-polar-form' && <label className="pl-label">Difficulty<select className="pl-input" value={choice.level ?? ''} onChange={event => update(item.id, { level: event.target.value ? Number(event.target.value) as Difficulty : null })}><option value="">Choose difficulty</option><option value="1">Basic</option><option value="2">Intermediate</option><option value="3">Advanced</option></select></label>}
          {item.kinds.length > 1 && <fieldset><legend className="pl-label">Exercise types</legend>{item.kinds.map(kind => <label className="pl-vis-toggle" key={kind}><input type="checkbox" checked={choice.kinds.includes(kind)} onChange={event => update(item.id, { kinds: event.target.checked ? [...choice.kinds, kind] : choice.kinds.filter(value => value !== kind) })} />{LABELS[kind] ?? kind}</label>)}</fieldset>}
          {item.id === 'matrix-operations' && <><div className="pl-matrix-dimensions">{sizeSelect(item.id, choice, 'rowsA', 'Rows of A')}{sizeSelect(item.id, choice, 'colsA', 'Columns of A')}</div><div className="pl-matrix-dimensions">{sizeSelect(item.id, choice, 'rowsB', 'Rows of B')}{sizeSelect(item.id, choice, 'colsB', 'Columns of B')}</div></>}
          {['determinants', 'inverse-matrices', 'linear-systems', 'matrix-rank'].includes(item.id) && sizeSelect(item.id, choice, 'size', item.id === 'matrix-rank' ? 'Rows' : item.id === 'linear-systems' ? 'Number of unknowns' : 'Matrix size', 2)}
          {item.id === 'matrix-rank' && sizeSelect(item.id, choice, 'columns', 'Columns', 2)}
          {issue && <p className="pl-small pl-muted">{issue}</p>}
        </div>}
      </div>;
    })}</div>
    </details>
    {error && <p role="alert">{error}</p>}
    {!problem && <button type="button" className="pl-btn pl-btn--secondary" disabled={busy} onClick={() => void run(next)}>Generate problem</button>}
    {problem && <ProblemCard topic={problem.topic === 'complex-polar-form' && problem.kind === 'argument' ? 'complex-argument' : problem.topic} difficulty={problem.level} difficultyScale={problem.topic === 'complex-polar-form' ? null : 3} problemLatex={problem.statement} answerInput={problem.input} answer={answer} onAnswerChange={value => { setAnswer(value); setResult(null); }} result={result} busy={busy}
      onCheck={() => void run(async () => { const data = await post('check', { code: problem.code, answer }); if (data.result !== 'correct' && data.result !== 'incorrect' && data.result !== 'invalid') throw new Error('Could not check the answer.'); setResult(data.result); })}
      onShowAnswer={() => void run(async () => { const data = await post('reveal-answer', { code: problem.code }); if (typeof data.answerLatex !== 'string') throw new Error('Invalid answer.'); setShown(data.answerLatex); })}
      onShowSolution={() => void run(async () => { const data = await post('reveal-solution', { code: problem.code }); if (!Array.isArray(data.steps)) throw new Error('Invalid solution.'); setSolution(data.steps as SolutionStep[]); setVisual(parseVisual(data.visual)); })}
      onNext={() => void run(next)} answerLatex={shown} solution={solution} visual={visual} />}
  </section>;
}
