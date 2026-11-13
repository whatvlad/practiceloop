import { useEffect, useId, useRef, useState } from 'react';
import { useTheme } from '../../theme';
import {
  AmbientLight,
  ArrowHelper,
  BufferAttribute,
  BufferGeometry,
  CanvasTexture,
  Color,
  CylinderGeometry,
  DirectionalLight,
  DoubleSide,
  Group,
  Line,
  LineBasicMaterial,
  LineDashedMaterial,
  LineSegments,
  Mesh,
  MeshBasicMaterial,
  MeshLambertMaterial,
  PerspectiveCamera,
  Scene,
  Sprite,
  SpriteMaterial,
  SphereGeometry,
  Vector3,
  WebGLRenderer,
} from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { axisOrigin, axisTicks, coordinateAxes, geometryViewDirection, type Scene3D } from './geometry';
import './three.css';

/** The 3D view of ADR-006, in its own chunk: loaded by dynamic import only with a 3D visual. */

export function hasWebGL(): boolean {
  try {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('webgl2') ?? canvas.getContext('webgl');
    const available = !!context;
    context?.getExtension?.('WEBGL_lose_context')?.loseContext();
    return available;
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
  objectLabel: string;
  active: Color;
  previous: Color;
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
    objectLabel: token('--ink', '#ffffff'),
    active: new Color(token('--correct', '#56b4e9')),
    previous: new Color(token('--ink-subtle', '#7e7e7e')),
  };
}

/** A text label that always faces the camera; `size` is its height in scene units. */
function labelSprite(text: string, color: string, size: number, font = 'italic 44px serif'): Sprite {
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  canvas.height = 64;
  if (context) context.font = font;
  // Wide enough for the text, in steps of 32 px so short labels share sizes.
  canvas.width = Math.max(64, Math.ceil(((context?.measureText(text).width ?? 0) + 12) / 32) * 32);
  if (context) {
    context.fillStyle = color;
    context.font = font;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, 34);
  }
  const sprite = new Sprite(new SpriteMaterial({ map: new CanvasTexture(canvas), depthTest: false, transparent: true }));
  sprite.scale.set((size * canvas.width) / canvas.height, size, 1);
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
  const hintId = useId();
  const [available] = useState(hasWebGL);
  // The scene reads its colors from the theme tokens, so a theme switch redraws it.
  const theme = useTheme();

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
    renderer.domElement.setAttribute('aria-describedby', hintId);
    renderer.domElement.tabIndex = 0;
    element.prepend(renderer.domElement);

    const scene = new Scene();
    const min = new Vector3(...data.box.min);
    const max = new Vector3(...data.box.max);
    const center = min.clone().add(max).multiplyScalar(0.5);
    const geometryPoints = data.analyticGeometry ? [
      ...(data.marks ?? []).map(point => point.at),
      ...(data.edges ?? []).flatMap(edge => [edge.start, edge.end]),
      ...data.meshes.flatMap(mesh => Array.from({ length: mesh.positions.length / 3 }, (_, i) =>
        [mesh.positions[i * 3], mesh.positions[i * 3 + 1], mesh.positions[i * 3 + 2]] as [number, number, number]),
      ),
      ...coordinateAxes(data.box).flatMap(axis => [axis.from, axis.to]),
    ] : [];
    const radius = data.analyticGeometry && geometryPoints.length
      ? Math.max(...geometryPoints.map(point => new Vector3(...point).distanceTo(center)), 1e-3) * 1.1
      : Math.max(max.clone().sub(min).length() / 2, 1e-3);

    const startWidth = element.clientWidth || 320;
    const camera = new PerspectiveCamera(FOV, startWidth / canvasHeight(startWidth), radius / 100, radius * 20);
    camera.up.set(0, 0, 1);
    // Far enough that the bounding sphere fits the narrower of the two fields of view.
    const halfFov = Math.min(FOV / 2, (Math.atan(Math.tan((FOV * Math.PI) / 360) * camera.aspect) * 180) / Math.PI);
    const distance = (radius / Math.sin((halfFov * Math.PI) / 180)) * 1.02;
    const direction = data.analyticGeometry ? geometryViewDirection(data) : [1.1, -1.7, 1.05] as const;
    const home = center.clone().add(new Vector3(...direction).normalize().multiplyScalar(distance));

    const colors = palette(element);
    scene.add(new AmbientLight(0xffffff, 1.4));
    const light = new DirectionalLight(0xffffff, 1.6);
    light.position.copy(home);
    scene.add(light);

    const disposables: Array<{ dispose(): void }> = [];
    const objectLabels: Array<{ sprite: Sprite; baseScale: Vector3 }> = [];
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
        const tone = mesh.tone === 'active' ? colors.active : mesh.tone === 'previous' ? colors.previous : mesh.tone === 'given' ? colors.edge : mesh.tone === 'floor' ? colors.floor : colors.wall;
        material = new MeshLambertMaterial({ color: tone, side: DoubleSide, transparent: true, opacity: mesh.tone === 'floor' ? 0.35 : mesh.tone === 'previous' ? 0.1 : 0.22, depthWrite: false });
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

    const toneColor = (tone: 'given' | 'active' | 'previous') => tone === 'active' ? colors.active : tone === 'previous' ? colors.previous : colors.edge;
    const segmentGeometry = data.edges?.length ? new CylinderGeometry(1, 1, 1, 8) : null;
    if (segmentGeometry) disposables.push(segmentGeometry);
    const labelledEdges = new Set<string>();
    for (const edge of data.edges ?? []) {
      const start = new Vector3(...edge.start); const end = new Vector3(...edge.end);
      const direction = end.clone().sub(start); const length = direction.length();
      if (edge.arrow && length > 1e-9) {
        const unit = direction.clone().normalize();
        const headLength = Math.min(radius * 0.14, length * 0.3);
        const arrow = new ArrowHelper(unit, start, length, toneColor(edge.tone), headLength, Math.min(radius * 0.075, length * 0.2));
        arrow.name = edge.label; scene.add(arrow); disposables.push(arrow);
        if (segmentGeometry) {
          const material = new MeshBasicMaterial({ color: toneColor(edge.tone) });
          const shaft = new Mesh(segmentGeometry, material);
          const shaftLength = length - headLength;
          shaft.scale.set(radius * 0.008, shaftLength, radius * 0.008);
          shaft.position.copy(start).addScaledVector(unit, shaftLength / 2);
          shaft.quaternion.setFromUnitVectors(new Vector3(0, 1, 0), unit);
          scene.add(shaft); disposables.push(material);
        }
      } else if (segmentGeometry && length > 1e-9) {
        // WebGL lineWidth is often fixed at one pixel, so use slim cylinders
        // for legible, consistent edges and an explicitly dashed altitude.
        const material = new MeshBasicMaterial({ color: toneColor(edge.tone), transparent: true, opacity: edge.tone === 'previous' ? 0.6 : 1 });
        const group = new Group(); group.name = edge.label;
        const count = edge.dashed ? Math.min(24, Math.max(2, Math.ceil(length / (radius * 0.15)))) : 1;
        const directionUnit = direction.clone().normalize();
        for (let i = 0; i < count; i++) {
          const fraction = edge.dashed ? 0.57 / count : 1;
          const partLength = length * fraction;
          const part = new Mesh(segmentGeometry, material);
          const thickness = radius * (edge.tone === 'active' ? 0.012 : 0.007);
          part.scale.set(thickness, partLength, thickness);
          part.position.copy(start).addScaledVector(direction, i / count + fraction / 2);
          part.quaternion.setFromUnitVectors(new Vector3(0, 1, 0), directionUnit);
          group.add(part);
        }
        scene.add(group); disposables.push(material);
      } else {
        const geometry = new BufferGeometry().setFromPoints([start, end]);
        const material = edge.dashed
          ? new LineDashedMaterial({ color: toneColor(edge.tone), dashSize: radius * 0.07, gapSize: radius * 0.04 })
          : new LineBasicMaterial({ color: toneColor(edge.tone), transparent: true, opacity: edge.tone === 'previous' ? 0.55 : 0.9 });
        const line = new Line(geometry, material); line.name = edge.label;
        if (edge.dashed) line.computeLineDistances();
        scene.add(line); disposables.push(geometry, material);
      }
      if (!labelledEdges.has(edge.label) && (edge.arrow || edge.tone === 'active' || data.analyticGeometry)) {
        labelledEdges.add(edge.label);
        const label = labelSprite(edge.label, colors.objectLabel, radius * 0.19, '40px ui-monospace, monospace');
        const labelOffset = new Vector3(...direction).cross(camera.up).normalize().multiplyScalar(radius * 0.08);
        label.position.copy(start.clone().lerp(end, data.analyticGeometry && !edge.arrow && !edge.dashed ? 0.7 : 0.62)).add(labelOffset);
        objectLabels.push({ sprite: label, baseScale: label.scale.clone() });
        disposables.push(label.material.map!, label.material); scene.add(label);
      }
    }
    if (data.marks?.length) {
      const geometry = new SphereGeometry(radius * 0.018, 12, 8); disposables.push(geometry);
      for (const point of data.marks) {
        const material = new MeshBasicMaterial({ color: toneColor(point.tone) });
        const dot = new Mesh(geometry, material); dot.name = point.label; dot.position.set(...point.at);
        scene.add(dot); disposables.push(material);
        const label = labelSprite(point.label, colors.objectLabel, radius * 0.16, '40px ui-monospace, monospace');
        label.position.copy(dot.position).add(new Vector3(radius * 0.07, radius * 0.07, radius * 0.07));
        objectLabels.push({ sprite: label, baseScale: label.scale.clone() });
        disposables.push(label.material.map!, label.material); scene.add(label);
      }
    }

    // Axes through the origin (or the nearest corner of the box), with x, y, z labels.
    const origin = new Vector3(...axisOrigin(data.box));
    const axisColor = data.analyticGeometry ? new Color(colors.label) : colors.axis;
    const axisMaterial = new LineBasicMaterial({ color: axisColor });
    disposables.push(axisMaterial);
    const ends: Array<[string, Vector3, Vector3]> = data.analyticGeometry ? coordinateAxes(data.box).map(
      axis => [axis.name, new Vector3(...axis.from), new Vector3(...axis.to)],
    ) : [
      ['x', new Vector3(min.x, origin.y, origin.z), new Vector3(max.x, origin.y, origin.z)],
      ['y', new Vector3(origin.x, min.y, origin.z), new Vector3(origin.x, max.y, origin.z)],
      ['z', new Vector3(origin.x, origin.y, Math.min(min.z, origin.z)), new Vector3(origin.x, origin.y, max.z + radius * 0.15)],
    ];
    for (const [name, from, to] of ends) {
      if (data.analyticGeometry) {
        const axis = new ArrowHelper(to.clone().sub(from).normalize(), from, to.distanceTo(from), axisColor, radius * 0.09, radius * 0.05);
        axis.name = `axis-${name}`; scene.add(axis); disposables.push(axis);
      } else {
        const geometry = new BufferGeometry().setFromPoints([from, to]);
        disposables.push(geometry);
        scene.add(new Line(geometry, axisMaterial));
      }
      const sprite = labelSprite(name, colors.label, radius * (data.analyticGeometry ? 0.18 : 0.14));
      sprite.position.copy(to).add(to.clone().sub(from).normalize().multiplyScalar(radius * (data.analyticGeometry ? 0.16 : 0.08)));
      if (data.analyticGeometry) objectLabels.push({ sprite, baseScale: sprite.scale.clone() });
      disposables.push(sprite.material.map!, sprite.material);
      scene.add(sprite);
    }
    if (data.analyticGeometry) {
      const zero = labelSprite('0', colors.label, radius * 0.1, '40px ui-monospace, monospace');
      zero.position.set(-radius * 0.08, -radius * 0.08, -radius * 0.08);
      objectLabels.push({ sprite: zero, baseScale: zero.scale.clone() });
      disposables.push(zero.material.map!, zero.material); scene.add(zero);
    }

    // Numeric values along each axis (#127): a short tick mark and its label beside it.
    // x and y ticks point toward −y and −x, z ticks toward both; the default view sees them from that side.
    const tickLength = radius * 0.04;
    const away = { x: new Vector3(0, -1, 0), y: new Vector3(-1, 0, 0), z: new Vector3(-1, -1, 0).normalize() };
    const tickPoints: Vector3[] = [];
    for (const tick of axisTicks(data.box, data.zScale, data.analyticGeometry ? 2 : undefined)) {
      const at = new Vector3(...tick.at);
      tickPoints.push(at, at.clone().addScaledVector(away[tick.axis], tickLength));
      const sprite = labelSprite(tick.label, colors.label, radius * (data.analyticGeometry ? 0.1 : 0.08), '40px ui-monospace, monospace');
      sprite.position.copy(at).addScaledVector(away[tick.axis], Math.max(tickLength * 3, tickLength + sprite.scale.x / 2));
      if (data.analyticGeometry) objectLabels.push({ sprite, baseScale: sprite.scale.clone() });
      disposables.push(sprite.material.map!, sprite.material);
      scene.add(sprite);
    }
    if (tickPoints.length) {
      const geometry = new BufferGeometry().setFromPoints(tickPoints);
      disposables.push(geometry);
      scene.add(new LineSegments(geometry, axisMaterial));
    }

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.copy(center);
    controls.minDistance = radius * 0.6;
    controls.maxDistance = distance * 3;
    const render = () => renderer.render(scene, camera);
    controls.addEventListener('change', render);
    const keyboard = (event: KeyboardEvent) => {
      const offset = camera.position.clone().sub(controls.target);
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') offset.applyAxisAngle(camera.up, event.key === 'ArrowLeft' ? 0.12 : -0.12);
      else if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
        const right = new Vector3().crossVectors(camera.up, offset).normalize();
        offset.applyAxisAngle(right, event.key === 'ArrowUp' ? 0.12 : -0.12);
      } else if (event.key === '+' || event.key === '=') offset.multiplyScalar(0.9);
      else if (event.key === '-' || event.key === '_') offset.multiplyScalar(1.1);
      else return;
      event.preventDefault();
      const size = Math.min(Math.max(offset.length(), controls.minDistance), controls.maxDistance);
      camera.position.copy(controls.target).add(offset.setLength(size));
      controls.update();
    };
    renderer.domElement.addEventListener('keydown', keyboard);
    const lost = (event: Event) => { event.preventDefault(); onUnavailable?.(); };
    renderer.domElement.addEventListener('webglcontextlost', lost);
    reset.current = () => {
      camera.position.copy(home);
      controls.target.copy(center);
      controls.update();
    };

    let lastWidth = 0; let lastHeight = 0;
    const resize = () => {
      const width = element.clientWidth || 320;
      const height = canvasHeight(width);
      if (width === lastWidth && height === lastHeight) return;
      lastWidth = width; lastHeight = height;
      const labelScale = Math.min(2, Math.max(1, 420 / width));
      for (const item of objectLabels) item.sprite.scale.copy(item.baseScale).multiplyScalar(labelScale);
      renderer.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      render();
    };
    // Resizing the canvas changes its observed parent; defer that change until the next frame.
    let resizeFrame: number | null = null;
    const scheduleResize = () => {
      if (resizeFrame !== null) return;
      resizeFrame = window.requestAnimationFrame(() => { resizeFrame = null; resize(); });
    };
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(scheduleResize);
    observer?.observe(element);
    window.addEventListener('resize', scheduleResize);
    camera.position.copy(home);
    controls.update();
    resize();

    return () => {
      observer?.disconnect();
      window.removeEventListener('resize', scheduleResize);
      if (resizeFrame !== null) window.cancelAnimationFrame(resizeFrame);
      renderer.domElement.removeEventListener('keydown', keyboard);
      renderer.domElement.removeEventListener('webglcontextlost', lost);
      controls.dispose();
      for (const item of disposables) item.dispose();
      renderer.forceContextLoss();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [available, data, hintId, label, onUnavailable, theme]);

  if (!available) return null;
  return (
    <div className="pl-visual-3d" ref={host}>
      <div className="pl-visual-3d-bar">
        <span id={hintId} className="pl-small pl-muted">Drag or use arrow keys to rotate; pinch, scroll or use + and - to zoom.</span>
        <button type="button" className="pl-btn pl-btn--ghost pl-btn--sm" onClick={() => reset.current()}>
          Reset view
        </button>
      </div>
    </div>
  );
}
