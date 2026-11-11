import { useState } from 'react';
import { analyseStructuredAnswer } from '../answerSyntax';
import type { AnswerInputSpec, CheckResult, ComputationalInputSpec, LegacyAnswerInputSpec } from '../data/types';
import { COMPUTATIONAL_KINDS } from '../data/answerInput';
import { ComputationalAnswerInput } from './ComputationalAnswerInput';
import { AnswerInput } from './AnswerInput';
import { Tex } from './Tex';
import { matrixDimensions, parseMatrixAnswer, serializeMatrixAnswer } from '../data/matrixContract';
import { MatrixAnswerInput } from './MatrixAnswerInput';
import { VectorAnswerInput } from './VectorAnswerInput';
import { ANSWER_VARIABLES, type AnswerVariable } from '../answerSyntax';

interface Props {
  id: string;
  spec: AnswerInputSpec;
  value: string;
  onChange: (value: string) => void;
  state?: CheckResult | null;
  onEnter?: () => void;
  describedBy?: string;
}

function entries(value: string, kind: AnswerInputSpec['kind']): string[] {
  const notation = value.trim();
  if (!notation) return kind === 'interval' ? ['', ''] : [''];
  if (notation === '{}') return [];
  // Scalar functions take one argument, so commas always separate fields.
  // This also preserves an unfinished opening group while the learner types.
  const parts = notation.slice(1, -1).split(',');
  return parts.map(p => {
    const normal = p.trim().replaceAll('∞', 'inf').replaceAll('−', '-');
    return kind === 'interval' && ['inf', '+inf', '-inf'].includes(normal) ? normal.replace('+', '') : p.trim();
  });
}

/** The server supplies only an input kind. Correctness remains server-side. */
export function StructuredAnswerInput({ id, spec, value, onChange, state, onEnter, describedBy }: Props) {
  const dimensions = matrixDimensions(spec as ComputationalInputSpec);
  const matrix = dimensions && parseMatrixAnswer(value, ...dimensions);
  if (matrix) {
    const symbols = (spec as ComputationalInputSpec).components?.[0]?.components?.[0]?.symbols;
    const variables = symbols ? Object.keys(symbols).filter((name): name is AnswerVariable => ANSWER_VARIABLES.includes(name as AnswerVariable)) : undefined;
    return <MatrixAnswerInput value={matrix} variables={variables} onChange={next => onChange(serializeMatrixAnswer(next))} />;
  }
  if (spec.kind === 'tuple' && spec.labels?.join('|') === 'x component|y component|z component'
    && spec.components?.length === 3 && spec.components.every(child => child.kind === 'formula' && !Object.keys(child.symbols ?? {}).length)) {
    return <VectorAnswerInput id={id} spec={spec as ComputationalInputSpec} value={value} onChange={onChange} state={state} onEnter={onEnter} describedBy={describedBy} />;
  }
  if ((COMPUTATIONAL_KINDS as readonly string[]).includes(spec.kind)) return <ComputationalAnswerInput
    id={id} spec={spec as ComputationalInputSpec} value={value} onChange={onChange} state={state} onEnter={onEnter} describedBy={describedBy} />;
  return <LegacyStructuredAnswerInput id={id} spec={spec as LegacyAnswerInputSpec} value={value} onChange={onChange} state={state} onEnter={onEnter} describedBy={describedBy} />;
}

function LegacyStructuredAnswerInput({ id, spec, value, onChange, state, onEnter, describedBy }: Props & { spec: LegacyAnswerInputSpec }) {
  const [plain, setPlain] = useState(false);
  const analysis = analyseStructuredAnswer(value, spec.kind);
  const parts = entries(value, spec.kind);
  const notation = value.trim();
  const representable = !notation || (spec.kind === 'finite_set' ? notation.startsWith('{') && notation.endsWith('}') && parts.length <= 8
    : '[('.includes(notation[0]) && '])'.includes(notation.at(-1)!) && parts.length === 2);
  const textMode = plain || !representable;
  const updateSet = (next: string[]) => onChange(`{${next.join(',')}}`);
  const updateInterval = (index: number, endpoint: string, left = notation[0] === '(' ? '(' : '[', right = notation.at(-1) === ')' ? ')' : ']') => {
    const next = [parts[0] ?? '', parts[1] ?? '']; next[index] = endpoint;
    onChange(`${next[0] === '-inf' ? '(' : left}${next.join(',')}${next[1] === 'inf' ? ')' : right}`);
  };
  return <fieldset className="pl-structured-answer pl-field pl-stack pl-gap-3" aria-describedby={[`${id}-preview`, describedBy].filter(Boolean).join(' ')}>
    <legend className="pl-label">Your answer</legend>
    {spec.kind === 'boolean' ? <div className="pl-chips">
      {(['true', 'false'] as const).map(choice => <label key={choice}>
        <input type="radio" name={id} value={choice} checked={notation === choice} onChange={() => onChange(choice)}
          onKeyDown={event => { if (event.key === 'Enter') { event.preventDefault(); onEnter?.(); } }} /> {choice === 'true' ? 'Yes' : 'No'}
      </label>)}
    </div> : <>
      <label><input type="checkbox" checked={textMode} onChange={event => setPlain(event.target.checked)} /> Edit as text</label>
      {textMode ? <label className="pl-label" htmlFor={id}>Answer notation<input className="pl-input" id={id} value={value}
        onChange={event => onChange(event.target.value)} onKeyDown={event => { if (event.key === 'Enter') { event.preventDefault(); onEnter?.(); } }}
        aria-invalid={state === 'invalid' || analysis.status === 'error'} autoComplete="off" spellCheck={false} /></label>
        : spec.kind === 'finite_set' ? <>
          {parts.map((part, index) => <div key={index} className="pl-stack pl-gap-2">
            <AnswerInput id={`${id}-${index}`} label={`Set entry ${index + 1}`} value={part} variables={[]} assist placeholder="e.g. 1/2"
              onChange={text => updateSet(parts.map((old, position) => position === index ? text : old))} onEnter={onEnter} />
            <button type="button" className="pl-btn pl-btn--ghost" onClick={() => updateSet(parts.filter((_, position) => position !== index))}>Remove entry {index + 1}</button>
          </div>)}
          <div className="pl-actions"><button type="button" className="pl-btn pl-btn--secondary" disabled={parts.length >= 8} onClick={() => updateSet([...parts, ''])}>Add entry</button>
            <button type="button" className="pl-btn pl-btn--ghost" onClick={() => updateSet([])}>Empty set</button></div>
        </> : <>{[0, 1].map(index => {
          const side = index === 0 ? 'Lower' : 'Upper'; const infinite = index === 0 ? '-inf' : 'inf';
          return <div key={index} className="pl-stack pl-gap-2">
            <label className="pl-label">{side} bound type<select className="pl-input" value={parts[index] === infinite ? 'unbounded' : 'finite'}
              onChange={event => updateInterval(index, event.target.value === 'unbounded' ? infinite : '')}>
              <option value="finite">Finite</option><option value="unbounded">{index === 0 ? 'Negative infinity' : 'Positive infinity'}</option></select></label>
            {parts[index] !== infinite && <AnswerInput id={`${id}-${index}`} label={`${side} endpoint`} value={parts[index] ?? ''} variables={[]} assist placeholder="e.g. 1/2"
              onChange={text => updateInterval(index, text)} onEnter={onEnter} />}
            <label className="pl-label">{side} endpoint inclusion<select className="pl-input" disabled={parts[index] === infinite}
              value={parts[index] === infinite || (index === 0 ? notation.startsWith('(') : notation.endsWith(')')) ? 'open' : 'closed'}
              onChange={event => updateInterval(index, parts[index] ?? '', index === 0 ? (event.target.value === 'open' ? '(' : '[') : undefined,
                index === 1 ? (event.target.value === 'open' ? ')' : ']') : undefined)}>
              <option value="closed">Included</option><option value="open">Excluded</option></select></label>
          </div>;
        })}</>}
    </>}
    {spec.kind === 'boolean' && notation && !['true', 'false'].includes(notation) ? <p>Previous answer: <code>{value}</code></p> : null}
    <div id={`${id}-preview`} className="pl-preview" role="status">
      {analysis.status === 'ok' ? <><span className="pl-label">Reads as</span><Tex latex={analysis.latex} /></>
        : <p className={analysis.status === 'error' ? 'pl-preview-problem' : 'pl-preview-note'}>{analysis.status === 'empty' ? (spec.kind === 'boolean' ? 'Choose Yes or No.' : 'Enter your answer.') : analysis.message}</p>}
    </div>
  </fieldset>;
}
