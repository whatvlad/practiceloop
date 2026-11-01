// @vitest-environment jsdom
import { act, useState } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { AnswerVariable } from '../answerSyntax';
import { AnswerInput } from './AnswerInput';

// These cover the plain-text field, used until (or where) the formula editor cannot load.
vi.mock('mathlive', () => ({}));

let root: Root;
let element: HTMLDivElement;

function Harness({ initial = '', variables }: { initial?: string; variables?: readonly AnswerVariable[] }) {
  const [value, setValue] = useState(initial);
  return <AnswerInput id="answer" value={value} onChange={setValue} assist variables={variables} />;
}

function field(): HTMLInputElement {
  return element.querySelector('input')!;
}

function key(name: string): HTMLButtonElement {
  return element.querySelector(`button[aria-label="${name}"]`)!;
}

// detail > 0 is a pointer click; keyboard activation sends 0.
function tap(button: HTMLButtonElement) {
  act(() => {
    button.dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 1 }));
  });
}

function render(initial?: string, variables?: readonly AnswerVariable[]) {
  act(() => root.render(<Harness initial={initial} variables={variables} />));
}

const keyLabels = () => [...element.querySelectorAll('.pl-key')].map((button) => button.textContent);

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  element = document.createElement('div');
  document.body.append(element);
  root = createRoot(element);
});

afterEach(() => {
  act(() => root.unmount());
  element.remove();
});

describe('AnswerInput assist', () => {
  it('inserts keypad text at the caret and keeps focus in the field', () => {
    render('x+C');
    field().setSelectionRange(1, 1);
    tap(key('squared'));
    expect(field().value).toBe('x^2+C');
    expect(field().selectionStart).toBe(3);
    expect(document.activeElement).toBe(field());
  });

  it('wraps the selection in a function and places the caret inside empty brackets', () => {
    render('x+1');
    field().setSelectionRange(0, 3);
    tap(key('square root'));
    expect(field().value).toBe('sqrt(x+1)');
    expect(field().selectionStart).toBe(9);

    tap(key('plus'));
    tap(key('sin'));
    expect(field().value).toBe('sqrt(x+1)+sin()');
    expect(field().selectionStart).toBe(14);
  });

  it('moves the caret with the arrow keys', () => {
    render('sin(x)');
    field().setSelectionRange(6, 6);
    tap(key('move left'));
    expect(field().selectionStart).toBe(5);
    tap(key('move right'));
    tap(key('move right'));
    expect(field().selectionStart).toBe(6);
  });

  it('shows more functions on request', () => {
    render();
    expect(key('arcsin')).toBeNull();
    tap(element.querySelector<HTMLButtonElement>('button[aria-expanded]')!);
    tap(key('atan'));
    expect(field().value).toBe('atan()');
  });

  it('previews how the answer reads', () => {
    render('x^2/2 + C');
    expect(element.querySelector('.pl-preview')!.textContent).toContain('Reads as');
    expect(element.querySelector('.pl-preview .katex')).not.toBeNull();
    expect(field().getAttribute('aria-invalid')).toBeNull();
  });

  it('flags a mistake while typing and applies the suggested fix', () => {
    render('x(x+1)');
    expect(field().getAttribute('aria-invalid')).toBe('true');
    expect(element.querySelector('.pl-preview-problem')!.textContent).toContain('Put * between them');
    tap(element.querySelector<HTMLButtonElement>('.pl-preview-fix')!);
    expect(field().value).toBe('x*(x+1)');
    expect(field().getAttribute('aria-invalid')).toBeNull();
  });

  it('does not flag unfinished input as wrong', () => {
    render('sqrt(');
    expect(field().getAttribute('aria-invalid')).toBeNull();
    expect(element.querySelector('.pl-preview')!.textContent).toBe('Close the bracket to finish.');
  });
});

describe('AnswerInput answer variables (ADR-005)', () => {
  it('changes suggested keys without changing the accepted answer grammar', () => {
    act(() => root.render(<AnswerInput id="answer" value="x-x+2" onChange={() => {}} assist keypadVariables={[]} />));
    expect(keyLabels()).not.toContain('x');
    expect(keyLabels()).not.toContain('+C');
    expect(element.querySelector('.pl-preview-math')).not.toBeNull();
    expect(field().getAttribute('aria-invalid')).toBeNull();
  });

  it('keeps the integration keys when the exercise declares no variables', () => {
    render();
    expect(keyLabels()).toContain('x');
    expect(keyLabels()).toContain('+C');
    for (const label of ['y', 'z', 'r', 'θ']) expect(keyLabels()).not.toContain(label);
  });

  it('offers only the declared variables, and no constant key', () => {
    render('', ['r', 'theta']);
    expect(keyLabels()).toEqual(expect.arrayContaining(['r', 'θ']));
    for (const label of ['x', 'y', 'z', '+C']) expect(keyLabels()).not.toContain(label);
  });

  it('types θ as theta and previews it with the declared variables', () => {
    render('', ['r', 'theta']);
    field().focus();
    tap(key('r'));
    tap(key('theta'));
    expect(field().value).toBe('rtheta');
    expect(element.querySelector('.pl-preview-problem')).toBeNull();
    expect(element.querySelector('.pl-preview-math')).not.toBeNull();
  });

  it('flags a variable the exercise does not use', () => {
    render('x + y', ['r', 'theta']);
    expect(element.querySelector('.pl-preview-problem')?.textContent).toContain('only r and θ');
  });
});
