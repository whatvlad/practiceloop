import { lazy, Suspense, useCallback, useMemo, useState } from 'react';
import { Tex } from '../../components/Tex';
import { VisualBoundary } from '../VisualBoundary';
import type { Solid3dSpec } from '../spec';
import { solidScene } from './solid';

// three.js stays out of the main bundle: this chunk loads only when a 3D visual is shown.
const ThreeView = lazy(() => import('../three/ThreeView'));

/** #114: the solid of a triple integral in 3D; the integrand is not shown. */
export function Solid3dVisual({ spec }: { spec: Solid3dSpec }) {
  const scene = useMemo(() => solidScene(spec), [spec]);
  const [webgl, setWebgl] = useState(true);
  const unavailable = useCallback(() => setWebgl(false), []);
  const system = spec.system === 'cylindrical' ? 'cylindrical coordinates' : 'Cartesian coordinates';
  const text = `Solid of integration in ${system}`;
  return (
    <section className="pl-visual pl-stack pl-gap-4" aria-label="Visualization">
      <div className="pl-small pl-muted">
        <span>{text}: </span>
        <Tex latex={spec.solid} />
      </div>
      {webgl && (
        <VisualBoundary>
          <Suspense fallback={<p className="pl-small pl-muted">Loading the 3D view…</p>}>
            <figure className="pl-stack pl-gap-2 pl-m-0">
              <ThreeView scene={scene} label={`${text}, in 3D`} onUnavailable={unavailable} />
              <figcaption className="pl-small pl-muted">
                The solid E between its bottom surface (grey) and its top surface, with the side walls along the edge of the region below it.
              </figcaption>
            </figure>
          </Suspense>
        </VisualBoundary>
      )}
    </section>
  );
}
