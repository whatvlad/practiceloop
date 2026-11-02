export interface CurriculumType {
  name: string;
  description: string;
  pdfExercises: number[];
  subtypes?: string[];
}

export interface CurriculumSection {
  name: string;
  types: CurriculumType[];
}

export const algebraSections: CurriculumSection[] = [
  { name: 'Algebraic expressions and the binomial theorem', types: [
    { name: 'Algebraic expressions', description: 'Simplify expressions and rationalize denominators.', pdfExercises: [1, 2, 3], subtypes: ['Simplification', 'Arithmetic', 'Rationalizing denominators'] },
    { name: 'Binomial theorem', description: 'Expand powers and determine terms or coefficients.', pdfExercises: [4, 5, 6, 7], subtypes: ['Binomial expansions', 'Coefficients', 'Numerical applications', 'Finding the exponent'] },
  ] },
  { name: 'Matrix operations', types: [
    { name: 'Matrix arithmetic', description: 'Add, multiply and transpose compatible matrices.', pdfExercises: [8, 9], subtypes: ['Operations and dimensions', 'Commuting matrices'] },
    { name: 'Matrix properties', description: 'Investigate orthogonal, symmetric and other special matrices.', pdfExercises: [10, 11], subtypes: ['Orthogonality and symmetry', 'Matrix identities and counterexamples'] },
    { name: 'Matrix equations', description: 'Find unknown matrices from equations and products.', pdfExercises: [12, 13], subtypes: ['Equations with transposes', 'Equations involving products'] },
  ] },
  { name: 'Determinants, inverses and rank', types: [
    { name: 'Determinant properties', description: 'Use determinant rules for transformed matrices.', pdfExercises: [14, 15], subtypes: ['Row and column operations', 'Powers, multiples and transposes'] },
    { name: 'Evaluating determinants', description: 'Expand and calculate determinants, including with parameters.', pdfExercises: [16, 17, 18], subtypes: ['Laplace expansion', 'Numerical determinants', 'Parameterized determinants'] },
    { name: 'Matrix invertibility', description: 'Determine when a parameterized matrix is invertible.', pdfExercises: [19] },
    { name: 'Inverse matrices', description: 'Find an inverse matrix using the selected method.', pdfExercises: [20, 21], subtypes: ['Cofactors', 'Elementary row operations'] },
    { name: 'Equations with inverses', description: 'Solve or justify identities involving inverse matrices.', pdfExercises: [22, 23, 24, 25], subtypes: ['Matrix equations', 'Invertibility and identities'] },
    { name: 'Matrix rank', description: 'Find ranks and examine rank statements.', pdfExercises: [26, 27, 28], subtypes: ['Calculating rank', 'Rank with parameters', 'Counterexamples'] },
  ] },
  { name: 'Systems of linear equations', types: [
    { name: 'Consistency of systems', description: 'Determine whether a linear system has solutions.', pdfExercises: [29] },
    { name: 'Cramer’s rule', description: 'Find unknowns in a system using determinants.', pdfExercises: [30] },
    { name: 'Gaussian elimination', description: 'Solve a system by elementary row operations.', pdfExercises: [31, 40], subtypes: ['Systems of equations', 'Augmented matrices'] },
    { name: 'Inverse-matrix method', description: 'Solve a system using the inverse coefficient matrix.', pdfExercises: [32] },
    { name: 'Applications of linear systems', description: 'Form and solve systems from given conditions.', pdfExercises: [33, 34, 35], subtypes: ['Averages', 'Circle equations', 'Linear combinations'] },
    { name: 'Systems with parameters', description: 'Study the number and nature of solutions.', pdfExercises: [36, 37, 38, 39], subtypes: ['Solution counts', 'Parameterized systems', 'Augmented matrices'] },
  ] },
  { name: 'Complex numbers', types: [
    { name: 'Complex arithmetic and equations', description: 'Calculate with complex numbers and solve equations.', pdfExercises: [41, 42], subtypes: ['Arithmetic', 'Equations'] },
    { name: 'Complex modulus', description: 'Calculate the modulus of a complex number.', pdfExercises: [] },
    { name: 'Complex-plane geometry', description: 'Interpret complex numbers and modulus conditions geometrically.', pdfExercises: [43, 44], subtypes: ['Points and triangles', 'Modulus loci'] },
    { name: 'Polar and exponential forms', description: 'Express complex numbers in trigonometric or exponential form.', pdfExercises: [45] },
    { name: 'De Moivre’s formula', description: 'Use polar form to calculate powers.', pdfExercises: [46] },
    { name: 'Modulus and argument conditions', description: 'Solve and depict conditions involving modulus and argument.', pdfExercises: [47, 48], subtypes: ['Combined conditions', 'Argument loci'] },
    { name: 'Complex roots', description: 'Find and plot roots in the complex plane.', pdfExercises: [49] },
    { name: 'Complex-number identities', description: 'Use complex numbers to justify identities.', pdfExercises: [50] },
    { name: 'Complex polynomial equations', description: 'Solve equations and investigate conjugate roots.', pdfExercises: [51, 52, 53], subtypes: ['Equations', 'Conjugate roots', 'Proofs and counterexamples'] },
  ] },
  { name: 'Polynomials and partial fractions', types: [
    { name: 'Sum of quadratic roots', description: 'Find the sum of the roots of a quadratic polynomial.', pdfExercises: [] },
    { name: 'Rational polynomial roots', description: 'List candidates and find rational roots.', pdfExercises: [54, 55], subtypes: ['Possible roots', 'Finding rational roots'] },
    { name: 'Real and complex roots', description: 'Find all roots, including when one root is known.', pdfExercises: [56, 57], subtypes: ['All roots', 'Using a known root'] },
    { name: 'Polynomial factorization', description: 'Factor a polynomial into irreducible real factors.', pdfExercises: [58] },
    { name: 'Partial fractions', description: 'Set up or calculate real partial-fraction decompositions.', pdfExercises: [59, 60], subtypes: ['Decomposition form', 'Finding coefficients'] },
    { name: 'Polynomial divisibility and remainders', description: 'Use divisibility and remainder conditions to find values.', pdfExercises: [61, 62, 63], subtypes: ['Finding coefficients', 'Divisibility', 'Remainders'] },
  ] },
  { name: 'Eigenvalues and eigenvectors', types: [
    { name: 'Eigenvalues and eigenvectors', description: 'Find eigenvalues and their corresponding eigenvectors.', pdfExercises: [64, 65] },
    { name: 'Powers of triangular matrices', description: 'Use triangular structure to find matrix powers.', pdfExercises: [66] },
    { name: 'Matrices from eigenvectors', description: 'Determine matrices from prescribed eigenvector information.', pdfExercises: [67, 68] },
    { name: 'Diagonalization', description: 'Diagonalize a matrix when possible.', pdfExercises: [69, 70] },
    { name: 'Similar matrices', description: 'Assess statements about similar matrices.', pdfExercises: [71] },
  ] },
  { name: 'Analytic geometry', types: [
    { name: 'Vector operations', description: 'Calculate with vectors and use their geometric properties.', pdfExercises: [72, 73, 74], subtypes: ['Vector products', 'Triangles', 'Lengths and angles'] },
    { name: 'Collinearity and orthogonality', description: 'Determine collinear or perpendicular vectors and points.', pdfExercises: [75, 76, 77], subtypes: ['Collinear points', 'Collinear vectors', 'Perpendicular unit vectors'] },
    { name: 'Areas, volumes and heights', description: 'Use vectors to calculate geometric measurements.', pdfExercises: [78, 79] },
    { name: 'Equations of planes', description: 'Find plane equations from points and geometric conditions.', pdfExercises: [80] },
    { name: 'Equations of lines', description: 'Find line equations from points, directions and constraints.', pdfExercises: [81] },
    { name: 'Intersections and containing planes', description: 'Find intersections and planes containing lines or points.', pdfExercises: [82, 83, 84] },
    { name: 'Vectors from geometric conditions', description: 'Find vector coordinates from plane, direction and volume conditions.', pdfExercises: [85] },
    { name: 'Distances', description: 'Calculate distances between points, lines and planes.', pdfExercises: [86] },
    { name: 'Equidistant planes', description: 'Find a plane subject to distance and parallelism conditions.', pdfExercises: [87] },
    { name: 'Angles', description: 'Calculate angles between lines or planes.', pdfExercises: [88, 89], subtypes: ['Angles between lines', 'Angles between planes'] },
    { name: 'Geometric parameter problems', description: 'Find parameters for positional relationships and intersections.', pdfExercises: [90, 91] },
    { name: 'Projections', description: 'Find orthogonal and directional projections.', pdfExercises: [92, 93], subtypes: ['Orthogonal projections', 'Directional projections'] },
    { name: 'Position relative to a plane', description: 'Decide whether points lie on the same side of a plane.', pdfExercises: [94] },
    { name: 'Reflections', description: 'Reflect a point across a line or plane.', pdfExercises: [95, 96], subtypes: ['Reflection across a line', 'Reflection across a plane'] },
    { name: 'Geometric statements', description: 'Evaluate vector and spatial-geometry statements.', pdfExercises: [97] },
  ] },
  { name: 'Combinatorics', types: [
    { name: 'Combinations', description: 'Count selections without regard to order.', pdfExercises: [] },
  ] },
];

export const analysisSections: CurriculumSection[] = [
  { name: 'Integrals', types: [
    { name: 'Basic integrals', description: 'Find elementary antiderivatives.', pdfExercises: [] },
    { name: 'Substitution', description: 'Apply a substitution to an integral.', pdfExercises: [] },
    { name: 'Integration by parts', description: 'Apply integration by parts.', pdfExercises: [] },
    { name: 'Rational functions', description: 'Integrate rational expressions.', pdfExercises: [] },
    { name: 'Trigonometric integrals', description: 'Integrate trigonometric expressions.', pdfExercises: [] },
    { name: 'Definite integrals', description: 'Evaluate integrals over an interval.', pdfExercises: [] },
    { name: 'Improper integrals', description: 'Study or calculate improper integrals.', pdfExercises: [] },
    { name: 'Double integrals', description: 'Evaluate integrals over planar regions.', pdfExercises: [] },
    { name: 'Triple integrals', description: 'Evaluate integrals over spatial regions.', pdfExercises: [] },
  ] },
  { name: 'Differentiation', types: [
    { name: 'Derivatives', description: 'Differentiate functions of one variable.', pdfExercises: [] },
    { name: 'Partial derivatives', description: 'Differentiate functions of several variables.', pdfExercises: [] },
  ] },
  { name: 'Further analysis', types: [
    { name: 'Functions and sequences', description: 'Study functions and sequences.', pdfExercises: [] },
    { name: 'Limits and continuity', description: 'Evaluate limits and examine continuity.', pdfExercises: [] },
    { name: 'Series', description: 'Study and calculate series.', pdfExercises: [] },
    { name: 'Multivariable functions', description: 'Study functions of several variables.', pdfExercises: [] },
    { name: 'Differential equations', description: 'Solve differential equations.', pdfExercises: [] },
  ] },
];
