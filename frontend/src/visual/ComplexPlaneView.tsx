import { useId, useState } from 'react';
import { Axes } from './Axes';
import { format, linear } from './plot';
import type { ComplexPlaneSpec } from './spec';

const COLORS = ['#65adff', '#ffb65c', '#65df91'];
type Point = readonly [number, number];

export function ComplexPlaneView({ spec }: { spec: ComplexPlaneSpec }) {
  return spec.mode === 'circle' ? <CircleView spec={spec} /> : <ComplexNumberView spec={spec} />;
}

function CircleView({ spec }: { spec: ComplexPlaneSpec }) {
  const id = useId().replace(/:/g, '');
  const [x, y] = spec.first; const radius = spec.radius!;
  const extent = Math.max(1, Math.abs(x) + radius, Math.abs(y) + radius) * 1.25;
  const sx = linear([-extent * 350 / 270, extent * 350 / 270], [25, 375]);
  const sy = linear([-extent, extent], [295, 25]);
  const label = (n: number) => format(n, 4);
  return <figure className="pl-vis pl-fade" aria-labelledby={`${id}-title`}>
    <figcaption id={`${id}-title`} className="pl-label">Modulus as distance</figcaption>
    <div className="pl-vis-plot"><svg viewBox="0 0 400 320" width="100%" role="img" aria-label={`Complex plane: circle with centre (${label(x)}, ${label(y)}) and radius ${label(radius)}.`}>
      <Axes sx={sx} sy={sy} id={id} />
      <circle data-locus cx={sx(x)} cy={sy(y)} r={sx(x + radius) - sx(x)} fill="none" stroke="#65adff" strokeWidth="2.5" />
      <line x1={sx(x)} y1={sy(y)} x2={sx(x + radius)} y2={sy(y)} stroke="#ffb65c" strokeWidth="2" />
      <circle cx={sx(x)} cy={sy(y)} r="4" fill="#ffb65c" />
      <text x={sx(x) + 7} y={sy(y) - 7} fill="#ffb65c" fontSize="13">Centre</text>
      <text x="375" y="312" textAnchor="end" fontSize="12" fill="currentColor">Re</text><text x="9" y="18" fontSize="12" fill="currentColor">Im</text>
    </svg></div>
    <p className="pl-small">Centre: ({label(x)}, {label(y)}). Radius: {label(radius)}.</p>
  </figure>;
}

function ComplexNumberView({ spec }: { spec: ComplexPlaneSpec }) {
  const id = useId().replace(/:/g, '');
  const [power, setPower] = useState(spec.power ?? 1);
  const [showParts, setShowParts] = useState(true);
  const [showAngle, setShowAngle] = useState(true);
  const [showInputs, setShowInputs] = useState(true);
  const firstName = spec.firstLabel ?? 'z';
  const [a, b] = spec.first;
  const radius = Math.hypot(a, b), argument = Math.atan2(b, a);
  const powered: Point = [radius ** power * Math.cos(power * argument), radius ** power * Math.sin(power * argument)];
  const target = spec.mode === 'power' ? powered : spec.result;
  const showSecond = showInputs && spec.second !== null;
  const extent = Math.max(1, ...[spec.first, ...(showSecond ? [spec.second!] : []), ...(target ? [target] : [])].flatMap(point => point.map(Math.abs))) * 1.35;
  const xLimit = extent * 350 / 270;
  const sx = linear([-xLimit, xLimit], [25, 375]), sy = linear([-extent, extent], [295, 25]);
  const ox = sx(0), oy = sy(0);
  const plotted: { label: string; point: Point; color: string }[] = [];
  if (showInputs) plotted.push({ label: firstName, point: spec.first, color: COLORS[0] });
  if (showSecond) plotted.push({ label: 'w', point: spec.second!, color: COLORS[1] });
  if (target) plotted.push({ label: spec.mode === 'power' ? `z^${power}` : spec.mode === 'root' ? 'root' : 'result', point: target, color: COLORS[2] });
  const val = (n: number) => format(Math.abs(n) < 1e-10 ? 0 : n, 4);
  const arc = `M ${ox + 36} ${oy} A 36 36 0 0 ${argument < 0 ? 1 : 0} ${ox + 36 * Math.cos(argument)} ${oy - 36 * Math.sin(argument)}`;
  const translated = spec.second && spec.result && (spec.mode === 'add' || spec.mode === 'subtract');
  return <figure className="pl-vis pl-fade" aria-labelledby={`${id}-title`}>
    <figcaption id={`${id}-title`} className="pl-label">Complex plane</figcaption>
    <div className="pl-vis-plot"><svg viewBox="0 0 400 320" width="100%" role="img" aria-label="Complex plane. The horizontal axis is real, and the vertical axis is imaginary. Colored arrows show the numbers and result.">
      <Axes sx={sx} sy={sy} id={id} />
      <defs>{COLORS.map((color, index) => <marker key={color} id={`${id}-arrow-${index}`} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill={color} /></marker>)}</defs>
      {showParts && showInputs && <><line x1={sx(a)} y1={oy} x2={sx(a)} y2={sy(b)} stroke={COLORS[0]} strokeDasharray="4 4" /><line x1={ox} y1={sy(b)} x2={sx(a)} y2={sy(b)} stroke={COLORS[0]} strokeDasharray="4 4" /></>}
      {showAngle && showInputs && radius > 0 && <path d={arc} fill="none" stroke={COLORS[0]} strokeWidth="1.5" />}
      {translated && showInputs && <line x1={sx(a)} y1={sy(b)} x2={sx(spec.result![0])} y2={sy(spec.result![1])} stroke={COLORS[1]} strokeWidth="1.5" strokeDasharray="5 4" />}
      {plotted.map(({ label, point, color }) => <g key={label}>
        <line x1={ox} y1={oy} x2={sx(point[0])} y2={sy(point[1])} stroke={color} strokeWidth="2.5" markerEnd={`url(#${id}-arrow-${COLORS.indexOf(color)})`} />
        <circle cx={sx(point[0])} cy={sy(point[1])} r="4" fill={color}><title>{label}: ({val(point[0])}, {val(point[1])})</title></circle>
        <text x={Math.min(365, Math.max(28, sx(point[0]) + 7))} y={Math.min(290, Math.max(18, sy(point[1]) - 7))} fill={color} fontSize="13">{label}</text>
      </g>)}
      <text x="375" y="312" textAnchor="end" fontSize="12" fill="currentColor">Re</text><text x="9" y="18" fontSize="12" fill="currentColor">Im</text>
    </svg></div>
    <ul className="pl-vis-legend pl-small">{plotted.map(item => <li key={item.label}><i className="dot" style={{ background: item.color }} />{item.label} ≈ {val(item.point[0])} {item.point[1] < 0 ? '−' : '+'} {val(Math.abs(item.point[1]))}i</li>)}</ul>
    <p className="pl-small pl-muted" aria-live="polite">{radius === 0 ? 'The zero vector has modulus 0 and no defined argument.' : `|${firstName}| ≈ ${val(radius)}; arg(${firstName}) ≈ ${val(argument)} rad (${val(argument * 180 / Math.PI)}°).`} {spec.mode === 'root' ? 'The green vector is the requested root.' : ''}</p>
    {spec.mode === 'power' && <p className="pl-small" aria-live="polite">|z^{power}| ≈ {val(radius ** power)}; arg(z^{power}) ≈ {val(Math.atan2(powered[1], powered[0]))} rad. The angle before reduction is {val(power * argument)} rad.</p>}
    {spec.mode === 'power' && <label className="pl-vis-slider pl-small">Power k <output>k = {power}</output><input type="range" min={1} max={spec.power!} value={power} onChange={event => setPower(Number(event.target.value))} /></label>}
    <div className="pl-vis-controls"><label className="pl-small pl-vis-toggle"><input type="checkbox" checked={showInputs} onChange={event => setShowInputs(event.target.checked)} /> Show given numbers</label>
      <label className="pl-small pl-vis-toggle"><input type="checkbox" checked={showParts} onChange={event => setShowParts(event.target.checked)} /> Show components</label>
      <label className="pl-small pl-vis-toggle"><input type="checkbox" checked={showAngle} onChange={event => setShowAngle(event.target.checked)} /> Show argument</label></div>
    {translated && <p className="pl-small pl-muted">The dashed line shows {spec.mode === 'subtract' ? '−w' : 'w'} translated to the tip of z.</p>}
  </figure>;
}
