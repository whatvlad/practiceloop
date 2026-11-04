/**
 * The `visual` that comes with a worked solution (ADR-006), checked at the data
 * boundary. Anything this build does not understand is `undefined`, so the
 * solution steps still show and only the visual is left out.
 */
import { compile, type Tree } from './expression';

type Interval = readonly [number, number];

export interface DefiniteSpec {
  kind: 'definite';
  version: 1;
  f: Tree;
  a: number;
  b: number;
  aLatex: string;
  bLatex: string;
  /** The interval of continuity of f around [a, b]; the bound sliders stay inside it. */
  range: Interval;
  y: Interval;
  /** The exact value at the original bounds, as LaTeX. */
  value: string;
}

export type PointKind = 'zero' | 'extremum' | 'inflection' | 'pole';

export interface IndefiniteSpec {
  kind: 'indefinite';
  version: 1;
  f: Tree;
  F: Tree;
  x: Interval;
  y: Interval;
  /** `zero` lies on f; `extremum` and `inflection` on F; `pole` is a vertical asymptote. */
  points: readonly { x: number; kind: PointKind }[];
}

/** #113: the solution's set-up of a double integral; the browser draws the region and the surface z = f. */
export interface Region2dSpec {
  kind: 'region2d';
  version: 1;
  system: 'cartesian' | 'polar';
  /** `[variable, lower, upper]`, innermost first; the inner bounds use the outer variable. */
  bounds: readonly [readonly [string, Tree, Tree], readonly [string, Tree, Tree]];
  /** The integrand in the system's variables, without the Jacobian. */
  f: Tree;
  window: { x: Interval; y: Interval; z: Interval };
  /** The region as inequalities (LaTeX), the text alternative. */
  region: string;
}

/** #114: the solution's set-up of a triple integral without its integrand; the browser draws the solid. */
export interface Solid3dSpec {
  kind: 'solid3d';
  version: 1;
  system: 'cartesian' | 'cylindrical';
  /** `[variable, lower, upper]`, innermost first: z, then the region's middle and outer variable. */
  bounds: readonly [readonly [string, Tree, Tree], readonly [string, Tree, Tree], readonly [string, Tree, Tree]];
  window: { x: Interval; y: Interval; z: Interval };
  /** The solid as inequalities (LaTeX), the text alternative. */
  solid: string;
}

export interface Plot2dSpec {
  kind: 'plot2d'; version: 1;
  title: string; description: string;
  x: Interval; y: Interval; xLabel: string; yLabel: string;
  paths: { label: string; points: (readonly [number, number])[]; closed: boolean; arrow: boolean }[];
  points: { label: string; x: number; y: number; included: boolean }[];
}

export type VisualSpec = DefiniteSpec | IndefiniteSpec | Region2dSpec | Solid3dSpec | Plot2dSpec;

const REGION_VARIABLES = { cartesian: ['x', 'y'], polar: ['r', 'theta'] } as const;
const SOLID_VARIABLES = { cartesian: ['x', 'y'], cylindrical: ['r', 'theta'] } as const;

const MAX_POINTS = 64;

function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Not an object');
  return value as Record<string, unknown>;
}

function finite(value: unknown): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new Error('Not a number');
  return value;
}

function interval(value: unknown): Interval {
  if (!Array.isArray(value) || value.length !== 2) throw new Error('Not an interval');
  const [lo, hi] = value.map(finite);
  if (!(lo < hi)) throw new Error('Empty interval');
  return [lo, hi];
}

function tree(value: unknown): Tree {
  compile(value);
  return value as Tree;
}

function text(value: unknown): string {
  if (typeof value !== 'string' || value.length > 400) throw new Error('Not a label');
  return value;
}

const POINT_KINDS: readonly PointKind[] = ['zero', 'extremum', 'inflection', 'pole'];

/** One validator per kind; a later Issue adds its kind here and in SolutionVisual. */
const VALIDATORS: Record<string, (data: Record<string, unknown>) => VisualSpec> = {
  plot2d(data) {
    if (new TextEncoder().encode(JSON.stringify(data)).length > 8192) throw new Error('Oversized diagram');
    const coordinate = (value: unknown) => {
      const number = finite(value);
      if (Math.abs(number) > 1e8) throw new Error('Coordinate outside supported range');
      return number;
    };
    const x = interval(data.x); const y = interval(data.y);
    [...x, ...y].forEach(coordinate);
    const label = (value: unknown) => {
      if (typeof value !== 'string' || value.length > 120 || !/^[A-Za-z0-9 .,():/+=-]+$/.test(value)) throw new Error('Bad diagram label');
      return value;
    };
    if (!Array.isArray(data.paths) || data.paths.length > 8 || !Array.isArray(data.points) || data.points.length > 32) throw new Error('Bad geometry');
    const paths = data.paths.map(value => {
      const path = record(value);
      if (!Array.isArray(path.points) || path.points.length < 2 || path.points.length > 96 || typeof path.closed !== 'boolean' || typeof path.arrow !== 'boolean') throw new Error('Bad path');
      const points = path.points.map((value: unknown) => {
        if (!Array.isArray(value) || value.length !== 2) throw new Error('Bad coordinate');
        return [coordinate(value[0]), coordinate(value[1])] as const;
      });
      return { label: label(path.label), points, closed: path.closed, arrow: path.arrow };
    });
    if (paths.reduce((sum, path) => sum + path.points.length, 0) > 192 || (!paths.length && !data.points.length)) throw new Error('Unbounded geometry');
    const points = data.points.map(value => {
      const point = record(value); const px = coordinate(point.x); const py = coordinate(point.y);
      if (px < x[0] || px > x[1] || py < y[0] || py > y[1] || typeof point.included !== 'boolean') throw new Error('Bad marked point');
      return { label: label(point.label), x: px, y: py, included: point.included };
    });
    return { kind: 'plot2d', version: 1, title: label(data.title), description: label(data.description), x, y,
      xLabel: label(data.xLabel), yLabel: label(data.yLabel), paths, points };
  },
  definite(data) {
    const range = interval(data.range);
    const a = finite(data.a);
    const b = finite(data.b);
    if (!(range[0] <= a && a < b && b <= range[1])) throw new Error('Bounds outside the range');
    return { kind: 'definite', version: 1, f: tree(data.f), a, b, aLatex: text(data.aLatex), bLatex: text(data.bLatex),
      range, y: interval(data.y), value: text(data.value) };
  },
  indefinite(data) {
    const x = interval(data.x);
    if (!Array.isArray(data.points) || data.points.length > MAX_POINTS) throw new Error('Bad points');
    const points = data.points.map(value => {
      const point = record(value);
      const at = finite(point.x);
      if (!POINT_KINDS.includes(point.kind as PointKind) || at < x[0] || at > x[1]) throw new Error('Bad point');
      return { x: at, kind: point.kind as PointKind };
    });
    return { kind: 'indefinite', version: 1, f: tree(data.f), F: tree(data.F), x, y: interval(data.y), points };
  },
  region2d(data) {
    if (data.system !== 'cartesian' && data.system !== 'polar') throw new Error('Bad system');
    const system = data.system;
    const names: readonly string[] = REGION_VARIABLES[system];
    if (!Array.isArray(data.bounds) || data.bounds.length !== 2) throw new Error('Bad bounds');
    const [inner, outer] = data.bounds.map((value: unknown) => {
      if (!Array.isArray(value) || value.length !== 3 || !names.includes(value[0])) throw new Error('Bad bound');
      return [value[0] as string, tree(value[1]), tree(value[2])] as const;
    });
    if (inner[0] === outer[0]) throw new Error('Repeated variable');
    const window = record(data.window);
    return { kind: 'region2d', version: 1, system, bounds: [inner, outer], f: tree(data.f),
      window: { x: interval(window.x), y: interval(window.y), z: interval(window.z) }, region: text(data.region) };
  },
  solid3d(data) {
    if (data.system !== 'cartesian' && data.system !== 'cylindrical') throw new Error('Bad system');
    const system = data.system;
    const names: readonly string[] = ['z', ...SOLID_VARIABLES[system]];
    if (!Array.isArray(data.bounds) || data.bounds.length !== 3) throw new Error('Bad bounds');
    const [z, middle, outer] = data.bounds.map((value: unknown) => {
      if (!Array.isArray(value) || value.length !== 3 || !names.includes(value[0])) throw new Error('Bad bound');
      return [value[0] as string, tree(value[1]), tree(value[2])] as const;
    });
    if (z[0] !== 'z' || middle[0] === 'z' || outer[0] === 'z' || middle[0] === outer[0]) throw new Error('Bad order');
    const window = record(data.window);
    return { kind: 'solid3d', version: 1, system, bounds: [z, middle, outer],
      window: { x: interval(window.x), y: interval(window.y), z: interval(window.z) }, solid: text(data.solid) };
  },
};

export function parseVisual(value: unknown): VisualSpec | undefined {
  try {
    const data = record(value);
    if (data.version !== 1 || typeof data.kind !== 'string' || !Object.hasOwn(VALIDATORS, data.kind)) return undefined;
    return VALIDATORS[data.kind](data);
  } catch {
    return undefined;
  }
}
