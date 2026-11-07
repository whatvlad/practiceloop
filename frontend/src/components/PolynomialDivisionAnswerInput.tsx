import { AnswerInput } from './AnswerInput';

export function PolynomialDivisionAnswerInput({ value, onChange, onEnter }: {
  value: string; onChange: (value: string) => void; onEnter?: () => void;
}) {
  const parts = value.startsWith('(') && value.endsWith(')') ? value.slice(1, -1).split(';') : ['', ''];
  const update = (index: number, next: string) => {
    const values = [parts[0] ?? '', parts[1] ?? '']; values[index] = next;
    onChange(`(${values.join(';')})`);
  };
  return <fieldset className="pl-field pl-stack pl-gap-3"><legend className="pl-label">Your answer</legend>
    <AnswerInput id="answer-quotient" label="Quotient Q(x)" value={parts[0] ?? ''} onChange={next => update(0, next)} onEnter={onEnter} variables={['x']} keypadVariables={['x']} assist placeholder="e.g. x^2+2x+1" />
    <AnswerInput id="answer-remainder" label="Remainder R(x)" value={parts[1] ?? ''} onChange={next => update(1, next)} onEnter={onEnter} variables={['x']} keypadVariables={['x']} assist placeholder="e.g. 0" />
  </fieldset>;
}
