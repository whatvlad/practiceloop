import { useState } from 'react';
import { algebraSections, analysisSections, probabilitySections } from '../data/curriculum';
import { algebraGroups } from '../data/algebraGroups';
import { Link } from '../router';

const PRACTICE: Record<string, { topic: string; scope: string }> = {
  'Events and counting': { topic: 'probability-events', scope: 'Use equally likely outcomes, complements, event operations, counting and independence.' },
  'Conditional probability and Bayes': { topic: 'conditional-probability', scope: 'Use conditional tables, replacement rules, total probability, Bayes and probability trees.' },
  'Discrete random variables': { topic: 'discrete-random-variables', scope: 'Normalize finite laws, read CDFs, identify supports and transform variables.' },
  'Standard discrete distributions': { topic: 'discrete-distributions', scope: 'Calculate Bernoulli, binomial, geometric, hypergeometric and Poisson probabilities.' },
  'Continuous distributions': { topic: 'continuous-distributions', scope: 'Work with uniform, polynomial, exponential and normal distributions and supplied tables.' },
  'Moments and joint distributions': { topic: 'moments-joint-distributions', scope: 'Find moments, marginals, conditionals, covariance, correlation and independence.' },
  'Descriptive statistics': { topic: 'descriptive-statistics', scope: 'Summarize small datasets, frequencies, quartiles, spread, correlation and least squares.' },
  'Confidence intervals': { topic: 'confidence-intervals', scope: 'Construct mean, proportion, paired and independent-mean confidence intervals.' },
  'Hypothesis tests': { topic: 'hypothesis-tests', scope: 'Use z, t, proportion, paired and independent-mean tests with stated assumptions.' },
  'Algebraic expressions': { topic: 'algebraic-expressions', scope: 'Selected radical simplification and denominator rationalization' },
  'Matrix arithmetic': { topic: 'matrix-operations', scope: 'Combinations with transposes, products and AB − BA' },
  'Determinant properties': { topic: 'determinants', scope: 'Determinants after scaling, powers and row operations' },
  'Evaluating determinants': { topic: 'determinants', scope: '3 × 3 and 4 × 4 determinants by Laplace expansion' },
  'Matrix invertibility': { topic: 'determinants', scope: 'The parameter value that makes a matrix singular' },
  'Inverse matrices': { topic: 'inverse-matrices', scope: 'Entries of 2 × 2 and 3 × 3 inverse matrices' },
  'Equations with inverses': { topic: 'inverse-matrices', scope: 'Matrix equations AX = C and XA = C' },
  'Matrix rank': { topic: 'matrix-rank', scope: 'Rank by row reduction' },
  'Consistency of systems': { topic: 'matrix-rank', scope: 'Free parameters of a consistent system' },
  'Cramer’s rule': { topic: 'linear-systems', scope: 'One unknown of a 2 × 2 or 3 × 3 system' },
  'Gaussian elimination': { topic: 'linear-systems', scope: 'Systems with three or four unknowns' },
  'Systems with parameters': { topic: 'linear-systems', scope: 'Parameter values giving nonzero solutions' },
  'Complex arithmetic and equations': { topic: 'complex-arithmetic', scope: 'Products, quotients and linear equations, answered as a + bi' },
  'Complex modulus': { topic: 'complex-numbers', scope: 'Modulus of a complex number' },
  'Polar and exponential forms': { topic: 'complex-polar-form', scope: 'Principal arguments' },
  'De Moivre’s formula': { topic: 'complex-polar-form', scope: 'Powers through the trigonometric form' },
  'Complex roots': { topic: 'complex-polar-form', scope: 'The n-th root with the smallest argument' },
  'Complex polynomial equations': { topic: 'complex-arithmetic', scope: 'Square roots and quadratic equations' },
  'Sum of quadratic roots': { topic: 'fundamental-theorem-algebra', scope: 'Quadratic root sums' },
  'Polynomial divisibility and remainders': { topic: 'polynomial-division', scope: 'Remainders, quotients, remainder conditions and divisibility' },
  'Eigenvalues and eigenvectors': { topic: 'eigenvalues', scope: 'Eigenvalues from the characteristic equation or an eigenvector' },
  'Powers of triangular matrices': { topic: 'eigenvalues', scope: 'Eigenvalues of a power of a triangular matrix' },
  'Matrices from eigenvectors': { topic: 'eigenvalues', scope: 'Entries of a matrix with given eigenpairs' },
  Diagonalization: { topic: 'eigenvalues', scope: 'Matrix powers by diagonalization' },
  'Vector operations': { topic: 'vectors', scope: 'Triple products and angles of triangles' },
  'Areas, volumes and heights': { topic: 'vectors', scope: 'Triangle areas, tetrahedron volumes and heights' },
  Distances: { topic: 'lines-and-planes', scope: 'Point to plane and between parallel planes' },
  Angles: { topic: 'lines-and-planes', scope: 'Angles between planes' },
  'Intersections and containing planes': { topic: 'lines-and-planes', scope: 'The intersection of a line and a plane' },
  Reflections: { topic: 'lines-and-planes', scope: 'Reflection of a point in a plane' },
  'Binomial theorem': { topic: 'binomial-theorem', scope: 'Coefficients, constant terms and the exponent' },
  'Rational polynomial roots': { topic: 'polynomial-roots', scope: 'The largest rational root' },
  'Real and complex roots': { topic: 'polynomial-roots', scope: 'The real root when a complex root is known' },
  'Polynomial factorization': { topic: 'polynomial-roots', scope: 'The irreducible quadratic factor of a cubic' },
  'Partial fractions': { topic: 'partial-fractions', scope: 'Real partial fractions, including repeated and quadratic factors' },
  Combinations: { topic: 'combinations', scope: 'Binomial coefficients' },
  'Basic integrals': { topic: 'basic-integrals', scope: 'Selected basic integrals' },
  Substitution: { topic: 'substitution', scope: 'Selected substitution integrals' },
  'Integration by parts': { topic: 'integration-by-parts', scope: 'Selected integration by parts' },
  'Rational functions': { topic: 'rational-functions', scope: 'Selected rational integrals' },
  'Trigonometric integrals': { topic: 'trigonometric-integrals', scope: 'Selected trigonometric integrals' },
  'Definite integrals': { topic: 'definite-integrals', scope: 'Selected definite integrals' },
  'Improper integrals': { topic: 'improper-integrals', scope: 'Convergence criteria, power and exponential tails, comparison and applications' },
  'Double integrals': { topic: 'double-integrals', scope: 'Cartesian and polar regions with bounds and Jacobian factors' },
  'Triple integrals': { topic: 'triple-integrals', scope: 'Cartesian and cylindrical regions with iterated bounds' },
  Derivatives: { topic: 'derivatives', scope: 'Selected derivatives' },
  'Partial derivatives': { topic: 'partial-derivatives', scope: 'Partial and higher derivatives, coordinate changes and Jacobians' },
  'Functions and sequences': { topic: 'functions-and-sequences', scope: 'Domains, parity, composition, inverses, monotonicity, bounds and sequence limits' },
  'Limits and continuity': { topic: 'limits-and-continuity', scope: 'Finite and infinite limits, one-sided limits, asymptotes, continuity and certified bisection' },
  'Differential calculus': { topic: 'differential-calculus', scope: 'Derivative definition, tangents, differentials, mean value theorem, extrema and optimization' },
  Series: { topic: 'series', scope: 'Convergence tests, power-series intervals, Taylor and Maclaurin expansions' },
  'Multivariable functions': { topic: 'multivariable-functions', scope: 'Domains in R²/R³, gradients, directional derivatives, differentials and optimization' },
  'Differential equations': { topic: 'differential-equations', scope: 'Separable, first-order linear, second-order linear and Laplace initial-value problems' },
};

export function CurriculumPage({ guest = false }: { guest?: boolean }) {
  const [area, setArea] = useState<'algebra' | 'analysis' | 'probability'>('algebra');
  const sections = area === 'algebra' ? algebraSections : area === 'analysis' ? analysisSections : probabilitySections;
  const practiceArea = area === 'algebra' ? 'algebra' : area === 'analysis' ? 'mathematical-analysis' : 'probability-statistics';

  return (
    <main id="main" tabIndex={-1} className="pl-wrap pl-app-main">
      <div className="pl-label">Curriculum</div>
      <h1 className="pl-display-md pl-page-title">Explore mathematics</h1>
      <p className="pl-muted">Choose an area and a problem type. Some exercises are available; others are in development.</p>
      {guest && <p className="pl-muted">Exercises need a free account. <Link to="/demo">Try a demo problem without signing in</Link>.</p>}
      <div className="pl-chips" role="group" aria-label="Area">
        <button type="button" className="pl-chip" aria-pressed={area === 'algebra'} onClick={() => setArea('algebra')}>Algebra</button>
        <button type="button" className="pl-chip" aria-pressed={area === 'analysis'} onClick={() => setArea('analysis')}>Mathematical Analysis</button>
        <button type="button" className="pl-chip" aria-pressed={area === 'probability'} onClick={() => setArea('probability')}>Probability and Statistics</button>
      </div>
      <section className="pl-card pl-mt-4" aria-labelledby="ready-to-practise">
        <h2 id="ready-to-practise" className="pl-h-lg">Ready to practise</h2>
        <p className="pl-muted">Choose an available exercise to start practising.</p>
        <ul>
          {area === 'algebra' ? algebraGroups.flatMap(group => group.items).filter(item => item.topic).map(item => (
            <li key={item.topic}><Link to={`/dashboard?area=algebra&topic=${item.topic}`}>{item.title}</Link>{item.note && ` — ${item.note}`}</li>
          )) : sections.flatMap(section => section.types).filter(type => PRACTICE[type.name]).map(type => (
            <li key={type.name}>
              <Link to={`/dashboard?area=${practiceArea}&topic=${PRACTICE[type.name].topic}`}>{PRACTICE[type.name].scope}</Link>
            </li>
          ))}
        </ul>
      </section>
      <div className="pl-stack pl-gap-4 pl-mt-4">
        {area === 'algebra' ? algebraGroups.map(group => (
          <details className="pl-card" key={group.title}>
            <summary className="pl-h-lg">{group.title}</summary>
            <ul>
              {group.items.map(item => <li key={item.title}>
                {item.topic ? <Link to={`/dashboard?area=algebra&topic=${item.topic}`}>{item.title}</Link> : item.title}
                <span className="pl-small pl-muted"> — {item.topic ? item.note ?? 'Available' : 'In develop'}</span>
              </li>)}
            </ul>
          </details>
        )) : sections.map(section => (
          <details className="pl-card" key={section.name}>
            <summary className="pl-h-lg">{section.name} <span className="pl-small pl-muted">— {section.types.some(type => PRACTICE[type.name]) ? 'Selected problems available' : 'In develop'}</span></summary>
            <div className="pl-stack pl-gap-3 pl-mt-4">
              {section.types.map(type => (
                <details className="pl-card" key={type.name}>
                  <summary className="pl-h-md">{type.name} <span className="pl-small pl-muted">— {PRACTICE[type.name] ? 'Selected problems available · In develop' : 'In develop'}</span></summary>
                  <p className="pl-muted">{type.description}</p>
                  {type.subtypes && <ul>{type.subtypes.map(subtype => <li key={subtype}>{subtype}</li>)}</ul>}
                  {PRACTICE[type.name] ? <div><p>{PRACTICE[type.name].scope}</p><Link className="pl-btn pl-btn--primary" to={`/dashboard?area=${practiceArea}&topic=${PRACTICE[type.name].topic}`}>Practice</Link></div> : <p className="pl-display-md" role="status">In develop</p>}
                </details>
              ))}
            </div>
          </details>
        ))}
      </div>
    </main>
  );
}
