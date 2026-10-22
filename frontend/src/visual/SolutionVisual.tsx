import type { ComponentType } from 'react';
import { DefiniteView } from './DefiniteView';
import { IndefiniteView } from './IndefiniteView';
import type { VisualSpec } from './spec';
import { VisualBoundary } from './VisualBoundary';
import { Region2dVisual } from './region2d/Region2dVisual';
import './visual.css';

type Views = { [Kind in VisualSpec['kind']]?: ComponentType<{ spec: Extract<VisualSpec, { kind: Kind }> }> };

/** One view per kind. A kind without a view yet shows nothing. */
const VIEWS: Views = { definite: DefiniteView, indefinite: IndefiniteView, region2d: Region2dVisual };

/** The interactive picture under a worked solution, isolated so a failure hides only itself. */
export function SolutionVisual({ spec }: { spec: VisualSpec }) {
  const View = VIEWS[spec.kind] as ComponentType<{ spec: VisualSpec }> | undefined;
  if (!View) return null;
  return (
    <VisualBoundary>
      <View spec={spec} />
    </VisualBoundary>
  );
}
