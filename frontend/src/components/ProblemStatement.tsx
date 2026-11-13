import { useLayoutEffect, useRef } from 'react';
import type { TopicSlug } from '../data/types';
import { displayProblem } from '../format';
import { Plot2dView } from '../visual/Plot2dView';
import type { Plot2dSpec } from '../visual/spec';
import { Tex } from './Tex';

// Below this a formula stops being comfortable to read, so it scrolls instead.
const SMALLEST_FORMULA_PX = 18;

/** Split only outer plain-text commands and separators; keep grouped maths intact. */
function geometryFragments(latex: string) {
  const parts: { text?: string; math?: string }[] = [];
  let start = 0;
  let depth = 0;
  const math = (end: number) => {
    const value = latex.slice(start, end).replace(/^(?:\s|\\ )+|(?:\s|\\ )+$/g, '');
    if (value) parts.push({ math: value });
  };
  for (let i = 0; i < latex.length; i++) {
    const remaining = latex.slice(i);
    const prose = depth === 0 ? remaining.match(/^\\text\{([^{}]*)\}/) : null;
    if (prose) {
      math(i);
      parts.push({ text: prose[1] });
      i += prose[0].length - 1;
      start = i + 1;
    } else if (depth === 0 && latex[i] === ',') {
      math(i);
      parts.push({ text: ', ' });
      start = i + 1;
    } else if (/^\\(?:left|begin)\b/.test(remaining)) {
      depth++;
    } else if (/^\\(?:right|end)\b/.test(remaining)) {
      depth = Math.max(0, depth - 1);
    } else if (latex[i] === '\\' && /[{}(),\\]/.test(latex[i + 1] ?? '')) {
      i++;
    } else if ('{(['.includes(latex[i])) {
      depth++;
    } else if ('})]'.includes(latex[i])) {
      depth = Math.max(0, depth - 1);
    }
  }
  math(latex.length);
  return parts;
}

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

export function ProblemStatement({ topic, problemLatex, promptVisual }: {
  topic: TopicSlug; problemLatex: string; promptVisual?: Plot2dSpec;
}) {
  const { instruction, formula } = displayProblem(topic, problemLatex);
  const box = useFittedFormula(formula);
  if ((topic === 'vectors' || topic === 'lines-and-planes') && problemLatex.startsWith('\\text{')) {
    return <div className="pl-geometry-statement" role="group" aria-label="Problem statement">
      {geometryFragments(problemLatex).map((part, index) => part.math !== undefined
        ? <span key={index} className="pl-geometry-given" tabIndex={0}><Tex latex={part.math} /></span>
        : <span key={index}>{part.text}</span>)}
    </div>;
  }
  return (
    <div className="pl-stack pl-gap-3">
      <p className="pl-lead">{instruction}</p>
      <div className="pl-expr" ref={box} tabIndex={0} role="group" aria-label="Problem formula"><Tex latex={formula} display /></div>
      {promptVisual && <Plot2dView spec={promptVisual} />}
    </div>
  );
}
