import { useLayoutEffect, useRef, useState } from 'react';
import { MathKeypad, type KeypadInsert, type KeypadMove } from './MathKeypad';
import type { AnswerVariable } from '../answerSyntax';

interface Props {
  value: string[][];
  onChange: (value: string[][]) => void;
  disabled?: boolean;
  variables?: readonly AnswerVariable[];
}

/** Cell editor only: validation and the wire format belong to the answer contract. */
export function MatrixAnswerInput({ value, onChange, disabled = false, variables }: Props) {
  const [active, setActive] = useState<[number, number] | null>(null);
  const fields = useRef(new Map<string, HTMLInputElement>());
  const caret = useRef<{ field: HTMLInputElement; position: number; focus: boolean } | null>(null);
  useLayoutEffect(() => {
    if (!caret.current) return;
    const { field, position, focus } = caret.current;
    if (focus) field.focus();
    field.setSelectionRange(position, position);
    caret.current = null;
  }, [value]);

  function change(row: number, column: number, next: string) {
    onChange(value.map((entries, r) => r === row ? entries.map((entry, c) => c === column ? next : entry) : entries));
  }
  function current() {
    if (!active) return null;
    const [row, column] = active;
    const field = fields.current.get(`${row},${column}`);
    return field ? { row, column, field, text: value[row]?.[column] ?? '' } : null;
  }
  function insert({ open, close = '' }: KeypadInsert, focus: boolean) {
    const cell = current();
    if (!cell) return;
    const start = cell.field.selectionStart ?? cell.text.length;
    const end = cell.field.selectionEnd ?? start;
    const selected = cell.text.slice(start, end);
    const next = cell.text.slice(0, start) + open + selected + close + cell.text.slice(end);
    const position = start + open.length + selected.length + (selected ? close.length : 0);
    if (next === cell.text) { if (focus) cell.field.focus(); cell.field.setSelectionRange(position, position); return; }
    caret.current = { field: cell.field, position, focus };
    change(cell.row, cell.column, next);
  }
  function move(step: KeypadMove, focus: boolean) {
    const cell = current();
    if (!cell) return;
    const at = cell.field.selectionStart ?? cell.text.length;
    const next = Math.max(0, Math.min(cell.text.length, at + step));
    if (focus) cell.field.focus();
    cell.field.setSelectionRange(next, next);
  }
  return <fieldset className="pl-matrix-answer" disabled={disabled}>
    <legend className="pl-label">Your answer</legend>
    <div className="pl-matrix-entry">
      <span className="pl-matrix-bracket pl-matrix-bracket--left" aria-hidden="true" />
      <div className="pl-matrix-grid" style={{ gridTemplateColumns: `repeat(${value[0]?.length ?? 0}, minmax(64px, 1fr))` }}>
        {value.flatMap((entries, row) => entries.map((entry, column) => <input
          key={`${row},${column}`}
          ref={field => { if (field) fields.current.set(`${row},${column}`, field); else fields.current.delete(`${row},${column}`); }}
          className="pl-input" aria-label={`Row ${row + 1}, column ${column + 1}`}
          value={entry} autoComplete="off" spellCheck={false}
          onFocus={() => setActive([row, column])}
          onChange={event => change(row, column, event.target.value)}
          onKeyDown={event => {
            const offsets: Record<string, [number, number]> = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1], Enter: [0, 1] };
            const offset = offsets[event.key];
            if (!offset || (event.key === 'ArrowLeft' && event.currentTarget.selectionStart !== 0)
              || (event.key === 'ArrowRight' && event.currentTarget.selectionStart !== entry.length)) return;
            const next = fields.current.get(`${row + offset[0]},${column + offset[1]}`);
            if (next) { event.preventDefault(); next.focus(); }
          }}
        />))}
      </div>
      <span className="pl-matrix-bracket pl-matrix-bracket--right" aria-hidden="true" />
    </div>
    {active && <div className="pl-matrix-keyboard">
      <div className="pl-row"><span className="pl-label">Math keypad</span><button type="button" className="pl-btn pl-btn--ghost pl-btn--sm" onClick={() => setActive(null)}>Close</button></div>
      <MathKeypad onInsert={insert} onMove={move} disabled={disabled} variables={variables} />
    </div>}
    <p className="pl-small pl-muted">Enter each element separately. Use arrow keys to move between cells.</p>
  </fieldset>;
}
