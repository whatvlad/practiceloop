import type { SolutionStep } from '../data/types';
import { Tex } from './Tex';

/** The full step-by-step solution, shown only after Show Solution. */
export function SolutionSteps({ steps }: { steps: readonly SolutionStep[] }) {
  return (
    <ol className="pl-steps pl-fade" aria-label="Solution">
      {steps.map((step, index) => (
        <li key={index} className={index === steps.length - 1 ? 'final' : undefined}>
          <div>
            <div className="say">{step.say}</div>
            <div className="m">
              <Tex latex={step.latex} />
            </div>
          </div>
        </li>
      ))}
    </ol>
  );
}
