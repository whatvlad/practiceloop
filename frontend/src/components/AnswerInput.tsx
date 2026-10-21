import { useLayoutEffect, useMemo, useRef, useState, type KeyboardEvent, type ReactNode } from 'react';
import type { MathfieldElement } from 'mathlive';
import { analyseAnswer, type AnswerVariable } from '../answerSyntax';
import type { CheckResult } from '../data/types';
import type { EditorAnswer } from '../mathEditor';
import { FormulaField, useMathLive, usesPhoneKeyboard } from './FormulaField';
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
  /**
   * Formula editor that shows the answer as 2D maths while typing, plus a math
   * keypad and a preview that flags syntax mistakes. Until the editor has
   * loaded (or where it cannot run) the field is plain text.
   */
  assist?: boolean;
  /**
   * ADR-005: the variables the exercise's template declares. The preview, keypad and
   * phone keyboard then use them; omitted, the integration grammar applies.
   */
  variables?: readonly AnswerVariable[];
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
  variables,
}: AnswerInputProps) {
  const input = useRef<HTMLInputElement>(null);
  const formula = useRef<MathfieldElement | null>(null);
  const caret = useRef<number | null>(null);
  const mathLive = useMathLive(assist && !readOnly);
  // An empty box in the formula editor (a fraction without its denominator, say).
  const [emptyBox, setEmptyBox] = useState(false);
  const analysis = useMemo(() => {
    if (!assist) return null;
    if (mathLive && emptyBox && value.trim() !== '') {
      return { status: 'unfinished', message: 'Fill in the empty box to finish.' } as const;
    }
    return analyseAnswer(value, variables);
  }, [assist, value, mathLive, emptyBox, variables]);
  const hintId = hint ? `${id}-hint` : undefined;
  const previewId = assist ? `${id}-preview` : undefined;
  const describedByIds = [previewId, hintId, describedBy].filter(Boolean).join(' ') || undefined;
  const invalid = state === 'invalid' || analysis?.status === 'error';
  const className = state ? `pl-input is-${state}` : 'pl-input';

  function handleFormula({ text, complete }: EditorAnswer) {
    setEmptyBox(!complete);
    onChange(text);
  }

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

  function insert({ open, close = '', latex }: KeypadInsert, focus: boolean) {
    if (formula.current) {
      formula.current.insert(latex, { focus, selectionMode: 'placeholder', format: 'latex' });
      return;
    }
    const field = input.current;
    const start = field?.selectionStart ?? value.length;
    const end = field?.selectionEnd ?? value.length;
    const selected = value.slice(start, end);
    const next = value.slice(0, start) + open + selected + close + value.slice(end);
    replace(next, start + open.length + selected.length + (selected ? close.length : 0), focus);
  }

  function move(step: KeypadMove, focus: boolean) {
    if (formula.current) {
      if (focus) formula.current.focus();
      formula.current.executeCommand(step < 0 ? 'moveToPreviousChar' : 'moveToNextChar');
      return;
    }
    const at = input.current?.selectionStart ?? value.length;
    replace(value, Math.min(value.length, Math.max(0, at + step)), focus);
  }

  return (
    <div className="pl-field">
      <label className="pl-label" htmlFor={id} onClick={() => formula.current?.focus()}>
        {label}
      </label>
      {mathLive ? (
        <FormulaField
          module={mathLive}
          id={id}
          label={label}
          value={value}
          onChange={handleFormula}
          className={`${className} pl-formula`}
          placeholder={placeholder}
          invalid={invalid}
          describedBy={describedByIds}
          onEnter={onEnter}
          fieldRef={formula}
          variables={variables}
        />
      ) : (
        <input
          ref={input}
          id={id}
          className={className}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          autoComplete="off"
          autoCapitalize="off"
          autoCorrect="off"
          spellCheck={false}
          readOnly={readOnly}
          aria-invalid={invalid || undefined}
          aria-describedby={describedByIds}
        />
      )}
      {analysis && (
        <div id={previewId} className="pl-preview">
          <AnswerPreview
            analysis={analysis}
            onFix={(fix) => {
              if (formula.current) {
                setEmptyBox(false);
                onChange(fix);
                formula.current.focus();
              } else replace(fix, fix.length, true);
            }}
          />
        </div>
      )}
      {assist && !readOnly && !(mathLive && usesPhoneKeyboard()) && <MathKeypad onInsert={insert} onMove={move} variables={variables} />}
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
