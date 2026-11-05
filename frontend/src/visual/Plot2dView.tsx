import { useId, useState } from 'react';
import type { Plot2dSpec } from './spec';
import { Axes } from './Axes';
import { linear } from './plot';
import { useWidth } from './useWidth';

/** Frozen parameter-derived geometry; toggles change visibility only. */
export function Plot2dView({ spec }: { spec: Plot2dSpec }) {
  const id = useId().replace(/:/g, '');
  const [ref, width] = useWidth<HTMLDivElement>();
  const [hidden, setHidden] = useState<Set<number>>(new Set());
  const [showLabels, setShowLabels] = useState(false);
  const height = Math.max(240, Math.min(380, width * 0.6));
  const sx = linear(spec.x, [35, width - 20]);
  const sy = linear(spec.y, [height - 35, 20]);
  return <figure className="pl-vis" aria-labelledby={`${id}-title`}>
    <figcaption id={`${id}-title`} className="pl-label">{spec.title}</figcaption>
    <div ref={ref} className="pl-vis-plot"><svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={spec.description}>
      <Axes sx={sx} sy={sy} id={id} />
      <defs><marker id={`${id}-arrow`} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="currentColor" /></marker></defs>
      <g clipPath={`url(#${id}-plot)`}>
        {spec.paths.map((path, index) => hidden.has(index) ? null : <path key={index} fill="none" stroke="currentColor" strokeWidth={index === 0 ? 2 : 1.5}
          strokeDasharray={index % 2 ? '5 3' : undefined} markerEnd={path.arrow ? `url(#${id}-arrow)` : undefined}
          d={path.points.map(([x, y], i) => `${i ? 'L' : 'M'}${sx(x)},${sy(y)}`).join(' ') + (path.closed ? ' Z' : '')}><title>{path.label}</title></path>)}
        {spec.points.map((point, index) => <g key={index}><circle cx={sx(point.x)} cy={sy(point.y)} r="4" stroke="currentColor" fill={point.included ? 'currentColor' : 'var(--surface)'}>
          <title>{point.label}: ({point.x}, {point.y}), {point.included ? 'included' : 'excluded'}</title></circle>
          {showLabels && <text x={sx(point.x) + 7} y={sy(point.y) - 7} fontSize="12" fill="currentColor">{point.label}</text>}</g>)}
      </g>
      <text x={width - 20} y={height - 6} textAnchor="end" fontSize="12" fill="currentColor">{spec.xLabel}</text>
      <text x="8" y="14" fontSize="12" fill="currentColor">{spec.yLabel}</text>
    </svg></div>
    <div className="pl-chips">{spec.paths.map((path, index) => <label key={index}><input type="checkbox" checked={!hidden.has(index)} onChange={() => setHidden(old => {
      const next = new Set(old); if (next.has(index)) next.delete(index); else next.add(index); return next;
    })} /> {path.label}</label>)}</div>
    {spec.points.length > 0 && <label className="pl-vis-toggle"><input type="checkbox" checked={showLabels} onChange={event => setShowLabels(event.target.checked)} /> Show point labels</label>}
    <p className="pl-small">{spec.description}</p>
  </figure>;
}
