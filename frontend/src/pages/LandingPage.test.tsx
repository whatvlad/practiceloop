import { renderToStaticMarkup } from 'react-dom/server';
import { expect, it } from 'vitest';
import { LandingPage } from './LandingPage';

it('offers guests the demo and describes what the product does', () => {
  const html = renderToStaticMarkup(<LandingPage onSignIn={() => {}} />);
  expect(html).toContain('Mathematics practice');
  expect(html).toContain('algebra, analysis and probability');
  expect(html).toContain('href="/demo"');
  expect(html).toContain('href="/practice"');
  expect(html).toContain('href="mailto:practiceloop.support@gmail.com?subject=PracticeLoop%20feedback"');
  expect(html).not.toContain('in development');
  expect(html).not.toContain('Example problem');
  expect(html).toContain('id="how"');
});
