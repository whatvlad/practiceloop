import { describe, expect, it } from 'vitest';
import { analyseAnswer, suggestFix } from './answerSyntax';
import { renderMath } from './math';

// The corpora mirror backend/tests/test_math_parser.py, so the preview never
// accepts what the backend rejects or the other way round.
const SUPPORTED = [
  '3pi', '3*pi', '3π', '3/5', 'sqrt(3)', '√3', 'e^2', 'e^(-x)', 'e^(2*x+1)', 'pi/4 + 2',
  '３π − 2×x ÷ 4', '2(x+1)', '√(x+1)', '.125 + 0.5', '-x^2', 'x^(-1/2)', 'sin^-2(x)',
  'sin^1/2(x)', '|x|+|x+1|', 'log|x|', 'x+C+2C', '2x + (x+1)(x-1)', 'sin^2(x) + ln|x|',
  '12345678', '12.123456', 'x^12', 'x^(-12)', 'x^(1/12)', '('.repeat(12) + 'x' + ')'.repeat(12),
  Array(16).fill('sin(x)').join('+'), '+'.repeat(95) + 'x', ' '.repeat(255) + 'x',
];

const REJECTED = [
  "__import__('os')", 'x.real', 'open(x)', 'f(x)', 'lambda x: x', 'y + z', 'i + 1', 'sin x', 'x**2',
  '1//2', '1e6', '[x]', 'x, y', '|x + |x||', '1/0', 'x^x', 'x^13', 'x^(1/13)', 'x^-13', 'sin^13(x)',
  'sin^1/0(x)', 'sin^x(x)', 'e^13', 'e^(-1/13)', 'e^(x^13)', '1/(-0.0)', '1 2', 'sin()', 'sin(x,x)',
  'x+', '(x', 'x)', '||x||', '√-3', '√', '1..2', 'nan', 'oo', 'x[0]', 'x=1', 'x!', 'α',
  '1'.repeat(257), ' '.repeat(255) + 'π', Array(65).fill('1').join('+'), Array(49).fill('1').join('+'),
  '('.repeat(13) + 'x' + ')'.repeat(13), Array(17).fill('sin(x)').join('+'),
  '123456789', '1.1234567', '000000001', '123.123456',
];

describe('analyseAnswer mirrors the backend grammar', () => {
  it.each(SUPPORTED)('accepts %j and renders it with KaTeX', (source) => {
    const result = analyseAnswer(source);
    expect(result.status).toBe('ok');
    if (result.status === 'ok') expect(() => renderMath(result.latex)).not.toThrow();
  });

  it.each(REJECTED)('does not accept %j', (source) => {
    expect(analyseAnswer(source).status).not.toBe('ok');
  });

  it('treats blank input as empty', () => {
    expect(analyseAnswer('').status).toBe('empty');
    expect(analyseAnswer('   ').status).toBe('empty');
  });
});

describe('preview reads the answer the way the backend does', () => {
  it.each([
    ['1/2x', '\\frac{1}{2}\\,x'],
    ['x^2/2+C', '\\frac{x^{2}}{2}+C'],
    ['ln|x|+C', '\\ln\\left|x\\right|+C'],
    ['sin^2(x)', '\\sin^{2}(x)'],
    ['(x+1)(x-1)', '(x+1)(x-1)'],
    ['sin(1/x)', '\\sin\\left(\\frac{1}{x}\\right)'],
    ['x-(x+1)', 'x-(x+1)'],
    ['2*3', '2\\cdot 3'],
  ])('%j reads as %j', (source, latex) => {
    expect(analyseAnswer(source)).toEqual({ status: 'ok', latex });
  });
});

describe('mistakes are flagged while typing', () => {
  it.each([
    ['x(x+1)', 'x*(x+1)'],
    ['2e^x', '2*e^x'],
    ['sin x', 'sin(x)'],
    ['sinx', 'sin(x)'],
    ['sin^2 x', 'sin^2(x)'],
    ['arctan(x)', 'atan(x)'],
    ['xe^x', 'x*e^x'],
    ['xcosx + C', 'x*cos(x) + C'],
    ['x**2', 'x^2'],
  ])('%j is an error with the fix %j', (source, fix) => {
    const result = analyseAnswer(source);
    expect(result.status).toBe('error');
    expect(result).toMatchObject({ fix });
    expect(analyseAnswer(fix).status).toBe('ok');
  });

  it('explains errors that have no single fix', () => {
    expect(analyseAnswer('2^x')).toEqual({
      status: 'error',
      message: 'Only e can have x in the exponent, like e^(2x).',
      fix: undefined,
    });
    expect(analyseAnswer('1e6')).toMatchObject({ status: 'error', fix: undefined });
  });

  it('warns when a superscript digit would be read as multiplication', () => {
    expect(analyseAnswer('x²+C')).toMatchObject({ status: 'ok', latex: 'x\\cdot 2+C', fix: 'x^2+C' });
  });

  it('warns when only the first number is in the exponent', () => {
    expect(analyseAnswer('e^2x')).toMatchObject({ status: 'ok', fix: 'e^(2x)' });
  });

  it.each(['x+', 'sqrt(', '|x', 's', 'si', 'sin', 'arc', 'sin^', '(x+1'])('%j is unfinished, not wrong', (source) => {
    expect(['unfinished', 'ok']).toContain(analyseAnswer(source).status);
  });

  it('leaves correct input unchanged when suggesting fixes', () => {
    for (const source of ['sin(x)+C', 'x*e^x', 'ln|x|', 'atan(x)', 'sqrt(x+1)', 'e^(2x)', 'exp(x)']) {
      expect(suggestFix(source)).toBe(source);
    }
  });
});
