// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { ProblemCard } from '../components/ProblemCard';
import { SolutionVisual } from './SolutionVisual';
import type { DefiniteSpec, IndefiniteSpec, VisualSpec } from './spec';
import { riemann, simpson } from './plot';

const definite: DefiniteSpec = { kind: 'definite', version: 1, f: ['mul', 2, 'x'], a: 0, b: 2, aLatex: '0', bLatex: '2',
  range: [-1, 3], y: [-2, 5], value: '4' };
const indefinite: IndefiniteSpec = { kind: 'indefinite', version: 1, f: ['pow', 'x', -1], F: ['log', ['abs', 'x']],
  x: [-4, 4], y: [-3, 3], points: [{ x: 0, kind: 'pole' }] };

let element: HTMLDivElement;
let root: Root;
beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  element = document.createElement('div'); document.body.append(element);
  root = createRoot(element);
});
afterEach(async () => { await act(async () => root.unmount()); element.remove(); });

const sliders = () => Array.from(element.querySelectorAll<HTMLInputElement>('input[type="range"]'));
function slide(input: HTMLInputElement, value: number) {
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!;
  setter.call(input, String(value));
  input.dispatchEvent(new Event('input', { bubbles: true }));
}

it('shows the exact value at the original bounds and an approximation elsewhere', async () => {
  await act(async () => root.render(<SolutionVisual spec={definite} />));
  expect(element.querySelector('svg[role="img"]')?.getAttribute('aria-label')).toMatch(/signed area from x = 0 to x = 2/);
  expect(element.textContent).toContain('exact');
  const [a, b] = sliders();
  expect([a.min, a.max, b.min, b.max]).toEqual(['-1', '3', '-1', '3']);
  expect(a.labels?.[0]?.textContent).toBe('Lower bound a');
  expect(a.getAttribute('aria-valuetext')).toBe('a = 0');
  await act(async () => slide(b, 1));
  expect(element.textContent).toContain('approximate');
  expect(element.textContent).toContain('1');
  await act(async () => (Array.from(element.querySelectorAll('button')).find(x => x.textContent === 'Reset bounds')!).click());
  expect(element.textContent).toContain('exact');
});

it('never lets the bounds cross or leave the continuity interval', async () => {
  await act(async () => root.render(<SolutionVisual spec={definite} />));
  const [a] = sliders();
  await act(async () => slide(a, 2.9));
  const value = Number(sliders()[0].getAttribute('aria-valuetext')!.replace('a = ', ''));
  expect(value).toBeLessThan(2);
  expect(Number(sliders()[0].value)).toBeGreaterThanOrEqual(-1);
});

it('offers a Riemann sum with 1 to 100 rectangles and three sample points', async () => {
  await act(async () => root.render(<SolutionVisual spec={definite} />));
  await act(async () => element.querySelector<HTMLInputElement>('input[type="checkbox"]')!.click());
  const n = sliders()[2];
  expect([n.min, n.max, n.step]).toEqual(['1', '100', '1']);
  expect(element.querySelectorAll('.pl-vis-riemann rect')).toHaveLength(8);
  await act(async () => slide(n, 100));
  expect(element.querySelectorAll('.pl-vis-riemann rect')).toHaveLength(100);
  expect(Array.from(element.querySelectorAll('[aria-pressed]')).map(b => b.textContent)).toEqual(['Left', 'Midpoint', 'Right']);
  expect(element.textContent).toMatch(/Midpoint sum with n = 100: ≈ 4/);
});

it('draws f, F + C, the constant slider and the marked points with a text alternative', async () => {
  await act(async () => root.render(<SolutionVisual spec={indefinite} />));
  expect(element.querySelectorAll('.pl-vis-curve')).toHaveLength(2);
  expect(element.querySelectorAll('.pl-vis-pole')).toHaveLength(1);
  expect(element.textContent).toContain('vertical asymptotes at x ≈ 0');
  const [c] = sliders();
  expect(c.labels?.[0]?.textContent).toBe('Constant C');
  await act(async () => slide(c, 1));
  expect(element.querySelector('svg')?.getAttribute('aria-label')).toContain('F plus 1');
});

it('hides only a visual that fails, and the steps stay', async () => {
  const quiet = vi.spyOn(console, 'error').mockImplementation(() => {});
  const broken = { ...definite, f: ['eval', 'x'] } as unknown as VisualSpec;
  await act(async () => root.render(
    <ProblemCard topic="basic-integrals" difficulty={1} problemLatex="\int_0^2 2x\,dx" answer="" onAnswerChange={() => {}}
      result={null} onCheck={() => {}} onShowAnswer={() => {}} onShowSolution={() => {}} onNext={() => {}}
      solution={[{ say: 'Integrate.', latex: 'x^2' }]} visual={broken} />));
  expect(element.querySelector('[aria-label="Solution"]')?.textContent).toContain('Integrate.');
  expect(element.querySelector('.pl-vis')).toBeNull();
  quiet.mockRestore();
});

it('computes Simpson and Riemann sums', () => {
  const square = (x: number) => x * x;
  expect(simpson(square, 0, 3)).toBeCloseTo(9, 10);
  expect(riemann(square, 0, 1, 1, 'left').sum).toBe(0);
  expect(riemann(square, 0, 1, 1, 'right').sum).toBe(1);
  expect(riemann(square, 0, 1, 2, 'midpoint').sum).toBeCloseTo(0.3125, 12);
});
