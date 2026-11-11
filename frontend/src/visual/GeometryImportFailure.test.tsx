// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { Geometry3dVisual } from './Geometry3dVisual';
import type { Geometry3dSpec } from './spec';

vi.mock('./three/ThreeView', () => { throw new Error('3D chunk unavailable'); });

it('keeps an honest 2D drawing when the 3D module fails to load', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const errors = vi.spyOn(console, 'error').mockImplementation(() => {});
  const spec: Geometry3dSpec = {
    kind: 'geometry3d', version: 1, title: 'Vector', description: 'Given vector u.',
    points: [], lines: [{ label: 'u', start: [0, 0, 0], end: [1, 1, 0], tone: 'given', arrow: true, dashed: false }], faces: [],
  };
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  try {
    await act(async () => root.render(<Geometry3dVisual spec={spec} />));
    await vi.waitFor(() => expect(host.textContent).toContain('3D could not be loaded'));
    expect(host.querySelector('svg')?.getAttribute('aria-label')).toContain('2D projection');
  } finally { await act(async () => root.unmount()); host.remove(); errors.mockRestore(); }
});
