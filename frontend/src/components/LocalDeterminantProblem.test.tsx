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
