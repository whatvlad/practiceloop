/** The types currently supported at all three analytic-geometry levels. */
export const VECTOR_MODES = [
  { id: 'vector-expression', label: 'Vector expressions' },
  { id: 'scalar-expression', label: 'Scalar expressions with vectors' },
  { id: 'vector-length', label: 'Lengths of vector differences' },
  { id: 'perpendicular-parameter', label: 'Perpendicularity and a parameter' },
  { id: 'triangle-angle', label: 'Angles between vectors' },
  { id: 'triangle-area', label: 'Triangle area' },
  { id: 'parallelogram-area', label: 'Parallelogram area' },
  { id: 'tetrahedron-volume', label: 'Tetrahedron volume' },
  { id: 'tetrahedron-height', label: 'Tetrahedron height' },
  { id: 'parallelepiped-area', label: 'Parallelepiped surface area' },
] as const;

export type VectorMode = typeof VECTOR_MODES[number]['id'];
export const VECTOR_MODE_IDS: readonly string[] = VECTOR_MODES.map(mode => mode.id);
