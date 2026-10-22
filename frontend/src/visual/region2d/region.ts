import { compile, type Tree } from '../expression';

/** ADR-006 `region2d`: the solution's set-up of a double integral (#113). */
export interface Region2dSpec {
  kind: 'region2d';
  version: 1;
  system: 'cartesian' | 'polar';
  /** `[variable, lower, upper]`, innermost first; the inner bounds use the outer variable. */
  bounds: [[string, Tree, Tree], [string, Tree, Tree]];
  /** The integrand in the system's variables, without the Jacobian. */
  f: Tree;
  window: { x: [number, number]; y: [number, number]; z: [number, number] };
  /** The region as inequalities (LaTeX), the text alternative. */
  region: string;
}

const VARIABLES = { cartesian: ['x', 'y'], polar: ['r', 'theta'] } as const;

function isTree(value: unknown, depth = 0): value is Tree {
  if (typeof value === 'number') return true;
  if (typeof value === 'string') return true;
  return Array.isArray(value) && depth < 64 && typeof value[0] === 'string' && value.slice(1).every(v => isTree(v, depth + 1));
}

function isPair(value: unknown): value is [number, number] {
  return Array.isArray(value) && value.length === 2 && value.every(Number.isFinite) && value[0] < value[1];
}

export function isRegion2d(value: unknown): value is Region2dSpec {
  if (typeof value !== 'object' || value === null) return false;
  const spec = value as Partial<Record<keyof Region2dSpec, unknown>>;
  if (spec.kind !== 'region2d' || spec.version !== 1) return false;
  if (spec.system !== 'cartesian' && spec.system !== 'polar') return false;
  const names: readonly string[] = VARIABLES[spec.system];
  const bounds = spec.bounds;
  if (!Array.isArray(bounds) || bounds.length !== 2) return false;
  const bound = (b: unknown) => Array.isArray(b) && b.length === 3 && names.includes(b[0]) && isTree(b[1]) && isTree(b[2]);
  if (!bounds.every(bound) || bounds[0][0] === bounds[1][0]) return false;
  const window = spec.window as Record<string, unknown> | undefined;
  return isTree(spec.f) && typeof spec.region === 'string' && !!window && isPair(window.x) && isPair(window.y) && isPair(window.z);
}

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
