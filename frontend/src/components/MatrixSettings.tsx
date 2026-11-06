import type { Difficulty, MatrixOptions } from '../data/types';

const choices: Partial<Record<Difficulty, Partial<Record<MatrixOptions['operation'], MatrixOptions['size'][]>>>> = {
  1: { add: ['2x2', '3x3'], subtract: ['2x2', '3x3'], multiply: ['2x2', '3x3', 'rectangular'] },
  2: { multiply: ['rectangular'], mixed: ['rectangular'] },
  3: { multiply: ['2x2'], mixed: ['2x2'] },
};
const operations: Record<MatrixOptions['operation'], string> = { add: 'Addition', subtract: 'Subtraction', multiply: 'Multiplication', mixed: 'Combined operations' };
const sizes: Record<MatrixOptions['size'], string> = { '2x2': '2 × 2', '3x3': '3 × 3', rectangular: 'Rectangular (2 × 3 and 3 × 2)' };

export function matrixOptionsValid(level: Difficulty, value: MatrixOptions): boolean {
  return choices[level]?.[value.operation]?.includes(value.size) ?? false;
}

export function initialMatrixOptions(level: Difficulty): MatrixOptions {
  const group = choices[level] ?? choices[1]!;
  const operation = Object.keys(group)[0] as MatrixOptions['operation'];
  return { operation, size: group[operation]![0] };
}

export function matrixOptionsFromSearch(params: URLSearchParams): MatrixOptions | undefined {
  const operation = params.get('matrixOperation');
  const size = params.get('matrixSize');
  if (!operation || !size || !Object.hasOwn(operations, operation) || !Object.hasOwn(sizes, size)) return undefined;
  return { operation: operation as MatrixOptions['operation'], size: size as MatrixOptions['size'] };
}

export function matrixOptionsQuery(options: MatrixOptions): string {
  return `&matrixOperation=${encodeURIComponent(options.operation)}&matrixSize=${encodeURIComponent(options.size)}`;
}

export function MatrixSettings({ level, value, onChange }: { level: Difficulty; value: MatrixOptions; onChange: (value: MatrixOptions) => void }) {
  const group = choices[level] ?? choices[1]!;
  const active = matrixOptionsValid(level, value) ? value : initialMatrixOptions(level);
  return <div className="pl-stack pl-gap-3">
    <label className="pl-label">Operation
      <select className="pl-input" value={active.operation} onChange={event => {
        const operation = event.target.value as MatrixOptions['operation'];
        onChange({ operation, size: group[operation]![0] });
      }}>{Object.keys(group).map(key => <option key={key} value={key}>{operations[key as MatrixOptions['operation']]}</option>)}</select>
    </label>
    <label className="pl-label">Matrix size
      <select className="pl-input" value={active.size} onChange={event => onChange({ ...active, size: event.target.value as MatrixOptions['size'] })}>
        {group[active.operation]!.map(size => <option key={size} value={size}>{sizes[size]}</option>)}
      </select>
    </label>
    <p className="pl-small pl-muted">These settings apply when you generate a problem.</p>
  </div>;
}
