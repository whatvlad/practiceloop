import { useId, useMemo, useState } from 'react';
import { Axes } from './Axes';
import { compile } from './expression';
import { curvePath, format, linear } from './plot';
import { RangeSlider } from './RangeSlider';
import type { IndefiniteSpec, PointKind } from './spec';
import { useWidth } from './useWidth';

const PAD = { left: 12, right: 12, top: 12, bottom: 12 };
const NAMES: Record<PointKind, string> = {
  zero: 'zeros of f',
  extremum: 'extrema of F',
  inflection: 'inflection points of F',
  pole: 'vertical asymptotes',
};

/** f and an antiderivative F + C on one set of axes, with the points SymPy marked (ADR-006). */
export function IndefiniteView({ spec }: { spec: IndefiniteSpec }) {
  const id = useId().replace(/:/g, '');
  const [f, big] = useMemo(() => {
    const [one, two] = [compile(spec.f), compile(spec.F)];
    return [(x: number) => one({ x }), (x: number) => two({ x })];
  }, [spec.f, spec.F]);
  const [c, setC] = useState(0);
  const span = spec.y[1] - spec.y[0];
  const reach = Math.max(1, Math.round(span / 2));
  const shifted = useMemo(() => (x: number) => big(x) + c, [big, c]);
  const [ref, width] = useWidth<HTMLDivElement>();
  const height = Math.round(Math.min(380, Math.max(220, width * 0.6)));
  const sx = linear(spec.x, [PAD.left, width - PAD.right]);
  const sy = linear(spec.y, [height - PAD.bottom, PAD.top]);
  const inside = (y: number) => Number.isFinite(y) && y >= spec.y[0] && y <= spec.y[1];
  const kinds = (['zero', 'extremum', 'inflection', 'pole'] as const)
    .map(kind => ({ kind, xs: spec.points.filter(point => point.kind === kind).map(point => point.x) }))
    .filter(group => group.xs.length);
  return (
    <figure className="pl-vis pl-fade" aria-labelledby={`${id}-title`}>
      <figcaption id={`${id}-title`} className="pl-label">The integrand and its antiderivatives</figcaption>
      <div ref={ref} className="pl-vis-plot">
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img"
          aria-label={`Graphs of the integrand f and of the antiderivative F plus ${format(c)} for x from ${format(spec.x[0])} to ${format(spec.x[1])}.`}>
          <Axes sx={sx} sy={sy} id={id} />
          <g clipPath={`url(#${id}-plot)`}>
            {spec.points.filter(point => point.kind === 'pole').map(point => (
              <line key={`pole${point.x}`} className="pl-vis-pole" x1={sx(point.x)} x2={sx(point.x)} y1={PAD.top} y2={height - PAD.bottom} />
            ))}
            <path className="pl-vis-curve f" d={curvePath(f, sx, sy)} />
            <path className="pl-vis-curve big" d={curvePath(shifted, sx, sy)} />
            {spec.points.map(point => {
              if (point.kind === 'pole') return null;
              const y = point.kind === 'zero' ? 0 : shifted(point.x);
              if (!inside(y)) return null;
              return <circle key={`${point.kind}${point.x}`} className={`pl-vis-point ${point.kind}`} cx={sx(point.x)} cy={sy(y)} r={point.kind === 'zero' ? 4 : 5} />;
            })}
          </g>
        </svg>
      </div>
      <ul className="pl-vis-legend pl-small" aria-label="Legend">
        <li><i className="f" aria-hidden="true" />f, the integrand</li>
        <li><i className="big" aria-hidden="true" />F + C, an antiderivative</li>
        {kinds.some(group => group.kind === 'zero') && <li><i className="dot zero" aria-hidden="true" />zero of f</li>}
        {kinds.some(group => group.kind === 'extremum') && <li><i className="dot extremum" aria-hidden="true" />extremum of F</li>}
        {kinds.some(group => group.kind === 'inflection') && <li><i className="dot inflection" aria-hidden="true" />inflection point of F</li>}
        {kinds.some(group => group.kind === 'pole') && <li><i className="pole" aria-hidden="true" />vertical asymptote</li>}
      </ul>
      <div className="pl-vis-controls">
        <RangeSlider label="Constant C" valueText={`C = ${format(c)}`} value={c} min={-reach} max={reach} step={reach / 100} onChange={setC} />
      </div>
      <p className="pl-small pl-muted pl-m-0">
        Every C gives an antiderivative: moving it shifts F up or down and leaves its slope, f, unchanged.
        {kinds.length > 0 && ' Marked: '}
        {kinds.map((group, index) => (
          <span key={group.kind}>{index ? '; ' : ''}{NAMES[group.kind]} at x ≈ {group.xs.slice(0, 6).map(x => format(x, 2)).join(', ')}{group.xs.length > 6 ? ', …' : ''}</span>
        ))}
        {kinds.length > 0 && '.'}
      </p>
    </figure>
  );
}
