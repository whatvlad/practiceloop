// Turns the LaTeX held by the formula editor into ADR-003 answer text, the same
// syntax the backend parses. The editor already makes the structure explicit
// (a fraction bar, a raised exponent, a root), so this is where common slips are
// corrected: implicit products get their *, `sin x` and `sin 2x` get brackets,
// `arctan` and `sin^-1` become atan/asin, and letters spelling a function name
// (typed without the editor's shortcut) become that function.

import { FUNCTIONS } from './answerSyntax';

export interface EditorAnswer {
  /** ADR-003 text that is submitted and shown to the checker preview. */
  text: string;
  /** False while the editor still holds an empty box (a placeholder). */
  complete: boolean;
}

// Longest first, so `asin` wins over `sin` and `sqrt` over `sec`.
const SPELLED = [...FUNCTIONS, 'arcsin', 'arccos', 'arctan', 'pi', 'theta'].sort((a, b) => b.length - a.length);
// Spelled names that are a value, not a function.
const CONSTANTS = new Set(['pi', 'theta']);
const INVERSE: Record<string, string> = { sin: 'asin', cos: 'acos', tan: 'atan' };

const COMMAND_FUNCTIONS: Record<string, string> = {
  sin: 'sin', cos: 'cos', tan: 'tan', sec: 'sec', csc: 'csc', cot: 'cot',
  arcsin: 'asin', arccos: 'acos', arctan: 'atan', asin: 'asin', acos: 'acos', atan: 'atan',
  exp: 'exp', ln: 'ln', log: 'log', abs: 'abs',
};
const OPERATORS: Record<string, string> = {
  '+': '+', '-': '-', '−': '-', '*': '*', '/': '/', cdot: '*', times: '*', ast: '*', div: '/',
};
const SPACING = new Set([',', ';', ':', '!', ' ', 'quad', 'qquad', 'enspace', 'thinspace', 'displaystyle', 'textstyle']);
const BARS = new Set(['|', 'vert', 'lvert', 'rvert', 'mid']);

type Token = { kind: 'command'; name: string } | { kind: 'char'; value: string };

function tokenise(latex: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;
  while (i < latex.length) {
    const c = latex[i];
    if (c === '\\') {
      const word = /^[A-Za-z]+/.exec(latex.slice(i + 1));
      const name = word ? word[0] : latex[i + 1] ?? '';
      tokens.push({ kind: 'command', name });
      i += 1 + Math.max(name.length, 1);
    } else if (/\s/.test(c)) {
      i += 1;
    } else {
      tokens.push({ kind: 'char', value: c });
      i += 1;
    }
  }
  return tokens;
}

interface Term {
  kind: 'term';
  text: string;
  /** Can be a power's base, a divisor or a numerator without brackets. */
  atomic: boolean;
}
interface Operator {
  kind: 'op';
  text: string;
}
type Item = Term | Operator;

const term = (text: string, atomic: boolean): Term => ({ kind: 'term', text, atomic });
const wrap = (t: Term) => (t.atomic ? t.text : `(${t.text})`);

class Reader {
  private position = 0;
  complete = true;

  constructor(private readonly tokens: Token[]) {}

  private peek(offset = 0): Token | undefined {
    return this.tokens[this.position + offset];
  }

  private isChar(value: string, token = this.peek()): boolean {
    return token?.kind === 'char' && token.value === value;
  }

  private isCommand(name: string, token = this.peek()): boolean {
    return token?.kind === 'command' && token.name === name;
  }

  private isBar(token = this.peek()): boolean {
    if (!token) return false;
    return token.kind === 'char' ? token.value === '|' : BARS.has(token.name);
  }

  private next(): Token | undefined {
    return this.tokens[this.position++];
  }

  atEnd(): boolean {
    return this.position >= this.tokens.length;
  }

  /** A row of terms and operators, up to a token `stop` accepts (left unread). */
  row(stop: (token: Token) => boolean): string {
    const items: Item[] = [];
    while (!this.atEnd() && !stop(this.peek()!)) {
      const operator = this.operator();
      if (operator !== null) {
        items.push({ kind: 'op', text: operator });
        continue;
      }
      const t = this.term();
      if (t) items.push(t);
    }
    return join(items);
  }

  /** The row as one term, for fraction parts, exponents and arguments. */
  rowTerm(stop: (token: Token) => boolean): Term {
    const items: Item[] = [];
    while (!this.atEnd() && !stop(this.peek()!)) {
      const operator = this.operator();
      if (operator !== null) items.push({ kind: 'op', text: operator });
      else {
        const t = this.term();
        if (t) items.push(t);
      }
    }
    if (items.length === 1 && items[0].kind === 'term') return items[0];
    return term(join(items), false);
  }

  private operator(): string | null {
    const token = this.peek()!;
    const key = token.kind === 'char' ? token.value : token.name;
    if (token.kind === 'char' && !'+-−*/'.includes(key)) return null;
    if (token.kind === 'command' && !['cdot', 'times', 'ast', 'div'].includes(key)) return null;
    this.next();
    return OPERATORS[key];
  }

  /** `{...}` or one token, as LaTeX reads a command's argument. */
  private argument(): Term {
    if (this.isChar('{')) {
      this.next();
      const inner = this.rowTerm((t) => this.isChar('}', t));
      this.next();
      if (inner.text === '') this.complete = false;
      return inner;
    }
    if (this.atEnd()) {
      this.complete = false;
      return term('', true);
    }
    // Without braces LaTeX takes one token: \frac12 is 1 over 2.
    const token = this.peek()!;
    if (token.kind === 'char' && /[0-9]/.test(token.value)) {
      this.next();
      return term(token.value, true);
    }
    return this.atom() ?? term('', true);
  }

  /** The letters of `{name}`, for \operatorname and \mathrm. */
  private word(): string {
    if (!this.isChar('{')) {
      const token = this.next();
      return token?.kind === 'char' ? token.value : '';
    }
    this.next();
    let text = '';
    while (!this.atEnd() && !this.isChar('}')) {
      const token = this.next()!;
      text += token.kind === 'char' ? token.value : '';
    }
    this.next();
    return text;
  }

  /** One term with any exponent after it; null for tokens that add nothing. */
  term(): Term | null {
    const base = this.atom();
    if (base === null) return null;
    return this.powers(base);
  }

  private powers(base: Term): Term {
    let result = base;
    for (;;) {
      if (this.isChar('^')) {
        this.next();
        const exponent = this.argument();
        result = term(`${wrap(result)}^${exponentText(exponent)}`, false);
      } else if (this.isChar('_')) {
        // Subscripts are not part of the answer syntax: keep them so the checker flags them.
        this.next();
        result = term(`${result.text}_${this.argument().text}`, false);
      } else if (this.isChar("'")) {
        this.next();
        result = term(`${result.text}'`, false);
      } else {
        return result;
      }
    }
  }

  atom(): Term | null {
    const token = this.next()!;
    if (token.kind === 'char') {
      const c = token.value;
      if (/[0-9.]/.test(c)) {
        let digits = c;
        while (this.peek()?.kind === 'char' && /[0-9.]/.test((this.peek() as { value: string }).value)) {
          digits += (this.next() as { value: string }).value;
        }
        return term(digits, !digits.includes('.'));
      }
      if (/[A-Za-z]/.test(c)) return this.letters(c);
      if (c === '{') {
        const inner = this.rowTerm((t) => this.isChar('}', t));
        this.next();
        return inner.text === '' ? null : inner;
      }
      if (c === '(' || c === '[') {
        const close = c === '(' ? ')' : ']';
        const inner = this.row((t) => this.isChar(close, t));
        if (this.atEnd()) this.complete = false;
        else this.next();
        return term(`(${inner})`, true);
      }
      if (c === '|') return this.bars();
      return term(c, true);
    }
    const name = token.name;
    if (SPACING.has(name)) return null;
    if (name === 'placeholder') {
      if (this.isChar('[')) while (!this.atEnd() && !this.isChar(']', this.next()));
      this.argument();
      this.complete = false;
      return null;
    }
    if (name === 'left' || name === 'mleft' || name === 'bigl' || name === 'Bigl') return this.fence();
    if (BARS.has(name)) return this.bars();
    if (name === 'frac' || name === 'dfrac' || name === 'tfrac' || name === 'cfrac') {
      const numerator = this.argument();
      const denominator = this.argument();
      const top = /[+-]/.test(numerator.text.slice(1)) && !numerator.atomic ? `(${numerator.text})` : numerator.text;
      return term(`${top}/${wrap(denominator)}`, false);
    }
    if (name === 'sqrt') {
      let index: Term | null = null;
      if (this.isChar('[')) {
        this.next();
        index = this.rowTerm((t) => this.isChar(']', t));
        this.next();
      }
      const radicand = this.argument();
      if (index === null || index.text === '2') return term(`sqrt(${radicand.text})`, true);
      if (index.text === '') this.complete = false;
      return term(`${wrap(radicand)}^(1/${wrap(index)})`, false);
    }
    if (name === 'pi') return term('pi', true);
    if (name === 'theta' || name === 'vartheta') return term('theta', true);
    if (name === 'exponentialE') return term('e', true);
    if (name === 'imaginaryI') return term('i', true);
    if (name === 'operatorname' || name === 'mathrm' || name === 'text' || name === 'mathit') {
      const word = this.word();
      const fn = COMMAND_FUNCTIONS[word];
      if (fn) return this.apply(fn);
      return word === '' ? null : this.spelled(word);
    }
    if (name in COMMAND_FUNCTIONS) return this.apply(COMMAND_FUNCTIONS[name]);
    if (name === 'right' || name === 'mright') {
      this.next();
      return null;
    }
    // Anything else is outside the answer syntax; keep it so the checker explains.
    return term(`\\${name}`, true);
  }

  /** `\left( ... \right)` and its bar, bracket and invisible variants. */
  private fence(): Term | null {
    const open = this.next();
    const bar = open !== undefined && this.isBar(open);
    const inner = this.row((t) => this.isCommand('right', t) || this.isCommand('mright', t) || this.isCommand('bigr', t) || this.isCommand('Bigr', t));
    if (this.atEnd()) this.complete = false;
    else {
      this.next();
      const close = this.next();
      if (close?.kind === 'char' && close.value === '.' && !(open?.kind === 'char' && open.value === '.')) {
        this.complete = false;
      }
    }
    if (inner === '') return null;
    return bar ? term(`abs(${inner})`, true) : term(`(${inner})`, true);
  }

  private bars(): Term {
    const inner = this.row((t) => this.isBar(t));
    if (this.atEnd()) this.complete = false;
    else this.next();
    return term(`abs(${inner})`, true);
  }

  /** A letter, or a run of letters that spells a function name, pi or theta. */
  private letters(first: string): Term {
    let run = first;
    for (let k = 0; k < 6; k += 1) {
      const t = this.peek(k);
      if (t?.kind !== 'char' || !/[A-Za-z]/.test(t.value)) break;
      run += t.value;
    }
    const word = SPELLED.find((w) => run.startsWith(w));
    if (!word) return term(first, true);
    this.position += word.length - 1;
    if (CONSTANTS.has(word)) return term(word, true);
    return this.apply(COMMAND_FUNCTIONS[word] ?? word);
  }

  private spelled(word: string): Term {
    const fn = SPELLED.find((w) => w === word);
    if (fn && CONSTANTS.has(fn)) return term(fn, true);
    if (fn) return this.apply(COMMAND_FUNCTIONS[fn] ?? fn);
    // A multi-letter word in text: one letter per term, like the editor shows it.
    return term(word.split('').join('*'), word.length === 1);
  }

  /** A function and its argument: brackets after it, or the next simple terms. */
  private apply(name: string): Term {
    let fn = name;
    let power: Term | null = null;
    if (this.isChar('^')) {
      this.next();
      power = this.argument();
      if (power.text === '-1' && fn in INVERSE) {
        fn = INVERSE[fn];
        power = null;
      }
    }
    while (this.peek()?.kind === 'command' && SPACING.has((this.peek() as { name: string }).name)) this.next();
    let argument: string;
    const token = this.peek();
    if (this.isChar('(') || this.isChar('[')) {
      argument = this.atom()!.text.slice(1, -1);
    } else if (this.isBar()) {
      this.next();
      argument = this.bars().text;
    } else if (token && (this.isCommand('left') || this.isCommand('mleft'))) {
      this.next();
      const fenced = this.fence();
      argument = fenced === null ? '' : fenced.text.startsWith('abs(') ? fenced.text : fenced.text.slice(1, -1);
    } else if (fn === 'sqrt' || fn === 'abs') {
      argument = this.argument().text;
    } else {
      argument = this.simpleTerms();
    }
    if (argument === '') this.complete = false;
    const call = `${fn}(${argument})`;
    if (power === null) return this.powers(term(call, true));
    if (/^-?\d+(\/\d+)?$/.test(power.text)) return term(`${fn}^${power.text}(${argument})`, true);
    return term(`${call}^${exponentText(power)}`, false);
  }

  /** `sin 2x` -> 2*x: the terms up to the next operator, function or bracket close. */
  private simpleTerms(): string {
    const items: Item[] = [];
    while (!this.atEnd()) {
      const t = this.peek()!;
      if (t.kind === 'char' && /[+\-−*/)\]}|=]/.test(t.value)) break;
      if (t.kind === 'command' && (t.name in COMMAND_FUNCTIONS || ['cdot', 'times', 'div', 'right', 'mright', 'operatorname'].includes(t.name) || BARS.has(t.name))) break;
      if (t.kind === 'char' && /[A-Za-z]/.test(t.value) && this.spellsFunction()) break;
      const next = this.term();
      if (next) items.push(next);
    }
    return join(items);
  }

  private spellsFunction(): boolean {
    let run = '';
    for (let k = 0; k < 6; k += 1) {
      const t = this.peek(k);
      if (t?.kind !== 'char' || !/[A-Za-z]/.test(t.value)) break;
      run += t.value;
    }
    return SPELLED.some((w) => !CONSTANTS.has(w) && run.startsWith(w));
  }
}

function exponentText(exponent: Term): string {
  return /^\d+$/.test(exponent.text) || /^[A-Za-z]$/.test(exponent.text) || CONSTANTS.has(exponent.text)
    ? exponent.text
    : `(${exponent.text})`;
}

/** Joins terms with an explicit * where the backend needs one, and spaces + and -. */
function join(items: Item[]): string {
  let out = '';
  let previous: Item | null = null;
  items.forEach((item, index) => {
    if (item.kind === 'op') {
      const binary = previous?.kind === 'term';
      out += binary && (item.text === '+' || item.text === '-') ? ` ${item.text} ` : item.text;
    } else {
      const after = items[index + 1];
      const divided = (previous?.kind === 'op' && previous.text === '/') || (after?.kind === 'op' && after.text === '/');
      const text = divided && !item.atomic ? `(${item.text})` : item.text;
      if (previous?.kind === 'term') out += needsTimes(previous.text, text) ? '*' : '';
      out += text;
    }
    previous = item;
  });
  return out;
}

/** `2x`, `2sin(x)` and `2(x+1)` read fine; anything else gets an explicit *. */
function needsTimes(left: string, right: string): boolean {
  if (!/^[0-9.]+$/.test(left)) return true;
  return !/^[A-DF-Za-df-z(√]/.test(right);
}

/** ADR-003 text for what the editor holds. */
export function latexToAnswer(latex: string): EditorAnswer {
  const reader = new Reader(tokenise(latex));
  const text = reader.row(() => false).trim();
  return { text, complete: reader.complete };
}

