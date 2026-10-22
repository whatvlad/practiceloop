import { compile } from '../expression';
import type { Region2dSpec } from '../spec';

export interface RegionPoint {
  x: number;
  y: number;
  /** z = f at the point, NaN where f is undefined. */
  z: number;
}

export interface Region {
  spec: Region2dSpec;
  /** The point at parameters s, t ∈ [0, 1]: outer u = a + s(b − a), inner v = g(u) + t(h(u) − g(u)). */
  point(s: number, t: number): RegionPoint | null;
  /** Closed boundary loops in (x, y), for the outline and the floor of the 3D view. */
  boundary(samples?: number): Array<Array<[number, number]>>;
  /** True when a polar region goes all the way round, so the edges θ = a and θ = b are a seam. */
  fullTurn: boolean;
}

/** Moves a parameter off an edge where an expression is undefined (sin y / y at y = 0). */
const NUDGE = 1e-6;

export function compileRegion(spec: Region2dSpec): Region {
  const [[inner, innerLow, innerHigh], [outer, outerLow, outerHigh]] = spec.bounds;
  const env: Record<string, number> = {};
  const a = compile(outerLow)(env);
  const b = compile(outerHigh)(env);
  const low = compile(innerLow);
  const high = compile(innerHigh);
  const f = compile(spec.f);
  const polar = spec.system === 'polar';

  function at(s: number, t: number): RegionPoint | null {
    const u = a + (b - a) * s;
    env[outer] = u;
    const g = low(env);
    const h = high(env);
    if (!Number.isFinite(g) || !Number.isFinite(h)) return null;
    const v = g + (h - g) * t;
    env[inner] = v;
    const z = f(env);
    const x = polar ? env.r * Math.cos(env.theta) : env.x;
    const y = polar ? env.r * Math.sin(env.theta) : env.y;
    return Number.isFinite(x) && Number.isFinite(y) ? { x, y, z } : null;
  }

  function point(s: number, t: number): RegionPoint | null {
    const found = at(s, t);
    if (found === null || Number.isFinite(found.z)) return found;
    const nudged = at(s + (s < 0.5 ? NUDGE : -NUDGE), t + (t < 0.5 ? NUDGE : -NUDGE));
    return nudged && Number.isFinite(nudged.z) ? { ...found, z: nudged.z } : found;
  }

  const fullTurn = polar && Math.abs(b - a - 2 * Math.PI) < 1e-9;

  function boundary(samples = 96): Array<Array<[number, number]>> {
    const edge = (from: [number, number], to: [number, number]) => {
      const points: Array<[number, number]> = [];
      for (let i = 0; i <= samples; i++) {
        const k = i / samples;
        const p = at(from[0] + (to[0] - from[0]) * k, from[1] + (to[1] - from[1]) * k);
        if (p) points.push([p.x, p.y]);
      }
      return points;
    };
    if (fullTurn) {
      // A disk or an annulus: the inner and the outer circle, no radial seam.
      return [edge([0, 1], [1, 1]), edge([0, 0], [1, 0])].filter(loop => spread(loop) > 1e-9);
    }
    return [[...edge([0, 0], [1, 0]), ...edge([1, 0], [1, 1]), ...edge([1, 1], [0, 1]), ...edge([0, 1], [0, 0])]];
  }

  return { spec, point, boundary, fullTurn };
}

function spread(loop: Array<[number, number]>): number {
  const xs = loop.map(p => p[0]);
  const ys = loop.map(p => p[1]);
  return Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
}
