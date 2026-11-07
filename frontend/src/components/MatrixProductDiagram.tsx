import { useId, useState } from 'react';
import { productColors } from '../data/matrixColors';
import { Tex } from './Tex';

/** Select an entry of AB to see the matching row, column and scalar products. */
export function MatrixProductDiagram({ matrices }: { matrices: [number[][], number[][]] }) {
  const [row, setRow] = useState(0);
  const [column, setColumn] = useState(0);
  const id = useId().replace(/:/g, '');
  const [a, b] = matrices;
  const activeRow = Math.min(row, a.length - 1), activeColumn = Math.min(column, b[0].length - 1);
  const value = (i: number, j: number) => a[i].reduce((sum, n, k) => sum + n * b[k][j], 0);
  const formula = a[activeRow].map((n, k) => String.raw`\color{${productColors[k]}}{(${n})\cdot(${b[k][activeColumn]})}`).join('+') + `=${value(activeRow, activeColumn)}`;
  const cellWidth = 50, cellHeight = 42, left = 25, top = 30;
  const dividerX = left + a[0].length * cellWidth + 10;
  const dividerY = top + b.length * cellHeight + 12;
  const resultX = dividerX + 28, resultY = dividerY + 26;
  const width = resultX + b[0].length * cellWidth + 5;
  const height = resultY + (a.length - 1) * cellHeight + 30;
  const ax = (j: number) => left + j * cellWidth + 15;
  const ay = (i: number) => resultY + i * cellHeight;
  const bx = (j: number) => resultX + j * cellWidth;
  const by = (i: number) => top + i * cellHeight;
  return <div className="pl-product-visual">
    <p className="pl-small pl-muted">Select a result to see how its row and column are multiplied.</p>
    <div className="pl-product-scroll" tabIndex={0} aria-label="Matrix multiplication diagram, scroll horizontally">
      <svg className="pl-product-grid" width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="group" aria-label="Matrix multiplication diagram">
        <defs>{productColors.map((color, k) => <marker key={color} id={`${id}-arrow-${k}`} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10" fill="none" stroke={color} strokeWidth="1.8" /></marker>)}</defs>
        <line className="pl-product-divider" x1={dividerX} y1="10" x2={dividerX} y2={height} />
        <line className="pl-product-divider" x1="0" y1={dividerY} x2={width} y2={dividerY} />
        {a[activeRow].map((_, k) => <line key={k} className="pl-product-arrow" x1={ax(k)} y1={ay(activeRow) - 15} x2={bx(activeColumn) - 17} y2={by(k)} stroke={productColors[k]} markerStart={`url(#${id}-arrow-${k})`} markerEnd={`url(#${id}-arrow-${k})`} />)}
        {b.map((line, i) => line.map((n, j) => <text key={`b-${i}-${j}`} x={bx(j)} y={by(i)} fill={j === activeColumn ? productColors[i] : 'currentColor'} className={j === activeColumn ? 'pl-product-active' : undefined}>{n}</text>))}
        {a.map((line, i) => line.map((n, j) => <text key={`a-${i}-${j}`} x={ax(j)} y={ay(i)} fill={i === activeRow ? productColors[j] : 'currentColor'} className={i === activeRow ? 'pl-product-active' : undefined}>{n}</text>))}
        {a.map((_, i) => b[0].map((_, j) => <foreignObject key={`result-${i}-${j}`} x={bx(j) - 20} y={ay(i) - 18} width="40" height="36"><button type="button" className={i === activeRow && j === activeColumn ? 'selected' : undefined} aria-label={`Result row ${i + 1}, column ${j + 1}: ${value(i, j)}`} aria-pressed={i === activeRow && j === activeColumn} onClick={() => { setRow(i); setColumn(j); }}>{value(i, j)}</button></foreignObject>))}
      </svg>
      <div className="pl-product-formula"><Tex latex={formula} /></div>
    </div>
  </div>;
}
