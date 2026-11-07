/** The public navigation groups; a missing topic is planned, not selectable. */
export interface AlgebraGroup {
  title: string;
  items: { title: string; topic?: string; note?: string }[];
}

export const algebraGroups: AlgebraGroup[] = [
  { title: 'Matrices', items: [
    { title: 'Matrix operations', topic: 'matrix-operations' },
    { title: 'Determinants', topic: 'determinants' },
    { title: 'Inverse matrices', topic: 'inverse-matrices' },
    { title: 'Matrix rank', topic: 'matrix-rank' },
    { title: 'Systems of linear equations', topic: 'linear-systems' },
    { title: 'Matrix basics', topic: 'matrices' },
  ] },
  { title: 'Complex numbers', items: [
    { title: 'Complex arithmetic and equations', topic: 'complex-arithmetic', note: 'Combined practice' },
    { title: 'Complex numbers', topic: 'complex-numbers' },
    { title: 'Polar form, powers and roots', topic: 'complex-polar-form', note: 'Combined practice' },
  ] },
  { title: 'Polynomials', items: [
    { title: 'Division, remainders and divisibility', topic: 'polynomial-division', note: 'Combined practice' },
    { title: 'Roots and factors', topic: 'polynomial-roots' },
    { title: 'Fundamental theorem of algebra', topic: 'fundamental-theorem-algebra' },
    { title: 'Partial fractions', topic: 'partial-fractions' },
    { title: 'Polynomial operations' },
  ] },
  { title: 'Eigenvalues and eigenvectors', items: [
    { title: 'Eigenvalues and eigenvectors', topic: 'eigenvalues', note: 'Combined practice' },
    { title: 'Diagonalization' },
    { title: 'Matrix powers' },
  ] },
  { title: 'Analytic geometry', items: [
    { title: 'Vectors, areas and volumes', topic: 'vectors', note: 'Combined practice' },
    { title: 'Lines and planes', topic: 'lines-and-planes', note: 'Combined practice' },
    { title: 'Vector operations' },
    { title: 'Lengths and angles' },
    { title: 'Distances and intersections' },
    { title: 'Projections and reflections' },
  ] },
];
