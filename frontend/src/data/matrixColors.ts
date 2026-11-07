// The same matrix position keeps the same color across the original operands.
export const productColors = ['#5fa8ff', '#ffab4d', '#65df91', '#d99bff', '#ff829d'];
const colors = [
  '#5fa8ff', '#65df91', '#ffab4d', '#d99bff', '#ff829d',
  '#32a7af', '#b99b1b', '#9b7fea', '#d97846', '#629535',
  '#779deb', '#ba6e9c', '#478f9c', '#c28563', '#8e9b38',
  '#8e78b9', '#c96950', '#4b9a80', '#b98d35', '#8492c0',
  '#ca7594', '#559db9', '#a687bb', '#b88343', '#718d50',
];

export function colorMatrixEntries(latex: string, product = false): string {
  let matrixIndex = 0;
  return latex.replace(/\\begin\{(p|b)matrix\}([\s\S]*?)\\end\{\1matrix\}/g, (_whole, kind: string, body: string) => {
    const operand = matrixIndex++;
    const rows = body.split(String.raw`\\`);
    const colored = rows.map((row, i) => row.split('&').map((cell, j) =>
      String.raw`\color{${product ? productColors[operand === 0 ? j : i] : colors[(i * 5 + j) % colors.length]}}{${cell}}`).join('&'));
    return String.raw`\begin{${kind}matrix}${colored.join(String.raw`\\`)}\end{${kind}matrix}`;
  });
}

/** Parse only a product of two numeric matrices; other exercises keep their usual display. */
export function numericMatrixProduct(latex: string): [number[][], number[][]] | null {
  const matches = [...latex.matchAll(/\\begin\{(p|b)matrix\}([\s\S]*?)\\end\{\1matrix\}/g)];
  if (matches.length !== 2) return null;
  if (latex.slice(matches[1].index! + matches[1][0].length).trimStart().startsWith('^')) return null;
  const between = latex.slice(matches[0].index! + matches[0][0].length, matches[1].index).trim();
  if (between !== '' && between !== String.raw`\cdot` && between !== String.raw`\times`) return null;
  const parse = (body: string) => body.split(String.raw`\\`).map(row => row.split('&').map(cell => {
    const value = cell.trim();
    return /^-?\d+$/.test(value) ? Number(value) : NaN;
  }));
  const a = parse(matches[0][2]), b = parse(matches[1][2]);
  if (!a.length || !b.length || !a[0].length || !b[0].length || a[0].length !== b.length
      || a.some(row => row.length !== a[0].length || row.some(value => !Number.isSafeInteger(value)))
      || b.some(row => row.length !== b[0].length || row.some(value => !Number.isSafeInteger(value)))) return null;
  return [a, b];
}
