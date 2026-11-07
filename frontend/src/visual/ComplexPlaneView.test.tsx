// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it } from 'vitest';
import { parseVisual } from './spec';
import { SolutionVisual } from './SolutionVisual';

it('shows the complex plane and lets the learner explore powers', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const spec = parseVisual({ kind: 'complex-plane', version: 1, mode: 'power', first: [1, 1], second: null, result: [-4, 0], power: 4 });
  expect(spec).toBeDefined();
  const host = document.createElement('div'); document.body.append(host);
  const root = createRoot(host);
  await act(async () => root.render(<SolutionVisual spec={spec!} />));
  expect(host.querySelector('svg[role="img"]')).not.toBeNull();
  expect(host.textContent).toContain('z^4');
  const slider = host.querySelector<HTMLInputElement>('input[type=range]')!;
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(slider, '2');
    slider.dispatchEvent(new Event('input', { bubbles: true }));
  });
  expect(host.textContent).toContain('z^2');
  expect(host.textContent).toContain('k = 2');
  await act(async () => root.unmount()); host.remove();
});

it('rejects invalid complex diagram data', () => {
  expect(parseVisual({ kind: 'complex-plane', version: 1, mode: 'power', first: [1, 2], second: null, result: [1, 1], power: 100 })).toBeUndefined();
  expect(parseVisual({ kind: 'complex-plane', version: 1, mode: 'add', first: [1, 2], second: null, result: [1, 1], power: null })).toBeUndefined();
});

it('shows the centre and radius for a modulus circle', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const spec = parseVisual({ kind: 'complex-plane', version: 1, mode: 'circle', first: [1, 2], second: null, result: null, power: null, radius: 3 });
  expect(spec).toBeDefined();
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  await act(async () => root.render(<SolutionVisual spec={spec!} />));
  expect(host.textContent).toContain('Centre');
  expect(host.textContent).toContain('Radius');
  expect(host.querySelector('circle[data-locus]')).not.toBeNull();
  await act(async () => root.unmount()); host.remove();
});

it('labels the plotted value of a modulus expression clearly', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const spec = parseVisual({ kind: 'complex-plane', version: 1, mode: 'modulus', first: [1, 2], second: null, result: null, power: null, firstLabel: 'value' });
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  await act(async () => root.render(<SolutionVisual spec={spec!} />));
  expect(host.textContent).toContain('|value|');
  await act(async () => root.unmount()); host.remove();
});
