import { gridMesh, polyline, type Scene3D, type Vec3 } from '../three/geometry';
import type { Region } from './region';

/** Grid over (outer, inner) parameters; the outer one carries the polar angle, so it gets more cells. */
const OUTER_CELLS = 48;
const INNER_CELLS = 24;
const WALL_CELLS = 64;
/** Heights are rescaled only when the surface would be much taller or flatter than the region is wide. */
const TALLEST = 1.5;
const FLATTEST = 0.2;

/** The factor applied to heights so the surface stays readable; 1 means true scale. */
export function heightScale(region: Region): number {
  const { x, y, z } = region.spec.window;
  const width = Math.max(x[1] - x[0], y[1] - y[0]);
  const ratio = (z[1] - z[0]) / width;
  if (ratio > TALLEST) return Number(((TALLEST * width) / (z[1] - z[0])).toPrecision(2));
  if (ratio < FLATTEST) return Number(((FLATTEST * width) / (z[1] - z[0])).toPrecision(2));
  return 1;
}

/** The surface z = f(x, y) over the region, meshed on the region's own parameter grid (#113). */
export function surfaceScene(region: Region): Scene3D {
  const k = heightScale(region);
  const { x, y, z } = region.spec.window;
  const lift = (s: number, t: number, height: boolean): Vec3 | null => {
    const p = region.point(s, t);
    return p ? [p.x, p.y, height ? p.z * k : 0] : null;
  };
  const surface = gridMesh(OUTER_CELLS, INNER_CELLS, (s, t) => lift(s, t, true));
  const floor = gridMesh(OUTER_CELLS, INNER_CELLS, (s, t) => lift(s, t, false), 'floor');
  // Parameter edges of the region; a full turn has no radial seam.
  const corners: Array<[number, number]> = [[0, 0], [1, 0], [1, 1], [0, 1]];
  const edges = region.fullTurn
    ? [[[0, 0], [1, 0]], [[0, 1], [1, 1]]]
    : corners.map((corner, i) => [corner, corners[(i + 1) % 4]]);
  const lines: Float32Array[] = [];
  const walls = [];
  for (const [[s0, t0], [s1, t1]] of edges) {
    const at = (k: number, height: boolean) => lift(s0 + (s1 - s0) * k, t0 + (t1 - t0) * k, height);
    const along = (height: boolean) => Array.from({ length: WALL_CELLS + 1 }, (_, i) => at(i / WALL_CELLS, height));
    lines.push(polyline(along(false)), polyline(along(true)));
    // A curtain from the floor up to the surface along the edge, so the volume reads as a solid.
    walls.push(gridMesh(WALL_CELLS, 1, (k, h) => {
      const top = at(k, true);
      return top && [top[0], top[1], top[2] * h];
    }, 'wall'));
  }
  return {
    meshes: [floor, ...walls, surface],
    lines: lines.filter(line => line.length >= 6),
    box: { min: [x[0], y[0], z[0] * k], max: [x[1], y[1], z[1] * k] },
  };
}
