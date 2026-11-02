import type { TopicSlug } from '../data/types';
import { displayProblem } from '../format';
import { Tex } from './Tex';

export function ProblemStatement({ topic, problemLatex }: { topic: TopicSlug; problemLatex: string }) {
  const { instruction, formula } = displayProblem(topic, problemLatex);
  return (
    <div className="pl-stack pl-gap-3">
      <p className="pl-lead">{instruction}</p>
      <div className="pl-expr"><Tex latex={formula} display /></div>
    </div>
  );
}
