import { DIFFICULTIES } from './topics';
import type { Difficulty } from './types';

export function difficultyLabel(topic: string, level: Difficulty): string {
  if (topic === 'matrix-operations' && level <= 3) return ['Basic', 'Intermediate', 'Advanced'][level - 1];
  return DIFFICULTIES.find(item => item.level === level)!.name;
}
