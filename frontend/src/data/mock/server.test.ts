import { beforeEach, describe, expect, it } from 'vitest';
import { BANK } from './bank';
import * as server from './server';

const PUBLIC_KEYS = [
  'answerRevealed',
  'createdAt',
  'difficulty',
  'id',
  'lastAnswer',
  'lastResult',
  'problemLatex',
  'solutionRevealed',
  'topic',
];

describe('mock server boundary', () => {
  beforeEach(() => server.resetMockServer());

  it('returns only public fields for problems', async () => {
    const generated = await server.generateProblem('substitution', 2);
    const listed = await server.listProblems();
    for (const problem of [generated, ...listed]) {
      expect(Object.keys(problem).sort()).toEqual(PUBLIC_KEYS);
    }
    const template = BANK.find((t) => t.problemLatex === generated.problemLatex);
    expect(JSON.stringify(listed)).not.toContain(template?.answerLatex);
  });

  it('records attempts and reveals like the API will', async () => {
    const problem = await server.generateProblem('basic-integrals', 1);
    expect(await server.submitAttempt(problem.id, 'x^(')).toBe('invalid');
    expect((await server.getProblem(problem.id)).lastResult).toBeNull();
    const result = await server.submitAttempt(problem.id, 'wrong + C');
    expect(result).toBe('incorrect');
    const { answerLatex } = await server.revealAnswer(problem.id);
    expect(answerLatex).toMatch(/\+ C$/);
    const reopened = await server.getProblem(problem.id);
    expect(reopened).toMatchObject({ lastResult: 'incorrect', lastAnswer: 'wrong + C', answerRevealed: true, solutionRevealed: false });
    expect((await server.revealSolution(problem.id)).steps.length).toBeGreaterThan(0);
  });

  it('counts generated, attempted and correct problems', async () => {
    const before = await server.getProfileCounts();
    const problem = await server.generateProblem('substitution', 3);
    const template = BANK.find((t) => t.problemLatex === problem.problemLatex);
    await server.submitAttempt(problem.id, template?.accepted[0] ?? '');
    expect(await server.getProfileCounts()).toEqual({
      generated: before.generated + 1,
      attempted: before.attempted + 1,
      correct: before.correct + 1,
    });
  });

  it('rejects unknown ids', async () => {
    await expect(server.getProblem('missing')).rejects.toBeInstanceOf(server.NotFoundError);
  });

  it('has a template for every topic and renders every formula', async () => {
    const { TOPICS } = await import('../topics');
    const { renderMath } = await import('../../math');
    for (const topic of TOPICS) expect(BANK.some((t) => t.topic === topic.slug), topic.slug).toBe(true);
    for (const t of BANK) {
      for (const latex of [t.problemLatex, t.answerLatex, ...t.steps.map((s) => s.latex)]) {
        expect(() => renderMath(latex), latex).not.toThrow();
      }
    }
  });
});
