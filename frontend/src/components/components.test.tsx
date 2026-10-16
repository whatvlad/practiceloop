import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
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

  it('flags invalid input for assistive tech', () => {
    expect(card({ result: 'invalid', answer: 'x +' })).toContain('aria-invalid="true"');
  });
});

describe('selection controls', () => {
  it('marks exactly one topic and one level as pressed', () => {
    const chips = renderToStaticMarkup(<TopicChips selected="substitution" onSelect={noop} />);
    expect(chips.match(/aria-pressed="true"/g)).toHaveLength(1);
    expect(chips.match(/aria-pressed="false"/g)).toHaveLength(4);
    const scale = renderToStaticMarkup(<DifficultyScale selected={3} onSelect={noop} />);
    expect(scale.match(/aria-pressed="true"/g)).toHaveLength(1);
  });
});
