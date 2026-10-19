import { describe, expect, it } from 'vitest';
import { analyseAnswer } from './answerSyntax';
import { latexToAnswer } from './mathEditor';

const read = (latex: string) => latexToAnswer(latex).text;

describe('latexToAnswer', () => {
  it.each([
    ['\\frac{x^2}{2}+C', 'x^2/2 + C'],
    ['\\frac{x^{2}}{2}+C', 'x^2/2 + C'],
    ['\\frac12x', '1/2*x'],
    ['x\\frac{1}{2}', 'x*1/2'],
    ['\\frac{x+1}{2x}', '(x + 1)/(2x)'],
    ['\\frac{1}{\\frac{1}{x}}', '1/(1/x)'],
    ['2x', '2x'],
    ['xC', 'x*C'],
    ['2e^{x}', '2*e^x'],
    ['e^{2x}', 'e^(2x)'],
    ['e^{-x}', 'e^(-x)'],
    ['x\\left(x+1\\right)', 'x*(x + 1)'],
    ['2\\left(x+1\\right)', '2(x + 1)'],
    ['\\left(x+1\\right)\\left(x-1\\right)', '(x + 1)*(x - 1)'],
    ['\\sin x', 'sin(x)'],
    ['\\sin 2x', 'sin(2x)'],
    ['\\sin x\\cos x', 'sin(x)*cos(x)'],
    ['\\sin x+C', 'sin(x) + C'],
    ['\\sin\\left(x\\right)', 'sin(x)'],
    ['\\sin(x)^2', 'sin(x)^2'],
    ['\\sin^2x', 'sin^2(x)'],
    ['\\sin^{2}\\left(x\\right)', 'sin^2(x)'],
    ['\\sin^{-1}x', 'asin(x)'],
    ['\\arctan x', 'atan(x)'],
    ['\\operatorname{atan}(x)', 'atan(x)'],
    ['\\mathrm{asin}(x)', 'asin(x)'],
    ['asin(x)', 'asin(x)'],
    ['xsinx', 'x*sin(x)'],
    ['\\sec(x)', 'sec(x)'],
    ['\\sqrt{x+1}', 'sqrt(x + 1)'],
    ['\\sqrt2', 'sqrt(2)'],
    ['2\\sqrt{x}', '2sqrt(x)'],
    ['\\sqrt[3]{x}', 'x^(1/3)'],
    ['\\left|x\\right|', 'abs(x)'],
    ['\\ln\\left|x\\right|+C', 'ln(abs(x)) + C'],
    ['\\ln|x|', 'ln(abs(x))'],
    ['\\pi x', 'pi*x'],
    ['3\\pi', '3pi'],
    ['x\\cdot 2', 'x*2'],
    ['6\\div 3', '6/3'],
    ['-\\frac{1}{3}\\cos^{3}\\left(x\\right)+C', '-1/3*cos^3(x) + C'],
    ['x^{-\\frac12}', 'x^(-1/2)'],
    ['\\exponentialE^x', 'e^x'],
    ['x^2\\ln x', 'x^2*ln(x)'],
    ['\\frac{\\sin x}{2}', 'sin(x)/2'],
  ])('%j -> %j', (latex, text) => {
    expect(latexToAnswer(latex)).toEqual({ text, complete: true });
  });

  it.each(['\\frac{\\placeholder{}}{2}', 'x^{\\placeholder{}}', '\\sqrt{}', '\\sin', '\\left(x\\right.'])(
    'marks %j as not finished',
    (latex) => {
      expect(latexToAnswer(latex).complete).toBe(false);
    },
  );

  it('leaves unsupported commands for the checker to flag', () => {
    expect(analyseAnswer(read('x_1')).status).toBe('error');
    expect(analyseAnswer(read('\\infty')).status).toBe('error');
  });

  // The editor shows answers as the preview LaTeX; reading that back must give the same answer.
  it.each([
    'x^2/2 + C', 'sin^2(x) + ln|x|', '2x + (x+1)(x-1)', 'e^(2*x+1)', 'x^(-1/2)', 'sqrt(3)', 'pi/4 + 2',
    '1/2x', 'sin(1/x)', '-x^2', 'sin^-2(x)', '|x|+|x+1|', '3/5', 'x*(x+1)', '2*e^x', '-1/3*cos^3(x) + C',
    'atan(x) + asin(x)', 'x^(1/12)', '.125 + 0.5', 'e^(-x)',
  ])('round-trips %j through its preview LaTeX', (source) => {
    const first = analyseAnswer(source);
    if (first.status !== 'ok') throw new Error(`${source} should parse`);
    const back = analyseAnswer(read(first.latex));
    expect(back).toEqual({ status: 'ok', latex: first.latex });
  });
});
