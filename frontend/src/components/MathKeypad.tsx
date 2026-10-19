import { useState, type MouseEvent } from 'react';

/**
 * Text a key adds at the caret; `close` goes after the selection, which it wraps.
 * `latex` is the same key for the formula editor, in MathLive insert syntax:
 * #0 is the selection, #@ the term before the caret and #? an empty box.
 */
export interface KeypadInsert {
  open: string;
  close?: string;
  latex: string;
}

/** A caret move by one character. */
export type KeypadMove = -1 | 1;

export interface Key {
  label: string;
  name: string;
  insert?: KeypadInsert;
  move?: KeypadMove;
  /** Show the label in the math font. */
  math?: boolean;
}

const fn = (name: string, label = name, command = label): Key => ({
  label,
  name,
  insert: { open: `${name}(`, close: ')', latex: `\\${command}\\left(#0\\right)` },
});

export const MAIN_KEYS: readonly Key[] = [
  { label: 'x', name: 'x', insert: { open: 'x', latex: 'x' }, math: true },
  { label: 'π', name: 'pi', insert: { open: 'pi', latex: '\\pi' }, math: true },
  { label: 'eˣ', name: 'e to the power', insert: { open: 'e^(', close: ')', latex: 'e^{#0}' }, math: true },
  { label: 'x²', name: 'squared', insert: { open: '^2', latex: '#@^{2}' }, math: true },
  { label: 'xⁿ', name: 'power', insert: { open: '^', latex: '#@^{#?}' }, math: true },
  { label: '√', name: 'square root', insert: { open: 'sqrt(', close: ')', latex: '\\sqrt{#0}' }, math: true },
  { label: '( )', name: 'brackets', insert: { open: '(', close: ')', latex: '\\left(#0\\right)' } },
  { label: '|x|', name: 'absolute value', insert: { open: 'abs(', close: ')', latex: '\\left|#0\\right|' }, math: true },
  { label: '+', name: 'plus', insert: { open: '+', latex: '+' } },
  { label: '−', name: 'minus', insert: { open: '-', latex: '-' } },
  { label: '×', name: 'times', insert: { open: '*', latex: '\\cdot' } },
  { label: '÷', name: 'divide', insert: { open: '/', latex: '\\frac{#@}{#?}' } },
  fn('sin'),
  fn('cos'),
  fn('tan'),
  fn('ln'),
  { label: '+C', name: 'plus constant', insert: { open: ' + C', latex: '+C' }, math: true },
  { label: '←', name: 'move left', move: -1 },
  { label: '→', name: 'move right', move: 1 },
];

export const MORE_KEYS: readonly Key[] = [
  fn('sec'),
  fn('csc'),
  fn('cot'),
  fn('asin', 'arcsin'),
  fn('acos', 'arccos'),
  fn('atan', 'arctan'),
  fn('exp'),
];

interface MathKeypadProps {
  /** `fromPointer` is false for keyboard activation, which keeps focus on the key. */
  onInsert: (insert: KeypadInsert, fromPointer: boolean) => void;
  onMove: (step: KeypadMove, fromPointer: boolean) => void;
  disabled?: boolean;
}

/** Math keys under the answer field, like the WolframAlpha app's extra keyboard row. */
export function MathKeypad({ onInsert, onMove, disabled }: MathKeypadProps) {
  const [more, setMore] = useState(false);
  const keys = more ? [...MAIN_KEYS, ...MORE_KEYS] : MAIN_KEYS;
  function press(key: Key, event: MouseEvent<HTMLButtonElement>) {
    const fromPointer = event.detail > 0;
    if (key.insert) onInsert(key.insert, fromPointer);
    else if (key.move) onMove(key.move, fromPointer);
  }
  return (
    <div className="pl-keypad" role="group" aria-label="Math keypad">
      {keys.map((key) => (
        <button
          key={key.name}
          type="button"
          className={['pl-key', key.math && 'is-math', key.label.length > 4 && 'is-wide'].filter(Boolean).join(' ')}
          aria-label={key.name}
          disabled={disabled}
          // Keep the caret, and the phone keyboard, in the answer field.
          onPointerDown={(event) => event.preventDefault()}
          onClick={(event) => press(key, event)}
        >
          {key.label}
        </button>
      ))}
      <button
        type="button"
        className="pl-key is-toggle"
        aria-expanded={more}
        disabled={disabled}
        onPointerDown={(event) => event.preventDefault()}
        onClick={() => setMore(!more)}
      >
        {more ? 'Less' : 'More'}
      </button>
    </div>
  );
}
