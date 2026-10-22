import type { ComponentType } from 'react';
import type { VisualSpec } from './spec';
import { VisualBoundary } from './VisualBoundary';
import { Region2dVisual } from './region2d/Region2dVisual';

type Views = { [Kind in VisualSpec['kind']]?: ComponentType<{ spec: Extract<VisualSpec, { kind: Kind }> }> };

/** One view per kind. A kind without a view yet shows nothing. */
const VIEWS: Views = {
  region2d: Region2dVisual,
};

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
