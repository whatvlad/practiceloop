/** Scene data for the lazy three.js view (ADR-006). Pure: it never imports three. */

import { format, ticks } from '../plot';
import type { Geometry3dSpec, GeometryTone } from '../spec';

export type Vec3 = [number, number, number];

export interface Mesh3D {
  /** x, y, z per vertex. */
  positions: Float32Array;
  /** Three vertex indices per triangle. */
  indices: Uint32Array;
  /** `surface` is coloured by sign (positive and negative parts); the others are flat. */
  tone: 'surface' | 'wall' | 'floor' | GeometryTone;
}

export interface Scene3D {
  meshes: Mesh3D[];
  /** Polylines (x, y, z per point) drawn as edges. */
  lines: Float32Array[];
  marks?: { label: string; at: Vec3; tone: GeometryTone }[];
  edges?: { label: string; start: Vec3; end: Vec3; tone: GeometryTone; arrow: boolean; dashed: boolean }[];
  box: { min: Vec3; max: Vec3 };
  /** Analytic-geometry scenes use their own camera and labelled coordinate axes. */
  analyticGeometry?: boolean;
  /** Factor the heights were drawn at; z labels divide by it to show true values. Default 1. */
  zScale?: number;
}

/** Convert checked parameter-derived geometry without changing its scale. */
export function geometryScene(spec: Geometry3dSpec): Scene3D {
  const vec = (value: readonly [number, number, number]): Vec3 => [value[0], value[1], value[2]];
  const marks = spec.points.map(point => ({ ...point, at: vec(point.at) }));
  const edges = spec.lines.map(line => ({ ...line, start: vec(line.start), end: vec(line.end) }));
  const meshes: Mesh3D[] = spec.faces.map(face => ({
    positions: Float32Array.from(face.vertices.flat()), indices: Uint32Array.from([0, 1, 2]), tone: face.tone,
  }));
  const all = [
    [0, 0, 0] as Vec3,
    ...marks.map(point => point.at), ...edges.flatMap(line => [line.start, line.end]),
    ...spec.faces.flatMap(face => face.vertices.map(vec)),
  ];
  const min = [0, 1, 2].map(i => Math.min(...all.map(point => point[i]))) as Vec3;
  const max = [0, 1, 2].map(i => Math.max(...all.map(point => point[i]))) as Vec3;
  const span = Math.max(...max.map((value, i) => value - min[i]), 1);
  const margin = span * 0.06;
  return { meshes, lines: [], marks, edges,
    box: {
      min: min.map(value => Math.min(value, -span * 0.3) - margin) as Vec3,
      max: max.map(value => Math.max(value, span * 0.3) + margin) as Vec3,
    }, analyticGeometry: true };
}

/** Axes pass through the actual origin and point towards positive coordinates. */
export function coordinateAxes(box: Scene3D['box']): { name: 'x' | 'y' | 'z'; from: Vec3; to: Vec3 }[] {
  return (['x', 'y', 'z'] as const).map((name, index) => {
    const from: Vec3 = [0, 0, 0]; const to: Vec3 = [0, 0, 0];
    from[index] = box.min[index]; to[index] = box.max[index];
    return { name, from, to };
  });
}

/** Pick a stable view that keeps given vectors and the coordinate axes distinct. */
export function geometryViewDirection(scene: Scene3D): Vec3 {
  const fallback: Vec3 = [1.1, -1.7, 1.05];
  const vectors = (scene.edges ?? []).filter(edge => edge.arrow && ['u', 'v', 'w'].includes(edge.label))
    .map(edge => edge.end.map((value, index) => value - edge.start[index]));
  const candidates: Vec3[] = [fallback, [1, 1, 1], [-1, -1, 1], [-1, 1, 1], [1, -1, 1],
    [2, 1, 1], [1, 2, 1], [2, -1, 1], [-2, 1, 1], [1, -2, 1], [-1, -2, 1],
    [-1, 2, 1], [-2, -1, 1],
    ...([-1, 1] as const).flatMap(x => ([-1, 1] as const).flatMap(y => [
      [x * 0.8, y * 1.3, 1] as Vec3, [x * 1.3, y * 0.8, 1] as Vec3, [x * 0.6, y * 0.9, 1] as Vec3,
    ]))];
  const axes = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  const dot = (a: readonly number[], b: readonly number[]) => a.reduce((sum, value, index) => sum + value * b[index], 0);
  let best = fallback; let bestScore = -Infinity;
  for (const candidate of candidates) {
    const unit = candidate.map(value => value / Math.hypot(...candidate));
    const project = (vector: number[]) => {
      const component = dot(vector, unit);
      const plane = vector.map((value, index) => value - component * unit[index]);
      return { plane, visible: Math.hypot(...plane), length: Math.hypot(...vector) };
    };
    const projected = vectors.map(project); const projectedAxes = axes.map(project);
    if ([...projected, ...projectedAxes].some(vector => vector.visible < 1e-9 || vector.length < 1e-9)) continue;
    const cosine = (a: typeof projected[number], b: typeof projected[number]) => dot(a.plane, b.plane) / (a.visible * b.visible);
    let separation = Infinity;
    for (let i = 0; i < projected.length; i++) for (let j = i + 1; j < projected.length; j++) {
      const a = projected[i]; const b = projected[j];
      separation = Math.min(separation, 1 - cosine(a, b));
    }
    let axisSeparation = 1; let vectorAxisSeparation = 1;
    for (let i = 0; i < axes.length; i++) {
      for (let j = i + 1; j < axes.length; j++) axisSeparation = Math.min(axisSeparation, 1 - Math.abs(cosine(projectedAxes[i], projectedAxes[j])));
      for (let j = 0; j < vectors.length; j++) {
        // Parallel vectors really do lie along the same line as the axis.
        if (Math.abs(dot(axes[i], vectors[j])) / projected[j].length < 0.995) {
          vectorAxisSeparation = Math.min(vectorAxisSeparation, 1 - Math.abs(cosine(projectedAxes[i], projected[j])));
        }
      }
    }
    const visible = projected.length ? Math.min(...projected.map(vector => vector.visible / vector.length)) : 1;
    const score = 3 * (Number.isFinite(separation) ? separation : 0) + 0.35 * visible
      + 1.2 * axisSeparation + 2.5 * Math.sqrt(Math.max(0, vectorAxisSeparation));
    if (score > bestScore) { bestScore = score; best = candidate; }
  }
  return best;
}

/** A genuine plane section through a perpendicular and one point of the base. */
export function altitudeSection(spec: Geometry3dSpec): { points: { label: string; at: readonly [number, number] }[] } | null {
  const altitudeLine = spec.lines.find(line => line.label === 'DH' || line.label === 'NH');
  if (!altitudeLine) return null;
  const point = (label: string) => spec.points.find(value => value.label === label);
  const h = point('H'); const d = point(altitudeLine.label[0]); const base = ['A', 'B', 'C'].map(point);
  if (!h || !d || base.some(value => !value)) return null;
  const subtract = (a: readonly number[], b: readonly number[]) => a.map((value, i) => value - b[i]);
  const dot = (a: readonly number[], b: readonly number[]) => a.reduce((sum, value, i) => sum + value * b[i], 0);
  const altitude = subtract(d.at, h.at); const height = Math.hypot(...altitude);
  if (height < 1e-9) return null;
  const reference = base.find(value => value && Math.hypot(...subtract(value.at, h.at)) > 1e-9);
  if (!reference) return null;
  for (const vertex of base) {
    const edge = subtract(vertex!.at, h.at); const length = Math.hypot(...edge);
    if (Math.abs(dot(edge, altitude)) > 1e-7 * Math.max(1, length * height)) return null;
  }
  const distance = Math.hypot(...subtract(reference.at, h.at));
  return { points: [
    { label: 'H', at: [0, 0] }, { label: d.label, at: [0, height] }, { label: reference.label, at: [distance, 0] },
  ] };
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
