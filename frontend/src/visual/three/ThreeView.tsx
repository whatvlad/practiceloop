import { useEffect, useRef, useState } from 'react';
import {
  AmbientLight,
  BufferAttribute,
  BufferGeometry,
  CanvasTexture,
  Color,
  DirectionalLight,
  DoubleSide,
  Line,
  LineBasicMaterial,
  Mesh,
  MeshLambertMaterial,
  PerspectiveCamera,
  Scene,
  Sprite,
  SpriteMaterial,
  Vector3,
  WebGLRenderer,
} from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import type { Scene3D } from './geometry';
import './three.css';

/** The 3D view of ADR-006, in its own chunk: loaded by dynamic import only with a 3D visual. */

export function hasWebGL(): boolean {
  try {
    const canvas = document.createElement('canvas');
    return !!(canvas.getContext('webgl2') ?? canvas.getContext('webgl'));
  } catch {
    return false;
  }
}

interface Palette {
  positive: Color;
  negative: Color;
  floor: Color;
  wall: Color;
  edge: Color;
  axis: Color;
  label: string;
}

function palette(element: Element): Palette {
  const style = getComputedStyle(element);
  const token = (name: string, fallback: string) => style.getPropertyValue(name).trim() || fallback;
  return {
    positive: new Color(token('--correct', '#56b4e9')),
    negative: new Color(token('--incorrect', '#ff8f55')),
    floor: new Color(token('--ink-subtle', '#7e7e7e')),
    wall: new Color(token('--ink-muted', '#a3a3a3')),
    edge: new Color(token('--ink', '#ffffff')),
    axis: new Color(token('--ink-subtle', '#7e7e7e')),
    label: token('--ink-muted', '#a3a3a3'),
  };
}

function labelSprite(text: string, color: string, size: number): Sprite {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 64;
  const context = canvas.getContext('2d');
  if (context) {
    context.fillStyle = color;
    context.font = 'italic 44px serif';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, 32, 34);
  }
  const sprite = new Sprite(new SpriteMaterial({ map: new CanvasTexture(canvas), depthTest: false, transparent: true }));
  sprite.scale.set(size, size, 1);
  return sprite;
}

/** Vertical field of view, in degrees. */
const FOV = 35;

/** Height of the canvas: about 3:4 of its width, never more than 60 % of the viewport. */
function canvasHeight(width: number): number {
  return Math.round(Math.min(width * 0.75, window.innerHeight * 0.6));
}

/**
 * Renders prebuilt meshes and lines with orbit controls: drag to rotate, pinch or wheel
 * to zoom, two fingers or right-drag to pan. Touch is captured only on the canvas, so
 * the page still scrolls outside it. Without WebGL it renders nothing.
 */
export default function ThreeView({ scene: data, label, onUnavailable }: { scene: Scene3D; label: string; onUnavailable?: () => void }) {
  const host = useRef<HTMLDivElement>(null);
  const reset = useRef<() => void>(() => {});
  const [available] = useState(hasWebGL);

  useEffect(() => {
    if (!available) onUnavailable?.();
  }, [available, onUnavailable]);

  useEffect(() => {
    const element = host.current;
    if (!available || !element) return;
    let renderer: WebGLRenderer;
    try {
      renderer = new WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      onUnavailable?.();
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.domElement.setAttribute('role', 'img');
    renderer.domElement.setAttribute('aria-label', label);
    element.prepend(renderer.domElement);

    const scene = new Scene();
    const min = new Vector3(...data.box.min);
    const max = new Vector3(...data.box.max);
    const center = min.clone().add(max).multiplyScalar(0.5);
    const radius = Math.max(max.clone().sub(min).length() / 2, 1e-3);

    const startWidth = element.clientWidth || 320;
    const camera = new PerspectiveCamera(FOV, startWidth / canvasHeight(startWidth), radius / 100, radius * 20);
    camera.up.set(0, 0, 1);
    // Far enough that the bounding sphere fits the narrower of the two fields of view.
    const halfFov = Math.min(FOV / 2, (Math.atan(Math.tan((FOV * Math.PI) / 360) * camera.aspect) * 180) / Math.PI);
    const distance = (radius / Math.sin((halfFov * Math.PI) / 180)) * 1.02;
    const home = center.clone().add(new Vector3(1.1, -1.7, 1.05).normalize().multiplyScalar(distance));

    const colors = palette(element);
    scene.add(new AmbientLight(0xffffff, 1.4));
    const light = new DirectionalLight(0xffffff, 1.6);
    light.position.copy(home);
    scene.add(light);

    const disposables: Array<{ dispose(): void }> = [];
    for (const mesh of data.meshes) {
      const geometry = new BufferGeometry();
      geometry.setAttribute('position', new BufferAttribute(mesh.positions, 3));
      geometry.setIndex(new BufferAttribute(mesh.indices, 1));
      geometry.computeVertexNormals();
      let material: MeshLambertMaterial;
      if (mesh.tone === 'surface') {
        const vertexColors = new Float32Array(mesh.positions.length);
        for (let i = 0; i < mesh.positions.length; i += 3) {
          const tone = mesh.positions[i + 2] < 0 ? colors.negative : colors.positive;
          vertexColors.set([tone.r, tone.g, tone.b], i);
        }
        geometry.setAttribute('color', new BufferAttribute(vertexColors, 3));
        material = new MeshLambertMaterial({ vertexColors: true, side: DoubleSide, transparent: true, opacity: 0.9 });
      } else {
        const tone = mesh.tone === 'floor' ? colors.floor : colors.wall;
        material = new MeshLambertMaterial({ color: tone, side: DoubleSide, transparent: true, opacity: mesh.tone === 'floor' ? 0.35 : 0.22, depthWrite: false });
      }
      disposables.push(geometry, material);
      scene.add(new Mesh(geometry, material));
    }
    const edgeMaterial = new LineBasicMaterial({ color: colors.edge, transparent: true, opacity: 0.8 });
    disposables.push(edgeMaterial);
    for (const points of data.lines) {
      const geometry = new BufferGeometry();
      geometry.setAttribute('position', new BufferAttribute(points, 3));
      disposables.push(geometry);
      scene.add(new Line(geometry, edgeMaterial));
    }

    // Axes through the origin (or the nearest corner of the box), with x, y, z labels.
    const origin = new Vector3(
      Math.min(Math.max(0, min.x), max.x),
      Math.min(Math.max(0, min.y), max.y),
      Math.min(Math.max(0, min.z), max.z),
    );
    const axisMaterial = new LineBasicMaterial({ color: colors.axis });
    disposables.push(axisMaterial);
    const ends: Array<[string, Vector3, Vector3]> = [
      ['x', new Vector3(min.x, origin.y, origin.z), new Vector3(max.x, origin.y, origin.z)],
      ['y', new Vector3(origin.x, min.y, origin.z), new Vector3(origin.x, max.y, origin.z)],
      ['z', new Vector3(origin.x, origin.y, Math.min(min.z, origin.z)), new Vector3(origin.x, origin.y, max.z + radius * 0.15)],
    ];
    for (const [name, from, to] of ends) {
      const geometry = new BufferGeometry().setFromPoints([from, to]);
      disposables.push(geometry);
      scene.add(new Line(geometry, axisMaterial));
      const sprite = labelSprite(name, colors.label, radius * 0.14);
      sprite.position.copy(to).add(to.clone().sub(from).normalize().multiplyScalar(radius * 0.08));
      disposables.push(sprite.material.map!, sprite.material);
      scene.add(sprite);
    }

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.copy(center);
    controls.minDistance = radius * 0.6;
    controls.maxDistance = distance * 3;
    const render = () => renderer.render(scene, camera);
    controls.addEventListener('change', render);
    reset.current = () => {
      camera.position.copy(home);
      controls.target.copy(center);
      controls.update();
    };

    const resize = () => {
      const width = element.clientWidth || 320;
      const height = canvasHeight(width);
      renderer.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      render();
    };
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(resize);
    observer?.observe(element);
    camera.position.copy(home);
    controls.update();
    resize();

    return () => {
      observer?.disconnect();
      controls.dispose();
      for (const item of disposables) item.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [available, data, label, onUnavailable]);

  if (!available) return null;
  return (
    <div className="pl-visual-3d" ref={host}>
      <div className="pl-visual-3d-bar">
        <span className="pl-small pl-muted">Drag to rotate, pinch or scroll to zoom.</span>
        <button type="button" className="pl-btn pl-btn--ghost pl-btn--sm" onClick={() => reset.current()}>
          Reset view
        </button>
      </div>
    </div>
  );
}
