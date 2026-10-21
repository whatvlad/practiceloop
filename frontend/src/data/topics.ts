import type { Area, AreaSlug, AvailableTopic, Difficulty, MixedPractice, Topic, TopicSlug } from './types';

// ADR-005 areas, matching supabase/migrations/202610210003_topic_areas.sql.
export const AREAS: readonly Area[] = [
  { slug: 'integrals', name: 'Integrals' },
  { slug: 'derivatives', name: 'Derivatives' },
];

// Matches the seed rows of public.topics. The API offers a topic only once its generator ships.
export const TOPICS: readonly Topic[] = [
  { slug: 'basic-integrals', name: 'Basic integrals', area: 'integrals' },
  { slug: 'substitution', name: 'Substitution', area: 'integrals' },
  { slug: 'integration-by-parts', name: 'Integration by parts', area: 'integrals' },
  { slug: 'rational-functions', name: 'Rational functions', area: 'integrals' },
  { slug: 'trigonometric-integrals', name: 'Trigonometric integrals', area: 'integrals' },
  { slug: 'double-integrals', name: 'Double integrals', area: 'integrals' },
  { slug: 'triple-integrals', name: 'Triple integrals', area: 'integrals' },
  { slug: 'derivatives', name: 'Derivatives', area: 'derivatives' },
  { slug: 'partial-derivatives', name: 'Partial derivatives', area: 'derivatives' },
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

export function areaOf(slug: TopicSlug): AreaSlug {
  return TOPICS.find((t) => t.slug === slug)?.area ?? 'integrals';
}

/** The problem tag's subject: "Integration — Substitution", "Differentiation — Derivatives". */
export function subjectName(slug: TopicSlug): string {
  return areaOf(slug) === 'derivatives' ? 'Differentiation' : 'Integration';
}

/** Each topic's share of mixed practice at one level: its weight over the weights offered there. */
export function mixedShares(topics: readonly AvailableTopic[], mixed: MixedPractice, difficulty: Difficulty): { topic: Topic; percent: number }[] {
  const offered = topics.filter(t => t.availableDifficulties.includes(difficulty) && (mixed.weights[t.slug] ?? 0) > 0);
  const total = offered.reduce((sum, t) => sum + (mixed.weights[t.slug] ?? 0), 0);
  return offered.map(t => ({ topic: t, percent: Math.round((100 * (mixed.weights[t.slug] ?? 0)) / total) }));
}
