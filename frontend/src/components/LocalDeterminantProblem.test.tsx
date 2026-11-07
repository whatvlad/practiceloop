// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { LocalDeterminantProblem } from './LocalDeterminantProblem';

it('waits for settings and generates a determinant with a scalar answer', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (path: string, options?: RequestInit) => {
    expect(path).toContain('/generate');
    expect(options?.method).toBe('POST');
    return new Response(JSON.stringify({ code: 'test', statement: String.raw`\text{Calculate the determinant: }\det\begin{pmatrix}1&2\\3&4\end{pmatrix}\text{.}`, answerInput: { kind: 'formula', maxBytes: 256 } }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem />));
  expect(fetch).not.toHaveBeenCalled();
  const size = [...host.querySelectorAll('label')].find(label => label.textContent?.startsWith('Matrix size'))!.querySelector('select')!;
  await act(async () => { size.value = '4'; size.dispatchEvent(new Event('change', { bubbles: true })); });
  const generate = [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!;
  await act(async () => generate.click());
  expect(JSON.parse(String(vi.mocked(fetch).mock.calls[0][1]?.body))).toEqual({ level: 1, determinantSize: 4 });
  expect(host.querySelector('.pl-problem')).not.toBeNull();
  expect(host.textContent).toContain('Show solution');
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('generates an inverse only after settings are chosen', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  const row = { kind: 'tuple', maxBytes: 256, labels: ['Column one', 'Column two'], components: [{ kind: 'formula', maxBytes: 256 }, { kind: 'formula', maxBytes: 256 }] };
  vi.stubGlobal('fetch', vi.fn(async (path: string, options?: RequestInit) => {
    expect(path).toContain('/generate');
    expect(JSON.parse(String(options?.body))).toEqual({ level: 1, inverseSize: 2 });
    return new Response(JSON.stringify({ code: 'inverse', statement: String.raw`\text{Find the inverse of the matrix: }A=\begin{pmatrix}1&2\\0&1\end{pmatrix}\text{.}`, answerInput: { kind: 'tuple', maxBytes: 256, labels: ['Matrix row one', 'Matrix row two'], components: [row, row] } }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem topic="inverse-matrices" />));
  expect(fetch).not.toHaveBeenCalled();
  expect(host.textContent).toContain('Inverse matrices');
  const generate = [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!;
  await act(async () => generate.click());
  expect(host.querySelectorAll('.pl-matrix-grid input')).toHaveLength(4);
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('generates rectangular matrix rank problems from selected dimensions', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (path: string, options?: RequestInit) => {
    expect(path).toContain('/generate');
    expect(JSON.parse(String(options?.body))).toEqual({ level: 1, rankDimensions: { rows: 2, columns: 3 } });
    return new Response(JSON.stringify({ code: 'rank', statement: String.raw`\text{Find the rank of the matrix: }\begin{pmatrix}1&0&2\\0&1&3\end{pmatrix}\text{.}`, answerInput: { kind: 'formula', maxBytes: 256 } }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem topic="matrix-rank" />));
  expect(fetch).not.toHaveBeenCalled();
  const columns = [...host.querySelectorAll('label')].find(label => label.textContent?.startsWith('Columns'))!.querySelector('select')!;
  await act(async () => { columns.value = '3'; columns.dispatchEvent(new Event('change', { bubbles: true })); });
  const generate = [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!;
  await act(async () => generate.click());
  expect(host.querySelector('.pl-problem')).not.toBeNull();
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('generates a system only after selecting its number of unknowns', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (path: string, options?: RequestInit) => {
    expect(path).toContain('/generate');
    expect(JSON.parse(String(options?.body))).toEqual({ level: 1, systemSize: 2 });
    return new Response(JSON.stringify({ code: 'system', statement: String.raw`Solve \(x_1=1, x_2=2\).`, answerInput: { kind: 'tuple', maxBytes: 256, labels: ['Variable one', 'Variable two'], components: [{ kind: 'formula', maxBytes: 256 }, { kind: 'formula', maxBytes: 256 }] } }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem topic="linear-systems" />));
  expect(fetch).not.toHaveBeenCalled();
  const generate = [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!;
  await act(async () => generate.click());
  expect(host.querySelector('.pl-problem')).not.toBeNull();
  expect(host.textContent).toContain('Variable one');
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('generates complex arithmetic with the selected operation and standard answer field', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (_path: string, options?: RequestInit) => {
    expect(JSON.parse(String(options?.body))).toEqual({ level: 1, complexOperation: 'divide' });
    return new Response(JSON.stringify({ code: 'complex', statement: String.raw`Calculate \((1+i)/(2-i)\).` }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem topic="complex-arithmetic" />));
  expect(fetch).not.toHaveBeenCalled();
  const operation = [...host.querySelectorAll('label')].find(label => label.textContent?.startsWith('Operation'))!.querySelector('select')!;
  await act(async () => { operation.value = 'divide'; operation.dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!.click());
  expect(host.querySelector('#answer')).not.toBeNull();
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('generates a modulus problem after choosing the difficulty', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (_path: string, options?: RequestInit) => {
    expect(JSON.parse(String(options?.body))).toEqual({ level: 1, complexModulus: true, modulusMode: 'expression' });
    return new Response(JSON.stringify({ code: 'modulus', statement: String.raw`\text{Calculate }|1+i|\text{.}` }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem topic="complex-numbers" />));
  expect(fetch).not.toHaveBeenCalled();
  expect(host.textContent).toContain('Modulus of a complex number');
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!.click());
  expect(host.querySelector('#answer')).not.toBeNull();
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('generates the selected polar-form exercise only after confirmation', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (_path: string, options?: RequestInit) => {
    expect(JSON.parse(String(options?.body))).toEqual({ level: 1, polarMode: 'root' });
    return new Response(JSON.stringify({ code: 'root', statement: String.raw`\text{Find the smallest root: }z^2=4\text{.}` }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem topic="complex-polar-form" />));
  expect(fetch).not.toHaveBeenCalled();
  const mode = [...host.querySelectorAll('label')].find(label => label.textContent?.startsWith('Exercise type'))!.querySelector('select')!;
  await act(async () => { mode.value = 'root'; mode.dispatchEvent(new Event('change', { bubbles: true })); });
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!.click());
  expect(host.querySelector('#answer')).not.toBeNull();
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('reveals the complex plane only when the solution is requested', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (path: string) => new Response(JSON.stringify(path.endsWith('/generate')
    ? { code: 'power', statement: String.raw`\text{Calculate }(1+i)^2\text{.}` }
    : { steps: [{ say: 'Evaluate.', latex: '2i' }], visual: { kind: 'complex-plane', version: 1, mode: 'power', first: [1, 1], second: null, result: [0, 2], power: 2 } }), { status: 200 })));
  await act(async () => root.render(<LocalDeterminantProblem topic="complex-polar-form" />));
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!.click());
  expect(host.textContent).not.toContain('Complex plane');
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Show solution'))!.click());
  expect(host.textContent).toContain('Complex plane');
  expect(host.querySelector('input[type=range]')).not.toBeNull();
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('generates a conversion and provides separate modulus and argument fields', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (_path: string, options?: RequestInit) => {
    expect(JSON.parse(String(options?.body))).toEqual({ level: 1, conversion: 'alg-trig' });
    return new Response(JSON.stringify({ code: 'conversion', statement: String.raw`\text{Convert: }z=1+i\text{.}`, answerInput: { kind: 'tuple', maxBytes: 256, labels: ['Modulus r', 'Principal argument'], components: [{ kind: 'formula', maxBytes: 256 }, { kind: 'formula', maxBytes: 256 }] } }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem topic="complex-conversion" />));
  expect(fetch).not.toHaveBeenCalled();
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!.click());
  expect(host.querySelector('#answer-modulus')).not.toBeNull();
  expect(host.querySelector('#answer-argument')).not.toBeNull();
  expect(host.textContent).toContain('Principal argument in radians');
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('generates polynomial division with separate quotient and remainder fields', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (_path: string, options?: RequestInit) => {
    expect(JSON.parse(String(options?.body))).toEqual({ level: 1, polynomialMode: 'division' });
    return new Response(JSON.stringify({ code: 'poly', statement: String.raw`\text{Find quotient and remainder: }(x^2+1)\div(x-1)\text{.}`, answerInput: { kind: 'tuple', maxBytes: 256, labels: ['Quotient', 'Remainder'], components: [{ kind: 'formula', maxBytes: 256, symbols: { x: 'real' } }, { kind: 'formula', maxBytes: 256, symbols: { x: 'real' } }] } }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem topic="polynomial-division" />));
  expect(fetch).not.toHaveBeenCalled();
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!.click());
  expect(host.querySelector('#answer-quotient')).not.toBeNull();
  expect(host.querySelector('#answer-remainder')).not.toBeNull();
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('generates real-root exercises with the set-answer input', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (_path: string, options?: RequestInit) => {
    expect(JSON.parse(String(options?.body))).toEqual({ level: 1, polynomialRoots: true });
    return new Response(JSON.stringify({ code: 'roots', statement: String.raw`\text{Find all distinct real roots: }x^2-1=0\text{.}`, answerInput: { kind: 'finite_set', maxBytes: 256, maxItems: 8 } }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem topic="polynomial-roots" />));
  expect(fetch).not.toHaveBeenCalled();
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!.click());
  expect(host.querySelector('#answer-0')).not.toBeNull();
  expect(host.textContent).toContain('Add entry');
  expect(host.textContent).toContain('Polynomial roots and factors');
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('generates partial fractions with separate coefficient fields', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async (_path: string, options?: RequestInit) => {
    expect(JSON.parse(String(options?.body))).toEqual({ level: 1, polynomialExtra: 'fractions' });
    return new Response(JSON.stringify({ code: 'frac', statement: String.raw`\text{Find coefficients: }1/(x^2-1)\text{.}`, answerInput: { kind: 'tuple', maxBytes: 256, labels: ['A', 'B'], components: [{ kind: 'formula', maxBytes: 256 }, { kind: 'formula', maxBytes: 256 }] } }), { status: 200 });
  }));
  await act(async () => root.render(<LocalDeterminantProblem topic="partial-fractions" />));
  expect(fetch).not.toHaveBeenCalled();
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!.click());
  expect(host.querySelector('#answer-coefficient-0')).not.toBeNull();
  expect(host.querySelector('#answer-coefficient-1')).not.toBeNull();
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});

it('shows a three-level indicator for local exercises', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify({ code: 'det', statement: String.raw`\text{Calculate }1\text{.}`, answerInput: { kind: 'formula', maxBytes: 256 } }), { status: 200 })));
  await act(async () => root.render(<LocalDeterminantProblem />));
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!.click());
  expect(host.querySelector('[aria-label="Difficulty 1 of 3"]')).not.toBeNull();
  expect(host.querySelector('.pl-dots')?.children).toHaveLength(3);
  await act(async () => root.unmount()); vi.unstubAllGlobals(); host.remove();
});
