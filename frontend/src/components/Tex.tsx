import { useMemo } from 'react';
import { renderMath } from '../math';

interface TexProps {
  latex: string;
  display?: boolean;
}

/** KaTeX output with trusted commands disabled; falls back to the source text. */
export function Tex({ latex, display = false }: TexProps) {
  const html = useMemo(() => {
    try {
      return renderMath(latex, display);
    } catch {
      return null;
    }
  }, [latex, display]);
  if (html === null) return <code className="pl-mono">{latex}</code>;
  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}
