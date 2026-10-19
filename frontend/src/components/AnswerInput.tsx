import { useLayoutEffect, useMemo, useRef, type KeyboardEvent, type ReactNode } from 'react';
import { analyseAnswer } from '../answerSyntax';
import type { CheckResult } from '../data/types';
import { MathKeypad, type KeypadInsert, type KeypadMove } from './MathKeypad';
import { Tex } from './Tex';

interface AnswerInputProps {
  id: string;
  label?: string;
  value: string;
  onChange: (value: string) => void;
  /** Result from the checker; only changes the border. */
  state?: CheckResult | null;
  placeholder?: string;
  hint?: ReactNode;
  /** Id of the element that describes the current result. */
  describedBy?: string;
  onEnter?: () => void;
  readOnly?: boolean;
  /** Math keypad plus a live preview that flags syntax mistakes while typing. */
  assist?: boolean;
}

export function AnswerInput({
  id,
  label = 'Your answer',
  value,
  onChange,
  state,
  placeholder = 'e.g. sin(x^2) + C',
  hint,
  describedBy,
  onEnter,
  readOnly,
  assist = false,
}: AnswerInputProps) {
  const input = useRef<HTMLInputElement>(null);
  const caret = useRef<number | null>(null);
  const analysis = useMemo(() => (assist ? analyseAnswer(value) : null), [assist, value]);
  const hintId = hint ? `${id}-hint` : undefined;
  const previewId = assist ? `${id}-preview` : undefined;

  useLayoutEffect(() => {
    if (caret.current === null || !input.current) return;
    input.current.setSelectionRange(caret.current, caret.current);
    caret.current = null;
  }, [value]);

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter' && onEnter) {
      event.preventDefault();
      onEnter();
    }
  }

  function replace(next: string, nextCaret: number, focus: boolean) {
    caret.current = nextCaret;
    if (focus) input.current?.focus();
    if (next === value) {
      input.current?.setSelectionRange(nextCaret, nextCaret);
      caret.current = null;
    } else {
      onChange(next);
    }
  }

  function insert({ open, close = '' }: KeypadInsert, focus: boolean) {
    const field = input.current;
    const start = field?.selectionStart ?? value.length;
    const end = field?.selectionEnd ?? value.length;
    const selected = value.slice(start, end);
    const next = value.slice(0, start) + open + selected + close + value.slice(end);
    replace(next, start + open.length + selected.length + (selected ? close.length : 0), focus);
  }

  function move(step: KeypadMove, focus: boolean) {
    const at = input.current?.selectionStart ?? value.length;
    replace(value, Math.min(value.length, Math.max(0, at + step)), focus);
  }

  return (
    <div className="pl-field">
      <label className="pl-label" htmlFor={id}>
        {label}
      </label>
      <input
        ref={input}
        id={id}
        className={state ? `pl-input is-${state}` : 'pl-input'}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoComplete="off"
        autoCapitalize="off"
        autoCorrect="off"
        spellCheck={false}
        readOnly={readOnly}
        aria-invalid={state === 'invalid' || analysis?.status === 'error' || undefined}
        aria-describedby={[previewId, hintId, describedBy].filter(Boolean).join(' ') || undefined}
      />
      {analysis && (
        <div id={previewId} className="pl-preview">
          <AnswerPreview analysis={analysis} onFix={(fix) => replace(fix, fix.length, true)} />
        </div>
      )}
      {assist && !readOnly && <MathKeypad onInsert={insert} onMove={move} />}
      {hint && (
        <div id={hintId} className="pl-hint">
          {hint}
        </div>
      )}
    </div>
  );
}

function AnswerPreview({
  analysis,
  onFix,
}: {
  analysis: ReturnType<typeof analyseAnswer>;
  onFix: (fix: string) => void;
}) {
  const fixButton = (fix: string | undefined) =>
    fix && (
      <button type="button" className="pl-preview-fix" onClick={() => onFix(fix)}>
        Use <code>{fix}</code>
      </button>
    );
  switch (analysis.status) {
    case 'empty':
      return <span className="pl-preview-note">The answer appears here as you type.</span>;
    case 'unfinished':
      return <span className="pl-preview-note">{analysis.message}</span>;
    case 'error':
      return (
        <p className="pl-preview-problem">
          <span>{analysis.message}</span> {fixButton(analysis.fix)}
        </p>
      );
    case 'ok':
      return (
        <>
          <div className="pl-preview-math">
            <span className="pl-label">Reads as</span>
            <Tex latex={analysis.latex} />
          </div>
          {analysis.warning && (
            <p className="pl-preview-problem">
              <span>{analysis.warning}</span> {fixButton(analysis.fix)}
            </p>
          )}
        </>
      );
  }
}
