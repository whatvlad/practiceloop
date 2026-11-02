import { useState } from 'react';
import { algebraSections, analysisSections } from '../data/curriculum';
import { Link } from '../router';

const PRACTICE: Record<string, { topic: string; scope: string }> = {
  'Algebraic expressions': { topic: 'algebraic-expressions', scope: 'Selected radical simplification and denominator rationalization' },
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
  'Complex modulus': { topic: 'complex-numbers', scope: 'Modulus of a complex number' },
  'Sum of quadratic roots': { topic: 'fundamental-theorem-algebra', scope: 'Quadratic root sums' },
  'Polynomial divisibility and remainders': { topic: 'polynomial-division', scope: 'Selected polynomial remainders and quotients' },
  'Partial fractions': { topic: 'partial-fractions', scope: 'Selected real partial fractions' },
  Combinations: { topic: 'combinations', scope: 'Binomial coefficients' },
  'Basic integrals': { topic: 'basic-integrals', scope: 'Selected basic integrals' },
  Substitution: { topic: 'substitution', scope: 'Selected substitution integrals' },
  'Integration by parts': { topic: 'integration-by-parts', scope: 'Selected integration by parts' },
  'Rational functions': { topic: 'rational-functions', scope: 'Selected rational integrals' },
  'Trigonometric integrals': { topic: 'trigonometric-integrals', scope: 'Selected trigonometric integrals' },
  'Definite integrals': { topic: 'definite-integrals', scope: 'Selected definite integrals' },
  'Improper integrals': { topic: 'improper-integrals', scope: 'Selected improper integrals' },
  'Double integrals': { topic: 'double-integrals', scope: 'Selected double integrals' },
  'Triple integrals': { topic: 'triple-integrals', scope: 'Selected triple integrals' },
  Derivatives: { topic: 'derivatives', scope: 'Selected derivatives' },
  'Partial derivatives': { topic: 'partial-derivatives', scope: 'Selected partial derivatives' },
  'Functions and sequences': { topic: 'functions-and-sequences', scope: 'A selected sequence' },
  'Limits and continuity': { topic: 'limits-and-continuity', scope: 'A removable limit' },
  Series: { topic: 'series', scope: 'A geometric series' },
  'Multivariable functions': { topic: 'multivariable-functions', scope: 'A selected partial derivative' },
  'Differential equations': { topic: 'differential-equations', scope: 'A selected initial-value problem' },
};

export function CurriculumPage() {
  const [area, setArea] = useState<'algebra' | 'analysis'>('algebra');
  const sections = area === 'algebra' ? algebraSections : analysisSections;

  return (
    <main id="main" tabIndex={-1} className="pl-wrap pl-app-main">
      <div className="pl-label">Curriculum</div>
      <h1 className="pl-display-md pl-page-title">Explore mathematics</h1>
      <p className="pl-muted">Choose an area and a problem type. Some exercises are available; others are in development.</p>
      <div className="pl-chips" role="group" aria-label="Area">
        <button type="button" className="pl-chip" aria-pressed={area === 'algebra'} onClick={() => setArea('algebra')}>Algebra</button>
        <button type="button" className="pl-chip" aria-pressed={area === 'analysis'} onClick={() => setArea('analysis')}>Mathematical Analysis</button>
      </div>
      <section className="pl-card pl-mt-4" aria-labelledby="ready-to-practise">
        <h2 id="ready-to-practise" className="pl-h-lg">Ready to practise</h2>
        <p className="pl-muted">Choose an available exercise to start practising.</p>
        <ul>
          {sections.flatMap(section => section.types).filter(type => PRACTICE[type.name]).map(type => (
            <li key={type.name}>
              <Link to={`/dashboard?area=${area === 'algebra' ? 'algebra' : 'mathematical-analysis'}&topic=${PRACTICE[type.name].topic}`}>{PRACTICE[type.name].scope}</Link>
            </li>
          ))}
        </ul>
      </section>
      <div className="pl-stack pl-gap-4 pl-mt-4">
        {sections.map(section => (
          <details className="pl-card" key={section.name}>
            <summary className="pl-h-lg">{section.name} <span className="pl-small pl-muted">— {section.types.some(type => PRACTICE[type.name]) ? 'Selected problems available' : 'In develop'}</span></summary>
            <div className="pl-stack pl-gap-3 pl-mt-4">
              {section.types.map(type => (
                <details className="pl-card" key={type.name}>
                  <summary className="pl-h-md">{type.name} <span className="pl-small pl-muted">— {PRACTICE[type.name] ? 'Selected problems available · In develop' : 'In develop'}</span></summary>
                  <p className="pl-muted">{type.description}</p>
                  {type.subtypes && <ul>{type.subtypes.map(subtype => <li key={subtype}>{subtype}</li>)}</ul>}
                  {PRACTICE[type.name] ? <div><p>{PRACTICE[type.name].scope}</p><Link className="pl-btn pl-btn--primary" to={`/dashboard?area=${area === 'algebra' ? 'algebra' : 'mathematical-analysis'}&topic=${PRACTICE[type.name].topic}`}>Practice</Link></div> : <p className="pl-display-md" role="status">In develop</p>}
                </details>
              ))}
            </div>
          </details>
        ))}
      </div>
    </main>
  );
}
