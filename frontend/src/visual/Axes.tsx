import { format, ticks, xTicks, type Scale } from './plot';

/** Grid, both axes through 0 when visible, and tick labels for one plot. */
export function Axes({ sx, sy, id }: { sx: Scale; sy: Scale; id: string }) {
  const [left, right] = sx.range;
  const [bottom, top] = sy.range;
  const x0 = Math.min(right, Math.max(left, sx(0)));
  const y0 = Math.min(bottom, Math.max(top, sy(0)));
  const xs = xTicks(sx.domain[0], sx.domain[1], Math.max(3, Math.round((right - left) / 90)));
  const ys = ticks(sy.domain[0], sy.domain[1], Math.max(3, Math.round((bottom - top) / 60)));
  return (
    <g className="pl-vis-axes" aria-hidden="true">
      <clipPath id={`${id}-plot`}><rect x={left} y={top} width={right - left} height={bottom - top} /></clipPath>
      {xs.map(t => <line key={`gx${t.value}`} className="grid" x1={sx(t.value)} x2={sx(t.value)} y1={top} y2={bottom} />)}
      {ys.map(v => <line key={`gy${v}`} className="grid" x1={left} x2={right} y1={sy(v)} y2={sy(v)} />)}
      <line className="axis" x1={left} x2={right} y1={y0} y2={y0} />
      <line className="axis" x1={x0} x2={x0} y1={top} y2={bottom} />
      {xs.filter(t => t.value !== 0).map(t => (
        <text key={`tx${t.value}`} x={sx(t.value)} y={Math.min(bottom - 4, y0 + 16)} textAnchor="middle">{t.label}</text>
      ))}
      {ys.filter(v => v !== 0).map(v => (
        <text key={`ty${v}`} x={Math.max(left + 4, x0 - 6)} y={sy(v) + 4} textAnchor={x0 - 6 < left + 30 ? 'start' : 'end'}>{format(v)}</text>
      ))}
    </g>
  );
}
