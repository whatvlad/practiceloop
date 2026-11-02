// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it } from 'vitest';
import { CurriculumPage } from './CurriculumPage';
import { algebraSections } from '../data/curriculum';

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
  const ready = element.querySelector('section[aria-labelledby="ready-to-practise"]')!;
  expect(ready.textContent).toContain('Ready to practise');
  expect(ready.querySelector('a[href="/dashboard?area=algebra&topic=matrices"]')).not.toBeNull();
  expect(ready.textContent).not.toContain('Inverse matrices');
  expect(element.textContent).toContain('Inverse matrices');
  const typeSummary = [...element.querySelectorAll('summary')].find(summary => summary.textContent?.includes('Inverse matrices'))!;
  expect(typeSummary.textContent).toContain('In develop');
  expect(element.querySelector('button[aria-label="Start practice"]')).toBeNull();
  const matrixLinks = element.querySelectorAll<HTMLAnchorElement>('a[href="/dashboard?area=algebra&topic=matrices"]');
  expect([...matrixLinks].some(link => link.textContent?.includes('Practice'))).toBe(true);
  const polynomialLink = element.querySelector<HTMLAnchorElement>('a[href="/dashboard?area=algebra&topic=fundamental-theorem-algebra"]');
  expect(polynomialLink).not.toBeNull();
  expect(element.textContent).toContain('Elementary row operations');
  expect(element.textContent).toContain('In develop');
  expect(element.querySelector('button')?.textContent).not.toContain('Generate');
  const analysis = [...element.querySelectorAll('button')].find(button => button.textContent === 'Mathematical Analysis')!;
  await act(async () => analysis.click());
  expect(ready.querySelector('a[href="/dashboard?area=mathematical-analysis&topic=derivatives"]')).not.toBeNull();
  expect(ready.textContent).not.toContain('Determinants of 2 × 2 matrices');
  expect(element.textContent).toContain('Partial derivatives');
  expect(element.textContent).toContain('Differential equations');
  expect(element.querySelector('a[href="/dashboard?area=mathematical-analysis&topic=derivatives"]')).not.toBeNull();
  expect(element.textContent).not.toContain('Inverse matrices');
  expect(element.textContent).toContain('In develop');
  await act(async () => root.unmount());
  element.remove();
});
