import { renderToStaticMarkup } from 'react-dom/server';
import { expect, it } from 'vitest';
import { LandingPage } from './LandingPage';

it('describes the available subjects while keeping the integral as an example', () => {
  const html = renderToStaticMarkup(<LandingPage onSignIn={() => {}} />);
  expect(html).toContain('Mathematics practice');
  expect(html).toContain('algebra, mathematical analysis and combinations');
  expect(html).toContain('Example problem');
  expect(html).not.toContain('Fresh integration problems');
});
