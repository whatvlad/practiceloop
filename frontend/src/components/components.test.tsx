import text from '../../../backend/app/content/en.json';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { ApiStatusNotice } from './ApiStatusNotice';
import { DifficultyScale } from './DifficultyScale';
import { ProblemCard } from './ProblemCard';
import { TopicChips } from './TopicChips';

const noop = () => {};

function card(props: Partial<Parameters<typeof ProblemCard>[0]> = {}) {
  return renderToStaticMarkup(
    <ProblemCard
      topic="substitution"
      difficulty={3}
      problemLatex={'\\int 2x\\cos(x^2)\\,dx'}
      answer=""
      onAnswerChange={noop}
      result={null}
      onCheck={noop}
      onShowAnswer={noop}
      onShowSolution={noop}
      onNext={noop}
      {...props}
    />,
  );
}

describe('ProblemCard', () => {
  it.each([
    ['algebraic-expressions', '\\text{Simplify }2\\sqrt{3}-\\sqrt{27}\\text{.}', 'Simplify', '2\\sqrt{3}-\\sqrt{27}'],
    ['algebraic-expressions', '\\text{Rationalize the denominator of }\\frac{1}{2+\\sqrt{3}}\\text{.}', 'Rationalize the denominator', '\\frac{1}{2+\\sqrt{3}}'],
    ['polynomial-division', '\\text{Find the remainder when }P(x)=x^{2}+1\\text{ is divided by }x-1\\text{.}', 'Find the remainder', 'x^{2}+1'],
    ['fundamental-theorem-algebra', 'x^2+1x+1=0: \\text{sum of the roots}', 'sum of the roots', 'x^2+1x+1=0'],
    ['linear-systems', '\\text{Use Cramer\'s rule to find y in the system: }\\begin{cases}x-3y=6\\\\x-2y=4\\end{cases}\\text{.}', 'Use Cramer', '\\begin{cases}x-3y=6'],
    ['inverse-matrices', '\\text{Find the entry in the first row and second column of the inverse matrix: }A=\\begin{pmatrix}1&-1\\\\1&-2\\end{pmatrix},\\quad A^{-1}=?\\text{.}', 'first row and second column', 'A=\\begin{pmatrix}'],
    ['limits-and-continuity', '\\text{Calculate }f(x)=\\frac{x^2-1}{x-1},\\quad f(1)=?\\text{ for continuity}\\text{.}', 'continuous', 'f(x)=\\frac{x^2-1}{x-1}'],
  ] as const)('separates the instruction from the formula for %s', (topic, problemLatex, instruction, formula) => {
    const html = card({ topic, problemLatex });
    const lead = html.match(/<p class="pl-lead">(.*?)<\/p>/)?.[1];
    const expression = html.match(/<div class="pl-expr"[^>]*>([\s\S]*?)<\/div>/)?.[1];
    expect(lead).toContain(instruction);
    expect(expression).toContain(formula);
    expect(expression).not.toContain(instruction);
    expect(expression).not.toContain('is divided by');
    if (topic === 'polynomial-division') expect(expression).toContain('x-1');
  });

  it('groups the polynomial and divisor as complete operands', () => {
    const html = card({ topic: 'polynomial-division', problemLatex: '\\text{Find the quotient when }x^{2}+1\\text{ is divided by }x-1\\text{.}' });
    expect(html).toContain('\\frac{x^{2}+1}{x-1}');
  });

  it.each(['\\frac{2x+3}{(x+1)(x+2)}=?', '\\text{Calculate }\\frac{2x+3}{(x+1)(x+2)}=?\\text{.}'])('tells a learner how to solve a partial-fractions exercise', problemLatex => {
    const html = card({ topic: 'partial-fractions', problemLatex });
    expect(html).toContain('Decompose into partial fractions.');
  });

  it('renders no answer or solution before they are revealed', () => {
    const html = card();
    expect(html).not.toContain('pl-answer');
    expect(html).not.toContain('pl-steps');
    expect(html).toContain('<label class="pl-label" for="answer">Your answer</label>');
    expect(html).toContain('role="status"');
  });

  it('promotes Generate next problem and disables Check answer after Correct', () => {
    const html = card({ result: 'correct', answer: 'sin(x^2) + C' });
    expect(html).toContain('pl-result--correct');
    expect(html).toContain('pl-input is-correct');
    expect(html).toMatch(/<button type="button" class="pl-btn pl-btn--primary pl-btn--lg pl-btn--block" disabled="">Check answer/);
    expect(html).toMatch(/class="pl-btn pl-btn--primary">Generate next problem/);
  });

  it('shows the revealed answer and steps, marking the last step final', () => {
    const html = card({ answerLatex: '\\sin(x^2) + C', solution: [{ say: 'Let', latex: 'u = x^2' }, { say: 'Integrate', latex: '\\sin(u) + C' }] });
    expect(html).toContain('pl-answer');
    expect(html).toContain('<li class="final">');
  });

  it('asks for a derivative with its own tag, hint and placeholder (#98)', () => {
    const html = card({ topic: 'derivatives', problemLatex: "\\frac{d}{dx}\\left(x^{2}\\right)", result: 'incorrect' });
    expect(html).toContain('Differentiation — Derivatives');
    expect(html).toContain(text.calculate_derivative.replace("'", '&#x27;'));
    expect(html).toContain(text.general_hint_derivative);
    expect(html).toContain('placeholder="e.g. 2x cos(x^2)"');
  });

  it('presents combinations as a numeric problem without an integration constant', () => {
    const html = card({ topic: 'combinations', problemLatex: '\\binom{5}{2}', result: 'incorrect' });
    expect(html).toContain('Calculate the value.');
    expect(html).toContain('Check your calculation, or reveal the solution.');
    expect(html).toContain('placeholder="e.g. 3/2"');
    expect(html).not.toContain('Calculate the indefinite integral.');
    expect(html).not.toContain('>+C<');
  });

  it('presents partial fractions as an expression problem without an integration constant', () => {
    const html = card({ topic: 'partial-fractions', problemLatex: '\\frac{1}{x+1}', result: 'incorrect' });
    expect(html).toContain('Decompose into partial fractions.');
    expect(html).toContain('Check your work, or reveal the solution.');
    expect(html).not.toContain('Calculate the indefinite integral.');
    expect(html).not.toContain('>+C<');
  });

  it('offers the declared variables of a partial derivative on the keypad (#96, #101)', () => {
    const polar = 'f = x y,\\quad x = r \\cos{\\left(\\theta \\right)}:\\quad \\frac{\\partial f}{\\partial \\theta}'
      + '\\quad(r > 0,\\ \\theta \\in \\mathbb{R})';
    const html = card({ topic: 'partial-derivatives', problemLatex: polar });
    expect(html).toContain(text.calculate_partial);
    expect(html).toContain('>θ<');
    expect(html).not.toContain('>+C<');
    expect(card()).not.toContain('>θ<');
  });

  it('asks for a definite integral without a constant when the statement has bounds', () => {
    expect(card()).toContain('Calculate the indefinite integral.');
    const html = card({ problemLatex: '\\int_{0}^{1} \\left(x e^{x}\\right)\\,dx' });
    expect(html).toContain('Calculate the definite integral.');
    expect(html).not.toContain('+ C');
  });

  it('flags invalid input for assistive tech', () => {
    expect(card({ result: 'invalid', answer: 'x +' })).toContain('aria-invalid="true"');
  });
});

describe('selection controls', () => {
  it('marks exactly one topic and one level as pressed', () => {
    const chips = renderToStaticMarkup(<TopicChips topics={['basic-integrals', 'substitution', 'integration-by-parts', 'rational-functions', 'derivatives'].map(slug => ({ slug, name: slug, area: 'mathematical-analysis' as const }))} selected="substitution" onSelect={noop} />);
    expect(chips.match(/aria-pressed="true"/g)).toHaveLength(1);
    expect(chips.match(/aria-pressed="false"/g)).toHaveLength(4);
    const scale = renderToStaticMarkup(<DifficultyScale selected={3} onSelect={noop} />);
    expect(scale.match(/aria-pressed="true"/g)).toHaveLength(1);
  });
});

describe('ApiStatusNotice', () => {
  it('renders only when the API is unreachable', () => {
    expect(renderToStaticMarkup(<ApiStatusNotice health="ok" />)).toBe('');
    expect(renderToStaticMarkup(<ApiStatusNotice health="unconfigured" />)).toBe('');
    expect(renderToStaticMarkup(<ApiStatusNotice health={undefined} />)).toBe('');
    const html = renderToStaticMarkup(<ApiStatusNotice health="unreachable" />);
    expect(html).toContain('role="status"');
    expect(html).toContain('reach the PracticeLoop server');
  });
});
