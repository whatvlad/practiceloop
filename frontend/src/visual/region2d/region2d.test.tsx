// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { describe, expect, it } from 'vitest';
import { gridMesh } from '../three/geometry';
import { compileRegion, isRegion2d, type Region2dSpec } from './region';
import { Region2dVisual } from './Region2dVisual';
import { ticks } from './RegionView';
import { heightScale, surfaceScene } from './surface';

const triangle: Region2dSpec = {
  kind: 'region2d',
  version: 1,
  system: 'cartesian',
  bounds: [['y', 0, 'x'], ['x', 0, 1]],
  f: ['mul', 6, 'x'],
  window: { x: [-0.1, 1.1], y: [-0.1, 1.1], z: [0, 6] },
  region: '0 \\le x \\le 1,\\quad 0 \\le y \\le x',
};

const annulus: Region2dSpec = {
  kind: 'region2d',
  version: 1,
  system: 'polar',
  bounds: [['r', 1, 2], ['theta', 0, ['mul', 2, 'pi']]],
  f: ['pow', 'r', -2],
  window: { x: [-2.2, 2.2], y: [-2.2, 2.2], z: [0, 1] },
  region: '0 \\le \\theta \\le 2\\pi,\\quad 1 \\le r \\le 2',
};

const sinc: Region2dSpec = {
  ...triangle,
  bounds: [['x', 0, 'y'], ['y', 0, 'pi']],
  f: ['mul', ['sin', 'y'], ['pow', 'y', -1]],
};

describe('isRegion2d', () => {
  it('accepts the specs the server sends', () => {
    expect(isRegion2d(triangle)).toBe(true);
    expect(isRegion2d(annulus)).toBe(true);
  });

  it('rejects other kinds, versions, variables and broken windows', () => {
    expect(isRegion2d({ ...triangle, version: 2 })).toBe(false);
    expect(isRegion2d({ ...triangle, kind: 'solid3d' })).toBe(false);
    expect(isRegion2d({ ...triangle, bounds: [['r', 0, 1], ['x', 0, 1]] })).toBe(false);
    expect(isRegion2d({ ...triangle, bounds: [['x', 0, 1], ['x', 0, 1]] })).toBe(false);
    expect(isRegion2d({ ...triangle, window: { ...triangle.window, x: [1, 0] } })).toBe(false);
    expect(isRegion2d({ ...triangle, f: [3, 'x'] })).toBe(false);
    expect(isRegion2d(null)).toBe(false);
  });
});

describe('compileRegion', () => {
  it('maps the parameters to the outer and inner variables', () => {
    const region = compileRegion(triangle);
    expect(region.point(1, 0.5)).toEqual({ x: 1, y: 0.5, z: 6 });
    expect(region.point(0.5, 1)).toEqual({ x: 0.5, y: 0.5, z: 3 });
  });

  it('maps polar parameters to x and y and has no seam on a full turn', () => {
    const region = compileRegion(annulus);
    const p = region.point(0.25, 1)!;
    expect(p.x).toBeCloseTo(0);
    expect(p.y).toBeCloseTo(2);
    expect(p.z).toBeCloseTo(0.25);
    expect(region.fullTurn).toBe(true);
    expect(region.boundary()).toHaveLength(2);
  });

  it('drops the degenerate inner circle of a disk and closes a triangle in one loop', () => {
    const disk = compileRegion({ ...annulus, bounds: [['r', 0, 2], annulus.bounds[1]] });
    expect(disk.boundary()).toHaveLength(1);
    expect(compileRegion(triangle).boundary()).toHaveLength(1);
  });

  it('takes a removable gap from just inside the edge', () => {
    const region = compileRegion(sinc);
    expect(region.point(0, 0.5)!.z).toBeCloseTo(1, 4);
  });
});

describe('surface', () => {
  it('meshes the surface, the floor and one wall per edge', () => {
    const scene = surfaceScene(compileRegion(triangle));
    expect(scene.meshes.map(mesh => mesh.tone)).toEqual(['floor', 'wall', 'wall', 'wall', 'wall', 'surface']);
    const surface = scene.meshes.at(-1)!;
    expect(surface.indices.length).toBeGreaterThan(0);
    expect(surface.positions.every(Number.isFinite)).toBe(true);
  });

  it('scales heights only for a very tall or very flat surface', () => {
    expect(heightScale(compileRegion(triangle))).toBeLessThan(1);
    expect(heightScale(compileRegion({ ...triangle, window: { ...triangle.window, z: [0, 1] } }))).toBe(1);
  });

  it('leaves out triangles that touch a non-finite point', () => {
    const mesh = gridMesh(2, 2, (s, t) => (s === 0.5 && t === 0.5 ? null : [s, t, 0]));
    // The centre touches six of the eight triangles; the two corner triangles stay.
    expect(mesh.indices.length).toBe(2 * 3);
    expect(gridMesh(2, 2, (s, t) => [s, t, 0]).indices.length).toBe(8 * 3);
  });
});

describe('ticks', () => {
  it('uses steps of 1, 2 or 5 times a power of ten', () => {
    expect(ticks(-0.1, 1.1)).toEqual([0, 0.5, 1]);
    expect(ticks(-0.2, 3.4)).toEqual([0, 1, 2, 3]);
    expect(ticks(-2.3, 2.3)).toEqual([-2, -1, 0, 1, 2]);
  });
});

describe('Region2dVisual', () => {
  it('shows the region with its text alternative and stays up without WebGL', async () => {
    const element = document.createElement('div');
    document.body.append(element);
    const root = createRoot(element);
    await act(async () => root.render(<Region2dVisual spec={annulus} />));
    await act(async () => { await new Promise(resolve => setTimeout(resolve, 50)); });
    const svg = element.querySelector('svg[role="img"]');
    expect(svg?.getAttribute('aria-label')).toContain('polar coordinates');
    expect(element.querySelectorAll('.pl-visual-region .edge')).toHaveLength(2);
    expect(element.querySelector('canvas')).toBeNull();
    expect(element.textContent).not.toContain('signed volume');
    await act(async () => root.unmount());
    element.remove();
  });
});
