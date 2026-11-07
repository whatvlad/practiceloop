/** Show the diagonals used by the 2×2 rule or Sarrus' 3×3 rule. */
export function DeterminantDiagram({ matrix }: { matrix: number[][] }) {
  const size = matrix.length;
  if ((size !== 2 && size !== 3) || matrix.some(row => row.length !== size || row.some(n => !Number.isSafeInteger(n)))) return null;
  const columns = size === 3 ? 5 : 2;
  const dx = 48, dy = 44, left = 28, top = 38;
  const x = (column: number) => left + column * dx;
  const y = (row: number) => top + row * dy;
  const width = left * 2 + (columns - 1) * dx;
  const height = top + (size - 1) * dy + 25;
  const starts = size === 3 ? [0, 1, 2] : [0];
  return <div className="pl-det-visual">
    <p className="pl-small pl-muted"><span className="pl-det-plus">+ downward diagonals</span> · <span className="pl-det-minus">− upward diagonals</span></p>
    <div className="pl-det-scroll" tabIndex={0} aria-label="Determinant diagonals, scroll horizontally">
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${size} by ${size} determinant diagonal diagram`}>
        {starts.map(start => <line key={`plus-${start}`} className="pl-det-line pl-det-line-plus" x1={x(start)} y1={y(0)} x2={x(start + size - 1)} y2={y(size - 1)} />)}
        {starts.map(start => <line key={`minus-${start}`} className="pl-det-line pl-det-line-minus" x1={x(start)} y1={y(size - 1)} x2={x(start + size - 1)} y2={y(0)} />)}
        <path className="pl-det-bracket" d={`M ${left - 12} ${top - 18} h -8 v ${(size - 1) * dy + 36} h 8 M ${x(size - 1) + 12} ${top - 18} h 8 v ${(size - 1) * dy + 36} h -8`} />
        {matrix.map((row, i) => Array.from({ length: columns }, (_, j) => <text key={`${i}-${j}`} x={x(j)} y={y(i)} className={j >= size ? 'pl-det-repeat' : undefined}>{row[j % size]}</text>))}
      </svg>
    </div>
  </div>;
}
