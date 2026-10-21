// @vitest-environment jsdom
import { act, useState } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AnswerInput } from './AnswerInput';
import { keyboardLayouts, loadMathLive } from './FormulaField';

// A stand-in for MathLive's <math-field>: it holds LaTeX and records what the keypad sends.
vi.mock('mathlive', () => {
  class FakeMathfield extends HTMLElement {
    static fontsDirectory: string | null = '';
    static soundsDirectory: string | null = '';
    static keypressSound: unknown = null;
    static plonkSound: unknown = null;
    static scientificNotationTemplate: string | null = '#1\\times10^{#2}';
    latex = '';
    inserted: string[] = [];
    commands: unknown[] = [];
    keybindings = [{ key: '[Escape]', command: ['switchMode', 'latex'] }, { key: '[Tab]', command: 'moveToNextPlaceholder' }];
    getValue() {
      return this.latex;
    }
    setValue(latex: string) {
      this.latex = latex;
    }
    insert(latex: string) {
      this.inserted.push(latex);
    }
    executeCommand(command: unknown) {
      this.commands.push(command);
    }
    hasFocus() {
      return document.activeElement === this;
    }
    type(latex: string) {
      this.latex = latex;
      this.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }
  customElements.define('math-field', FakeMathfield);
  return {
    MathfieldElement: FakeMathfield,
    convertAsciiMathToLatex: (text: string) => `\\text{${text}}`,
  };
});

type Fake = HTMLElement & {
  latex: string;
  mathVirtualKeyboardPolicy: string;
  inserted: string[];
  commands: unknown[];
  keybindings: { key: string }[];
  type: (latex: string) => void;
};

let root: Root;
let element: HTMLDivElement;
const changes: string[] = [];
let checks = 0;

function Harness({ initial = '' }: { initial?: string }) {
  const [value, setValue] = useState(initial);
  return (
    <>
      <AnswerInput
        id="answer"
        value={value}
        onChange={(next) => {
          changes.push(next);
          setValue(next);
        }}
        onEnter={() => (checks += 1)}
        assist
      />
      <button type="button" id="reset" onClick={() => setValue('')} />
    </>
  );
}

async function render(initial?: string) {
  await act(async () => {
    root.render(<Harness initial={initial} />);
    await loadMathLive();
  });
}

const field = () => element.querySelector('math-field') as Fake;
const preview = () => element.querySelector('.pl-preview')!.textContent;

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  element = document.createElement('div');
  document.body.append(element);
  root = createRoot(element);
  changes.length = 0;
  checks = 0;
});

afterEach(() => {
  act(() => root.unmount());
  element.remove();
});

describe('AnswerInput formula editor', () => {
  it('replaces the text box and turns off LaTeX mode', async () => {
    await render();
    expect(element.querySelector('input')).toBeNull();
    expect(field().id).toBe('answer');
    expect(field().keybindings.map((binding) => binding.key)).toEqual(['[Tab]']);
  });

  it('never turns a number before e into scientific notation', async () => {
    const module = await loadMathLive();
    expect(module?.MathfieldElement.scientificNotationTemplate).toBeNull();
  });

  it('sends what the editor holds as answer text and previews it', async () => {
    await render();
    act(() => field().type('\\frac{x^2}{2}+C'));
    expect(changes).toEqual(['x^2/2 + C']);
    expect(preview()).toContain('Reads as');
    act(() => field().type('x\\left(x+1\\right)'));
    expect(changes.at(-1)).toBe('x*(x + 1)');
    expect(field().getAttribute('aria-invalid')).toBeNull();
  });

  it('treats an empty box as unfinished, not wrong', async () => {
    await render();
    act(() => field().type('\\frac{x}{\\placeholder{}}'));
    expect(preview()).toBe('Fill in the empty box to finish.');
    expect(field().getAttribute('aria-invalid')).toBeNull();
  });

  it('ignores input events that do not change the answer', async () => {
    await render();
    act(() => field().type('x'));
    act(() => field().type('x'));
    expect(changes).toEqual(['x']);
  });

  it('drives the editor from the keypad', async () => {
    await render();
    act(() => {
      element.querySelector<HTMLButtonElement>('button[aria-label="square root"]')!.click();
      element.querySelector<HTMLButtonElement>('button[aria-label="divide"]')!.click();
      element.querySelector<HTMLButtonElement>('button[aria-label="move left"]')!.click();
    });
    expect(field().inserted).toEqual(['\\sqrt{#0}', '\\frac{#@}{#?}']);
    expect(field().commands).toEqual(['moveToPreviousChar']);
  });

  it('leaves the phone keyboard to MathLive, which keeps it open through a key tap', async () => {
    vi.stubGlobal('matchMedia', (query: string) => ({ matches: query === '(pointer: coarse)' }));
    try {
      await render();
      expect(field().mathVirtualKeyboardPolicy).toBe('auto');
      expect(element.querySelector('.pl-keypad')).toBeNull();
    } finally {
      vi.unstubAllGlobals();
    }
  });

  it('keeps the phone keyboard off on desktop, where the inline keypad is', async () => {
    await render();
    expect(field().mathVirtualKeyboardPolicy).toBe('manual');
    expect(element.querySelector('.pl-keypad')).not.toBeNull();
  });

  it('gives long key labels two columns', async () => {
    await render();
    act(() => element.querySelector<HTMLButtonElement>('.pl-key.is-toggle')!.click());
    const wide = [...element.querySelectorAll('.pl-key.is-wide')].map((key) => key.textContent);
    expect(wide).toEqual(['arcsin', 'arccos', 'arctan']);
  });

  it('checks on Enter', async () => {
    await render();
    act(() => {
      field().dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    });
    expect(checks).toBe(1);
  });

  it('shows a value set from outside, and clears with it', async () => {
    await render('x^2/2 + C');
    expect(field().latex).toBe('\\frac{x^{2}}{2}+C');
    act(() => element.querySelector<HTMLButtonElement>('#reset')!.click());
    expect(field().latex).toBe('');
  });
});

type Layout = { rows: (string | { label: string; insert: string })[][] };
const labels = (variables?: Parameters<typeof keyboardLayouts>[0]) =>
  (keyboardLayouts(variables)[0] as Layout).rows.flat().map((key) => (typeof key === 'string' ? key : key.label));

describe('phone keyboard answer variables (ADR-005)', () => {
  it('keeps x and +C for integration exercises', () => {
    expect(labels()).toEqual(expect.arrayContaining(['x', '+C']));
    for (const label of ['y', 'z', 'r', 'θ']) expect(labels()).not.toContain(label);
  });

  it('shows only the declared variables, θ inserting \\theta', () => {
    expect(labels(['r', 'theta', 'z'])).toEqual(expect.arrayContaining(['r', 'θ', 'z']));
    for (const label of ['x', 'y', '+C']) expect(labels(['r', 'theta', 'z'])).not.toContain(label);
    const theta = (keyboardLayouts(['r', 'theta'])[0] as Layout).rows.flat().find((key) => typeof key !== 'string' && key.label === 'θ');
    expect(theta).toMatchObject({ insert: '\\theta' });
  });

  it("switches the shared keyboard to the focused exercise's variables", async () => {
    const keyboard = { layouts: [] as unknown, addEventListener: () => {}, visible: false };
    vi.stubGlobal('mathVirtualKeyboard', keyboard);
    try {
      await act(async () => {
        root.render(<AnswerInput id="answer" value="" onChange={() => {}} assist variables={['x', 'y']} />);
        await loadMathLive();
      });
      act(() => field().dispatchEvent(new FocusEvent('focusin', { bubbles: true })));
      const first = (keyboard.layouts as Layout[])[0].rows[0][0];
      expect(first).toMatchObject({ label: 'x' });
      expect((keyboard.layouts as Layout[])[0].rows.flat()).toEqual(expect.arrayContaining([expect.objectContaining({ label: 'y' })]));
    } finally {
      vi.unstubAllGlobals();
    }
  });
});
