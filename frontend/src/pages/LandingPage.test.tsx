import { renderToStaticMarkup } from 'react-dom/server';
import { expect, it } from 'vitest';
import { LandingPage } from './LandingPage';

it('describes mathematics practice and keeps the integral as a labelled example (#202)', () => {
  const html = renderToStaticMarkup(<LandingPage onSignIn={() => {}} />);
  expect(html).toContain('Algebra · Mathematical Analysis');
  expect(html).toContain('Fresh mathematics problems');
  expect(html).not.toMatch(/Calculus · Integration|Fresh integration problems/);
  expect(html).toContain('Example problem');
});
