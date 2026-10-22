// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { describe, expect, it } from 'vitest';
import { parseVisual, type Solid3dSpec } from '../spec';
import { SolutionVisual } from '../SolutionVisual';
import { solidScene } from './solid';

const box: Solid3dSpec = {
  kind: 'solid3d',
  version: 1,
  system: 'cartesian',
  bounds: [['z', 0, 3], ['y', 0, 2], ['x', 0, 1]],
  window: { x: [-0.2, 1.2], y: [-0.2, 2.2], z: [-0.2, 3.2] },
  solid: '0 \\le x \\le 1',
};

const cylinder: Solid3dSpec = {
  ...box,
  system: 'cylindrical',
  bounds: [['z', 0, 2], ['r', 0, 1], ['theta', 0, ['mul', 2, 'pi']]],
};

const halfCone: Solid3dSpec = {
  ...box,
  system: 'cylindrical',
  bounds: [['z', 'r', 2], ['r', 0, 2], ['theta', 0, 'pi']],
};

const simplex: Solid3dSpec = {
  ...box,
  bounds: [['z', 0, ['add', 1, ['mul', -1, 'x'], ['mul', -1, 'y']]], ['y', 0, ['add', 1, ['mul', -1, 'x']]], ['x', 0, 1]],
};

function points(positions: Float32Array): Array<[number, number, number]> {
  const out: Array<[number, number, number]> = [];
  for (let k = 0; k < positions.length; k += 3) out.push([positions[k], positions[k + 1], positions[k + 2]]);
  return out;
}

describe('the solid3d spec', () => {
  it('accepts the specs and rejects broken ones', () => {
    for (const spec of [box, cylinder, halfCone, simplex]) expect(parseVisual(spec)).toEqual(spec);
    expect(parseVisual({ ...box, version: 2 })).toBeUndefined();
    expect(parseVisual({ ...box, system: 'spherical' })).toBeUndefined();
    expect(parseVisual({ ...box, bounds: [['y', 0, 1], ['z', 0, 1], ['x', 0, 1]] })).toBeUndefined();
    expect(parseVisual({ ...box, bounds: [['z', 0, 1], ['x', 0, 1], ['x', 0, 1]] })).toBeUndefined();
    expect(parseVisual({ ...cylinder, bounds: [['z', 0, 1], ['x', 0, 1], ['theta', 0, 1]] })).toBeUndefined();
    expect(parseVisual({ ...box, bounds: [['z', 0, ['eval', 'x']], ['y', 0, 1], ['x', 0, 1]] })).toBeUndefined();
    expect(parseVisual({ ...box, window: { x: [1, 0], y: [0, 1], z: [0, 1] } })).toBeUndefined();
    expect(parseVisual({ ...box, solid: 42 })).toBeUndefined();
  });
});

describe('solidScene', () => {
  it('draws a box as bottom, top, four walls and twelve edges', () => {
    const scene = solidScene(box, 4, 2);
    expect(scene.meshes).toHaveLength(6);
    expect(scene.meshes.map(mesh => mesh.tone)).toEqual(['floor', 'wall', 'wall', 'wall', 'wall', 'wall']);
    expect(new Set(points(scene.meshes[1].positions).map(p => p[2]))).toEqual(new Set([3]));
    expect(scene.lines).toHaveLength(12);
    expect(scene.box).toEqual({ min: [-0.2, -0.2, -0.2], max: [1.2, 2.2, 3.2] });
  });

  it('leaves out the seam and the axis of a full-turn cylinder', () => {
    const scene = solidScene(cylinder, 8, 2);
    expect(scene.meshes).toHaveLength(3);
    for (const [x, y] of points(scene.meshes[2].positions)) expect(Math.hypot(x, y)).toBeCloseTo(1, 5);
    // The bottom and top circles only.
    expect(scene.lines).toHaveLength(2);
  });

  it('keeps the flat walls of a half turn and follows the cone', () => {
    const scene = solidScene(halfCone, 6, 3);
    expect(scene.meshes).toHaveLength(2 + 3);
    for (const [x, y, z] of points(scene.meshes[0].positions)) expect(z).toBeCloseTo(Math.hypot(x, y), 5);
  });

  it('meshes the simplex down to its tip', () => {
    const scene = solidScene(simplex, 4, 4);
    for (const [x, y, z] of points(scene.meshes[1].positions)) expect(z).toBeCloseTo(1 - x - y, 5);
    expect(scene.meshes.every(mesh => mesh.indices.length > 0)).toBe(true);
  });

  it('leaves a gap, not a spike, where a bound is undefined', () => {
    const spec: Solid3dSpec = { ...box, bounds: [['z', 0, ['log', ['add', 'x', -0.5]]], ['y', 0, 1], ['x', 0, 1]] };
    const scene = solidScene(spec, 4, 1);
    expect(scene.meshes[1].indices.length).toBeLessThan(4 * 1 * 6);
    expect(Array.from(scene.meshes[1].positions).every(Number.isFinite)).toBe(true);
  });
});

describe('Solid3dVisual', () => {
  it('shows the solid as text and leaves out only the 3D view without WebGL', async () => {
    const element = document.createElement('div');
    document.body.append(element);
    const root = createRoot(element);
    await act(async () => root.render(<SolutionVisual spec={{ ...halfCone, solid: '0 \\le r \\le 2' }} />));
    await act(async () => { await new Promise(resolve => setTimeout(resolve, 50)); });
    const section = element.querySelector('section[aria-label="Visualization"]');
    expect(section?.textContent).toContain('Solid of integration in cylindrical coordinates');
    expect(element.querySelector('.katex')).not.toBeNull();
    expect(element.querySelector('canvas')).toBeNull();
    await act(async () => root.unmount());
    element.remove();
  });
});
