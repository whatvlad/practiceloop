import { analyseComputationalAnswer, splitComputationalParts } from '../answerSyntax';
import type { CheckResult, ComputationalInputSpec } from '../data/types';
import { ComputationalAnswerInput } from './ComputationalAnswerInput';
import { Tex } from './Tex';

interface Props {
  id: string;
  spec: ComputationalInputSpec;
  value: string;
  onChange: (value: string) => void;
  state?: CheckResult | null;
  onEnter?: () => void;
  describedBy?: string;
}

/** The existing ordered-tuple contract, presented as three compact coordinates. */
export function VectorAnswerInput(props: Props) {
  const { id, spec, value, onChange, state, onEnter, describedBy } = props;
  let parts: string[] | undefined;
  try {
    const text = value.trim();
    parts = !text ? ['', '', ''] : text.startsWith('(') && text.endsWith(')')
      ? splitComputationalParts(text.slice(1, -1), ';') : undefined;
    if (parts?.length !== 3) parts = undefined;
  } catch { /* Keep an old malformed answer editable as text. */ }
  if (!parts) return <ComputationalAnswerInput {...props} />;
  const entries = parts;
  const complete = entries.every(part => part.trim());
  const analysis = complete ? analyseComputationalAnswer(value, spec) : null;
  const invalid = state === 'invalid' || analysis?.status === 'error';
  return <fieldset className="pl-structured-answer pl-vector-answer pl-field pl-stack pl-gap-3"
    aria-describedby={[`${id}-hint`, `${id}-preview`, describedBy].filter(Boolean).join(' ')}>
    <legend className="pl-label">Your answer</legend>
    <div className="pl-vector-grid">{entries.map((entry, index) => {
      const label = spec.labels![index];
      return <label className="pl-label" key={label} htmlFor={`${id}-${index}`}>{label}
        <input id={`${id}-${index}`} aria-label={label} className="pl-input" value={entry}
          autoComplete="off" spellCheck={false} aria-invalid={invalid}
          onChange={event => onChange(`(${entries.map((old, i) => i === index ? event.target.value : old).join(';')})`)}
          onKeyDown={event => { if (event.key === 'Enter') { event.preventDefault(); onEnter?.(); } }} />
      </label>;
    })}</div>
    <p id={`${id}-hint`} className="pl-small pl-muted">Use exact values, for example <code>1/2</code> or <code>sqrt(3)</code>.</p>
    <div id={`${id}-preview`} className="pl-preview" role="status">
      {analysis?.status === 'ok' ? <><span className="pl-label">Reads as</span><Tex latex={analysis.latex} /></>
        : analysis?.status === 'error' ? <p className="pl-preview-problem">{analysis.message}</p> : null}
    </div>
  </fieldset>;
}
