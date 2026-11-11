import { expect, it } from 'vitest';
import corpus from '../../backend/tests/fixtures/computational_answer_syntax.json';
import { analyseComputationalAnswer } from './answerSyntax';
import { parseAnswerInput } from './data/answerInput';
import type { ComputationalInputSpec } from './data/types';
import { renderMath } from './math';

it.each(corpus)('shared computational syntax: $text', ({ contract, text, valid }) => {
  const spec = parseAnswerInput(contract) as ComputationalInputSpec;
  const result = analyseComputationalAnswer(text, spec);
  expect(result.status === 'ok').toBe(valid);
  if (result.status === 'ok') expect(() => renderMath(result.latex)).not.toThrow();
});

it('applies aggregate budgets to nested components and does not decide equality', () => {
  const spec: ComputationalInputSpec = { kind: 'tuple', maxBytes: 256,
    components: Array(8).fill({ kind: 'formula', maxBytes: 256 }), labels: Array(8).fill('Value') };
  expect(analyseComputationalAnswer(`(${Array(8).fill('sin(cos(sin(1)))').join(';')})`, spec).status).toBe('error');
  const formula: ComputationalInputSpec = { kind: 'formula', maxBytes: 256, symbols: { x: 'real' } };
  expect(analyseComputationalAnswer('x/x', formula).status).toBe('ok'); // domain correctness belongs to the worker
});

it('projects only safe metadata recursively and rejects oversized or unknown schemas', () => {
  expect(parseAnswerInput({ kind: 'tuple', maxBytes: 256, labels: ['Value'], expected: 12,
    components: [{ kind: 'formula', maxBytes: 256, expected: 'secret', symbols: { a: 'positive' } }] }))
    .toEqual({ kind: 'tuple', maxBytes: 256, labels: ['Value'], components: [{ kind: 'formula', maxBytes: 256, symbols: { a: 'positive' } }] });
  expect(() => parseAnswerInput({ kind: 'formula', maxBytes: 256, symbols: { os: 'real' } })).toThrow();
  expect(() => parseAnswerInput({ kind: 'category', maxBytes: 256, choices: ['__proto__', 'ok'] })).toThrow();
  expect(() => parseAnswerInput({ kind: 'tuple', maxBytes: 256, components: Array(9).fill({ kind: 'formula', maxBytes: 256 }), labels: Array(9).fill('Value') })).toThrow();
});

it('accepts the declared symbolic mass used by inertia exercises', () => {
  const formula = parseAnswerInput({ kind: 'formula', maxBytes: 256, symbols: { m: 'positive' } }) as ComputationalInputSpec;
  expect(analyseComputationalAnswer('m*(pi-2)/(4*pi)', formula).status).toBe('ok');
  expect(analyseComputationalAnswer('x*m', formula).status).toBe('error');
});
