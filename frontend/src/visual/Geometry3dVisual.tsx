import { lazy, Suspense, useCallback, useEffect, useId, useMemo, useRef, useState } from 'react';
import type { Geometry3dSpec, GeometryPoint3 } from './spec';
import { altitudeSection, coordinateAxes, geometryScene, type Scene3D } from './three/geometry';
import { VisualBoundary } from './VisualBoundary';

const ThreeView = lazy(() => import('./three/ThreeView'));

/** An orthographic projection: useful for orientation, but not true lengths or angles. */
function Projection({ spec, box }: { spec: Geometry3dSpec; box: Scene3D['box'] }) {
  const id = useId().replaceAll(':', '');
  const project = ([x, y, z]: GeometryPoint3) => [(x - y) / Math.SQRT2, (2 * z - x - y) / Math.sqrt(6)] as const;
  const axes = coordinateAxes(box);
  const labelledLines = new Set<string>();
  const all = [
    ...spec.points.map(point => point.at), ...spec.lines.flatMap(line => [line.start, line.end]),
    ...spec.faces.flatMap(face => face.vertices),
    ...axes.flatMap(axis => [axis.from, axis.to]),
  ].map(project);
  const minX = Math.min(...all.map(point => point[0])); const maxX = Math.max(...all.map(point => point[0]));
  const minY = Math.min(...all.map(point => point[1])); const maxY = Math.max(...all.map(point => point[1]));
  const width = 320; const height = 240; const padding = 28;
  const scale = Math.min((width - 2 * padding) / Math.max(maxX - minX, 0.01), (height - 2 * padding) / Math.max(maxY - minY, 0.01));
  const map = (point: GeometryPoint3) => {
    const [x, y] = project(point);
    return [width / 2 + (x - (minX + maxX) / 2) * scale, height / 2 - (y - (minY + maxY) / 2) * scale] as const;
  };
  const [originX, originY] = map([0, 0, 0]);
  const occupied = axes.map(axis => { const [x, y] = map(axis.to); return { x: x + 5, y: y - 21, width: 11, height: 20 }; });
  occupied.push({ x: originX - 10, y: originY - 2, width: 11, height: 20 });
  // Place point names first, then active constructions. Try nearby free positions
  // so a line's name does not cover its foot or leave the drawing on a phone.
  const labelAt = (x: number, y: number, label: string) => {
    const textWidth = Math.min(width - 16, label.length * 11);
    const positions = [[0, 0], [0, 22], [0, -22], [-textWidth - 12, 0], [-textWidth - 12, 22], [-textWidth - 12, -22], [0, 44], [0, -44]]
      .map(([dx, dy]) => ({ x: Math.max(8, Math.min(width - 8 - textWidth, x + dx)), y: Math.max(18, Math.min(height - 8, y + dy)) }));
    const chosen = positions.find(position => !occupied.some(box => position.x < box.x + box.width + 2
      && position.x + textWidth + 2 > box.x && position.y - 16 < box.y + box.height + 2 && position.y + 6 > box.y)) ?? positions[0];
    occupied.push({ x: chosen.x, y: chosen.y - 16, width: textWidth, height: 20 });
    return chosen;
  };
  const pointLabels = new Map(spec.points.map((point, index) => ({ point, index })).sort((a, b) => Number(b.point.tone === 'active') - Number(a.point.tone === 'active'))
    .map(({ point, index }) => { const [x, y] = map(point.at); return [index, labelAt(x + 7, y - 7, point.label)] as const; }));
  const lineLabels = new Map<string, { x: number; y: number }>();
  const priority = { active: 0, previous: 1, given: 2 };
  for (const line of [...spec.lines].sort((a, b) => priority[a.tone] - priority[b.tone])) {
    if (lineLabels.has(line.label)) continue;
    const [x1, y1] = map(line.start); const [x2, y2] = map(line.end);
    const along = !line.arrow && !line.dashed ? 0.7 : 0.5;
    lineLabels.set(line.label, labelAt(x1 + (x2 - x1) * along + 4, y1 + (y2 - y1) * along - 5, line.label));
  }
  return <div className="pl-geometry-projection">
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${spec.description} 2D projection with coordinate axes x, y and z; angles and lengths may look different.`}>
      <defs><marker id={`arrow-${id}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" /></marker></defs>
      {spec.faces.map((face, index) => <polygon key={`${face.label}-${index}`} className={`pl-geometry-face ${face.tone}`} points={face.vertices.map(point => map(point).join(',')).join(' ')} />)}
      {axes.map(axis => {
        const [x1, y1] = map(axis.from); const [x2, y2] = map(axis.to);
        return <g key={axis.name} data-axis={axis.name} className="pl-geometry-axis">
          <line x1={x1} y1={y1} x2={x2} y2={y2} markerEnd={`url(#arrow-${id})`} />
          <text x={x2 + 5} y={y2 - 5}>{axis.name}</text>
        </g>;
      })}
      <g className="pl-geometry-axis"><circle data-axis-origin cx={originX} cy={originY} r="2" /><text x={originX - 10} y={originY + 14}>0</text></g>
      {spec.lines.map((line, index) => {
        const [x1, y1] = map(line.start); const [x2, y2] = map(line.end);
        const showLabel = !labelledLines.has(line.label);
        labelledLines.add(line.label);
        return <g key={`${line.label}-${index}`} className={`pl-geometry-line ${line.tone}`}>
          <line x1={x1} y1={y1} x2={x2} y2={y2} strokeDasharray={line.dashed ? '5 4' : undefined} markerEnd={line.arrow ? `url(#arrow-${id})` : undefined} />
          {showLabel && <text {...lineLabels.get(line.label)}>{line.label}</text>}
        </g>;
      })}
      {spec.points.map((point, index) => {
        const [x, y] = map(point.at);
        return <g key={`${point.label}-${index}`} className={`pl-geometry-point ${point.tone}`}><circle cx={x} cy={y} r="3.5" /><text {...pointLabels.get(index)}>{point.label}</text></g>;
      })}
    </svg>
  </div>;
}

function HeightSection({ section }: { section: NonNullable<ReturnType<typeof altitudeSection>> }) {
  const id = useId().replaceAll(':', '');
  const [, d, base] = section.points;
  const width = 320; const height = 240; const x = 55; const y = 195;
  const scale = Math.min(220 / base.at[0], 155 / d.at[1]);
  const naturalHeight = d.at[1] * scale;
  const shownHeight = Math.max(60, naturalHeight);
  const notToScale = shownHeight > naturalHeight + 0.1;
  const baseX = x + base.at[0] * scale; const topY = y - shownHeight;
  const axisS = Math.min(width - 22, baseX + 18); const axisT = Math.max(17, topY - 16);
  const corner = Math.min(13, base.at[0] * scale / 4, shownHeight / 4);
  return <div className="pl-geometry-projection">
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`A perpendicular section through ${d.label}, H and ${base.label}. ${d.label}H is perpendicular to the base plane. The local coordinates s and t start at H, toward ${base.label} and ${d.label}; they are not the original x, y and z axes.${notToScale ? ' Lengths are not to scale.' : ''}`}>
      <defs><marker id={`section-arrow-${id}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" /></marker></defs>
      <g data-axis="section-s" className="pl-geometry-axis"><line x1={x - 20} y1={y} x2={axisS} y2={y} markerEnd={`url(#section-arrow-${id})`} /><text x={axisS + 4} y={y + 14}>s</text></g>
      <g data-axis="section-t" className="pl-geometry-axis"><line x1={x} y1={y + 10} x2={x} y2={axisT} markerEnd={`url(#section-arrow-${id})`} /><text x={x + 7} y={axisT - 4}>t</text></g>
      <g className="pl-geometry-line active"><line x1={x} y1={y} x2={x} y2={topY} strokeDasharray="5 4" />
        <path d={`M ${x} ${y - corner} L ${x + corner} ${y - corner} L ${x + corner} ${y}`} fill="none" stroke="var(--correct)" />
      </g>
      {[[x, y, 'H'], [x, topY, d.label], [baseX, y, base.label]].map(([px, py, label]) =>
        <g key={label} className="pl-geometry-point"><circle cx={px} cy={py} r="3.5" /><text x={Number(px) + (label === 'H' ? -17 : 7)} y={Number(py) + (label === 'H' ? 17 : -7)}>{label}</text></g>)}
      <text className="pl-geometry-section-label" x={x + 20} y={y + 25}>section of plane ABC</text>
    </svg>
    <p className="pl-small pl-muted pl-geometry-scale-note">Local axes s and t start at H; they are not the original x, y, z axes.{notToScale && ' Section not to scale; the right angle is preserved.'}</p>
  </div>;
}

export function Geometry3dVisual({ spec }: { spec: Geometry3dSpec }) {
  const scene = useMemo(() => geometryScene(spec), [spec]);
  const section = useMemo(() => altitudeSection(spec), [spec]);
  const figure = useRef<HTMLElement>(null);
  const [nearViewport, setNearViewport] = useState(() => typeof IntersectionObserver === 'undefined');
  const [view, setView] = useState<'3d' | '2d'>('3d');
  const [webgl, setWebgl] = useState(true);
  const unavailable = useCallback(() => { setWebgl(false); setView('2d'); }, []);
  useEffect(() => {
    if (!figure.current || typeof IntersectionObserver === 'undefined') return;
    const observer = new IntersectionObserver(([entry]) => setNearViewport(entry.isIntersecting), { rootMargin: '300px' });
    observer.observe(figure.current);
    return () => observer.disconnect();
  }, []);
  return <figure ref={figure} className="pl-vis pl-geometry" aria-label={spec.title}>
    <div className="pl-geometry-head"><strong>{spec.title}</strong>
      <div className="pl-vis-choice" role="group" aria-label="Drawing view">
        <button type="button" aria-pressed={view === '3d'} disabled={!webgl} onClick={() => setView('3d')}>3D</button>
        <button type="button" aria-pressed={view === '2d'} onClick={() => setView('2d')}>2D</button>
      </div>
    </div>
    {view === '3d' && webgl && nearViewport ? <VisualBoundary fallback={<><Projection spec={spec} box={scene.box} /><p className="pl-small pl-muted">3D could not be loaded. The drawing is a 2D projection.</p></>}>
      <Suspense fallback={<><Projection spec={spec} box={scene.box} /><p className="pl-small pl-muted">Loading interactive 3D; preview is a projection.</p></>}>
        <ThreeView scene={scene} label={`${spec.description} Coordinate axes x, y and z.`} onUnavailable={unavailable} />
      </Suspense>
    </VisualBoundary> : view === '2d' && section ? <HeightSection section={section} /> : <Projection spec={spec} box={scene.box} />}
    <figcaption className="pl-small pl-muted">{spec.description}{view === '2d' && (section ? ' Perpendicular section through the altitude and a point of the base.' : ' 2D projection: angles and lengths may look different.')}{!section || view === '3d' ? ' Axes show this illustration; any unspecified position or orientation is chosen for display.' : ''}{!webgl && ' 3D is unavailable on this device.'}</figcaption>
  </figure>;
}
