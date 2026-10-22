/** Scene data for the lazy three.js view (ADR-006). Pure: it never imports three. */

export type Vec3 = [number, number, number];

export interface Mesh3D {
  /** x, y, z per vertex. */
  positions: Float32Array;
  /** Three vertex indices per triangle. */
  indices: Uint32Array;
  /** `surface` is coloured by sign (positive and negative parts); the others are flat. */
  tone: 'surface' | 'wall' | 'floor';
}

export interface Scene3D {
  meshes: Mesh3D[];
  /** Polylines (x, y, z per point) drawn as edges. */
  lines: Float32Array[];
  box: { min: Vec3; max: Vec3 };
}

/**
 * Triangulates an `nu` × `nv` grid over the parameters s, t ∈ [0, 1].
 * A point that is `null` or not finite drops every triangle that touches it,
 * which leaves a gap instead of a spike.
 */
export function gridMesh(nu: number, nv: number, point: (s: number, t: number) => Vec3 | null, tone: Mesh3D['tone'] = 'surface'): Mesh3D {
  const positions = new Float32Array((nu + 1) * (nv + 1) * 3);
  const valid = new Uint8Array((nu + 1) * (nv + 1));
  for (let i = 0; i <= nu; i++) {
    for (let j = 0; j <= nv; j++) {
      const k = i * (nv + 1) + j;
      const p = point(i / nu, j / nv);
      if (p && p.every(Number.isFinite)) {
        positions.set(p, k * 3);
        valid[k] = 1;
      }
    }
  }
  const indices: number[] = [];
  for (let i = 0; i < nu; i++) {
    for (let j = 0; j < nv; j++) {
      const a = i * (nv + 1) + j;
      const b = a + nv + 1;
      if (valid[a] && valid[b] && valid[a + 1]) indices.push(a, b, a + 1);
      if (valid[b] && valid[b + 1] && valid[a + 1]) indices.push(b, b + 1, a + 1);
    }
  }
  return { positions, indices: Uint32Array.from(indices), tone };
}

/** A polyline from points; non-finite points are skipped. */
export function polyline(points: Array<Vec3 | null>): Float32Array {
  return Float32Array.from(points.filter((p): p is Vec3 => !!p && p.every(Number.isFinite)).flat());
}
