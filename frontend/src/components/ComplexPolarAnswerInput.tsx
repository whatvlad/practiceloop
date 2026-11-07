import { AnswerInput } from './AnswerInput';

export function ComplexPolarAnswerInput({ value, onChange, onEnter }: {
  value: string; onChange: (value: string) => void; onEnter?: () => void;
}) {
  const parts = value.startsWith('(') && value.endsWith(')') ? value.slice(1, -1).split(';') : ['', ''];
  const update = (index: number, next: string) => {
    const values = [parts[0] ?? '', parts[1] ?? ''];
    values[index] = next;
    onChange(`(${values.join(';')})`);
  };
  return <fieldset className="pl-field pl-stack pl-gap-3"><legend className="pl-label">Your answer</legend>
    <AnswerInput id="answer-modulus" label="Modulus r" value={parts[0] ?? ''} onChange={next => update(0, next)} onEnter={onEnter} variables={[]} keypadVariables={[]} assist placeholder="e.g. sqrt(2)" />
    <AnswerInput id="answer-argument" label="Principal argument in radians" value={parts[1] ?? ''} onChange={next => update(1, next)} onEnter={onEnter} variables={[]} keypadVariables={[]} assist placeholder="e.g. pi/4" />
    <p className="pl-small pl-muted">Use the principal argument in (−π, π].</p>
  </fieldset>;
}
