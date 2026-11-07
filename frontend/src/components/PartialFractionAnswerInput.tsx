import { AnswerInput } from './AnswerInput';

export function PartialFractionAnswerInput({ labels, value, onChange, onEnter, legend = 'Partial-fraction coefficients' }: {
  labels: string[]; value: string; onChange: (value: string) => void; onEnter?: () => void; legend?: string;
}) {
  const existing = value.startsWith('(') && value.endsWith(')') ? value.slice(1, -1).split(';') : [];
  const parts = labels.map((_, index) => existing[index] ?? '');
  const update = (index: number, next: string) => {
    const values = [...parts]; values[index] = next; onChange(`(${values.join(';')})`);
  };
  return <fieldset className={`pl-field pl-stack pl-gap-3${legend === 'Centre and radius' ? ' pl-circle-answer' : ''}`}><legend className="pl-label">{legend}</legend>
    {labels.map((label, index) => <AnswerInput key={label} id={`answer-coefficient-${index}`} label={label} value={parts[index]} onChange={next => update(index, next)} onEnter={onEnter} variables={[]} keypadVariables={[]} assist placeholder="e.g. 1/2" />)}
  </fieldset>;
}
