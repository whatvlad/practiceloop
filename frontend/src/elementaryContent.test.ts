import { expect, it } from 'vitest';
import golden from '../../backend/tests/fixtures/engine_golden_v1.json';
import { renderMath } from './math';

it.each(Object.entries(golden).filter(([version]) => version.startsWith('elementary-')))(
  'renders every new golden statement, complete answer and worked step: %s',
  (_version, examples) => {
    for (const example of examples) {
      for (const match of example.statement.matchAll(/\\\((.*?)\\\)/gs)) expect(() => renderMath(match[1])).not.toThrow();
      expect(() => renderMath(example.answer_latex)).not.toThrow();
      for (const [,latex] of example.steps) expect(() => renderMath(latex)).not.toThrow();
    }
  },
);
