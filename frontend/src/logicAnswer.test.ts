import { expect, it } from 'vitest';
import corpus from '../../backend/tests/fixtures/logic_answer_syntax.json';
import { analyseAnswer, analyseComputationalAnswer } from './answerSyntax';
import { parseAnswerInput } from './data/answerInput';
import type { ComputationalInputSpec } from './data/types';
import { renderMath } from './math';

const spec = parseAnswerInput({kind:'logic',maxBytes:256,choices:['p','q'],expected:'secret'}) as ComputationalInputSpec;
it.each(corpus)('shared propositional syntax: $text', ({text,valid}) => {
  const result = analyseComputationalAnswer(text, spec);
  expect(result.status === 'ok').toBe(valid);
  if (result.status === 'ok') expect(() => renderMath(result.latex)).not.toThrow();
});
it('keeps only declared atoms in public metadata', () => {
  expect(spec).toEqual({kind:'logic',maxBytes:256,choices:['p','q']});
  expect(() => parseAnswerInput({kind:'logic',maxBytes:256,choices:['os']})).toThrow();
});

it('allows positive literal bases only in computational formulas and rejects towers promptly', () => {
  const formula: ComputationalInputSpec = {kind:'formula',maxBytes:256,symbols:{x:'real'}};
  for (const text of ['3^x','(1/2)^x','0.5^x']) {
    expect(analyseComputationalAnswer(text,formula).status).toBe('ok');
    expect(analyseAnswer(text).status).toBe('error');
  }
  let tower = '99999999';
  for (let i=0;i<10;i++) tower = `(${tower}^12)`;
  for (const text of ['(-3)^x','0^x',`${tower}^x`]) expect(analyseComputationalAnswer(text,formula).status).toBe('error');
});
