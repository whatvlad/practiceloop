/** Small 2D plotting helpers shared by the SVG views (ADR-006): no plotting library. */

export type Fn = (x: number) => number;
export type Interval = readonly [number, number];

export interface Scale {
  (value: number): number;
  domain: Interval;
  range: Interval;
}

export function linear(domain: Interval, range: Interval): Scale {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const scale = ((value: number) => r0 + ((value - d0) / (d1 - d0)) * (r1 - r0)) as Scale;
  scale.domain = domain;
  scale.range = range;
  return scale;
}

/** About `count` round tick values inside [lo, hi]: steps of 1, 2 or 5 times a power of ten. */
export function ticks(lo: number, hi: number, count = 6): number[] {
  const raw = (hi - lo) / Math.max(1, count);
  const power = 10 ** Math.floor(Math.log10(raw));
  // The round step whose tick count is closest to the one asked for.
  const step = [1, 2, 5, 10].map(m => m * power)
    .reduce((best, s) => (Math.abs((hi - lo) / s - count) < Math.abs((hi - lo) / best - count) ? s : best));
  const out: number[] = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + step * 1e-9; v += step) out.push(Math.abs(v) < step * 1e-9 ? 0 : v);
  return out;
}

/** Ticks on multiples of π/2 for trigonometric windows, else round numbers. */
export function xTicks(lo: number, hi: number, count = 6): { value: number; label: string }[] {
  const piLike = Math.abs(Math.abs(hi) / Math.PI - Math.round(Math.abs(hi) / Math.PI)) < 1e-6 && Math.abs(hi) >= Math.PI - 1e-6;
  if (piLike) {
    const half = Math.PI / 2;
    const step = (hi - lo) / half > 2 * count ? Math.PI : half;
    const out: { value: number; label: string }[] = [];
    for (let k = Math.ceil(lo / step - 1e-9); k * step <= hi + 1e-9; k += 1) out.push({ value: k * step, label: piLabel(k * step / half) });
    return out;
  }
  return ticks(lo, hi, count).map(value => ({ value, label: format(value) }));
}

function piLabel(halves: number): string {
  const n = Math.round(halves);
  if (n === 0) return '0';
  if (n % 2 === 0) { const k = n / 2; return k === 1 ? 'π' : k === -1 ? '−π' : `${k < 0 ? '−' : ''}${Math.abs(k)}π`; }
  return `${n < 0 ? '−' : ''}${Math.abs(n) === 1 ? '' : Math.abs(n)}π/2`;
}

/** A short readable number: 3 significant decimals, a real minus sign. */
export function format(value: number, digits = 3): string {
  if (!Number.isFinite(value)) return '—';
  if (Math.abs(value) < 1e-9) return '0';
  const text = Math.abs(value) >= 1000 ? value.toFixed(0) : String(Number(value.toFixed(digits)));
  return text.replace('-', '−');
}

/**
 * An SVG path of y = fn(x). Non-finite values and jumps that leave the window
 * (a pole) break the line instead of drawing a false vertical segment.
 */
export function curvePath(fn: Fn, sx: Scale, sy: Scale, samples = 480, from = sx.domain[0], to = sx.domain[1]): string {
  const [top, bottom] = [Math.min(...sy.range), Math.max(...sy.range)];
  const height = bottom - top;
  const band: Interval = [top - 2 * height, bottom + 2 * height];
  let path = '';
  let previous: number | null = null;
  for (let i = 0; i <= samples; i += 1) {
    const x = from + ((to - from) * i) / samples;
    const value = fn(x);
    if (!Number.isFinite(value)) { previous = null; continue; }
    const py = sy(value);
    const outside = py < band[0] || py > band[1];
    const jump = previous !== null && Math.abs(py - previous) > 1.5 * height && (outside || previous < band[0] || previous > band[1]);
    const y = Math.min(band[1], Math.max(band[0], py));
    path += `${previous === null || jump ? 'M' : 'L'}${sx(x).toFixed(2)},${y.toFixed(2)}`;
    previous = py;
  }
  return path;
}

/** The region between y = fn(x) and the x-axis over [a, b], as one closed path. */
export function areaPath(fn: Fn, sx: Scale, sy: Scale, a: number, b: number, samples = 240): string {
  const zero = sy(0).toFixed(2);
  let path = `M${sx(a).toFixed(2)},${zero}`;
  const [top, bottom] = [Math.min(...sy.range), Math.max(...sy.range)];
  const height = bottom - top;
  for (let i = 0; i <= samples; i += 1) {
    const x = a + ((b - a) * i) / samples;
    const value = fn(x);
    const y = Number.isFinite(value) ? Math.min(bottom + height, Math.max(top - height, sy(value))) : sy(0);
    path += `L${sx(x).toFixed(2)},${y.toFixed(2)}`;
  }
  return `${path}L${sx(b).toFixed(2)},${zero}Z`;
}

/** Composite Simpson's rule with an even number of panels. */
export function simpson(fn: Fn, a: number, b: number, panels = 400): number {
  const n = panels % 2 ? panels + 1 : panels;
  const h = (b - a) / n;
  let sum = fn(a) + fn(b);
  for (let i = 1; i < n; i += 1) sum += (i % 2 ? 4 : 2) * fn(a + i * h);
  return (sum * h) / 3;
}

export type Rule = 'left' | 'midpoint' | 'right';

export interface Partition {
  x0: number;
  x1: number;
  height: number;
}

/** The n rectangles of a Riemann sum and their total signed area. */
export function riemann(fn: Fn, a: number, b: number, n: number, rule: Rule): { parts: Partition[]; sum: number } {
  const width = (b - a) / n;
  const offset = { left: 0, midpoint: 0.5, right: 1 }[rule];
  const parts = Array.from({ length: n }, (_, i) => {
    const x0 = a + i * width;
    return { x0, x1: x0 + width, height: fn(x0 + offset * width) };
  });
  return { parts, sum: parts.reduce((total, part) => total + part.height * width, 0) };
}
