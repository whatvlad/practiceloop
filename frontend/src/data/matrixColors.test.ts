import { expect, it } from 'vitest';
import { colorMatrixEntries, numericMatrixProduct } from './matrixColors';
import { renderMath } from '../math';

it('assigns matching coordinates the same color and preserves matrix contents', () => {
  const latex = String.raw`\begin{pmatrix}1&2\\3&4\end{pmatrix}+\begin{pmatrix}5&6\\7&8\end{pmatrix}`;
  const colored = colorMatrixEntries(latex);
  expect(colored).toContain(String.raw`\color{#5fa8ff}{1}`);
  expect(colored).toContain(String.raw`\color{#5fa8ff}{5}`);
  expect(colored).toContain(String.raw`\color{#65df91}{2}`);
  expect(colored).toContain(String.raw`\color{#65df91}{6}`);
  expect(renderMath(colored, true)).toContain('color:#5fa8ff');
});

it('pairs each column of A with the corresponding row of B for multiplication', () => {
  const latex = String.raw`\begin{pmatrix}2&0&3\\1&4&-1\end{pmatrix}\cdot\begin{pmatrix}1&2\\3&5\\1&1\end{pmatrix}`;
  expect(numericMatrixProduct(latex)).toEqual([[[2, 0, 3], [1, 4, -1]], [[1, 2], [3, 5], [1, 1]]]);
  const colored = colorMatrixEntries(latex, true);
  expect(colored).toContain(String.raw`\color{#5fa8ff}{2}&\color{#ffab4d}{0}&\color{#65df91}{3}`);
  expect(colored).toContain(String.raw`\color{#ffab4d}{3}&\color{#ffab4d}{5}`);
  expect(numericMatrixProduct(latex.replace(String.raw`\cdot`, '+'))).toBeNull();
  expect(numericMatrixProduct(latex + String.raw`^{-1}`)).toBeNull();
});

it('renders the augmented matrix used for inverse row operations', () => {
  expect(renderMath(String.raw`R_{2}\leftarrow R_{2}-(2)R_{1}\quad \left[\begin{array}{cc|cc}1&2&1&0\\0&1&-2&1\end{array}\right]`, true)).toContain('katex');
});
