import type { ComponentType } from 'react';
import type { VisualSpec } from './spec';
import { VisualBoundary } from './VisualBoundary';

type Views = { [Kind in VisualSpec['kind']]?: ComponentType<{ spec: Extract<VisualSpec, { kind: Kind }> }> };

/** One view per kind. A kind without a view yet shows nothing. */
const VIEWS: Views = {};

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
