import { describe, expect, it } from 'vitest';
import corpus from '../../backend/tests/fixtures/structured_answer_syntax.json';
import { analyseStructuredAnswer } from './answerSyntax';
import { renderMath } from './math';
import { parseAnswerInput } from './data/answerInput';
import type { LegacyAnswerInputSpec } from './data/types';

describe('structured grammar shared with the backend', () => {
  it.each(corpus)('$kind: $text', ({ kind, text, valid }) => {
    const result = analyseStructuredAnswer(text, kind as LegacyAnswerInputSpec['kind']);
    expect(result.status === 'ok').toBe(valid);
    if (result.status === 'ok') expect(() => renderMath(result.latex)).not.toThrow();
  });
  it('applies the byte and function budget to the whole structured input', () => {
    expect(analyseStructuredAnswer(`{${'1'.repeat(257)}}`, 'finite_set').status).toBe('error');
    expect(analyseStructuredAnswer(`{${Array(8).fill('sin(cos(sin(1)))').join(',')}}`, 'finite_set').status).toBe('error');
  });
  it('retains only allowlisted input instructions', () => {
    expect(parseAnswerInput({ kind: 'interval', maxBytes: 256, expected: [1,2] })).toEqual({ kind: 'interval', maxBytes: 256 });
    expect(() => parseAnswerInput({ kind: 'expression', maxBytes: 256 })).toThrow();
    expect(() => parseAnswerInput({ kind: 'finite_set', maxBytes: 256, maxItems: 999 })).toThrow();
  });
});
