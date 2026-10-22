import { describe, expect, it } from 'vitest';
import { compile, evaluate, ExpressionError, HEADS } from './expression';

describe('expression evaluator', () => {
  it('evaluates every listed head', () => {
    const x = 0.7;
    const cases: [unknown, number][] = [
      [['add', 'x', 2, 'pi'], x + 2 + Math.PI],
      [['mul', -3, 'x', 'e'], -3 * x * Math.E],
      [['pow', 'x', 3], x ** 3],
      [['exp', 'x'], Math.exp(x)],
      [['log', 'x'], Math.log(x)],
      [['sin', 'x'], Math.sin(x)],
      [['cos', 'x'], Math.cos(x)],
      [['tan', 'x'], Math.tan(x)],
      [['abs', ['mul', -1, 'x']], x],
      [['sqrt', 'x'], Math.sqrt(x)],
    ];
    for (const [tree, expected] of cases) expect(evaluate(tree, { x })).toBeCloseTo(expected, 12);
    expect(HEADS.sort()).toEqual(['abs', 'add', 'cos', 'exp', 'log', 'mul', 'pow', 'sin', 'sqrt', 'tan']);
  });

  it('uses the other names of the multiple-integral specs', () => {
    expect(evaluate(['mul', 'r', ['cos', 'theta'], 'y', 'z'], { r: 2, theta: 0, y: 3, z: 4 })).toBe(24);
  });

  it('turns values outside the domain into gaps, never errors', () => {
    for (const tree of [['log', -1], ['sqrt', -1], ['pow', 0, -1], ['exp', 1000], ['mul', 'x', ['pow', 'x', -1]]]) {
      expect(evaluate(tree, { x: 0 })).toBeNaN();
    }
    expect(evaluate('x', {})).toBeNaN();
  });

  it('rejects unknown heads, names, arities and shapes before evaluating', () => {
    for (const tree of [['eval', 'x'], ['Function', 'x'], ['constructor', 1], ['toString', 1], 'u', '__proto__',
      ['pow', 'x'], ['sin', 'x', 'x'], ['add'], [1, 2], {}, null, true, Infinity, NaN]) {
      expect(() => compile(tree)).toThrow(ExpressionError);
    }
  });

  it('bounds the size of a tree', () => {
    let deep: unknown = 'x';
    for (let i = 0; i < 100; i += 1) deep = ['sin', deep];
    expect(() => compile(deep)).toThrow(ExpressionError);
    expect(() => compile(['add', ...Array(5000).fill(1)])).toThrow(ExpressionError);
  });

  it('never reaches eval or Function', async () => {
    const source = (await import('./expression.ts?raw')).default;
    expect(source).not.toMatch(/\beval\s*\(|new Function|Function\s*\(/);
  });
});
