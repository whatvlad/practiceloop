import { renderToString } from 'katex';

// Explicitly disable trusted HTML/URL commands from generated or user-provided math.
export function renderMath(latex: string): string {
  return renderToString(latex, {
    trust: false,
    throwOnError: true,
    maxExpand: 100,
    maxSize: 20,
    output: 'htmlAndMathml',
  });
}
