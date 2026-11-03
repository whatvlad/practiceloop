// Browser mirror of backend/app/math_input/parser.py (ADR-003). It only previews
// how the backend will read an answer and explains syntax mistakes; it never decides
// correctness, and the submitted text is never rewritten behind the learner's back.
// Keep the rules and limits in step with the backend parser.

export const MAX_INPUT_BYTES = 256;
const MAX_TOKENS = 128;
const MAX_NODES = 96;
const MAX_NESTING = 12;
const MAX_FUNCTION_CALLS = 16;
const MAX_LITERAL_DIGITS = 8;
const MAX_FRACTION_DIGITS = 6;
const MAX_EXPONENT_PART = 12;

export const FUNCTIONS = [
  'sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'asin', 'acos', 'atan', 'exp', 'ln', 'log', 'sqrt', 'abs',
] as const;
const FUNCTION_SET: ReadonlySet<string> = new Set(FUNCTIONS);
/** ADR-005: the variables a template may declare for its answers; `i` is the imaginary unit (#221). */
export const ANSWER_VARIABLES = ['x', 'y', 'z', 'r', 'theta', 'i'] as const;
export type AnswerVariable = (typeof ANSWER_VARIABLES)[number];
// Names a letter run splits into when a template declares variables, longest first.
const SPLIT_NAMES = [...new Set([...FUNCTIONS, ...ANSWER_VARIABLES, 'pi', 'e'])].sort((a, b) => b.length - a.length);
const RESERVED = new Set(['i', 'I', 'j', 'J']);
// Partial words that are still on their way to a valid name: not yet a mistake.
const WORDS_IN_PROGRESS = [...FUNCTIONS, 'pi', 'arcsin', 'arccos', 'arctan'];
// Python's str.isspace() for the ASCII range.
const SPACES = new Set([' ', '\t', '\n', '\r', '\x0b', '\x0c', '\x1c', '\x1d', '\x1e', '\x1f']);

type Node =
  | { kind: 'number'; text: string; value: Fraction }
  | { kind: 'symbol'; name: string }
  | { kind: 'unary'; op: '+' | '-'; arg: Node }
  | { kind: 'binary'; op: '+' | '-' | '*' | '/' | '^'; left: Node; right: Node; implicit?: boolean }
  | { kind: 'function'; name: string; arg: Node };

interface Fraction {
  n: bigint;
  d: bigint;
}

interface Token {
  kind: string;
  value: string;
}

class SyntaxProblem extends Error {
  constructor(message: string, readonly unfinished = false) {
    super(message);
  }
}

class TooLong extends SyntaxProblem {}

const SUPERSCRIPTS: Record<string, string> = {
  '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '-',
};

function normalise(source: string): string {
  if ([...source].length > MAX_INPUT_BYTES) throw new TooLong('Input length exceeds the supported range');
  // NFKC would turn x² into x2 (read as x*2), so superscript runs become powers first.
  const normalised = source
    .replace(/⁻?[⁰¹²³⁴⁵⁶⁷⁸⁹]+/g, (run) => `^${[...run].map((c) => SUPERSCRIPTS[c]).join('')}`)
    .normalize('NFKC')
    .replace(/π/g, 'pi')
    .replace(/[θϑ]/g, 'theta')
    .replace(/[−–]/g, '-')
    .replace(/×/g, '*')
    .replace(/÷/g, '/');
  const sizeForm = normalised.replace(/√/g, 'sqrt');
  if ([...sizeForm].some((c) => c.charCodeAt(0) > 0x7f)) throw new SyntaxProblem('Input contains unsupported characters');
  if (sizeForm.length > MAX_INPUT_BYTES) throw new TooLong('Input length exceeds the supported range');
  return normalised;
}

const isDigit = (c: string) => c >= '0' && c <= '9';
const isLetter = (c: string) => (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');

/**
 * ADR-005 rule for templates with declared variables: a run of letters is read from
 * the left, each time as the longest function, variable, `pi` or `e` that starts
 * there, so `2xy` is 2*x*y and `rtheta` is r*theta. Mirrors math_input.parser._split_name.
 */
function splitName(run: string, last: boolean): string[] {
  const names: string[] = [];
  let start = 0;
  while (start < run.length) {
    const name = SPLIT_NAMES.find((n) => run.startsWith(n, start));
    if (!name) {
      // A partial name at the end, like `thet`, is still being typed.
      const typing = last && [...SPLIT_NAMES, 'arcsin', 'arccos', 'arctan'].some((n) => n.startsWith(run.slice(start)));
      throw new SyntaxProblem('Symbol is not allowlisted', typing);
    }
    names.push(name);
    start += name.length;
  }
  return names;
}

function tokenise(source: string, splitNames = false): Token[] {
  const tokens: Token[] = [];
  let i = 0;
  while (i < source.length) {
    const c = source[i];
    if (SPACES.has(c)) {
      i += 1;
      continue;
    }
    if (isDigit(c) || c === '.') {
      const start = i;
      let dots = 0;
      while (i < source.length && (isDigit(source[i]) || source[i] === '.')) {
        if (source[i] === '.') dots += 1;
        i += 1;
      }
      const literal = source.slice(start, i);
      if (dots > 1 || literal === '.') throw new SyntaxProblem('Malformed number');
      const [integer, fraction = ''] = literal.split('.');
      if ((integer + fraction).length > MAX_LITERAL_DIGITS || fraction.length > MAX_FRACTION_DIGITS) {
        throw new SyntaxProblem('Numeric literal is too long');
      }
      if (i < source.length && (source[i] === 'e' || source[i] === 'E')) {
        throw new SyntaxProblem('Scientific notation is not supported');
      }
      tokens.push({ kind: 'NUMBER', value: literal });
    } else if (isLetter(c)) {
      const start = i;
      while (i < source.length && isLetter(source[i])) i += 1;
      const run = source.slice(start, i);
      const last = source.slice(i).trim() === '';
      for (const name of splitNames ? splitName(run, last) : [run]) tokens.push({ kind: 'NAME', value: name });
    } else if (c === '√') {
      tokens.push({ kind: 'ROOT', value: c });
      i += 1;
    } else if ('+-*/^()|'.includes(c)) {
      const pair = source.slice(i, i + 2);
      if (pair === '**' || pair === '//') throw new SyntaxProblem('Unsupported operator');
      tokens.push({ kind: c, value: c });
      i += 1;
    } else {
      throw new SyntaxProblem('Input contains unsupported syntax');
    }
    if (tokens.length > MAX_TOKENS) throw new SyntaxProblem('Expression has too many tokens');
  }
  if (tokens.length === 0) throw new SyntaxProblem('Expression is empty');
  return [...tokens, { kind: 'EOF', value: '' }];
}

function gcd(a: bigint, b: bigint): bigint {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y) [x, y] = [y, x % y];
  return x;
}

function fraction(n: bigint, d: bigint): Fraction {
  if (d < 0n) [n, d] = [-n, -d];
  const g = gcd(n, d) || 1n;
  return { n: n / g, d: d / g };
}

function numberFraction(literal: string): Fraction {
  const [integer, fractionDigits] = literal.split('.');
  if (fractionDigits === undefined) return fraction(BigInt(integer), 1n);
  return fraction(BigInt((integer || '0') + fractionDigits || '0'), 10n ** BigInt(fractionDigits.length));
}

function constantFraction(node: Node): Fraction | null {
  if (node.kind === 'number') return node.value;
  if (node.kind === 'unary') {
    const value = constantFraction(node.arg);
    if (value === null) return null;
    return node.op === '+' ? value : { n: -value.n, d: value.d };
  }
  if (node.kind === 'binary' && node.op !== '^') {
    const l = constantFraction(node.left);
    const r = constantFraction(node.right);
    if (l === null || r === null || (node.op === '/' && r.n === 0n)) return null;
    if (node.op === '+') return fraction(l.n * r.d + r.n * l.d, l.d * r.d);
    if (node.op === '-') return fraction(l.n * r.d - r.n * l.d, l.d * r.d);
    if (node.op === '*') return fraction(l.n * r.n, l.d * r.d);
    return fraction(l.n * r.d, l.d * r.n);
  }
  return null;
}

const absBig = (v: bigint) => (v < 0n ? -v : v);

class Parser {
  private position = 0;
  private nodeCount = 0;
  private functionCount = 0;
  private groupDepth = 0;
  private insideAbsolute = false;
  private extraSymbol: string | null = null;

  /** `variables` null is the ADR-003 integration grammar: x, plus one constant letter. */
  constructor(
    private readonly tokens: Token[],
    private readonly variables: ReadonlySet<string> | null = null,
  ) {}

  private get current(): Token {
    return this.tokens[this.position];
  }

  private fail(message: string): never {
    throw new SyntaxProblem(message, this.current.kind === 'EOF');
  }

  private advance(): Token {
    const token = this.current;
    this.position += 1;
    return token;
  }

  private expect(kind: string): void {
    if (this.current.kind !== kind) this.fail('Malformed expression');
    this.advance();
  }

  private count<T extends Node>(node: T): T {
    this.nodeCount += 1;
    if (this.nodeCount > MAX_NODES) throw new SyntaxProblem('Expression has too many nodes');
    return node;
  }

  parse(): Node {
    const result = this.expression();
    if (this.current.kind !== 'EOF') this.fail('Malformed expression');
    return result;
  }

  private expression(minimumPrecedence = 0): Node {
    let left = this.prefix();
    for (;;) {
      const kind = this.current.kind;
      const implicit = startsAtom(kind) && !(kind === '|' && this.insideAbsolute);
      let precedence: number;
      let operator: '+' | '-' | '*' | '/' | '^';
      if (kind === '+' || kind === '-') {
        precedence = 10;
        operator = kind;
      } else if (kind === '*' || kind === '/') {
        precedence = 20;
        operator = kind;
      } else if (kind === '^') {
        precedence = 30;
        operator = kind;
      } else if (implicit) {
        if (kind === 'NUMBER' && this.tokens[this.position - 1].kind === 'NUMBER') {
          throw new SyntaxProblem('Adjacent numbers require an operator');
        }
        precedence = 20;
        operator = '*';
      } else {
        break;
      }
      if (precedence < minimumPrecedence) break;
      if (!implicit) this.advance();
      const right = this.expression(operator === '^' ? precedence : precedence + 1);
      if (operator === '/' && constantFraction(right)?.n === 0n) {
        throw new SyntaxProblem('Division by zero is not allowed');
      }
      if (operator === '^') validateExponent(left, right);
      left = this.count({ kind: 'binary', op: operator, left, right, implicit });
    }
    return left;
  }

  private prefix(): Node {
    const token = this.current;
    if (token.kind === '+' || token.kind === '-') {
      this.advance();
      return this.count({ kind: 'unary', op: token.kind, arg: this.expression(25) });
    }
    if (token.kind === 'NUMBER') {
      this.advance();
      return this.count({ kind: 'number', text: token.value, value: numberFraction(token.value) });
    }
    if (token.kind === 'NAME') return this.name();
    if (token.kind === 'ROOT') {
      this.advance();
      if (!['NUMBER', 'NAME', '('].includes(this.current.kind)) {
        this.fail('Square root requires a number, name, or group');
      }
      return this.callFunction('sqrt', this.prefix());
    }
    if (token.kind === '(') return this.group();
    if (token.kind === '|') return this.absolute();
    this.fail('Expected a number, symbol, or group');
  }

  private name(): Node {
    const word = this.advance().value;
    const last = this.current.kind === 'EOF';
    if (FUNCTION_SET.has(word)) {
      let power: Node | null = null;
      if (this.current.kind === '^') {
        this.advance();
        power = this.functionPower();
      }
      let argument: Node;
      if (this.current.kind === '|' && (word === 'ln' || word === 'log')) {
        argument = this.absolute();
      } else {
        if (this.current.kind !== '(') this.fail('Functions require parentheses');
        argument = this.group();
      }
      let result: Node = this.callFunction(word, argument);
      if (power !== null) {
        validateExponent(result, power);
        result = this.count({ kind: 'binary', op: '^', left: result, right: power });
      }
      return result;
    }
    if (this.variables !== null) {
      if (!this.variables.has(word) && word !== 'pi' && word !== 'e') {
        throw new SyntaxProblem('Variable is not used in this exercise');
      }
    } else if (!['x', 'pi', 'e'].includes(word)) {
      if (word.length !== 1 || RESERVED.has(word)) {
        const typing = last && WORDS_IN_PROGRESS.some(w => w.startsWith(word));
        throw new SyntaxProblem('Symbol is not allowlisted', typing);
      }
      if (this.extraSymbol !== null && this.extraSymbol !== word) {
        throw new SyntaxProblem('Only one arbitrary constant is supported');
      }
      this.extraSymbol = word;
    }
    if (this.current.kind === '(') throw new SyntaxProblem('Arbitrary function calls are not supported');
    return this.count({ kind: 'symbol', name: word });
  }

  private group(): Node {
    this.expect('(');
    this.groupDepth += 1;
    if (this.groupDepth > MAX_NESTING) throw new SyntaxProblem('Expression nesting is too deep');
    const result = this.expression();
    this.expect(')');
    this.groupDepth -= 1;
    return result;
  }

  private absolute(): Node {
    if (this.insideAbsolute) throw new SyntaxProblem('Nested absolute-value bars are not supported');
    this.expect('|');
    this.insideAbsolute = true;
    this.groupDepth += 1;
    if (this.groupDepth > MAX_NESTING) throw new SyntaxProblem('Expression nesting is too deep');
    const result = this.expression();
    this.expect('|');
    this.groupDepth -= 1;
    this.insideAbsolute = false;
    return this.callFunction('abs', result);
  }

  private callFunction(name: string, arg: Node): Node {
    this.functionCount += 1;
    if (this.functionCount > MAX_FUNCTION_CALLS) throw new SyntaxProblem('Expression has too many function calls');
    return this.count({ kind: 'function', name, arg });
  }

  private functionPower(): Node {
    let sign: '+' | '-' | '' = '';
    if (this.current.kind === '+' || this.current.kind === '-') sign = this.advance().kind as '+' | '-';
    if (this.current.kind !== 'NUMBER') this.fail('Function powers must be numeric');
    const text = this.advance().value;
    let numerator: Node = this.count({ kind: 'number', text, value: numberFraction(text) });
    if (sign) numerator = this.count({ kind: 'unary', op: sign, arg: numerator });
    // Index directly: the getter's narrowing above does not survive advance().
    if (this.tokens[this.position].kind !== '/') return numerator;
    this.advance();
    if (this.current.kind !== 'NUMBER') this.fail('Malformed function power');
    const dText = this.advance().value;
    const denominator: Node = this.count({ kind: 'number', text: dText, value: numberFraction(dText) });
    if (constantFraction(denominator)?.n === 0n) throw new SyntaxProblem('Division by zero is not allowed');
    return this.count({ kind: 'binary', op: '/', left: numerator, right: denominator });
  }
}

function startsAtom(kind: string): boolean {
  return kind === 'NUMBER' || kind === 'NAME' || kind === 'ROOT' || kind === '(' || kind === '|';
}

function validateExponent(base: Node, exponent: Node): void {
  const value = constantFraction(exponent);
  if (value === null) {
    if (base.kind === 'symbol' && base.name === 'e') return;
    throw new SyntaxProblem('Variable exponents are only supported for e');
  }
  if (absBig(value.n) > BigInt(MAX_EXPONENT_PART) || value.d > BigInt(MAX_EXPONENT_PART)) {
    throw new SyntaxProblem('Exponent is outside the supported range');
  }
}

// ---------- LaTeX preview ----------

const LATEX_FUNCTIONS: Record<string, string> = {
  sin: '\\sin', cos: '\\cos', tan: '\\tan', sec: '\\sec', csc: '\\csc', cot: '\\cot',
  asin: '\\arcsin', acos: '\\arccos', atan: '\\arctan', exp: '\\exp', ln: '\\ln', log: '\\ln',
};

const isSum = (n: Node) => n.kind === 'binary' && (n.op === '+' || n.op === '-');
// Plain brackets keep function spacing tight; \left/\right only when a fraction needs taller ones.
const paren = (s: string) => (s.includes('\\frac') ? `\\left(${s}\\right)` : `(${s})`);

function startsWithDigit(n: Node): boolean {
  if (n.kind === 'number') return true;
  if (n.kind === 'binary') return n.op === '/' ? false : startsWithDigit(n.left);
  return false;
}

function toLatex(node: Node): string {
  switch (node.kind) {
    case 'number':
      return node.text.startsWith('.') ? `0${node.text}` : node.text;
    case 'symbol':
      return node.name === 'pi' ? '\\pi ' : node.name === 'theta' ? '\\theta ' : node.name;
    case 'unary': {
      const inner = toLatex(node.arg);
      return `${node.op}${isSum(node.arg) ? paren(inner) : inner}`;
    }
    case 'function': {
      const inner = toLatex(node.arg);
      if (node.name === 'sqrt') return `\\sqrt{${inner}}`;
      if (node.name === 'abs') return `\\left|${inner}\\right|`;
      if ((node.name === 'ln' || node.name === 'log') && node.arg.kind === 'function' && node.arg.name === 'abs') {
        return `\\ln${inner}`;
      }
      return `${LATEX_FUNCTIONS[node.name]}${paren(inner)}`;
    }
    case 'binary': {
      const { op, left, right } = node;
      if (op === '/') return `\\frac{${toLatex(left)}}{${toLatex(right)}}`;
      if (op === '^') {
        const exponent = toLatex(right);
        if (left.kind === 'function' && left.name in LATEX_FUNCTIONS) {
          return `${LATEX_FUNCTIONS[left.name]}^{${exponent}}${paren(toLatex(left.arg))}`;
        }
        const base = toLatex(left);
        const simple = left.kind === 'symbol' || (left.kind === 'number' && !left.text.includes('.'));
        return `${simple || left.kind === 'function' ? base : paren(base)}^{${exponent}}`;
      }
      if (op === '*') {
        const l = toLatex(left);
        const r = toLatex(right);
        const wrapLeft = isSum(left);
        const wrapRight = isSum(right) || right.kind === 'unary';
        const ls = wrapLeft ? paren(l) : l;
        const rs = wrapRight ? paren(r) : r;
        if (right.kind === 'unary' || (!wrapRight && startsWithDigit(right))) return `${ls}\\cdot ${rs}`;
        // Variables side by side (`x y`, `r \\theta`) need no thin space, which also keeps
        // long products inside KaTeX's expansion limit.
        if (right.kind === 'symbol' && /[A-Za-z] ?$/.test(ls)) return `${ls} ${rs}`;
        return /^[\\(]/.test(rs) ? `${ls}${rs}` : `${ls}\\,${rs}`;
      }
      const r = toLatex(right);
      const wrapRight = right.kind === 'unary' || (op === '-' && isSum(right));
      return `${toLatex(left)}${op}${wrapRight ? paren(r) : r}`;
    }
  }
}

// ---------- Learner feedback ----------

const FUNCTION_PATTERN = 'asin|acos|atan|sqrt|sin|cos|tan|sec|csc|cot|exp|abs|ln|log';

/** Rewrites common slips into the accepted syntax; the learner chooses whether to apply it. */
export function suggestFix(source: string): string {
  let text = source.replace(/\*\*/g, '^');
  text = text.replace(/arc(sin|cos|tan)/g, 'a$1');
  // A number directly before e reads as scientific notation: 2e^x -> 2*e^x.
  text = text.replace(/(\d)(?=[eE](?!\d))/g, '$1*');
  // Run-together names: xe -> x*e, xsin -> x*sin, sinx -> sin x (bracketed below).
  text = text.replace(/[A-Za-z]+/g, splitWord);
  // A function without brackets takes the next simple term: sin x -> sin(x), sin^2 x -> sin^2(x).
  text = text.replace(
    new RegExp(`(?<![A-Za-z])(${FUNCTION_PATTERN})(\\^-?\\d+)?\\s*(?![\\s(|]|$)([0-9.]*(?:pi|[A-Za-z])?)`, 'g'),
    (match, name: string, power: string | undefined, term: string) =>
      term ? `${name}${power ?? ''}(${term})` : match,
  );
  // A variable or constant directly before a bracket: x(x+1) -> x*(x+1).
  text = text.replace(/(?<![A-Za-z])(pi|[A-Za-z])\s*\(/g, (match, name: string) =>
    FUNCTION_SET.has(name) ? match : `${name}*(`,
  );
  return text;
}

function splitWord(word: string): string {
  if (FUNCTION_SET.has(word) || word === 'pi' || word.length === 1) return word;
  const parts: string[] = [];
  let rest = word;
  while (rest) {
    const piece = [...FUNCTIONS, 'pi', 'x', 'e'].find(p => rest.startsWith(p));
    if (!piece) return word;
    parts.push(piece);
    rest = rest.slice(piece.length);
  }
  let out = '';
  parts.forEach((piece, index) => {
    if (index > 0) out += FUNCTION_SET.has(parts[index - 1]) ? ' ' : '*';
    out += piece;
  });
  return out;
}

const HINTS: Record<string, string> = {
  'Input contains unsupported characters': 'Some characters are not supported. Use the keypad or plain keyboard symbols.',
  'Input contains unsupported syntax': 'Some symbols are not supported. Use + - * / ^ ( ) and |x|.',
  'Malformed number': 'A number has more than one decimal point.',
  'Numeric literal is too long': 'Numbers can have at most 8 digits, 6 after the decimal point.',
  'Scientific notation is not supported': 'A number right before e reads as scientific notation, which is not supported. For the constant e, write 2*e^x.',
  'Unsupported operator': 'Use ^ for powers and a single / for division.',
  'Expression has too many tokens': 'The answer is too long.',
  'Expression has too many nodes': 'The answer is too long.',
  'Malformed expression': 'Something is out of place. Check the brackets and operators.',
  'Expected a number, symbol, or group': 'An operator is missing a number or term next to it.',
  'Adjacent numbers require an operator': 'Two numbers are next to each other. Put an operator between them.',
  'Division by zero is not allowed': 'You are dividing by zero.',
  'Square root requires a number, name, or group': 'Put the square root around a number or brackets, like √(x+1).',
  'Functions require parentheses': 'Functions need brackets, like sin(x).',
  'Symbol is not allowlisted': 'Unknown name. Use x, pi, e, one letter for the constant, or a keypad function.',
  'Only one arbitrary constant is supported': 'Only one constant letter is allowed besides x and e.',
  'Arbitrary function calls are not supported': 'A letter right before a bracket reads as a function. Put * between them, like x*(x+1).',
  'Expression nesting is too deep': 'There are too many nested brackets.',
  'Nested absolute-value bars are not supported': 'Bars inside bars are not supported. Use abs() for the inner one.',
  'Expression has too many function calls': 'There are too many functions in one answer.',
  'Function powers must be numeric': 'A function power must be a number, like sin^2(x).',
  'Malformed function power': 'Write a fractional function power as a number over a number.',
  'Variable exponents are only supported for e': 'Only e can have x in the exponent, like e^(2x).',
  'Exponent is outside the supported range': 'Powers must stay between -12 and 12.',
  'Input length exceeds the supported range': 'The answer is too long.',
};

export type AnswerAnalysis =
  | { status: 'empty' }
  | { status: 'ok'; latex: string; warning?: string; fix?: string }
  | { status: 'unfinished'; message: string }
  | { status: 'error'; message: string; fix?: string };

function parseOnly(source: string, variables?: readonly string[]): Node {
  const declared = variables ? new Set(variables) : null;
  return new Parser(tokenise(normalise(source), declared !== null), declared).parse();
}

function usable(candidate: string, variables?: readonly string[]): boolean {
  try {
    parseOnly(candidate, variables);
    return true;
  } catch (error) {
    return error instanceof SyntaxProblem && error.unfinished;
  }
}

/** `x, y and θ`, for hints. */
export function variableList(variables: readonly string[]): string {
  const names = variables.map((v) => (v === 'theta' ? 'θ' : v));
  return names.length < 2 ? names.join('') : `${names.slice(0, -1).join(', ')} and ${names[names.length - 1]}`;
}

function hint(message: string, variables?: readonly string[]): string {
  if (variables && (message === 'Variable is not used in this exercise' || message === 'Symbol is not allowlisted')) {
    return `Unknown name. This answer uses only ${variableList(variables)}, with pi, e and the keypad functions.`;
  }
  return HINTS[message] ?? message;
}

/**
 * How the backend will read an answer, with a learner-facing hint when it cannot.
 * `variables` is the exercise's declared set (ADR-005); without it the integration
 * grammar applies.
 */
export function analyseAnswer(source: string, variables?: readonly string[]): AnswerAnalysis {
  if (source.trim() === '') return { status: 'empty' };
  let tree: Node;
  try {
    tree = parseOnly(source, variables);
  } catch (error) {
    if (!(error instanceof SyntaxProblem)) throw error;
    if (error.unfinished && !(error instanceof TooLong)) {
      return { status: 'unfinished', message: unfinishedMessage(source) };
    }
    const candidate = suggestFix(source);
    const fix = candidate !== source && usable(candidate, variables) ? candidate : undefined;
    return { status: 'error', message: hint(error.message, variables), fix };
  }
  const latex = toLatex(tree);
  const exponentRun = /e\^(-?\d+(?:\.\d+)?)([A-Za-z(])/.exec(source);
  if (exponentRun) {
    const fix = source.replace(/e\^(-?\d+(?:\.\d+)?)(x|\([^()]*\))/, 'e^($1$2)');
    return { status: 'ok', latex, warning: `Only ${exponentRun[1]} is in the exponent. Use brackets for more, like e^(2x).`, fix: fix !== source ? fix : undefined };
  }
  return { status: 'ok', latex };
}

function unfinishedMessage(source: string): string {
  const opens = (source.match(/\(/g) ?? []).length;
  const closes = (source.match(/\)/g) ?? []).length;
  if (opens > closes) return 'Close the bracket to finish.';
  if ((source.match(/\|/g) ?? []).length % 2 === 1) return 'Close the | bar to finish.';
  if (/[A-Za-z]$/.test(source.trim())) return 'Keep typing the name, then add brackets.';
  return 'Keep going: the answer is not finished yet.';
}

/** Top-level commas only; scalar component syntax is checked by the existing parser. */
export function splitStructuredParts(source: string): string[] {
  const parts: string[] = [];
  let depth = 0; let start = 0;
  for (let i = 0; i < source.length; i += 1) {
    if (source[i] === '(') depth += 1;
    else if (source[i] === ')') depth -= 1;
    else if (source[i] === ',' && depth === 0) { parts.push(source.slice(start, i)); start = i + 1; }
    if (depth < 0) throw new SyntaxProblem('Unbalanced component');
  }
  if (depth !== 0) throw new SyntaxProblem('Unbalanced component', true);
  parts.push(source.slice(start));
  return parts;
}

/** Mirror of math_input/structured.py. Syntax preview only, never correctness. */
export function analyseStructuredAnswer(source: string, kind: 'boolean' | 'finite_set' | 'interval'): AnswerAnalysis {
  if (!source.trim()) return { status: 'empty' };
  try {
    const text = normalise(source.replaceAll('∞', 'inf')).trim();
    if (kind === 'boolean') {
      if (text !== 'true' && text !== 'false') throw new SyntaxProblem('Choose Yes or No.');
      return { status: 'ok', latex: text === 'true' ? '\\text{Yes}' : '\\text{No}' };
    }
    if (kind === 'finite_set' ? !(text.startsWith('{') && text.endsWith('}'))
      : !(text.length >= 5 && '[('.includes(text[0]) && '])'.includes(text.at(-1)!))) throw new SyntaxProblem('Complete the answer brackets.', true);
    const parts = kind === 'finite_set' && !text.slice(1, -1).trim() ? [] : splitStructuredParts(text.slice(1, -1));
    if (kind === 'finite_set' ? parts.length > 8 : parts.length !== 2) throw new SyntaxProblem('Check the number of entries.');
    const latex: string[] = []; const stack: Node[] = [];
    let tokens = 2 + parts.length;
    for (let i = 0; i < parts.length; i += 1) {
      const part = parts[i].trim();
      if (!part) throw new SyntaxProblem('Fill in every entry.', true);
      if (kind === 'interval' && ['-inf', 'inf', '+inf'].includes(part)) {
        if ((i === 0) !== (part === '-inf') || text[i === 0 ? 0 : text.length - 1] !== (i === 0 ? '(' : ')')) throw new SyntaxProblem('Infinite endpoints must be open and correctly signed.');
        latex.push(i === 0 ? '-\\infty' : '\\infty'); tokens += 1;
      } else {
        const analysis = analyseAnswer(part, []);
        if (analysis.status !== 'ok') return analysis;
        const tree = parseOnly(part, []); stack.push(tree); tokens += tokenise(normalise(part), true).length;
        latex.push(toLatex(tree));
      }
    }
    let nodes = 1 + parts.filter(p => ['inf', '+inf', '-inf'].includes(p.trim())).length; let functions = 0;
    while (stack.length) {
      const node = stack.pop()!; nodes += 1;
      if (node.kind === 'binary') stack.push(node.left, node.right);
      else if (node.kind === 'unary' || node.kind === 'function') { stack.push(node.arg); if (node.kind === 'function') functions += 1; }
    }
    if (nodes > MAX_NODES || tokens > MAX_TOKENS || functions > MAX_FUNCTION_CALLS) throw new SyntaxProblem('Structured answer exceeds the shared complexity budget.');
    return { status: 'ok', latex: kind === 'finite_set' ? (parts.length ? `\\left\\{${latex.join(',')}\\right\\}` : '\\emptyset') : `\\left${text[0]}${latex.join(',')}\\right${text.at(-1)}` };
  } catch (error) {
    if (!(error instanceof SyntaxProblem)) throw error;
    return { status: error.unfinished && !(error instanceof TooLong) ? 'unfinished' : 'error', message: error.message };
  }
}
