import { expect, it } from 'vitest';
import { parseVisual } from './spec';

const definite = { kind: 'definite', version: 1, f: ['mul', 2, 'x'], a: 0, b: 2, aLatex: '0', bLatex: '2',
  range: [-1, 3], y: [-1, 5], value: '4' };

it('accepts the two single-integral kinds', () => {
  expect(parseVisual(definite)).toEqual(definite);
  const indefinite = { kind: 'indefinite', version: 1, f: 'x', F: ['mul', 0.5, ['pow', 'x', 2]], x: [-4, 4], y: [-2, 9],
    points: [{ x: 0, kind: 'zero' }, { x: 0, kind: 'extremum' }] };
  expect(parseVisual(indefinite)).toEqual(indefinite);
});

it('drops unknown, newer or broken specs instead of throwing', () => {
  for (const value of [undefined, null, 'definite', [], { ...definite, version: 2 }, { ...definite, kind: 'region3d' },
    { ...definite, kind: 'toString' }, { ...definite, f: ['eval', 'x'] }, { ...definite, a: 5 },
    { ...definite, range: [3, -1] }, { ...definite, y: [0, NaN] }, { ...definite, value: 7 },
    { kind: 'indefinite', version: 1, f: 'x', F: 'x', x: [-1, 1], y: [-1, 1], points: [{ x: 9, kind: 'zero' }] },
    { kind: 'indefinite', version: 1, f: 'x', F: 'x', x: [-1, 1], y: [-1, 1], points: [{ x: 0, kind: 'peak' }] }]) {
    expect(parseVisual(value)).toBeUndefined();
  }
});

it('accepts bounded geometry while removing fields unrelated to the drawing', () => {
  const geometry = {
    kind: 'geometry3d', version: 1, title: 'Vectors', description: 'Given vectors.',
    points: [{ label: 'A', at: [0, 1, 2], tone: 'given' }],
    lines: [{ label: 'u', start: [0, 0, 0], end: [1, 2, 3], tone: 'active', arrow: true, dashed: false }],
    faces: [],
  };
  expect(parseVisual({ ...geometry, answer: 'private' })).toEqual(geometry);
  for (const bad of [
    { ...geometry, points: [{ ...geometry.points[0], at: [Infinity, 0, 0] }] },
    { ...geometry, points: Array(17).fill(geometry.points[0]) },
    { ...geometry, lines: [{ ...geometry.lines[0], tone: 'unknown' }] },
    { ...geometry, lines: [{ ...geometry.lines[0], arrow: 'yes' }] },
  ]) expect(parseVisual(bad)).toBeUndefined();
});
