import { describe, expect, it } from 'vitest';
import { axisOrigin, axisTicks } from './geometry';

describe('3D axis ticks (#127)', () => {
  it('crosses at the origin, or the nearest point of the box', () => {
    expect(axisOrigin({ min: [-1, -1, 0], max: [1, 1, 2] })).toEqual([0, 0, 0]);
    expect(axisOrigin({ min: [1, 2, -3], max: [4, 5, -1] })).toEqual([1, 2, -1]);
  });

  it('labels round values on each axis and leaves out 0 at the origin', () => {
    const ticks = axisTicks({ min: [-2, 0, 0], max: [2, 1, 4] });
    const labels = (axis: string) => ticks.filter(t => t.axis === axis).map(t => t.label);
    expect(labels('x')).toEqual(['−2', '−1', '1', '2']);
    expect(labels('y')).toEqual(['0.2', '0.4', '0.6', '0.8', '1']);
    expect(labels('z')).toEqual(['1', '2', '3', '4']);
    const x1 = ticks.find(t => t.axis === 'x' && t.label === '1');
    expect(x1?.at).toEqual([1, 0, 0]);
  });

  it('keeps 0 when the axes do not cross there', () => {
    const ticks = axisTicks({ min: [1, 0, 0], max: [3, 2, 2] });
    expect(ticks.filter(t => t.axis === 'y').map(t => t.label)).toContain('0');
    expect(ticks.filter(t => t.axis === 'x').map(t => t.at)).toContainEqual([1, 0, 0]);
  });

  it('shows true heights when z is drawn rescaled', () => {
    // f runs up to 40 but is drawn ×0.05, so the box reaches z = 2.
    const z = axisTicks({ min: [0, 0, 0], max: [1, 1, 2] }, 0.05).filter(t => t.axis === 'z');
    expect(z.map(t => t.label)).toEqual(['10', '20', '30', '40']);
    expect(z[3].at[2]).toBeCloseTo(2);
  });

  it('skips an axis with an empty span', () => {
    expect(axisTicks({ min: [0, 0, 1], max: [1, 1, 1] }).some(t => t.axis === 'z')).toBe(false);
  });
});
