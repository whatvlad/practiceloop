// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import type { PerspectiveCamera, Scene } from 'three';
import { geometryScene } from './geometry';
import type { Geometry3dSpec } from '../spec';

const captured = vi.hoisted(() => ({ scene: null as Scene | null, camera: null as PerspectiveCamera | null, setSize: vi.fn() }));
vi.mock('three', async original => {
  const real = await original<typeof import('three')>();
  return { ...real, WebGLRenderer: class {
    domElement = document.createElement('canvas');
    setPixelRatio() {}
    setSize(width: number, height: number) { captured.setSize(width, height); }
    render(scene: Scene, camera: PerspectiveCamera) { captured.scene = scene; captured.camera = camera; }
    forceContextLoss() {}
    dispose() {}
  } };
});

it('resizes scenes outside the observer callback and ignores repeated dimensions', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const context = { measureText: () => ({ width: 20 }), fillText: () => {}, font: '', fillStyle: '', textAlign: '', textBaseline: '' };
  const canvas = vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockImplementation(
    ((kind: string) => kind === '2d' ? context : {}) as typeof HTMLCanvasElement.prototype.getContext,
  );
  let notify: ResizeObserverCallback | undefined;
  const frames: FrameRequestCallback[] = [];
  vi.stubGlobal('ResizeObserver', class {
    constructor(callback: ResizeObserverCallback) { notify = callback; }
    observe() {}
    disconnect() {}
  });
  vi.spyOn(window, 'requestAnimationFrame').mockImplementation(callback => { frames.push(callback); return frames.length; });
  vi.spyOn(window, 'cancelAnimationFrame').mockImplementation(() => {});
  captured.setSize.mockClear();
  const spec: Geometry3dSpec = {
    kind: 'geometry3d', version: 1, title: 'Vectors', description: 'Given vector u.',
    points: [],
    lines: [{ label: 'u', start: [0, 0, 0], end: [2, 1, 0], tone: 'given', arrow: true, dashed: false }],
    faces: [],
  };
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  try {
    await act(async () => root.render(<ThreeView scene={geometryScene(spec)} label={spec.description} />));
    expect(captured.setSize).toHaveBeenCalledTimes(1);
    Object.defineProperty(host.querySelector('.pl-visual-3d'), 'clientWidth', { value: 400, configurable: true });
    notify!([], {} as ResizeObserver);
    expect(captured.setSize).toHaveBeenCalledTimes(1);
    frames.shift()!(0);
    expect(captured.setSize).toHaveBeenLastCalledWith(400, 300);
    notify!([], {} as ResizeObserver);
    frames.shift()!(0);
    expect(captured.setSize).toHaveBeenCalledTimes(2);
    vi.stubGlobal('innerHeight', 400);
    window.dispatchEvent(new Event('resize'));
    window.dispatchEvent(new Event('resize'));
    expect(frames).toHaveLength(1);
    frames.shift()!(0);
    expect(captured.setSize).toHaveBeenLastCalledWith(400, 240);
  } finally {
    await act(async () => root.unmount()); host.remove(); canvas.mockRestore();
    vi.unstubAllGlobals(); vi.restoreAllMocks(); captured.setSize.mockClear();
    captured.scene = null; captured.camera = null;
  }
});

import ThreeView from './ThreeView';

it('renders the actual labelled points and arrows in the interactive scene', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const context = { measureText: () => ({ width: 20 }), fillText: () => {}, font: '', fillStyle: '', textAlign: '', textBaseline: '' };
  const canvas = vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockImplementation(
    ((kind: string) => kind === '2d' ? context : {}) as typeof HTMLCanvasElement.prototype.getContext,
  );
  const spec: Geometry3dSpec = {
    kind: 'geometry3d', version: 1, title: 'Vectors', description: 'Given vector u.',
    points: [{ label: 'A', at: [0, 0, 0], tone: 'given' }],
    lines: [{ label: 'u', start: [0, 0, 0], end: [2, 1, 0], tone: 'active', arrow: true, dashed: false }],
    faces: [],
  };
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  try {
    await act(async () => root.render(<ThreeView scene={geometryScene(spec)} label={spec.description} />));
    expect(captured.scene?.getObjectByName('A')).toBeDefined();
    expect(captured.scene?.getObjectByName('u')).toBeDefined();
    for (const axis of ['x', 'y', 'z']) expect(captured.scene?.getObjectByName(`axis-${axis}`)).toBeDefined();
    expect(host.querySelector('canvas')?.getAttribute('aria-label')).toBe(spec.description);
    const hintId = host.querySelector('canvas')?.getAttribute('aria-describedby');
    expect(hintId && document.getElementById(hintId)?.textContent).toContain('arrow keys');
    const before = captured.camera!.position.clone();
    await act(async () => host.querySelector('canvas')!.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft', bubbles: true })));
    expect(captured.camera!.position.equals(before)).toBe(false);
  } finally { await act(async () => root.unmount()); host.remove(); canvas.mockRestore(); captured.scene = null; captured.camera = null; }
});
