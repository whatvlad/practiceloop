// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { Geometry3dVisual } from './Geometry3dVisual';
import type { Geometry3dSpec } from './spec';

vi.mock('./three/ThreeView', () => ({ default: () => <div data-testid="interactive-scene" /> }));

it('starts interactive 3D automatically near the viewport and releases it when far away', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  let notify!: (visible: boolean) => void;
  class Observer {
    constructor(callback: IntersectionObserverCallback) {
      notify = visible => callback([{ isIntersecting: visible } as IntersectionObserverEntry], this as unknown as IntersectionObserver);
    }
    observe() {}
    disconnect() {}
  }
  vi.stubGlobal('IntersectionObserver', Observer);
  const spec: Geometry3dSpec = {
    kind: 'geometry3d', version: 1, title: 'Triangle', description: 'Given points.',
    points: [{ label: 'A', at: [0, 0, 0], tone: 'given' }], lines: [], faces: [],
  };
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  try {
    await act(async () => root.render(<Geometry3dVisual spec={spec} />));
    expect(host.querySelector('[data-testid="interactive-scene"]')).toBeNull();
    await act(async () => { notify(true); });
    await vi.waitFor(() => expect(host.querySelector('[data-testid="interactive-scene"]')).not.toBeNull());
    await act(async () => { notify(false); });
    expect(host.querySelector('[data-testid="interactive-scene"]')).toBeNull();
    await act(async () => { notify(true); });
    expect(host.querySelector('[data-testid="interactive-scene"]')).not.toBeNull();
  } finally { await act(async () => root.unmount()); host.remove(); vi.unstubAllGlobals(); }
});
