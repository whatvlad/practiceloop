// @vitest-environment jsdom
import { act, useState } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { AnswerInput } from './AnswerInput';

let root: Root;
let element: HTMLDivElement;

function Harness({ initial = '' }: { initial?: string }) {
  const [value, setValue] = useState(initial);
  return <AnswerInput id="answer" value={value} onChange={setValue} assist />;
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

function render(initial?: string) {
  act(() => root.render(<Harness initial={initial} />));
}

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
