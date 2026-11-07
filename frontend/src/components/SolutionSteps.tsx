import type { SolutionStep } from '../data/types';
import { Tex } from './Tex';
import { colorMatrixEntries, numericMatrixProduct } from '../data/matrixColors';
import { MatrixProductDiagram } from './MatrixProductDiagram';
import { DeterminantDiagram } from './DeterminantDiagram';
import { MinorExpansion } from './MinorExpansion';

function StepFormula({ latex }: { latex: string }) {
  // Row operations are clearer above the augmented matrix on narrow screens.
  const separator = String.raw`\quad \left[\begin{array}`;
  const split = latex.indexOf(separator);
  if (split < 0) return <span className="m" tabIndex={0}><Tex latex={latex} /></span>;
  const operation = latex.slice(0, split);
  const matrix = latex.slice(split + String.raw`\quad `.length);
  const rows = [...operation.matchAll(/R_\{(\d+)\}/g)].map(match => Number(match[1]));
  const target = rows[0], reference = rows.find(row => row !== target);
  const array = matrix.match(/^(\\left\[\\begin\{array\}\{[^}]+\})([\s\S]*)(\\end\{array\}\\right\])$/);
  if (!target || !array) return <><span className="m" tabIndex={0}><Tex latex={operation} /></span><span className="m" tabIndex={0}><Tex latex={matrix} /></span></>;
  const rowColor = (row: number) => row === target ? '#65df91' : row === reference ? '#5fa8ff' : null;
  const coloredOperation = operation.replace(/R_\{(\d+)\}/g, (match, row: string) => {
    const color = rowColor(Number(row));
    return color ? String.raw`\color{${color}}{${match}}` : match;
  });
  const coloredRows = array[2].split(String.raw`\\`).map((row, index) => {
    const color = rowColor(index + 1);
    return color ? row.split('&').map(cell => String.raw`\color{${color}}{${cell}}`).join('&') : row;
  });
  const coloredMatrix = array[1] + coloredRows.join(String.raw`\\`) + array[3];
  const swap = operation.includes(String.raw`\leftrightarrow`);
  return <>
    <span className="m" tabIndex={0}><Tex latex={coloredOperation} /></span>
    <span className="m" tabIndex={0}><Tex latex={coloredMatrix} /></span>
    <span className="pl-row-legend pl-small"><span className="pl-row-target">{swap ? 'Exchanged row' : 'Modified row'}</span>{reference && <> · <span className="pl-row-reference">{swap ? 'Other exchanged row' : 'Reference row'}</span></>}</span>
  </>;
}

/** The full step-by-step solution, shown only after Show Solution. */
export function SolutionSteps({ steps, matrixStatement, colorEntries = true }: { steps: readonly SolutionStep[]; matrixStatement?: string; colorEntries?: boolean }) {
  const statementProduct = matrixStatement ? numericMatrixProduct(matrixStatement) : null;
  const rewriteIndex = matrixStatement && !statementProduct ? steps.findIndex(step => numericMatrixProduct(step.latex)) : -1;
  const product = statementProduct ?? (rewriteIndex >= 0 ? numericMatrixProduct(steps[rewriteIndex].latex) : null);
  const multiplyIndex = statementProduct && steps.length === 3 ? 1 : rewriteIndex >= 0 ? rewriteIndex + 1 : -1;
  return (
    <ol className="pl-steps pl-fade" aria-label="Solution">
      {matrixStatement && <li><div><div className="m" tabIndex={0}><Tex latex={colorEntries ? colorMatrixEntries(matrixStatement, !!statementProduct) : matrixStatement} /></div></div></li>}
      {steps.map((step, index) => (
        <li key={index} className={index === steps.length - 1 ? 'final' : undefined}>
          <div>
            {product && index === multiplyIndex && step.latex.includes(String.raw`\cdot`) && step.latex.includes(String.raw`\begin{`) ? <>
              <strong>Multiply the matrices</strong>
              <MatrixProductDiagram matrices={product} />
              <details className="pl-solution-detail"><summary className="pl-small pl-muted">Show explanation</summary><div className="say">{step.say}</div></details>
            </> : matrixStatement ? <>
              {step.determinantMatrix && <DeterminantDiagram matrix={step.determinantMatrix} />}
              {step.minorExpansion && <MinorExpansion expansion={step.minorExpansion} />}
              <details className="pl-solution-detail">
              <summary><StepFormula latex={product || !colorEntries ? step.latex : colorMatrixEntries(step.latex)} /><span className="pl-small pl-muted">Show explanation</span></summary>
              <div className="say">{step.say}</div>
            </details></> : step.rules?.length ? <details className="pl-solution-detail">
              <summary><span className="say">{step.say}</span><StepFormula latex={step.latex} /><span className="pl-small pl-muted">Show formula and explanation</span></summary>
              {step.rules.map(rule => <div className="pl-rule" key={rule.title}>
                <strong className="pl-small">{rule.title}</strong>
                <StepFormula latex={rule.latex} />
                <p className="say">{rule.explanation}</p>
              </div>)}
            </details> : <>
              <div className="say">{step.say}</div>
              <div className="m" tabIndex={0}><Tex latex={step.latex} /></div>
            </>}
          </div>
        </li>
      ))}
    </ol>
  );
}
