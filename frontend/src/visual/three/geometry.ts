/** Scene data for the lazy three.js view (ADR-006). Pure: it never imports three. */

import { format, ticks } from '../plot';

export type Vec3 = [number, number, number];

export interface Mesh3D {
  /** x, y, z per vertex. */
  positions: Float32Array;
  /** Three vertex indices per triangle. */
  indices: Uint32Array;
  /** `surface` is coloured by sign (positive and negative parts); the others are flat. */
  tone: 'surface' | 'wall' | 'floor';
}

export interface Scene3D {
  meshes: Mesh3D[];
  /** Polylines (x, y, z per point) drawn as edges. */
  lines: Float32Array[];
  box: { min: Vec3; max: Vec3 };
  /** Factor the heights were drawn at; z labels divide by it to show true values. Default 1. */
  zScale?: number;
}

/** Round tick values per axis in 3D: few, so the labels do not crowd the scene. */
const AXIS_TICKS = 4;

/** Where the three axes cross: the origin, or the nearest point of the box to it. */
export function axisOrigin(box: Scene3D['box']): Vec3 {
  return [0, 1, 2].map(i => Math.min(Math.max(0, box.min[i]), box.max[i])) as Vec3;
}

export interface AxisTick {
  axis: 'x' | 'y' | 'z';
  /** The tick's point on its axis, in scene units. */
  at: Vec3;
  label: string;
}

/**
 * Numeric ticks along the axes through `axisOrigin(box)`. When the axes cross at the
 * origin its 0s are left out, as in the 2D plots; z values are shown unscaled.
 */
export function axisTicks(box: Scene3D['box'], zScale = 1, count = AXIS_TICKS): AxisTick[] {
  const origin = axisOrigin(box);
  const atZero = origin.every(v => v === 0);
  const out: AxisTick[] = [];
  (['x', 'y', 'z'] as const).forEach((axis, i) => {
    const k = i === 2 ? zScale : 1;
    const [lo, hi] = [box.min[i] / k, box.max[i] / k];
    if (!(hi > lo)) return;
    for (const value of ticks(lo, hi, count)) {
      if (value === 0 && atZero) continue;
      const at = [...origin] as Vec3;
      at[i] = value * k;
      out.push({ axis, at, label: format(value) });
    }
  });
  return out;
}

/**
 * Triangulates an `nu` × `nv` grid over the parameters s, t ∈ [0, 1].
 * A point that is `null` or not finite drops every triangle that touches it,
 * which leaves a gap instead of a spike.
 */
export function gridMesh(nu: number, nv: number, point: (s: number, t: number) => Vec3 | null, tone: Mesh3D['tone'] = 'surface'): Mesh3D {
  const positions = new Float32Array((nu + 1) * (nv + 1) * 3);
  const valid = new Uint8Array((nu + 1) * (nv + 1));
  for (let i = 0; i <= nu; i++) {
    for (let j = 0; j <= nv; j++) {
      const k = i * (nv + 1) + j;
      const p = point(i / nu, j / nv);
      if (p && p.every(Number.isFinite)) {
        positions.set(p, k * 3);
        valid[k] = 1;
      }
    }
  }
  const indices: number[] = [];
  for (let i = 0; i < nu; i++) {
    for (let j = 0; j < nv; j++) {
      const a = i * (nv + 1) + j;
      const b = a + nv + 1;
      if (valid[a] && valid[b] && valid[a + 1]) indices.push(a, b, a + 1);
      if (valid[b] && valid[b + 1] && valid[a + 1]) indices.push(b, b + 1, a + 1);
    }
  }
  return { positions, indices: Uint32Array.from(indices), tone };
}

/** A polyline from points; non-finite points are skipped. */
export function polyline(points: Array<Vec3 | null>): Float32Array {
  return Float32Array.from(points.filter((p): p is Vec3 => !!p && p.every(Number.isFinite)).flat());
}
