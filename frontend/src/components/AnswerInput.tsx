import type { KeyboardEvent, ReactNode } from 'react';
import type { CheckResult } from '../data/types';

interface AnswerInputProps {
  id: string;
  label?: string;
  value: string;
  onChange: (value: string) => void;
  /** Result from the checker; only changes the border. Never live-validated. */
  state?: CheckResult | null;
  placeholder?: string;
  hint?: ReactNode;
  /** Id of the element that describes the current result. */
  describedBy?: string;
  onEnter?: () => void;
  readOnly?: boolean;
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
}: AnswerInputProps) {
  const hintId = hint ? `${id}-hint` : undefined;
  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter' && onEnter) {
      event.preventDefault();
      onEnter();
    }
  }
  return (
    <div className="pl-field">
      <label className="pl-label" htmlFor={id}>
        {label}
      </label>
      <input
        id={id}
        className={state ? `pl-input is-${state}` : 'pl-input'}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoComplete="off"
        autoCapitalize="off"
        spellCheck={false}
        readOnly={readOnly}
        aria-invalid={state === 'invalid' || undefined}
        aria-describedby={[hintId, describedBy].filter(Boolean).join(' ') || undefined}
      />
      {hint && (
        <div id={hintId} className="pl-hint">
          {hint}
        </div>
      )}
    </div>
  );
}
