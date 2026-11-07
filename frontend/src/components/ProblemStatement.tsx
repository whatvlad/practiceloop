import { useLayoutEffect, useRef } from 'react';
import type { TopicSlug } from '../data/types';
import { displayProblem } from '../format';
import { Tex } from './Tex';

// Below this a formula stops being comfortable to read, so it scrolls instead.
const SMALLEST_FORMULA_PX = 18;

/** Shrinks a long formula to fit its box, so no part of the statement is hidden behind a scrollbar. */
function useFittedFormula(formula: string) {
  const box = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    const element = box.current;
    if (!element) return;
    const fit = () => {
      element.style.fontSize = '';
      const { clientWidth, scrollWidth } = element;
      if (!clientWidth || scrollWidth <= clientWidth) return;
      const size = parseFloat(getComputedStyle(element).fontSize);
      const style = getComputedStyle(element);
      const padding = parseFloat(style.paddingLeft) + parseFloat(style.paddingRight);
      const scale = (clientWidth - padding) / (scrollWidth - padding);
      element.style.fontSize = `${Math.max(SMALLEST_FORMULA_PX, Math.floor(size * scale))}px`;
    };
    fit();
    let width = element.clientWidth;
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(() => {
      if (element.clientWidth === width) return;
      width = element.clientWidth;
      fit();
    });
    observer?.observe(element);
    let active = true;
    // KaTeX's fonts change the width once they load.
    void document.fonts?.ready.then(() => { if (active) fit(); });
    return () => { active = false; observer?.disconnect(); };
  }, [formula]);
  return box;
}

export function ProblemStatement({ topic, problemLatex }: { topic: TopicSlug; problemLatex: string }) {
  const { instruction, formula } = displayProblem(topic, problemLatex);
  const box = useFittedFormula(formula);
  return (
    <div className="pl-stack pl-gap-3">
      <p className="pl-lead">{instruction}</p>
      <div className="pl-expr" ref={box} tabIndex={0} role="group" aria-label="Problem formula"><Tex latex={formula} display /></div>
    </div>
  );
}
