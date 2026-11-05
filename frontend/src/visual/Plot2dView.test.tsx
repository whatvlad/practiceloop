// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it } from 'vitest';
import { parseVisual, type Plot2dSpec } from './spec';
import { Plot2dView } from './Plot2dView';

const spec: Plot2dSpec = { kind: 'plot2d', version: 1, title: 'Tangent', description: 'The curve and its tangent at the contact point.',
  x: [-1, 3], y: [-2, 6], xLabel: 'x', yLabel: 'height', paths: [{ label: 'Tangent', points: [[0, 0], [2, 4]], closed: false, arrow: true }],
  points: [{ label: 'Contact', x: 1, y: 2, included: false }] };

it('validates bounded geometry and strips unrelated private fields', () => {
  expect(parseVisual({ ...spec, expected: 999 })).toEqual(spec);
  for (const bad of [{ ...spec, x: [1, 1] }, { ...spec, title: '<script>' }, { ...spec, paths: Array(9).fill(spec.paths[0]) },
    { ...spec, points: [{ ...spec.points[0], y: Infinity }] }, { ...spec, paths: [{ ...spec.paths[0], closed: 'false' }] }]) expect(parseVisual(bad)).toBeUndefined();
});

it('renders accessible parameter geometry with explicit endpoint closure and visibility controls', () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const element = document.createElement('div'); document.body.append(element); const root = createRoot(element);
  try {
    act(() => root.render(<Plot2dView spec={spec} />));
    expect(element.querySelector('svg')!.getAttribute('aria-label')).toBe(spec.description);
    expect(element.querySelector('circle')!.getAttribute('fill')).toBe('var(--surface)');
    expect(element.querySelector('path[marker-end]')).not.toBeNull();
    expect(element.querySelector('circle title')!.textContent).toContain('Contact: (1, 2), excluded');
    expect([...element.querySelectorAll('text')].some(node => node.textContent === 'Contact')).toBe(false);
    act(() => element.querySelectorAll<HTMLInputElement>('input[type=checkbox]')[1].click());
    expect([...element.querySelectorAll('text')].some(node => node.textContent === 'Contact')).toBe(true);
    act(() => element.querySelector<HTMLInputElement>('input[type=checkbox]')!.click());
    expect(element.querySelector('path[marker-end]')).toBeNull();
    expect(element.textContent).toContain('height');
  } finally { act(() => root.unmount()); element.remove(); }
});
