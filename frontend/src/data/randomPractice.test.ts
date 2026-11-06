import { describe, expect, it } from 'vitest';
import { eligibleRandomChoices, pickRandomChoice } from './randomPractice';
import type { AvailableTopic } from './types';

const topics: AvailableTopic[] = [
  { slug: 'matrices', name: 'Matrices', area: 'algebra', availableDifficulties: [1, 2] },
  { slug: 'derivatives', name: 'Derivatives', area: 'mathematical-analysis', availableDifficulties: [3] },
];

describe('random practice', () => {
  it('requires an available level for every selected topic', () => {
    expect(eligibleRandomChoices({ matrices: 1, derivatives: 3 }, topics)).toHaveLength(2);
    expect(eligibleRandomChoices({ matrices: null }, topics)).toBeNull();
    expect(eligibleRandomChoices({ matrices: 5 }, topics)).toBeNull();
    expect(eligibleRandomChoices({ removed: 1 }, topics)).toBeNull();
    expect(eligibleRandomChoices({}, topics)).toBeNull();
  });
  it('picks by topic with equal slots regardless of available levels', () => {
    const choices = eligibleRandomChoices({ matrices: 1, derivatives: 3 }, topics)!;
    expect(pickRandomChoice(choices, () => 0).topic).toBe('matrices');
    expect(pickRandomChoice(choices, () => 0.99).topic).toBe('derivatives');
  });
});
