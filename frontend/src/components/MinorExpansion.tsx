import { useState } from 'react';

type Expansion = { matrix: number[][]; row: number; columns: number[] };

export function MinorExpansion({ expansion }: { expansion: Expansion }) {
  const [selected, setSelected] = useState<number | null>(null);
  const { matrix, row, columns } = expansion;
  const size = matrix.length;
  if (size < 2 || size > 5 || !Number.isInteger(row) || row < 0 || row >= size
      || matrix.some(line => line.length !== size || line.some(value => !Number.isSafeInteger(value)))
      || columns.some(col => !Number.isInteger(col) || col < 0 || col >= size)) return null;
  return <div className="pl-minor-expansion">
    <p className="pl-small pl-muted">Select a minor to see its entries in the parent matrix.</p>
    <div className="pl-minor-scroll" tabIndex={0} aria-label="Parent matrix and minors, scroll horizontally">
      <p className="pl-small">Cofactor signs: sign = (−1)<sup>row + column</sup></p>
      <div className="pl-cofactor-signs" role="grid" aria-label="Cofactor sign checkerboard">
        {matrix.map((line, i) => <div role="row" key={i}>{line.map((_, j) => <span role="gridcell" key={j}
          className={`${(i + j) % 2 === 0 ? 'is-positive' : 'is-negative'}${i === row && j === selected ? ' is-active' : ''}`}>{(i + j) % 2 === 0 ? '+' : '−'}</span>)}</div>)}
      </div>
      <p className="pl-small">Parent matrix</p>
      <div className="pl-minor-parent" role="grid" aria-label="Parent matrix">
        {matrix.map((line, i) => <div role="row" key={i}>{line.map((value, j) => <span role="gridcell" key={j}
          className={selected === null ? undefined : i === row || j === selected ? 'is-excluded' : 'is-included'}>{value}</span>)}</div>)}
      </div>
      <div className="pl-minor-options">
        {columns.map(col => {
          const coefficient = (row + col) % 2 === 0 ? matrix[row][col] : -matrix[row][col];
          const minor = matrix.filter((_, i) => i !== row).map(line => line.filter((_, j) => j !== col));
          return <div className="pl-minor-choice" key={col}>
            <span className="pl-small">{coefficient >= 0 ? '+' : '−'}{Math.abs(coefficient)} ×</span>
            <button type="button" aria-pressed={selected === col} aria-label={`Minor: remove row ${row + 1}, column ${col + 1}`}
              onClick={() => setSelected(col)}>
              {minor.map((line, i) => <span className="pl-minor-row" key={i}>{line.map((value, j) => <span key={j}>{value}</span>)}</span>)}
            </button>
          </div>;
        })}
      </div>
    </div>
    <p className="pl-small pl-muted" aria-live="polite">{selected === null ? 'Select a minor to check its cofactor sign.' : `Row ${row + 1} and column ${selected + 1} are removed. The cofactor sign is ${(row + selected) % 2 === 0 ? '+' : '−'}. Multiplying this sign by ${matrix[row][selected]} gives the coefficient ${(row + selected) % 2 === 0 ? matrix[row][selected] : -matrix[row][selected]}.`}</p>
  </div>;
}
