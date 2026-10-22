import { useId, useMemo, useState } from 'react';
import { Tex } from '../components/Tex';
import { Axes } from './Axes';
import { compile } from './expression';
import { areaPath, curvePath, format, linear, riemann, simpson, type Rule } from './plot';
import { RangeSlider } from './RangeSlider';
import type { DefiniteSpec } from './spec';
import { useWidth } from './useWidth';

const STEPS = 400;
const RULES: { rule: Rule; name: string }[] = [
  { rule: 'left', name: 'Left' },
  { rule: 'midpoint', name: 'Midpoint' },
  { rule: 'right', name: 'Right' },
];
const PAD = { left: 12, right: 12, top: 12, bottom: 12 };
const tex = (value: number) => format(value).replace('−', '-');

/** y = f(x), the signed area over [a, b], movable bounds and a Riemann sum (ADR-006). */
export function DefiniteView({ spec }: { spec: DefiniteSpec }) {
  const id = useId().replace(/:/g, '');
  const f = useMemo(() => { const run = compile(spec.f); return (x: number) => run({ x }); }, [spec.f]);
  const [lo, hi] = spec.range;
  const step = (hi - lo) / STEPS;
  const [a, setA] = useState(spec.a);
  const [b, setB] = useState(spec.b);
  const [showSum, setShowSum] = useState(false);
  const [n, setN] = useState(8);
  const [rule, setRule] = useState<Rule>('midpoint');
  const [ref, width] = useWidth<HTMLDivElement>();
  const height = Math.round(Math.min(380, Math.max(220, width * 0.6)));
  const sx = linear([lo, hi], [PAD.left, width - PAD.right]);
  const sy = linear(spec.y, [height - PAD.bottom, PAD.top]);
  const original = a === spec.a && b === spec.b;
  const area = useMemo(() => simpson(f, a, b), [f, a, b]);
  const sum = useMemo(() => (showSum ? riemann(f, a, b, n, rule) : null), [f, a, b, n, rule, showSum]);
  const minGap = step;
  // A bound still at its original value keeps its exact label, e.g. π or e.
  const label = (value: number, exact: number, latex: string) => (value === exact ? latex : tex(value));
  return (
    <figure className="pl-vis pl-fade" aria-labelledby={`${id}-title`}>
      <figcaption id={`${id}-title`} className="pl-label">Area under the curve</figcaption>
      <div ref={ref} className="pl-vis-plot">
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img"
          aria-label={`Graph of the integrand for x from ${format(lo)} to ${format(hi)}. The signed area from x = ${format(a)} to x = ${format(b)} is shaded: blue above the x-axis counts as positive, orange below as negative.`}>
          <Axes sx={sx} sy={sy} id={id} />
          <clipPath id={`${id}-above`}><rect x={0} y={0} width={width} height={Math.max(0, sy(0))} /></clipPath>
          <clipPath id={`${id}-below`}><rect x={0} y={sy(0)} width={width} height={Math.max(0, height - sy(0))} /></clipPath>
          <g clipPath={`url(#${id}-plot)`}>
            {sum ? (
              <g className="pl-vis-riemann">
                {sum.parts.map((part, index) => Number.isFinite(part.height) && (
                  <rect key={index} className={part.height >= 0 ? 'pos' : 'neg'} x={sx(part.x0)} width={Math.max(0.5, sx(part.x1) - sx(part.x0))}
                    y={Math.min(sy(0), sy(part.height))} height={Math.abs(sy(part.height) - sy(0))} />
                ))}
              </g>
            ) : (
              <>
                <path className="pl-vis-area pos" d={areaPath(f, sx, sy, a, b)} clipPath={`url(#${id}-above)`} />
                <path className="pl-vis-area neg" d={areaPath(f, sx, sy, a, b)} clipPath={`url(#${id}-below)`} />
              </>
            )}
            <path className="pl-vis-curve" d={curvePath(f, sx, sy)} />
            <line className="pl-vis-bound" x1={sx(a)} x2={sx(a)} y1={PAD.top} y2={height - PAD.bottom} />
            <line className="pl-vis-bound" x1={sx(b)} x2={sx(b)} y1={PAD.top} y2={height - PAD.bottom} />
          </g>
        </svg>
      </div>
      <p className="pl-vis-value" aria-live="polite">
        {original ? (
          <><Tex latex={`\\int_{${spec.aLatex}}^{${spec.bLatex}} f(x)\\,dx = ${spec.value}`} /> <span className="pl-small pl-muted">exact</span></>
        ) : (
          <><Tex latex={`\\int_{${label(a, spec.a, spec.aLatex)}}^{${label(b, spec.b, spec.bLatex)}} f(x)\\,dx \\approx ${tex(area)}`} /> <span className="pl-small pl-muted">approximate (Simpson&apos;s rule)</span></>
        )}
      </p>
      <div className="pl-vis-controls">
        <RangeSlider label="Lower bound a" valueText={`a = ${format(a)}`} display={<Tex latex={`a = ${label(a, spec.a, spec.aLatex)}`} />}
          value={a} min={lo} max={hi} step={step} onChange={value => setA(Math.min(value, b - minGap))} />
        <RangeSlider label="Upper bound b" valueText={`b = ${format(b)}`} display={<Tex latex={`b = ${label(b, spec.b, spec.bLatex)}`} />}
          value={b} min={lo} max={hi} step={step} onChange={value => setB(Math.max(value, a + minGap))} />
        {!original && (
          <button type="button" className="pl-btn pl-btn--secondary pl-btn--sm" onClick={() => { setA(spec.a); setB(spec.b); }}>
            Reset bounds
          </button>
        )}
      </div>
      <div className="pl-vis-controls">
        <label className="pl-small pl-vis-toggle">
          <input type="checkbox" checked={showSum} onChange={event => setShowSum(event.currentTarget.checked)} /> Show a Riemann sum
        </label>
        {sum && (
          <>
            <RangeSlider label="Rectangles n" valueText={`n = ${n}`} value={n} min={1} max={100} step={1} onChange={setN} />
            <div className="pl-vis-choice" role="group" aria-label="Sample point">
              {RULES.map(option => (
                <button key={option.rule} type="button" aria-pressed={rule === option.rule} onClick={() => setRule(option.rule)}>{option.name}</button>
              ))}
            </div>
            <p className="pl-small pl-m-0" aria-live="polite">
              {RULES.find(option => option.rule === rule)?.name} sum with n = {n}: ≈ {format(sum.sum, 4)}
              <span className="pl-muted"> (integral ≈ {format(area, 4)})</span>
            </p>
          </>
        )}
      </div>
    </figure>
  );
}
