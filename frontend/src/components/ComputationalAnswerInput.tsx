import { useState } from 'react';
import { analyseComputationalAnswer, splitComputationalParts } from '../answerSyntax';
import type { CheckResult, ComputationalInputSpec } from '../data/types';
import { Tex } from './Tex';

interface Props {
  id: string;
  spec: ComputationalInputSpec;
  value: string;
  onChange: (value: string) => void;
  state?: CheckResult | null;
  onEnter?: () => void;
  describedBy?: string;
  label?: string;
}

/** Syntax only: no expected values or correctness decisions are present here. */
export function ComputationalAnswerInput({ id, spec, value, onChange, state, onEnter, describedBy, label = 'Your answer' }: Props) {
  const [plain, setPlain] = useState(false);
  const names = Object.keys(spec.symbols ?? {});
  const analysis = analyseComputationalAnswer(value, spec);
  let parts: string[] | undefined;
  if (spec.kind === 'tuple') {
    try {
      const trimmed = value.trim();
      parts = trimmed ? (trimmed.startsWith('(') && trimmed.endsWith(')') ? splitComputationalParts(trimmed.slice(1, -1), ';') : undefined)
        : Array(spec.components!.length).fill('');
      if (parts?.length !== spec.components!.length) parts = undefined;
    } catch { /* Preserve malformed historical text for explicit editing. */ }
  }
  const update = (index: number, next: string) => onChange(`(${parts!.map((old, position) => position === index ? next : old).join(';')})`);
  return <fieldset className="pl-structured-answer pl-field pl-stack pl-gap-3" aria-describedby={[`${id}-preview`, describedBy].filter(Boolean).join(' ')}>
    <legend className="pl-label">{label}</legend>
    {spec.kind === 'category' ? <div className="pl-chips">{spec.choices!.map(choice => <label key={choice}>
      <input type="radio" name={id} value={choice} checked={value.trim() === choice} onChange={() => onChange(choice)}
        onKeyDown={event => { if (event.key === 'Enter') { event.preventDefault(); onEnter?.(); } }} /> {choice.replaceAll('_', ' ')}
    </label>)}</div> : <>
      {spec.kind === 'tuple' && <label><input type="checkbox" checked={plain || !parts} onChange={event => setPlain(event.target.checked)} /> Edit as text</label>}
      {spec.kind === 'tuple' && parts && !plain ? spec.components!.map((child, index) => <div key={index}>
        <ComputationalAnswerInput id={`${id}-${index}`} label={spec.labels![index]} spec={child} value={parts![index]} onChange={text => update(index, text)} onEnter={onEnter} />
      </div>) : <label className="pl-label" htmlFor={id}>Answer notation<input className="pl-input" id={id} value={value}
        onChange={event => onChange(event.target.value)} autoComplete="off" spellCheck={false}
        aria-invalid={state === 'invalid' || analysis.status === 'error'}
        onKeyDown={event => { if (event.key === 'Enter') { event.preventDefault(); onEnter?.(); } }} /></label>}
      {spec.kind === 'real_set' && <p className="pl-small">Use intervals and sets joined by <code>U</code>, for example <code>(-inf,0) U [2,3]</code>. Use <code>{'{}'}</code> for the empty set, <code>R</code> for all reals, or <code>{'R\\{0}'}</code> to exclude points.</p>}
      {spec.kind === 'formula' && <p className="pl-small">{names.length ? <>Use explicit multiplication, for example <code>{`2*${names[0]}`}</code>. {Object.entries(spec.symbols!).map(([name, domain]) => `${name}: ${domain}`).join('; ')}. Each numeric exponent part is at most 12; write a larger power as nested powers, for example <code>{`(${names[0]}^4)^4`}</code>.</> : <>Use exact constants only, for example <code>sqrt(2)/3</code>.</>}</p>}
      {spec.kind === 'limit_result' && <p className="pl-small">Enter the exact finite value, <code>inf</code>, <code>-inf</code>, or <code>does_not_exist</code>.</p>}
      {spec.kind === 'logic' && <p className="pl-small">Atoms: {spec.choices!.join(', ')}. Use <code>!</code> for not, <code>&amp;</code> for and, <code>|</code> for inclusive or, <code>^</code> for exclusive or, <code>-&gt;</code> for implication and <code>&lt;-&gt;</code> for equivalence. Parentheses make grouping explicit; implication associates to the right.</p>}
      {spec.kind === 'tuple' && <p className="pl-small">Keep the displayed order. Separate components with semicolons inside parentheses.</p>}
    </>}
    <div id={`${id}-preview`} className="pl-preview" role="status">{analysis.status === 'ok' ? <><span className="pl-label">Reads as</span><Tex latex={analysis.latex} /></>
      : <p className={analysis.status === 'error' ? 'pl-preview-problem' : 'pl-preview-note'}>{analysis.status === 'empty' ? 'Enter your answer.' : analysis.message}</p>}</div>
  </fieldset>;
}
