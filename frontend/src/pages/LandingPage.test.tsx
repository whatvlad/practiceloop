import { renderToStaticMarkup } from 'react-dom/server';
import { expect, it } from 'vitest';
import { LandingPage } from './LandingPage';

it('describes the curriculum while practice is inactive', () => {
  const html = renderToStaticMarkup(<LandingPage onSignIn={() => {}} />);
  expect(html).toContain('Mathematics practice');
  expect(html).toContain('algebra and mathematical analysis');
  expect(html).toContain('Practice is currently in development');
  expect(html).not.toContain('Example problem');
  expect(html).toContain('id="how"');
});
