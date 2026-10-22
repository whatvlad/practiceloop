import { lazy, Suspense, useCallback, useMemo, useState } from 'react';
import { Tex } from '../../components/Tex';
import { VisualBoundary } from '../VisualBoundary';
import type { Region2dSpec } from '../spec';
import { compileRegion } from './region';
import { RegionView } from './RegionView';
import { heightScale, surfaceScene } from './surface';
import './region2d.css';

// three.js stays out of the main bundle: this chunk loads only when a 3D visual is shown.
const ThreeView = lazy(() => import('../three/ThreeView'));

/** #113: the region of a double integral in 2D, and the surface z = f over it in 3D. */
export function Region2dVisual({ spec }: { spec: Region2dSpec }) {
  const region = useMemo(() => compileRegion(spec), [spec]);
  const scene = useMemo(() => surfaceScene(region), [region]);
  const scale = heightScale(region);
  const [webgl, setWebgl] = useState(true);
  const unavailable = useCallback(() => setWebgl(false), []);
  const system = spec.system === 'polar' ? 'polar coordinates' : 'Cartesian coordinates';
  const text = `Region of integration in ${system}`;
  return (
    <section className="pl-visual pl-stack pl-gap-4" aria-label="Visualization">
      <div className="pl-small pl-muted">
        <span>{text}: </span>
        <Tex latex={spec.region} />
      </div>
      <RegionView region={region} label={`${text}. The shaded area is the region.`} />
      {webgl && (
        <VisualBoundary>
          <Suspense fallback={<p className="pl-small pl-muted">Loading the 3D view…</p>}>
            <figure className="pl-stack pl-gap-2 pl-m-0">
              <ThreeView scene={scene} label="The surface z = f(x, y) over the region, in 3D" onUnavailable={unavailable} />
              <figcaption className="pl-small pl-muted">
                The surface z = f(x, y) over the region; the integral is the signed volume between it and the plane z = 0.
                {scale !== 1 && ` Heights are drawn ×${scale}.`}
              </figcaption>
            </figure>
          </Suspense>
        </VisualBoundary>
      )}
    </section>
  );
}
