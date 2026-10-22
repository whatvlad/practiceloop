/**
 * ADR-006 expression trees, evaluated without eval, Function or a CAS.
 *
 * A tree is a JSON number, a name or `[head, ...args]`. `compile` checks the whole
 * tree once and returns a plain closure; a value that is not finite is NaN, which
 * the plot draws as a gap. The server's twin is backend/app/visuals/expression.py.
 */

export type Tree = number | string | Tree[];
export type Env = Readonly<Record<string, number>>;
export type Compiled = (env: Env) => number;

export const NAMES = ['x', 'y', 'z', 'r', 'theta'] as const;
const CONSTANTS: Record<string, number> = { pi: Math.PI, e: Math.E };
const UNARY: Record<string, (value: number) => number> = {
  exp: Math.exp, log: Math.log, sin: Math.sin, cos: Math.cos, tan: Math.tan, abs: Math.abs, sqrt: Math.sqrt,
};
export const HEADS = ['add', 'mul', 'pow', ...Object.keys(UNARY)];
const MAX_DEPTH = 64;
const MAX_NODES = 4000;

export class ExpressionError extends Error {}

export function compile(tree: unknown): Compiled {
  let nodes = 0;
  function build(node: unknown, depth: number): Compiled {
    nodes += 1;
    if (depth > MAX_DEPTH || nodes > MAX_NODES) throw new ExpressionError('Expression too large');
    if (typeof node === 'number') {
      if (!Number.isFinite(node)) throw new ExpressionError('Numbers must be finite');
      return () => node;
    }
    if (typeof node === 'string') {
      if (Object.hasOwn(CONSTANTS, node)) { const value = CONSTANTS[node]; return () => value; }
      if (!(NAMES as readonly string[]).includes(node)) throw new ExpressionError(`Unknown name ${node}`);
      return env => (Object.hasOwn(env, node) ? env[node] : NaN);
    }
    if (!Array.isArray(node) || typeof node[0] !== 'string') throw new ExpressionError('Not an expression');
    const [head, ...rest] = node;
    const args = rest.map(arg => build(arg, depth + 1));
    if (head === 'add' || head === 'mul') {
      if (!args.length) throw new ExpressionError(`${head} needs arguments`);
      return head === 'add'
        ? env => args.reduce((sum, arg) => sum + arg(env), 0)
        : env => args.reduce((product, arg) => product * arg(env), 1);
    }
    if (head === 'pow') {
      if (args.length !== 2) throw new ExpressionError('pow takes two arguments');
      const [base, exponent] = args;
      return env => Math.pow(base(env), exponent(env));
    }
    if (!Object.hasOwn(UNARY, head)) throw new ExpressionError(`Unknown head ${head}`);
    if (args.length !== 1) throw new ExpressionError(`${head} takes one argument`);
    const apply = UNARY[head];
    const [arg] = args;
    return env => apply(arg(env));
  }
  const run = build(tree, 0);
  return env => { const value = run(env); return Number.isFinite(value) ? value : NaN; };
}

export function evaluate(tree: unknown, env: Env): number {
  return compile(tree)(env);
}
