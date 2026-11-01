import { useEffect, useRef, useState } from 'react';
import type { MathfieldElement, VirtualKeyboardLayout, VirtualKeyboardName } from 'mathlive';
import { analyseAnswer, type AnswerVariable } from '../answerSyntax';
import { latexToAnswer, type EditorAnswer } from '../mathEditor';
import { MAIN_KEYS, MORE_KEYS, mainKeys, type Key } from './MathKeypad';

type MathLive = typeof import('mathlive');

let loading: Promise<MathLive | null> | null = null;

/** Loads the formula editor once, on first use; null where it cannot run (tests, old browsers). */
export function loadMathLive(): Promise<MathLive | null> {
  loading ??= import('mathlive')
    .then((module) => {
      if (typeof module.MathfieldElement !== 'function' || !window.customElements) return null;
      // KaTeX's stylesheet (main.tsx) already loads the same fonts.
      module.MathfieldElement.fontsDirectory = null;
      module.MathfieldElement.soundsDirectory = null;
      module.MathfieldElement.keypressSound = null;
      module.MathfieldElement.plonkSound = null;
      // e is the constant, never scientific notation: keep 3e-6 from becoming 3×10^{-6}.
      module.MathfieldElement.scientificNotationTemplate = null;
      configureKeyboard();
      return module;
    })
    .catch(() => null);
  return loading;
}

/** Phones and tablets get MathLive's keyboard in place of the inline keypad. */
export function usesPhoneKeyboard(): boolean {
  return window.matchMedia?.('(pointer: coarse)').matches ?? false;
}

export function useMathLive(enabled: boolean): MathLive | null {
  const [module, setModule] = useState<MathLive | null>(null);
  useEffect(() => {
    if (!enabled) return;
    let live = true;
    void loadMathLive().then((loaded) => {
      if (live) setModule(loaded);
    });
    return () => {
      live = false;
    };
  }, [enabled]);
  return enabled ? module : null;
}

/** Typing a name turns it into the function, matching the keypad. */
const SHORTCUTS: Record<string, string> = {
  pi: '\\pi',
  sqrt: '\\sqrt{#?}',
  sin: '\\sin',
  cos: '\\cos',
  tan: '\\tan',
  sec: '\\sec',
  csc: '\\csc',
  cot: '\\cot',
  arcsin: '\\arcsin',
  arccos: '\\arccos',
  arctan: '\\arctan',
  asin: '\\arcsin',
  acos: '\\arccos',
  atan: '\\arctan',
  ln: '\\ln',
  log: '\\log',
  exp: '\\exp',
  abs: '\\left|#?\\right|',
  theta: '\\theta',
};

const keycap = (key: Key) =>
  key.insert
    ? { label: key.label, insert: key.insert.latex, ariaLabel: key.name, class: key.math ? '' : 'small' }
    : key.move === -1
      ? '[left]'
      : '[right]';

const byName = (name: string) => [...MAIN_KEYS, ...MORE_KEYS].find((key) => key.name === name)!;

function configureKeyboard() {
  const keyboard = window.mathVirtualKeyboard;
  if (!keyboard) return;
  // Keep the page scrollable above the keyboard, with the answer in view.
  keyboard.addEventListener('geometrychange', () => {
    const height = keyboard.visible ? keyboard.boundingRect.height : 0;
    document.body.style.paddingBottom = height ? `${height}px` : '';
    if (height) document.activeElement?.closest('.pl-field')?.scrollIntoView({ block: 'center' });
  });
  keyboard.layouts = keyboardLayouts();
}

/**
 * The phone keyboard: the keypad's keys plus digits, in MathLive's virtual keyboard.
 * The first variable takes x's place and the others take +C's (ADR-005).
 */
export function keyboardLayouts(variables?: readonly AnswerVariable[]): (VirtualKeyboardLayout | VirtualKeyboardName)[] {
  const keys = (...names: string[]) => names.map((name) => keycap(byName(name)));
  const [first, ...rest] = mainKeys(variables)
    .filter((key) => key.name === 'x' || key.name === 'plus constant' || isVariableKey(key, variables))
    .map(keycap);
  return [
    {
      label: '123',
      tooltip: 'Numbers and operators',
      rows: [
        [...(first === undefined ? [] : [first]), ...keys('pi', 'e to the power', 'squared'), '[separator-5]', '7', '8', '9', keycap(byName('divide'))],
        [...keys('power', 'square root', 'brackets', 'absolute value'), '[separator-5]', '4', '5', '6', keycap(byName('times'))],
        [...keys('sin', 'cos', 'tan', 'ln'), '[separator-5]', '1', '2', '3', keycap(byName('minus'))],
        [...rest, '[left]', '[right]', '[backspace]', '[separator-5]', '0', '.', '[return]', keycap(byName('plus'))],
      ],
    },
    {
      label: 'f(x)',
      tooltip: 'More functions',
      rows: [
        MORE_KEYS.slice(0, 4).map(keycap),
        [...MORE_KEYS.slice(4).map(keycap), '[backspace]'],
        ['[left]', '[right]', '[return]'],
      ],
    },
    'alphabetic',
  ];
}

const isVariableKey = (key: Key, variables?: readonly AnswerVariable[]) =>
  variables?.some((name) => name === key.name) ?? false;

/** The keyboard is shared by every field: show the focused exercise's variables. */
function showKeyboardFor(variables?: readonly AnswerVariable[]) {
  const keyboard = window.mathVirtualKeyboard;
  if (keyboard) keyboard.layouts = keyboardLayouts(variables);
}

/** LaTeX for answer text set from outside (a reset, an applied fix). */
function answerLatex(text: string, module: MathLive, variables?: readonly AnswerVariable[]): string {
  if (text.trim() === '') return '';
  const analysis = analyseAnswer(text, variables);
  return analysis.status === 'ok' ? analysis.latex : module.convertAsciiMathToLatex(text);
}

/** `e.g. x^2/2 + C` shown the way the editor would show the example. */
function placeholderLatex(text: string, module: MathLive): string {
  const example = /^e\.g\.\s*/.exec(text);
  if (!example) return `\\mathrm{${text}}`;
  return `\\mathrm{e.g.}\\;${answerLatex(text.slice(example[0].length), module)}`;
}

interface FormulaFieldProps {
  module: MathLive;
  id: string;
  label: string;
  value: string;
  onChange: (answer: EditorAnswer) => void;
  className: string;
  placeholder: string;
  invalid: boolean;
  describedBy?: string;
  onEnter?: () => void;
  fieldRef: { current: MathfieldElement | null };
  /** The exercise's declared answer variables; omitted for integration. */
  variables?: readonly AnswerVariable[];
  keypadVariables?: readonly AnswerVariable[];
}

/** The answer as a 2D formula: `/` builds a fraction, `^` raises an exponent, `sqrt` a root. */
export function FormulaField({
  module,
  id,
  label,
  value,
  onChange,
  className,
  placeholder,
  invalid,
  describedBy,
  onEnter,
  fieldRef,
  variables,
  keypadVariables,
}: FormulaFieldProps) {
  const host = useRef<HTMLDivElement>(null);
  const emitted = useRef<string | null>(null);
  const complete = useRef(true);
  const handlers = useRef({ onChange, onEnter, variables: keypadVariables ?? variables });
  useEffect(() => {
    handlers.current = { onChange, onEnter, variables: keypadVariables ?? variables };
  });

  useEffect(() => {
    const field = new module.MathfieldElement();
    field.id = id;
    // Most options need the element in the document first.
    host.current!.append(field);
    const coarse = usesPhoneKeyboard();
    // On phones MathLive shows its keyboard on focus and hides it only once focus has
    // really gone: iOS blurs the field for a moment on each key tap.
    field.mathVirtualKeyboardPolicy = coarse ? 'auto' : 'manual';
    field.inlineShortcuts = SHORTCUTS;
    // No LaTeX or text mode: Escape or a backslash would otherwise hide what is typed.
    field.keybindings = field.keybindings.filter(
      (binding) => !(Array.isArray(binding.command) && binding.command[0] === 'switchMode'),
    );
    field.menuItems = [];
    field.popoverPolicy = 'off';
    field.smartSuperscript = true;
    field.defaultMode = 'math';
    field.setAttribute('aria-label', label);
    const onInput = () => {
      const answer = latexToAnswer(field.getValue('latex'));
      // MathLive also sends input for Enter and moves; only real edits count.
      if (answer.text === emitted.current && answer.complete === complete.current) return;
      emitted.current = answer.text;
      complete.current = answer.complete;
      handlers.current.onChange(answer);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Enter' && handlers.current.onEnter) {
        event.preventDefault();
        handlers.current.onEnter();
      }
    };
    // The virtual keyboard's return key commits the field with a change event.
    const onCommit = () => {
      if (coarse && field.hasFocus()) handlers.current.onEnter?.();
    };
    // A tap on the empty part of the box should focus it too.
    const onClick = () => {
      if (!field.hasFocus()) field.focus();
    };
    const onFocus = () => showKeyboardFor(handlers.current.variables);
    field.addEventListener('focusin', onFocus);
    field.addEventListener('input', onInput);
    field.addEventListener('keydown', onKeyDown);
    field.addEventListener('change', onCommit);
    field.addEventListener('click', onClick);
    fieldRef.current = field;
    return () => {
      field.removeEventListener('focusin', onFocus);
      field.removeEventListener('input', onInput);
      field.removeEventListener('keydown', onKeyDown);
      field.removeEventListener('change', onCommit);
      field.removeEventListener('click', onClick);
      field.remove();
      fieldRef.current = null;
      emitted.current = null;
    };
  }, [module, id, label, fieldRef]);

  useEffect(() => {
    const field = fieldRef.current;
    if (!field || value === emitted.current) return;
    emitted.current = value;
    complete.current = true;
    field.setValue(answerLatex(value, module, variables), { silenceNotifications: true });
  }, [value, module, fieldRef, variables]);

  useEffect(() => {
    const field = fieldRef.current;
    if (!field) return;
    field.className = className;
    field.placeholder = placeholderLatex(placeholder, module);
    if (invalid) field.setAttribute('aria-invalid', 'true');
    else field.removeAttribute('aria-invalid');
    if (describedBy) field.setAttribute('aria-describedby', describedBy);
    else field.removeAttribute('aria-describedby');
  }, [className, placeholder, invalid, describedBy, fieldRef]);

  return <div ref={host} className="pl-formula-host" />;
}
