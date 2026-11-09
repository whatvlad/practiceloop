// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it } from 'vitest';
import { CurriculumPage } from './CurriculumPage';
import { algebraSections, probabilitySections } from '../data/curriculum';

it('includes every numbered PDF exercise exactly once and keeps inverse methods together', () => {
  const types = algebraSections.flatMap(section => section.types);
  const numbers = types.flatMap(type => type.pdfExercises).sort((a, b) => a - b);
  expect(numbers).toEqual(Array.from({ length: 97 }, (_, i) => i + 1));
  const inverse = types.find(type => type.name === 'Inverse matrices');
  expect(inverse?.subtypes).toEqual(['Cofactors', 'Elementary row operations']);
  expect(inverse?.pdfExercises).toEqual([20, 21]);
});

it('shows both areas, descriptions, subtypes and an inactive placeholder', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const element = document.createElement('div');
  document.body.append(element);
  const root = createRoot(element);
  await act(async () => root.render(<CurriculumPage />));
  expect(element.textContent).toContain('Algebra');
  expect(element.textContent).toContain('Mathematical Analysis');
  expect(element.querySelector('section[aria-labelledby="ready-to-practise"]')).toBeNull();
  const ready = element;
  expect(ready.querySelector('a[href="/dashboard?area=algebra&topic=determinants"]')).not.toBeNull();
  expect(ready.querySelector('a[href="/dashboard?area=algebra&topic=linear-systems"]')).not.toBeNull();
  expect(ready.querySelector('a[href="/dashboard?area=algebra&topic=algebraic-expressions"]')).toBeNull();
  expect(ready.querySelector('a[href="/dashboard?area=algebra&topic=binomial-theorem"]')).toBeNull();
  expect(ready.querySelector('a[href="/dashboard?area=algebra&topic=polynomial-division"]')).not.toBeNull();
  expect(element.textContent).toContain('Diagonalization');
  const planned = [...element.querySelectorAll('li')].find(item => item.textContent?.includes('Diagonalization'))!;
  expect(planned.textContent).toContain('Coming soon');
  expect(element.querySelector('button[aria-label="Start practice"]')).toBeNull();
  const matrixLinks = element.querySelectorAll<HTMLAnchorElement>('a[href="/dashboard?area=algebra&topic=inverse-matrices"]');
  expect(matrixLinks.length).toBeGreaterThan(0);
  const polynomialLink = element.querySelector<HTMLAnchorElement>('a[href="/dashboard?area=algebra&topic=fundamental-theorem-algebra"]');
  expect(polynomialLink).not.toBeNull();
  expect(element.textContent).toContain('Matrix operations');
  expect(element.textContent).toContain('Coming soon');
  expect(element.querySelector('button')?.textContent).not.toContain('Generate');
  const analysis = [...element.querySelectorAll('button')].find(button => button.textContent === 'Mathematical Analysis')!;
  await act(async () => analysis.click());
  expect(ready.querySelector('a[href="/dashboard?area=mathematical-analysis&topic=derivatives"]')).not.toBeNull();
  expect(ready.querySelector('a[href="/dashboard?area=mathematical-analysis&topic=differential-calculus"]')).not.toBeNull();
  expect(ready.textContent).toContain('certified bisection');
  expect(ready.querySelector('a[href="/dashboard?area=mathematical-analysis&topic=series"]')).not.toBeNull();
  expect(ready.textContent).toContain('Laplace');
  expect(element.textContent).toContain('Cauchy-Hadamard');
  expect(ready.textContent).not.toContain('Determinants of 2 × 2 matrices');
  expect(element.textContent).toContain('Partial derivatives');
  expect(element.textContent).toContain('Differential equations');
  expect(element.querySelector('a[href="/dashboard?area=mathematical-analysis&topic=derivatives"]')).not.toBeNull();
  expect(element.textContent).not.toContain('Inverse matrices');
  expect(element.textContent).toContain('Coming soon');
  const probability = [...element.querySelectorAll('button')].find(button => button.textContent === 'Probability and Statistics')!;
  await act(async () => probability.click());
  expect(probabilitySections.flatMap(section => section.types)).toHaveLength(9);
  expect(ready.querySelectorAll('a')).toHaveLength(9);
  for (const topic of ['probability-events', 'conditional-probability', 'discrete-random-variables', 'discrete-distributions',
    'continuous-distributions', 'moments-joint-distributions', 'descriptive-statistics', 'confidence-intervals', 'hypothesis-tests']) {
    expect(ready.querySelector(`a[href="/dashboard?area=probability-statistics&topic=${topic}"]`)).not.toBeNull();
  }
  await act(async () => root.unmount());
  element.remove();
});
