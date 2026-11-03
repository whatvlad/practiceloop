import type { Area, AreaSlug, AvailableTopic, Difficulty, MixedPractice, Topic, TopicSlug } from './types';

// ADR-005 amendment (#144), matching 202610260001_mathematics_practice_areas.sql.
export const AREAS: readonly Area[] = [
  { slug: 'algebra', name: 'Algebra' },
  { slug: 'mathematical-analysis', name: 'Mathematical Analysis' },
  { slug: 'probability-statistics', name: 'Probability and Statistics' },
];

// #191: topics come from GET /topics. This build keeps only the latest list it was sent,
// so a new topic needs no frontend change.
const known = new Map<TopicSlug, Topic>();
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export function isTopicSlug(value: unknown): value is TopicSlug {
  return typeof value === 'string' && value.length <= 64 && SLUG.test(value);
}

/** Names and areas for history rows, tags and statistics; called with each catalogue. */
export function rememberTopics(topics: readonly Topic[]): void {
  for (const { slug, name, area } of topics) known.set(slug, { slug, name, area });
}

export const DIFFICULTIES: readonly { level: Difficulty; name: string }[] = [
  { level: 1, name: 'Basic' },
  { level: 2, name: 'Easy' },
  { level: 3, name: 'Medium' },
  { level: 4, name: 'Hard' },
  { level: 5, name: 'Advanced' },
];

export function topicName(slug: TopicSlug): string {
  const name = known.get(slug)?.name;
  if (name) return name;
  // Before the catalogue arrives (a shared link, say), the slug reads as the name.
  const words = slug.replaceAll('-', ' ');
  return words.charAt(0).toUpperCase() + words.slice(1);
}

/** The area the latest catalogue lists the topic under, if it lists the topic. */
export function listedArea(slug: TopicSlug): AreaSlug | undefined {
  return known.get(slug)?.area;
}

export function areaOf(slug: TopicSlug): AreaSlug {
  return listedArea(slug) ?? 'mathematical-analysis';
}

const INTEGRATION = ['basic-integrals', 'substitution', 'integration-by-parts', 'rational-functions',
  'trigonometric-integrals', 'definite-integrals', 'double-integrals', 'triple-integrals'];
const DIFFERENTIATION = ['derivatives', 'partial-derivatives'];

/** The problem tag: "Integration — Substitution", "Algebra — Combinations", or the name alone. */
export function problemTag(slug: TopicSlug): string {
  const area = listedArea(slug);
  const subject = DIFFERENTIATION.includes(slug) ? 'Differentiation' : INTEGRATION.includes(slug) ? 'Integration'
    : AREAS.find(a => a.slug === area)?.name;
  return subject ? `${subject} — ${topicName(slug)}` : topicName(slug);
}

/** Each topic's share of mixed practice at one level: its weight over the weights offered there. */
export function mixedShares(topics: readonly AvailableTopic[], mixed: MixedPractice, difficulty: Difficulty): { topic: Topic; percent: number }[] {
  const offered = topics.filter(t => t.availableDifficulties.includes(difficulty) && (mixed.weights[t.slug] ?? 0) > 0);
  const total = offered.reduce((sum, t) => sum + (mixed.weights[t.slug] ?? 0), 0);
  return offered.map(t => ({ topic: t, percent: Math.round((100 * (mixed.weights[t.slug] ?? 0)) / total) }));
}
