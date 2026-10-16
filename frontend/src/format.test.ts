import { describe, expect, it } from 'vitest';
import { formatWhen } from './format';

const NOW = new Date(2026, 9, 16, 15, 0);

describe('history timestamps', () => {
  it('formats today, yesterday and older dates', () => {
    expect(formatWhen(new Date(2026, 9, 16, 14, 20).toISOString(), NOW)).toBe('Today, 14:20');
    expect(formatWhen(new Date(2026, 9, 15, 9, 5).toISOString(), NOW)).toBe('Yesterday');
    expect(formatWhen(new Date(2026, 9, 12, 9, 5).toISOString(), NOW)).toBe('12 Oct');
    expect(formatWhen(new Date(2025, 0, 3).toISOString(), NOW)).toBe('3 Jan 2025');
  });
});
