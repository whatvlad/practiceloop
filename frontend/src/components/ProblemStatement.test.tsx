// @vitest-environment jsdom
import { renderToStaticMarkup } from 'react-dom/server';
import { expect, it } from 'vitest';
import { ProblemStatement } from './ProblemStatement';

it('lays out a worded geometry statement as wrapping prose and separate givens', () => {
  const host = document.createElement('div');
  host.innerHTML = renderToStaticMarkup(<ProblemStatement topic="lines-and-planes" problemLatex={String.raw`\text{Find the plane through P: }P=\left(1,2,3\right),\ n=\left(0,0,1\right)\text{. Enter an equivalent equation.}`} />);
  expect(host.textContent).toContain('Find the plane through P:');
  expect(host.textContent).toContain('Enter an equivalent equation.');
  expect(host.textContent).not.toContain('Calculate the value.');
  expect(host.querySelector('.pl-expr')).toBeNull();
  expect(host.querySelectorAll('.pl-geometry-given .katex')).toHaveLength(2);
});

it('keeps text commands inside mathematical groups in their formula', () => {
  const host = document.createElement('div');
  host.innerHTML = renderToStaticMarkup(<ProblemStatement topic="vectors" problemLatex={String.raw`\text{Classify: }\left\{x\in\mathbb R\mid\text{a condition}\right\}\text{. Choose a case.}`} />);
  expect(host.querySelectorAll('.pl-geometry-given .katex')).toHaveLength(1);
  expect(host.querySelector('.pl-geometry-given')?.textContent).toContain('a condition');
});

it('renders complete parameter criteria separated by TeX control spaces', () => {
  const host = document.createElement('div');
  host.innerHTML = renderToStaticMarkup(<ProblemStatement topic="lines-and-planes" problemLatex={String.raw`\text{Find A,B in }a=A\ \text{and}\ b\ne B\text{.}`} />);
  expect(host.querySelector('code.pl-mono')).toBeNull();
  expect(host.querySelectorAll('.pl-geometry-given .katex')).toHaveLength(2);
});
