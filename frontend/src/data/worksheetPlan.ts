// The Practice worksheet builder's rules (#117), kept apart from React so tests can call them.
import { DIFFICULTIES, topicName } from './topics';
import type { AreaSlug, Catalogue, Difficulty, PracticeTopic } from './types';
import { WORKSHEET_LIMITS, worksheetTopic, type WorksheetGroupRequest } from './worksheets';

export interface DraftGroup {
  /** Stable React key; never sent. */
  key: number;
  area: AreaSlug;
  topic: PracticeTopic;
  difficulty: Difficulty;
  count: number;
}

export interface PlannedGroup {
  group: DraftGroup;
  label: string;
  /** The levels this topic offers; the picker hides the others. */
  levels: Difficulty[];
  /** Distinct problems still left in the cell for this group, when the API publishes cell sizes. */
  capacity: number | undefined;
  /** An earlier group already takes problems from the same cell. */
  shared: boolean;
  /** What the group will get: the request capped to the cell (ADR-007 decision 4). */
  count: number;
  capped: boolean;
}

export interface WorksheetPlan {
  groups: PlannedGroup[];
  total: number;
  /** Why "Generate PDF" is off, or null when the worksheet can be made. */
  blocked: string | null;
}

export function levelsOf(catalogue: Catalogue, area: AreaSlug, topic: PracticeTopic): Difficulty[] {
  if (topic === 'mixed') return catalogue.areas.find(a => a.slug === area)?.mixed?.availableDifficulties ?? [];
  return catalogue.topics.find(t => t.slug === topic)?.availableDifficulties ?? [];
}

export function capacityOf(catalogue: Catalogue, area: AreaSlug, topic: PracticeTopic, difficulty: Difficulty): number | undefined {
  const cells = topic === 'mixed'
    ? catalogue.areas.find(a => a.slug === area)?.mixed?.worksheetCapacity
    : catalogue.topics.find(t => t.slug === topic)?.worksheetCapacity;
  return cells?.[difficulty];
}

/** ADR-007's group label: "Substitution, level 2"; mixed groups name their area. */
export function groupLabel(catalogue: Catalogue, area: AreaSlug, topic: PracticeTopic, difficulty: Difficulty): string {
  const name = topic === 'mixed' ? `Mixed ${catalogue.areas.find(a => a.slug === area)?.name.toLowerCase() ?? area}` : topicName(topic);
  return `${name}, level ${difficulty}`;
}

export function levelName(level: Difficulty): string {
  return DIFFICULTIES.find(d => d.level === level)?.name ?? String(level);
}

/** A level the topic offers: the same one if it can, otherwise the nearest (as on the dashboard). */
export function nearestLevel(levels: readonly Difficulty[], wanted: Difficulty): Difficulty {
  if (levels.length === 0 || levels.includes(wanted)) return wanted;
  return levels.reduce((best, level) => (Math.abs(level - wanted) < Math.abs(best - wanted) ? level : best));
}

export function clampCount(value: number): number {
  if (!Number.isFinite(value)) return 1;
  return Math.min(WORKSHEET_LIMITS.perGroup, Math.max(1, Math.round(value)));
}

export function planWorksheet(catalogue: Catalogue, groups: readonly DraftGroup[]): WorksheetPlan {
  // No record repeats in a worksheet, so groups that draw from the same cell share it, in order.
  // A mixed group draws from its area's topic cells at that level, so earlier groups there use up its room too.
  const used = new Map<string, number>();
  const cell = (area: AreaSlug, topic: PracticeTopic, difficulty: Difficulty) => `${area}:${topic}:${difficulty}`;
  const planned = groups.map((group) => {
    const levels = levelsOf(catalogue, group.area, group.topic);
    const total = capacityOf(catalogue, group.area, group.topic, group.difficulty);
    const own = cell(group.area, group.topic, group.difficulty);
    const taken = group.topic === 'mixed'
      ? [...used].filter(([key]) => key.startsWith(`${group.area}:`) && key.endsWith(`:${group.difficulty}`)).reduce((sum, [, n]) => sum + n, 0)
      : used.get(own) ?? 0;
    const capacity = total === undefined ? undefined : Math.max(0, total - taken);
    const requested = clampCount(group.count);
    const count = capacity === undefined ? requested : Math.min(requested, capacity);
    used.set(own, (used.get(own) ?? 0) + count);
    return { group, levels, capacity, count, capped: count < requested, shared: taken > 0,
      label: groupLabel(catalogue, group.area, group.topic, group.difficulty) };
  });
  const total = planned.reduce((sum, g) => sum + g.count, 0);
  let blocked: string | null = null;
  if (planned.length === 0) blocked = 'Add at least one group.';
  else if (planned.length > WORKSHEET_LIMITS.groups) blocked = `A worksheet has at most ${WORKSHEET_LIMITS.groups} groups.`;
  else if (planned.some(g => !g.levels.includes(g.group.difficulty))) blocked = 'Choose a level each topic offers.';
  else if (planned.some(g => g.count < 1)) blocked = 'A group has no problems left: earlier groups use all of its topic and level. Change or remove it.';
  else if (total > WORKSHEET_LIMITS.total) blocked = `A worksheet has at most ${WORKSHEET_LIMITS.total} problems. Remove ${total - WORKSHEET_LIMITS.total}.`;
  return { groups: planned, total, blocked };
}

/** The groups as POST /api/worksheets takes them, with the capped counts. */
export function groupRequests(plan: WorksheetPlan): WorksheetGroupRequest[] {
  return plan.groups.map(({ group, count }) => ({ topic: worksheetTopic(group.topic, group.area), difficulty: group.difficulty, count }));
}
