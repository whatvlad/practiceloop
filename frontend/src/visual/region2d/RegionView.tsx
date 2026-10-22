import type { Region } from './region';

/** Width of the drawing in SVG units; the height follows the window at equal x and y scale. */
const WIDTH = 320;
const MAX_HEIGHT = 320;
/** Lines of constant outer variable: the inner integral runs along each of them. */
const CHORDS = 9;

/** A tick step of 1, 2 or 5 times a power of ten, about `count` ticks over the span. */
export function tickStep(span: number, count = 5): number {
  const raw = span / count;
  const power = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].find(m => m * power >= raw) ?? 10;
  return step * power;
}

export function ticks(low: number, high: number): number[] {
  const step = tickStep(high - low);
  const out: number[] = [];
  for (let v = Math.ceil(low / step) * step; v <= high + 1e-9; v += step) out.push(Math.abs(v) < 1e-9 ? 0 : Number(v.toPrecision(6)));
  return out;
}

function path(loop: Array<[number, number]>, sx: (x: number) => number, sy: (y: number) => number, close = true): string {
  return loop.map(([x, y], i) => `${i ? 'L' : 'M'}${sx(x).toFixed(2)} ${sy(y).toFixed(2)}`).join('') + (close ? 'Z' : '');
}

/** The region in the xy-plane, drawn from the bounds (#113). */
export function RegionView({ region, label }: { region: Region; label: string }) {
  const { x: [x0, x1], y: [y0, y1] } = region.spec.window;
  const scale = Math.min(WIDTH / (x1 - x0), MAX_HEIGHT / (y1 - y0));
  const width = (x1 - x0) * scale;
  const height = (y1 - y0) * scale;
  const sx = (x: number) => (x - x0) * scale;
  const sy = (y: number) => height - (y - y0) * scale;
  const loops = region.boundary();
  const chords: Array<Array<[number, number]>> = [];
  for (let i = 1; i < CHORDS; i++) {
    const line: Array<[number, number]> = [];
    for (let j = 0; j <= 24; j++) {
      const p = region.point(i / CHORDS, j / 24);
      if (p) line.push([p.x, p.y]);
    }
    chords.push(line);
  }
  const [inner, outer] = region.spec.bounds.map(b => b[0] === 'theta' ? 'θ' : b[0]);
  return (
    <figure className="pl-visual-region">
      <svg viewBox={`-28 -8 ${width + 40} ${height + 30}`} role="img" aria-label={label}>
        <g className="grid">
          {ticks(x0, x1).map(t => <line key={`x${t}`} x1={sx(t)} x2={sx(t)} y1={0} y2={height} />)}
          {ticks(y0, y1).map(t => <line key={`y${t}`} y1={sy(t)} y2={sy(t)} x1={0} x2={width} />)}
        </g>
        <g className="axes">
          {y0 < 0 && y1 > 0 && <line x1={0} x2={width} y1={sy(0)} y2={sy(0)} />}
          {x0 < 0 && x1 > 0 && <line y1={0} y2={height} x1={sx(0)} x2={sx(0)} />}
        </g>
        <g className="labels" aria-hidden="true">
          {ticks(x0, x1).map(t => <text key={`x${t}`} x={sx(t)} y={height + 14} textAnchor="middle">{t}</text>)}
          {ticks(y0, y1).map(t => <text key={`y${t}`} x={-6} y={sy(t) + 4} textAnchor="end">{t}</text>)}
          <text x={width + 4} y={height + 14}>x</text>
          <text x={-6} y={-0} textAnchor="end">y</text>
        </g>
        <path className="fill" d={loops.map(loop => path(loop, sx, sy)).join('')} fillRule="evenodd" />
        <g className="chords">
          {chords.map((line, i) => <path key={i} d={path(line, sx, sy, false)} />)}
        </g>
        {loops.map((loop, i) => <path key={i} className="edge" d={path(loop, sx, sy)} />)}
      </svg>
      <figcaption className="pl-small pl-muted">
        The region of integration. Each faint line is one inner integral in {inner} at a fixed {outer}.
      </figcaption>
    </figure>
  );
}
