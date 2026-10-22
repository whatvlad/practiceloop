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

export type VisualSpec = DefiniteSpec | IndefiniteSpec;

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
