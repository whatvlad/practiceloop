import type { WorksheetPageOptions } from '../data/worksheets';
import { Chips } from './TopicChips';

interface WorksheetOptionsProps {
  value: WorksheetPageOptions;
  onChange: (value: WorksheetPageOptions) => void;
  disabled?: boolean;
  /** Prefix for element ids, so two option blocks can share a page. */
  idPrefix: string;
}

/** ADR-007 page options shared by the Practice builder (#117) and the History export (#118). */
export function WorksheetOptions({ value, onChange, disabled = false, idPrefix }: WorksheetOptionsProps) {
  const off = disabled ? [] : undefined;
  return (
    <div className="pl-stack pl-gap-4">
      <div className="pl-worksheet-options">
        <div className="pl-stack pl-gap-2">
          <div id={`${idPrefix}-paper`} className="pl-label">Paper</div>
          <Chips label="Paper" labelledBy={`${idPrefix}-paper`} selected={value.paper} available={off}
            options={[{ value: 'a4', label: 'A4' }, { value: 'letter', label: 'Letter' }]}
            onSelect={(paper) => onChange({ ...value, paper })} />
        </div>
        <div className="pl-stack pl-gap-2">
          <div id={`${idPrefix}-columns`} className="pl-label">Layout</div>
          <Chips label="Layout" labelledBy={`${idPrefix}-columns`} selected={value.columns === 2 ? '2' : '1'} available={off}
            options={[{ value: '1', label: 'One column' }, { value: '2', label: 'Two columns' }]}
            onSelect={(columns) => onChange({ ...value, columns: columns === '2' ? 2 : 1 })} />
        </div>
      </div>
      <label className="pl-row pl-worksheet-check">
        <input type="checkbox" checked={value.answerKey} disabled={disabled}
          aria-describedby={`${idPrefix}-key-note`} onChange={(event) => onChange({ ...value, answerKey: event.target.checked })} />
        <span>Include answer key</span>
      </label>
      <p id={`${idPrefix}-key-note`} className="pl-small pl-muted pl-m-0">
        {value.answerKey
          ? 'The final answers are printed on the last page, so these problems are marked as answer revealed in your history.'
          : 'No answers are printed, and the problems stay unrevealed until you reveal them.'}
      </p>
    </div>
  );
}
