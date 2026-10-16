import type { Difficulty, Topic, TopicSlug } from './types';

// Matches the seed rows in supabase/migrations/202610150001_initial_schema.sql.
export const TOPICS: readonly Topic[] = [
  { slug: 'basic-integrals', name: 'Basic integrals' },
  { slug: 'substitution', name: 'Substitution' },
  { slug: 'integration-by-parts', name: 'Integration by parts' },
  { slug: 'rational-functions', name: 'Rational functions' },
  { slug: 'trigonometric-integrals', name: 'Trigonometric integrals' },
];

export const DIFFICULTIES: readonly { level: Difficulty; name: string }[] = [
  { level: 1, name: 'Basic' },
  { level: 2, name: 'Easy' },
  { level: 3, name: 'Medium' },
  { level: 4, name: 'Hard' },
  { level: 5, name: 'Advanced' },
];

export function topicName(slug: TopicSlug): string {
  return TOPICS.find((t) => t.slug === slug)?.name ?? slug;
}
