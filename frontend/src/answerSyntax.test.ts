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
  'x²+C', '2x³', '-x²', 'x⁻¹', 'x¹²', 'e²', 'sin²(x)',
];

const REJECTED = [
  "__import__('os')", 'x.real', 'open(x)', 'f(x)', 'lambda x: x', 'y + z', 'i + 1', 'sin x', 'x**2',
  '1//2', '1e6', '[x]', 'x, y', '|x + |x||', '1/0', 'x^x', 'x^13', 'x^(1/13)', 'x^-13', 'sin^13(x)',
  'sin^1/0(x)', 'sin^x(x)', 'e^13', 'e^(-1/13)', 'e^(x^13)', '1/(-0.0)', '1 2', 'sin()', 'sin(x,x)',
  'x+', '(x', 'x)', '||x||', '√-3', '√', '1..2', 'nan', 'oo', 'x[0]', 'x=1', 'x!', 'α',
  '1'.repeat(257), ' '.repeat(255) + 'π', Array(65).fill('1').join('+'), Array(49).fill('1').join('+'),
  '('.repeat(13) + 'x' + ')'.repeat(13), Array(17).fill('sin(x)').join('+'),
  '123456789', '1.1234567', '000000001', '123.123456', 'x¹³',
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

  it('reads superscript digits as powers, like the backend', () => {
    expect(analyseAnswer('x²+C')).toEqual(analyseAnswer('x^2+C'));
    expect(analyseAnswer('x⁻¹')).toEqual(analyseAnswer('x^-1'));
    expect(analyseAnswer('x²+C')).not.toHaveProperty('warning');
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

// ADR-005 corpora, shared with backend/tests/test_answer_variables.py.
const XY = ['x', 'y'] as const;
const XYZ = ['x', 'y', 'z'] as const;
const POLAR = ['r', 'theta'] as const;
const CYLINDRICAL = ['r', 'theta', 'z'] as const;

const VARIABLE_SUPPORTED: [string, readonly string[]][] = [
  ['2xy', XY], ['x y', XY], ['xy^2', XY], ['2r', POLAR], ['r theta', POLAR], ['rtheta', POLAR],
  ['rθ', POLAR], ['2r θ^2', POLAR], ['rcos(theta)', POLAR], ['r^2sin(θ)cos(θ)', POLAR],
  ['xsin(y)', XY], ['ye^(xy)', XY], ['e^(xy)', XY], ['ex', XY], ['pixy', XY], ['exp(x)y', XY],
  ['xyz', XYZ], ['2x*y + y/z', XYZ], ['r^2 z', CYLINDRICAL], ['θ - theta', POLAR],
  ['sqrt(x^2 + y^2)', XY], ['ln|xy|', XY], ['atan(y/x)', XY], ['sec^2(xy)', XY], ['3pi/4', POLAR],
  ['y²x³', XY],
  // Exact limits, reached through the variables.
  ['xy'.repeat(24), XY], [Array(42).fill('theta').join('+'), POLAR], ['('.repeat(12) + 'theta' + ')'.repeat(12), POLAR],
  [Array(16).fill('sin(xy)').join('+'), XY], ['12345678y', XY], ['y^12', XY], ['r^(-12)', POLAR], ['theta^(1/12)', POLAR],
];

const VARIABLE_REJECTED: [string, readonly string[]][] = [
  ['x + y', POLAR], ['r', XY], ['theta', XY], ['z', XY], ['x + C', XY], ['a', XY], ['xa', XY], ['xq', XY],
  ['t', POLAR], ['x(y+1)', XY], ['x^y', XY], ['r^theta', POLAR], ['sin xy', XY], ['y(x)', XY],
  ['2 3x', XY], ['x**y', XY], ['1e3x', XY], ['α', POLAR], ['i*x', XY],
  // Every parser limit, reached through the variables.
  ['xy'.repeat(65), XY], [Array(65).fill('r').join('+'), POLAR], [Array(49).fill('r').join('+'), POLAR],
  ['xy'.repeat(24) + 'x', XY], ['('.repeat(13) + 'theta' + ')'.repeat(13), POLAR], [Array(17).fill('sin(xy)').join('+'), XY],
  ['123456789y', XY], ['1.1234567r', POLAR], ['y^13', XY], ['theta^(1/13)', POLAR], ['sin^13(r)', POLAR],
  ['e^(z^13)', XYZ], ['|x + |y||', XY], ['y/0', XY], ['x^(y)', XY], ['θ'.repeat(52), POLAR], ['x'.repeat(257), XY],
];

describe('declared answer variables (ADR-005)', () => {
  it.each(VARIABLE_SUPPORTED)('accepts %j with %j and renders it', (source, variables) => {
    const result = analyseAnswer(source, variables);
    expect(result.status).toBe('ok');
    if (result.status === 'ok') expect(() => renderMath(result.latex)).not.toThrow();
  });

  it.each(VARIABLE_REJECTED)('does not accept %j with %j', (source, variables) => {
    expect(analyseAnswer(source, variables).status).not.toBe('ok');
  });

  it.each(['y + z', 'xy', '2xy', 'r theta', 'θ', 'theta', 'x y z'])('keeps the integration grammar for %j', (source) => {
    expect(analyseAnswer(source).status).not.toBe('ok');
  });

  it.each([
    ['2xy', XY, '2\\,x y'],
    ['r θ', POLAR, 'r \\theta '],
    ['r theta', POLAR, 'r \\theta '],
    ['theta r', POLAR, '\\theta  r'],
  ])('%j reads as %j', (source, variables, latex) => {
    expect(analyseAnswer(source, variables)).toEqual({ status: 'ok', latex });
  });

  it('names the exercise variables when another one is used', () => {
    expect(analyseAnswer('x + y', POLAR)).toMatchObject({
      status: 'error',
      message: 'Unknown name. This answer uses only r and θ, with pi, e and the keypad functions.',
    });
  });

  it('treats a partly typed theta as unfinished', () => {
    expect(analyseAnswer('r thet', POLAR).status).toBe('unfinished');
    expect(analyseAnswer('r thetq', POLAR).status).toBe('error');
  });
});
