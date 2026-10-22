import { compile } from '../expression';
import type { Solid3dSpec } from '../spec';
import { gridMesh, polyline, type Scene3D, type Vec3 } from '../three/geometry';

/** Cells of the region grid (the outer variable may be the angle, so it gets more) and along each wall. */
const OUTER_CELLS = 48;
const MIDDLE_CELLS = 24;
const EPSILON = 1e-9;

type Edge = [[number, number], [number, number]];
const EDGES: Edge[] = [
  [[0, 0], [1, 0]],
  [[1, 0], [1, 1]],
  [[1, 1], [0, 1]],
  [[0, 1], [0, 0]],
];

/**
 * The solid z ∈ [g, h] over a planar region: the bottom and top surfaces over the
 * region's parameter grid (s over the outer interval, t across the middle one) and
 * a side wall on each edge of that grid. An edge that collapses to a point (r from 0)
 * or lies on the opposite edge (θ over a full turn) gets no wall and no outline.
 */
export function solidScene(spec: Solid3dSpec, outerCells = OUTER_CELLS, middleCells = MIDDLE_CELLS): Scene3D {
  const [[, zLow, zHigh], [middle, middleLow, middleHigh], [outer, outerLow, outerHigh]] = spec.bounds;
  const env: Record<string, number> = {};
  const a = compile(outerLow)(env);
  const b = compile(outerHigh)(env);
  const low = compile(middleLow);
  const high = compile(middleHigh);
  const bottom = compile(zLow);
  const top = compile(zHigh);
  const cylindrical = spec.system === 'cylindrical';

  /** The point at parameters s, t on the bottom (w = 0) or the top (w = 1) surface. */
  function at(s: number, t: number, w: number): Vec3 | null {
    env[outer] = a + (b - a) * s;
    const g = low(env);
    const h = high(env);
    env[middle] = g + (h - g) * t;
    const x = cylindrical ? env.r * Math.cos(env.theta) : env.x;
    const y = cylindrical ? env.r * Math.sin(env.theta) : env.y;
    if (cylindrical) Object.assign(env, { x, y });
    const z = w === 0 ? bottom(env) : top(env);
    const point: Vec3 = [x, y, z];
    return point.every(Number.isFinite) ? point : null;
  }

  const cells = (edge: Edge) => (edge[0][0] === edge[1][0] ? middleCells : outerCells);
  const along = (edge: Edge, w: number) => {
    const [[s0, t0], [s1, t1]] = edge;
    const n = cells(edge);
    return Array.from({ length: n + 1 }, (_, i) => at(s0 + ((s1 - s0) * i) / n, t0 + ((t1 - t0) * i) / n, w));
  };
  const flat = (p: Vec3 | null, q: Vec3 | null) => !!p && !!q && Math.hypot(p[0] - q[0], p[1] - q[1]) < EPSILON;
  const collapsed = (edge: Edge) => {
    const points = along(edge, 0);
    return points.every(p => !p || flat(p, points[0]));
  };
  // s = 0 and s = 1 coincide when the region closes on itself (a full turn in θ).
  const s0 = along(EDGES[3], 0).reverse();
  const seam = along(EDGES[1], 0).every((p, i) => flat(p, s0[i]));
  const kept = EDGES.map((edge, i) => !collapsed(edge) && !(seam && (i === 1 || i === 3)));

  const meshes = [
    gridMesh(outerCells, middleCells, (s, t) => at(s, t, 0), 'floor'),
    gridMesh(outerCells, middleCells, (s, t) => at(s, t, 1), 'wall'),
  ];
  const lines: Float32Array[] = [];
  EDGES.forEach((edge, i) => {
    if (!kept[i]) return;
    const [[s0, t0], [s1, t1]] = edge;
    meshes.push(gridMesh(cells(edge), 1, (k, w) => at(s0 + (s1 - s0) * k, t0 + (t1 - t0) * k, w), 'wall'));
    lines.push(polyline(along(edge, 0)), polyline(along(edge, 1)));
    // A vertical edge where this wall meets the next one.
    const [s, t] = edge[1];
    if (kept[(i + 1) % 4]) lines.push(polyline([at(s, t, 0), at(s, t, 1)]));
  });
  const { x, y, z } = spec.window;
  return {
    meshes,
    lines: lines.filter(line => line.length >= 6),
    box: { min: [x[0], y[0], z[0]], max: [x[1], y[1], z[1]] },
  };
}
