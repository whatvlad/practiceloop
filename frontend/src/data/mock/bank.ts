// TEMPORARY STUB. Stands in for the backend rule engine (PL-006, PL-009) until
// the API exists. It is the only frontend file that holds answers and
// solutions, and only ./server.ts may import it (enforced by ESLint).
// Difficulty does not change the problem here; the real generator decides that.

import type { SolutionStep, TopicSlug } from '../types';

export interface MockTemplate {
  id: string;
  topic: TopicSlug;
  problemLatex: string;
  answerLatex: string;
  /** Typed forms the stand-in checker accepts, before normalisation. */
  accepted: string[];
  steps: SolutionStep[];
}

export const BANK: readonly MockTemplate[] = [
  {
    id: 'basic-power',
    topic: 'basic-integrals',
    problemLatex: '\\int 3x^2\\,dx',
    answerLatex: 'x^3 + C',
    accepted: ['x^3'],
    steps: [
      { say: 'Use the power rule', latex: '\\int x^n\\,dx = \\frac{x^{n+1}}{n+1} + C' },
      { say: 'Apply it with n = 2', latex: '\\int 3x^2\\,dx = 3\\cdot\\frac{x^3}{3} + C' },
      { say: 'Simplify', latex: '= x^3 + C' },
    ],
  },
  {
    id: 'basic-poly',
    topic: 'basic-integrals',
    problemLatex: '\\int (4x^3 + 2x)\\,dx',
    answerLatex: 'x^4 + x^2 + C',
    accepted: ['x^4+x^2', 'x^2+x^4'],
    steps: [
      { say: 'Integrate term by term', latex: '\\int 4x^3\\,dx + \\int 2x\\,dx' },
      { say: 'Use the power rule', latex: '= x^4 + x^2 + C' },
    ],
  },
  {
    id: 'sub-cos',
    topic: 'substitution',
    problemLatex: '\\int 2x\\cos(x^2)\\,dx',
    answerLatex: '\\sin(x^2) + C',
    accepted: ['sin(x^2)'],
    steps: [
      { say: 'Let', latex: 'u = x^2' },
      { say: 'Then', latex: 'du = 2x\\,dx' },
      { say: 'Therefore', latex: '\\int 2x\\cos(x^2)\\,dx = \\int \\cos(u)\\,du' },
      { say: 'Integrate', latex: '= \\sin(u) + C' },
      { say: 'Substitute back', latex: '= \\sin(x^2) + C' },
    ],
  },
  {
    id: 'sub-exp',
    topic: 'substitution',
    problemLatex: '\\int 3x^2 e^{x^3}\\,dx',
    answerLatex: 'e^{x^3} + C',
    accepted: ['e^(x^3)', 'e^x^3', 'exp(x^3)'],
    steps: [
      { say: 'Let', latex: 'u = x^3' },
      { say: 'Then', latex: 'du = 3x^2\\,dx' },
      { say: 'Therefore', latex: '\\int 3x^2 e^{x^3}\\,dx = \\int e^u\\,du' },
      { say: 'Integrate', latex: '= e^u + C' },
      { say: 'Substitute back', latex: '= e^{x^3} + C' },
    ],
  },
  {
    id: 'parts-exp',
    topic: 'integration-by-parts',
    problemLatex: '\\int x e^{x}\\,dx',
    answerLatex: 'x e^{x} - e^{x} + C',
    accepted: ['xe^x-e^x', '(x-1)e^x', 'e^x(x-1)', '-e^x+xe^x'],
    steps: [
      { say: 'Let', latex: 'u = x,\\quad dv = e^{x}\\,dx' },
      { say: 'Then', latex: 'du = dx,\\quad v = e^{x}' },
      { say: 'By parts', latex: '\\int x e^{x}\\,dx = x e^{x} - \\int e^{x}\\,dx' },
      { say: 'Integrate', latex: '= x e^{x} - e^{x} + C' },
    ],
  },
  {
    id: 'parts-cos',
    topic: 'integration-by-parts',
    problemLatex: '\\int x\\cos x\\,dx',
    answerLatex: 'x\\sin x + \\cos x + C',
    accepted: ['xsin(x)+cos(x)', 'cos(x)+xsin(x)', 'xsinx+cosx', 'cosx+xsinx'],
    steps: [
      { say: 'Let', latex: 'u = x,\\quad dv = \\cos x\\,dx' },
      { say: 'Then', latex: 'du = dx,\\quad v = \\sin x' },
      { say: 'By parts', latex: '\\int x\\cos x\\,dx = x\\sin x - \\int \\sin x\\,dx' },
      { say: 'Integrate', latex: '= x\\sin x + \\cos x + C' },
    ],
  },
  {
    id: 'rational-partial',
    topic: 'rational-functions',
    problemLatex: '\\int \\frac{1}{x^2-1}\\,dx',
    answerLatex: '\\frac{1}{2}\\ln\\left|\\frac{x-1}{x+1}\\right| + C',
    accepted: ['1/2ln|(x-1)/(x+1)|', '(1/2)ln|(x-1)/(x+1)|', 'ln|(x-1)/(x+1)|/2'],
    steps: [
      { say: 'Split into partial fractions', latex: '\\frac{1}{x^2-1} = \\frac{1}{2}\\left(\\frac{1}{x-1} - \\frac{1}{x+1}\\right)' },
      { say: 'Integrate each term', latex: '= \\frac{1}{2}\\ln|x-1| - \\frac{1}{2}\\ln|x+1| + C' },
      { say: 'Combine the logarithms', latex: '= \\frac{1}{2}\\ln\\left|\\frac{x-1}{x+1}\\right| + C' },
    ],
  },
  {
    id: 'rational-log',
    topic: 'rational-functions',
    problemLatex: '\\int \\frac{2x}{x^2+1}\\,dx',
    answerLatex: '\\ln(x^2+1) + C',
    accepted: ['ln(x^2+1)', 'ln(1+x^2)', 'ln|x^2+1|', 'log(x^2+1)'],
    steps: [
      { say: 'Notice the numerator is the derivative of the denominator', latex: '\\frac{d}{dx}(x^2+1) = 2x' },
      { say: 'Therefore', latex: '\\int \\frac{f\'(x)}{f(x)}\\,dx = \\ln|f(x)| + C' },
      { say: 'Since x² + 1 > 0', latex: '= \\ln(x^2+1) + C' },
    ],
  },
  {
    id: 'trig-sin2',
    topic: 'trigonometric-integrals',
    problemLatex: '\\int \\sin^2 x\\,dx',
    answerLatex: '\\frac{x}{2} - \\frac{\\sin 2x}{4} + C',
    accepted: ['x/2-sin(2x)/4', 'x/2-sin(x)cos(x)/2', '(x-sin(x)cos(x))/2'],
    steps: [
      { say: 'Use the half-angle identity', latex: '\\sin^2 x = \\frac{1 - \\cos 2x}{2}' },
      { say: 'Then', latex: '\\int \\sin^2 x\\,dx = \\int \\frac{1}{2}\\,dx - \\int \\frac{\\cos 2x}{2}\\,dx' },
      { say: 'Integrate', latex: '= \\frac{x}{2} - \\frac{\\sin 2x}{4} + C' },
    ],
  },
  {
    id: 'trig-cos3',
    topic: 'trigonometric-integrals',
    problemLatex: '\\int \\cos^3 x\\,dx',
    answerLatex: '\\sin x - \\frac{\\sin^3 x}{3} + C',
    accepted: ['sin(x)-sin(x)^3/3', 'sinx-sin^3x/3', 'sin(x)-(sin(x))^3/3', 'sin(x)-sin^3(x)/3'],
    steps: [
      { say: 'Split off one factor', latex: '\\cos^3 x = (1 - \\sin^2 x)\\cos x' },
      { say: 'Let', latex: 'u = \\sin x,\\quad du = \\cos x\\,dx' },
      { say: 'Therefore', latex: '\\int (1 - u^2)\\,du = u - \\frac{u^3}{3} + C' },
      { say: 'Substitute back', latex: '= \\sin x - \\frac{\\sin^3 x}{3} + C' },
    ],
  },
];
