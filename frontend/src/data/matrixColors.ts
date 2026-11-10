import type { Theme } from '../theme';

// The same matrix position keeps the same color across the original operands.
// Light-theme colors are the same hues, darkened to at least 4.5:1 on the paper canvas.
const PRODUCT: Record<Theme, readonly string[]> = {
  dark: ['#5fa8ff', '#ffab4d', '#65df91', '#d99bff', '#ff829d'],
  light: ['#0069e6', '#ab5a00', '#1a7f3f', '#8a3fd1', '#c8264f'],
};
const ENTRIES: Record<Theme, readonly string[]> = {
  dark: [
    '#5fa8ff', '#65df91', '#ffab4d', '#d99bff', '#ff829d',
    '#32a7af', '#b99b1b', '#9b7fea', '#d97846', '#629535',
    '#779deb', '#ba6e9c', '#478f9c', '#c28563', '#8e9b38',
    '#8e78b9', '#c96950', '#4b9a80', '#b98d35', '#8492c0',
    '#ca7594', '#559db9', '#a687bb', '#b88343', '#718d50',
  ],
  light: [
    '#0069e6', '#1a7f3f', '#ab5a00', '#8a3fd1', '#c8264f',
    '#247a7f', '#816c13', '#7953e3', '#b15424', '#517b2c',
    '#2e68e0', '#a95186', '#3b7782', '#9d603e', '#6a742a',
    '#7c62ae', '#b45137', '#3b7965', '#8b6a28', '#5a6daa',
    '#b84770', '#3b778e', '#885ea4', '#916735', '#5f7643',
  ],
};
/** Row-operation highlights: the modified row and the reference row. */
export const ROW_COLORS: Record<Theme, { target: string; reference: string }> = {
  dark: { target: '#65df91', reference: '#5fa8ff' },
  light: { target: '#1a7f3f', reference: '#0069e6' },
};

export const productColors = (theme: Theme = 'dark') => PRODUCT[theme];

export function colorMatrixEntries(latex: string, product = false, theme: Theme = 'dark'): string {
  const colors = ENTRIES[theme], products = PRODUCT[theme];
  let matrixIndex = 0;
  return latex.replace(/\\begin\{(p|b)matrix\}([\s\S]*?)\\end\{\1matrix\}/g, (_whole, kind: string, body: string) => {
    const operand = matrixIndex++;
    const rows = body.split(String.raw`\\`);
    const colored = rows.map((row, i) => row.split('&').map((cell, j) =>
      String.raw`\color{${product ? products[operand === 0 ? j : i] : colors[(i * 5 + j) % colors.length]}}{${cell}}`).join('&'));
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
