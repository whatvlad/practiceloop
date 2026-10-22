// ADR-007 printable worksheets (#116): create one, then download its PDF.
// Shared by the Practice builder (#117) and the History export (#118).
import text from '../../../backend/app/content/en.json';
import { accountSession, sessionCurrent } from './practice';
import { AREAS, TOPICS } from './topics';
import type { AreaSlug, Difficulty, PracticeTopic, TopicSlug } from './types';

const base = (import.meta.env.VITE_API_BASE_URL ?? '/api').trim().replace(/\/+$/, '');

/** ADR-007 "Limits and errors". */
export const WORKSHEET_LIMITS = { groups: 8, perGroup: 20, total: 40, ids: 40 } as const;

/** A group's topic on the wire: a topic slug, or mixed practice within one area. */
export type WorksheetTopic = TopicSlug | `mixed:${AreaSlug}`;

export interface WorksheetGroupRequest {
  topic: WorksheetTopic;
  difficulty: Difficulty;
  count: number;
}

export interface WorksheetPageOptions {
  paper: 'a4' | 'letter';
  columns: 1 | 2;
  /** On by default; printing the key marks every included answer as revealed. */
  answerKey: boolean;
}

export type WorksheetRequest = WorksheetPageOptions & (
  | { source: 'generate'; groups: WorksheetGroupRequest[] }
  | { source: 'history'; problemIds: string[] }
);

export interface WorksheetGroup {
  label: string;
  topic: WorksheetTopic;
  difficulty: Difficulty;
  requested: number;
  /** Below `requested` when the cell had fewer distinct problems (ADR-007 decision 4). */
  count: number;
}

export interface Worksheet {
  id: string;
  groups: WorksheetGroup[];
  problemIds: string[];
}

export const DEFAULT_PAGE_OPTIONS: WorksheetPageOptions = { paper: 'a4', columns: 1, answerKey: true };

export function worksheetTopic(topic: PracticeTopic, area: AreaSlug): WorksheetTopic {
  return topic === 'mixed' ? `mixed:${area}` : topic;
}

function isWorksheetTopic(value: unknown): value is WorksheetTopic {
  return TOPICS.some(t => t.slug === value) || AREAS.some(a => value === `mixed:${a.slug}`);
}

const keys = new Map<string, string>();
let retryAfter = 0;

/** Forgets retry keys and the rate-limit pause when the signed-in identity changes. */
export function resetWorksheets(): void {
  keys.clear();
  retryAfter = 0;
}

async function failure(response: Response): Promise<Error> {
  const delay = Number(response.headers.get('Retry-After'));
  if (Number.isFinite(delay) && delay > 0) retryAfter = Date.now() + delay * 1000;
  let code = '';
  try {
    const body: unknown = await response.json();
    const error = (body as { error?: { code?: unknown } } | null)?.error;
    if (typeof error?.code === 'string') code = error.code;
  } catch { /* An empty or non-JSON body keeps the status message. */ }
  // Only our own messages: never the server's text or the TeX log.
  if (response.status === 401) return new Error('Please sign in again to print a worksheet.');
  if (response.status === 404) return new Error('Some of these problems are no longer in your history. Reload and try again.');
  if (response.status === 422) return new Error('Check the worksheet groups and options and try again.');
  if (response.status === 429) return new Error('You have made a lot of worksheets just now. Wait a minute and try again.');
  if (code === 'worksheet_busy') return new Error('The PDF service is busy with another worksheet. Try again in a few seconds.');
  if (code === 'worksheet_render_failed') return new Error('The PDF could not be made. Try again; if it fails again, please report it.');
  return new Error(text.service_error);
}

function checkPause() {
  if (Date.now() < retryAfter) throw new Error('Please wait a moment before trying again.');
}

function parseWorksheet(value: unknown): Worksheet {
  const data = (value as { worksheet?: unknown } | null)?.worksheet as Record<string, unknown> | undefined;
  if (!data || typeof data.id !== 'string' || !Array.isArray(data.groups) || !Array.isArray(data.problemIds)
    || data.problemIds.some(id => typeof id !== 'string')) throw new Error(text.service_error);
  const groups = data.groups.map((item: unknown) => {
    const group = item as Record<string, unknown> | null;
    if (!group || typeof group.label !== 'string' || !isWorksheetTopic(group.topic)
      || ![1, 2, 3, 4, 5].includes(group.difficulty as number)
      || !Number.isSafeInteger(group.requested) || !Number.isSafeInteger(group.count)
      || (group.count as number) < 0 || (group.count as number) > (group.requested as number)) throw new Error(text.service_error);
    return { label: group.label, topic: group.topic, difficulty: group.difficulty as Difficulty,
      requested: group.requested as number, count: group.count as number };
  });
  if (groups.reduce((sum, g) => sum + g.count, 0) !== data.problemIds.length) throw new Error(text.service_error);
  return { id: data.id, groups, problemIds: data.problemIds as string[] };
}

/** POST /api/worksheets. An exact retry after a failure reuses its Idempotency-Key, so it returns the same worksheet. */
export async function createWorksheet(request: WorksheetRequest): Promise<Worksheet> {
  checkPause();
  const { bearer, started } = await accountSession('Sign in to print a worksheet.');
  const operation = JSON.stringify(request);
  const key = keys.get(operation) ?? crypto.randomUUID();
  keys.set(operation, key);
  let response: Response;
  try {
    response = await fetch(`${base}/worksheets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${bearer}`, 'Idempotency-Key': key },
      body: operation,
      // Generating up to 40 problems takes longer than a single one.
      signal: AbortSignal.timeout(30000),
      cache: 'no-store',
    });
  } catch { throw new Error(text.service_error); }
  if (!sessionCurrent(started)) throw new Error(text.expired);
  if (!response.ok) {
    if (response.status === 422 || response.status === 409) keys.delete(operation);
    throw await failure(response);
  }
  let worksheet: Worksheet;
  try { worksheet = parseWorksheet(await response.json()); } catch { throw new Error(text.service_error); }
  keys.delete(operation);
  return worksheet;
}

function filename(disposition: string | null): string {
  const match = /filename="?(practiceloop-worksheet-[\w-]+\.pdf)"?/.exec(disposition ?? '');
  return match ? match[1] : 'practiceloop-worksheet.pdf';
}

/** GET /api/worksheets/{id}/pdf: read-only, so a failed render can simply be retried. */
export async function fetchWorksheetPdf(id: string): Promise<{ blob: Blob; filename: string }> {
  checkPause();
  const { bearer, started } = await accountSession('Sign in to print a worksheet.');
  let response: Response;
  try {
    response = await fetch(`${base}/worksheets/${encodeURIComponent(id)}/pdf`, {
      headers: { Authorization: `Bearer ${bearer}`, Accept: 'application/pdf' },
      // The compile may wait up to 10 s for its turn and then run up to 20 s.
      signal: AbortSignal.timeout(40000),
      cache: 'no-store',
    });
  } catch { throw new Error(text.service_error); }
  if (!sessionCurrent(started)) throw new Error(text.expired);
  if (!response.ok) throw await failure(response);
  const blob = await response.blob();
  if (blob.size === 0) throw new Error(text.service_error);
  return { blob: blob.type === 'application/pdf' ? blob : new Blob([blob], { type: 'application/pdf' }), filename: filename(response.headers.get('Content-Disposition')) };
}

/** Fetches the worksheet's PDF and hands it to the browser as a download. */
export async function downloadWorksheetPdf(id: string): Promise<void> {
  const { blob, filename: name } = await fetchWorksheetPdf(id);
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  link.rel = 'noopener';
  document.body.append(link);
  link.click();
  link.remove();
  // Give the browser time to start the download before the URL goes away.
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}
