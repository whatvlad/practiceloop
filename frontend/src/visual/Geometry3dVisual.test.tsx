// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import type { Geometry3dSpec } from './spec';
import { SolutionVisual } from './SolutionVisual';

const spec: Geometry3dSpec = {
  kind: 'geometry3d', version: 1, title: 'Triangle ABC', description: 'Given triangle ABC.',
  points: [{ label: 'A', at: [0, 0, 0], tone: 'given' }, { label: 'B', at: [2, 0, 0], tone: 'active' }],
  lines: [{ label: 'AB', start: [0, 0, 0], end: [2, 0, 0], tone: 'active', arrow: true, dashed: false }],
  faces: [],
};

it('labels given infinite lines and plane patches once in the 2D fallback', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const canvas = vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(null);
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  const diagram: Geometry3dSpec = { ...spec, points: [], lines: [
    { label: 'l', start: [-2, 0, 0], end: [2, 0, 0], tone: 'given', arrow: false, dashed: false },
    { label: 'pi', start: [-1, -1, 0], end: [1, -1, 0], tone: 'given', arrow: false, dashed: false },
    { label: 'pi', start: [1, -1, 0], end: [1, 1, 0], tone: 'given', arrow: false, dashed: false },
  ] };
  try {
    await act(async () => root.render(<SolutionVisual spec={diagram} />));
    await vi.waitFor(() => expect(host.textContent).toContain('3D is unavailable'));
    const labels = [...host.querySelectorAll('svg text')].map(node => node.textContent);
    expect(labels).toContain('l');
    expect(labels.filter(label => label === 'pi')).toHaveLength(1);
    expect(labels).toEqual(expect.arrayContaining(['x', 'y', 'z']));
  } finally { await act(async () => root.unmount()); host.remove(); canvas.mockRestore(); }
});

it('keeps a labelled projection available when 3D graphics are unavailable', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const canvas = vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(null);
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  try {
    await act(async () => root.render(<SolutionVisual spec={spec} />));
    await vi.waitFor(() => expect(host.textContent).toContain('3D is unavailable'));
    expect(host.textContent).toContain('Triangle ABC');
    expect(host.textContent).toContain('projection');
    expect(host.querySelector('svg')!.getAttribute('aria-label')).toContain('Given triangle ABC');
    expect([...host.querySelectorAll('svg text')].map(node => node.textContent)).toContain('A');
    const origin = host.querySelector<SVGCircleElement>('[data-axis-origin]')!;
    const ox = Number(origin.getAttribute('cx')); const oy = Number(origin.getAttribute('cy'));
    for (const axis of ['x', 'y', 'z']) {
      const line = host.querySelector<SVGLineElement>(`[data-axis="${axis}"] line`)!;
      const x1 = Number(line.getAttribute('x1')); const y1 = Number(line.getAttribute('y1'));
      const x2 = Number(line.getAttribute('x2')); const y2 = Number(line.getAttribute('y2'));
      expect(Math.abs((ox - x1) * (y2 - y1) - (oy - y1) * (x2 - x1))).toBeLessThan(1e-5);
    }
    const end = (axis: string) => {
      const line = host.querySelector<SVGLineElement>(`[data-axis="${axis}"] line`)!;
      return [Number(line.getAttribute('x2')), Number(line.getAttribute('y2'))];
    };
    expect(end('x')[0]).toBeGreaterThan(ox); expect(end('x')[1]).toBeGreaterThan(oy);
    expect(end('y')[0]).toBeLessThan(ox); expect(end('y')[1]).toBeGreaterThan(oy);
    expect(end('z')[0]).toBeCloseTo(ox); expect(end('z')[1]).toBeLessThan(oy);
  } finally {
    await act(async () => root.unmount());
    host.remove(); canvas.mockRestore();
  }
});

it('shows a true perpendicular section for the altitude instead of a misleading projection', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const canvas = vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(null);
  const height: Geometry3dSpec = {
    kind: 'geometry3d', version: 1, title: 'Height', description: 'Altitude DH.',
    points: [
      { label: 'A', at: [0, 0, 0], tone: 'given' }, { label: 'B', at: [1, 0, 0], tone: 'given' },
      { label: 'C', at: [0, 1, 0], tone: 'given' }, { label: 'D', at: [2, 2, 1], tone: 'given' },
      { label: 'H', at: [2, 2, 0], tone: 'active' },
    ],
    lines: [{ label: 'DH', start: [2, 2, 1], end: [2, 2, 0], tone: 'active', arrow: false, dashed: true }],
    faces: [],
  };
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  try {
    await act(async () => root.render(<SolutionVisual spec={height} />));
    await vi.waitFor(() => expect(host.textContent).toContain('Perpendicular section'));
    expect(host.querySelector('svg')?.getAttribute('aria-label')).toContain('perpendicular');
    expect(host.querySelector('[data-axis="section-s"]')).not.toBeNull();
    expect(host.querySelector('[data-axis="section-t"]')).not.toBeNull();
    expect(host.querySelector('svg')?.getAttribute('aria-label')).toContain('local coordinates');
  } finally { await act(async () => root.unmount()); host.remove(); canvas.mockRestore(); }
});

it('labels the section as not to scale when a very short height needs enlargement', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const canvas = vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(null);
  const height: Geometry3dSpec = {
    kind: 'geometry3d', version: 1, title: 'Height', description: 'Altitude NH.',
    points: [
      { label: 'A', at: [0, 0, 0], tone: 'given' }, { label: 'B', at: [1, 0, 0], tone: 'given' },
      { label: 'C', at: [0, 1, 0], tone: 'given' }, { label: 'N', at: [2, 2, 0.05], tone: 'given' },
      { label: 'H', at: [2, 2, 0], tone: 'active' },
    ],
    lines: [{ label: 'NH', start: [2, 2, 0.05], end: [2, 2, 0], tone: 'active', arrow: false, dashed: true }], faces: [],
  };
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  try {
    await act(async () => root.render(<SolutionVisual spec={height} />));
    await vi.waitFor(() => expect(host.textContent).toContain('not to scale'));
    expect(host.querySelector('svg')?.getAttribute('aria-label')).toContain('NH is perpendicular');
  } finally { await act(async () => root.unmount()); host.remove(); canvas.mockRestore(); }
});
