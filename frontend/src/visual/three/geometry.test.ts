import { describe, expect, it } from 'vitest';
import * as geometry from './geometry';
import { axisOrigin, axisTicks } from './geometry';
import type { Geometry3dSpec } from '../spec';

it('turns a bounded diagram into a scene with labelled points, arrows and faces', () => {
  const spec: Geometry3dSpec = {
    kind: 'geometry3d', version: 1, title: 'Triangle', description: 'Triangle ABC.',
    points: [{ label: 'A', at: [0, 0, 0], tone: 'given' }, { label: 'B', at: [2, 0, 0], tone: 'active' }],
    lines: [{ label: 'AB', start: [0, 0, 0], end: [2, 0, 0], tone: 'active', arrow: true, dashed: false }],
    faces: [{ label: 'ABC', vertices: [[0, 0, 0], [2, 0, 0], [0, 3, 0]], tone: 'previous' }],
  };
  expect(geometry).toHaveProperty('geometryScene');
  const scene = (geometry as unknown as { geometryScene: (input: Geometry3dSpec) => {
    marks: { label: string; at: number[] }[]; edges: { label: string; arrow: boolean }[];
    meshes: { positions: Float32Array; indices: Uint32Array }[]; box: { min: number[]; max: number[] };
  } }).geometryScene(spec);
  expect(scene.marks.map(point => point.label)).toEqual(['A', 'B']);
  expect(scene.edges[0]).toMatchObject({ label: 'AB', arrow: true });
  expect(Array.from(scene.meshes[0].positions)).toEqual([0, 0, 0, 2, 0, 0, 0, 3, 0]);
  expect(Array.from(scene.meshes[0].indices)).toEqual([0, 1, 2]);
  expect(scene.box.min[0]).toBeLessThanOrEqual(0);
  expect(scene.box.max[1]).toBeGreaterThanOrEqual(3);
});

it('keeps the true origin and all three coordinate axes visible even for a flat or translated figure', () => {
  const spec: Geometry3dSpec = {
    kind: 'geometry3d', version: 1, title: 'Triangle', description: 'Triangle ABC.',
    points: [
      { label: 'A', at: [3, 4, 5], tone: 'given' },
      { label: 'B', at: [5, 4, 5], tone: 'given' },
      { label: 'C', at: [3, 6, 5], tone: 'given' },
    ], lines: [], faces: [],
  };
  const scene = geometry.geometryScene(spec);
  const axes = geometry.coordinateAxes(scene.box);
  expect(scene.analyticGeometry).toBe(true);
  expect(geometry.axisOrigin(scene.box)).toEqual([0, 0, 0]);
  expect(axes.map(axis => axis.name)).toEqual(['x', 'y', 'z']);
  for (const [index, axis] of axes.entries()) {
    expect(axis.from[index]).toBeLessThan(0);
    expect(axis.to[index]).toBeGreaterThan(0);
    expect(axis.from.filter((_, i) => i !== index)).toEqual([0, 0]);
    expect(axis.to.filter((_, i) => i !== index)).toEqual([0, 0]);
  }
  expect(axes[2].to[2] - axes[2].from[2]).toBeGreaterThan(1);
});

it('chooses an initial view that separates otherwise overlapping vector arrows', () => {
  const spec: Geometry3dSpec = {
    kind: 'geometry3d', version: 1, title: 'Vectors', description: 'Given vectors.', points: [], faces: [],
    lines: [[-2, 1, 0], [-2, 0, -1], [0, -1, 1]].map((end, index) => ({
      label: ['u', 'v', 'w'][index], start: [0, 0, 0], end: end as [number, number, number],
      tone: 'given', arrow: true, dashed: false,
    })),
  };
  const direction = geometry.geometryViewDirection(geometry.geometryScene(spec));
  const dot = (a: readonly number[], b: readonly number[]) => a.reduce((sum, value, index) => sum + value * b[index], 0);
  const norm = (a: readonly number[]) => Math.hypot(...a);
  const unit = direction.map(value => value / norm(direction));
  const projected = spec.lines.map(line => line.end.map((value, i) => value - dot(line.end, unit) * unit[i]));
  const cos = dot(projected[0], projected[1]) / (norm(projected[0]) * norm(projected[1]));
  expect(cos).toBeLessThan(0.9);
});

it('chooses a view where coordinate axes and the source vectors are distinct', () => {
  const values: [number, number, number][] = [[2, 1, 1], [1, -2, 2], [1, 3, -5]];
  const scene = geometry.geometryScene({
    kind: 'geometry3d', version: 1, title: 'Vectors', description: 'Source vectors.', points: [], faces: [],
    lines: values.map((end, i) => ({ label: ['u', 'v', 'w'][i], start: [0, 0, 0], end, tone: 'given', arrow: true, dashed: false })),
  });
  const direction = geometry.geometryViewDirection(scene);
  const dot = (a: readonly number[], b: readonly number[]) => a.reduce((sum, value, index) => sum + value * b[index], 0);
  const norm = (a: readonly number[]) => Math.hypot(...a);
  const unit = direction.map(value => value / norm(direction));
  const project = (vector: readonly number[]) => vector.map((value, i) => value - dot(vector, unit) * unit[i]);
  const axes = [[1, 0, 0], [0, 1, 0], [0, 0, 1]].map(project);
  const vectors = values.map(project);
  const cosine = (a: number[], b: number[]) => Math.abs(dot(a, b) / (norm(a) * norm(b)));
  for (let i = 0; i < axes.length; i++) {
    for (let j = i + 1; j < axes.length; j++) expect(cosine(axes[i], axes[j])).toBeLessThan(0.8);
    for (const vector of vectors) expect(cosine(axes[i], vector)).toBeLessThan(0.98);
  }
});

it.each(['D', 'N'])('constructs a true perpendicular section from %s, even outside the base', (top) => {
  const spec: Geometry3dSpec = {
    kind: 'geometry3d', version: 1, title: 'Height', description: 'Altitude DH.',
    points: [
      { label: 'A', at: [0, 0, 0], tone: 'given' }, { label: 'B', at: [1, 0, 0], tone: 'given' },
      { label: 'C', at: [0, 1, 0], tone: 'given' }, { label: top, at: [2, 2, 1], tone: 'given' },
      { label: 'H', at: [2, 2, 0], tone: 'active' },
    ],
    lines: [{ label: `${top}H`, start: [2, 2, 1], end: [2, 2, 0], tone: 'active', arrow: false, dashed: true }],
    faces: [],
  };
  expect(geometry).toHaveProperty('altitudeSection');
  const section = (geometry as unknown as { altitudeSection: (input: Geometry3dSpec) => {
    points: { label: string; at: readonly [number, number] }[];
  } | null }).altitudeSection(spec)!;
  const points = Object.fromEntries(section.points.map(point => [point.label, point.at]));
  expect(points.H).toEqual([0, 0]);
  expect(points[top][0]).toBeCloseTo(0);
  expect(points[top][1]).toBeCloseTo(1);
  expect(points.A[0]).toBeCloseTo(Math.sqrt(8));
  expect(points.A[1]).toBeCloseTo(0);
});

describe('3D axis ticks (#127)', () => {
  it('crosses at the origin, or the nearest point of the box', () => {
    expect(axisOrigin({ min: [-1, -1, 0], max: [1, 1, 2] })).toEqual([0, 0, 0]);
    expect(axisOrigin({ min: [1, 2, -3], max: [4, 5, -1] })).toEqual([1, 2, -1]);
  });

  it('labels round values on each axis and leaves out 0 at the origin', () => {
    const ticks = axisTicks({ min: [-2, 0, 0], max: [2, 1, 4] });
    const labels = (axis: string) => ticks.filter(t => t.axis === axis).map(t => t.label);
    expect(labels('x')).toEqual(['−2', '−1', '1', '2']);
    expect(labels('y')).toEqual(['0.2', '0.4', '0.6', '0.8', '1']);
    expect(labels('z')).toEqual(['1', '2', '3', '4']);
    const x1 = ticks.find(t => t.axis === 'x' && t.label === '1');
    expect(x1?.at).toEqual([1, 0, 0]);
  });

  it('keeps 0 when the axes do not cross there', () => {
    const ticks = axisTicks({ min: [1, 0, 0], max: [3, 2, 2] });
    expect(ticks.filter(t => t.axis === 'y').map(t => t.label)).toContain('0');
    expect(ticks.filter(t => t.axis === 'x').map(t => t.at)).toContainEqual([1, 0, 0]);
  });

  it('shows true heights when z is drawn rescaled', () => {
    // f runs up to 40 but is drawn ×0.05, so the box reaches z = 2.
    const z = axisTicks({ min: [0, 0, 0], max: [1, 1, 2] }, 0.05).filter(t => t.axis === 'z');
    expect(z.map(t => t.label)).toEqual(['10', '20', '30', '40']);
    expect(z[3].at[2]).toBeCloseTo(2);
  });

  it('skips an axis with an empty span', () => {
    expect(axisTicks({ min: [0, 0, 1], max: [1, 1, 1] }).some(t => t.axis === 'z')).toBe(false);
  });
});
