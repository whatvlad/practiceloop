import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import * as practice from './practice';
import { createWorksheet, fetchWorksheetPdf, resetWorksheets } from './worksheets';
import { planWorksheet, groupRequests, type DraftGroup } from './worksheetPlan';
import type { Catalogue } from './types';

const fetchMock = vi.fn<typeof fetch>();
const json = (body: unknown, status = 200, headers: Record<string, string> = {}) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', ...headers } });
const worksheet = { worksheet: { id: 'w-1', source: 'generate', createdAt: '2026-10-22T00:00:00Z', paper: 'a4', columns: 1, answerKey: true,
  groups: [{ label: 'Substitution, level 2', topic: 'substitution', difficulty: 2, requested: 3, count: 2 }], problemIds: ['p1', 'p2'] } };
const request = { source: 'generate' as const, groups: [{ topic: 'substitution' as const, difficulty: 2 as const, count: 3 }], paper: 'a4' as const, columns: 1 as const, answerKey: true, solutions: false };
beforeEach(() => { practice.resetPractice(); resetWorksheets(); practice.configurePracticeAuth(async () => 'account-token'); fetchMock.mockReset(); vi.stubGlobal('fetch', fetchMock); });
afterEach(() => vi.unstubAllGlobals());

it('needs an account and never calls the API for a guest', async () => {
  practice.configurePracticeAuth(async () => null);
  await expect(createWorksheet(request)).rejects.toThrow('Sign in');
  await expect(fetchWorksheetPdf('w-1')).rejects.toThrow('Sign in');
  expect(fetchMock).not.toHaveBeenCalled();
});

it('posts the ADR-007 body with a stable Idempotency-Key across a retry and reads the capped counts', async () => {
  fetchMock.mockRejectedValueOnce(new TypeError('connection lost'));
  await expect(createWorksheet(request)).rejects.toThrow();
  fetchMock.mockResolvedValueOnce(json(worksheet, 201));
  const made = await createWorksheet(request);
  expect(made).toEqual({ id: 'w-1', problemIds: ['p1', 'p2'],
    groups: [{ label: 'Substitution, level 2', topic: 'substitution', difficulty: 2, requested: 3, count: 2 }] });
  const [url, options] = fetchMock.mock.calls[1];
  expect(url).toBe('/api/worksheets');
  expect(options?.method).toBe('POST');
  expect(JSON.parse(String(options?.body))).toEqual(request);
  const headers = options?.headers as Record<string, string>;
  expect(headers.Authorization).toBe('Bearer account-token');
  expect(headers['Idempotency-Key']).toMatch(/^[0-9a-f-]{36}$/);
  expect(headers['Idempotency-Key']).toBe((fetchMock.mock.calls[0][1]?.headers as Record<string, string>)['Idempotency-Key']);
  // After a success the same settings make a new worksheet.
  fetchMock.mockResolvedValueOnce(json(worksheet, 201));
  await createWorksheet(request);
  expect((fetchMock.mock.calls[2][1]?.headers as Record<string, string>)['Idempotency-Key']).not.toBe(headers['Idempotency-Key']);
});

it('rejects a response whose ids do not match the group counts', async () => {
  fetchMock.mockResolvedValueOnce(json({ worksheet: { ...worksheet.worksheet, problemIds: ['p1'] } }, 201));
  await expect(createWorksheet(request)).rejects.toThrow('could not finish');
});

it('maps rate limits, a busy compiler and a failed render to clear messages without the server text', async () => {
  fetchMock.mockResolvedValueOnce(json({ error: { code: 'worksheet_busy', message: 'SECRET LOG', retryable: true } }, 503));
  await expect(fetchWorksheetPdf('w-1')).rejects.toThrow('busy');
  fetchMock.mockResolvedValueOnce(json({ error: { code: 'worksheet_render_failed', message: 'SECRET LOG', retryable: true } }, 503));
  await expect(fetchWorksheetPdf('w-1')).rejects.toThrow('could not be made');
  fetchMock.mockResolvedValueOnce(json({ error: { code: 'invalid_request', message: 'x', retryable: false } }, 422));
  await expect(createWorksheet(request)).rejects.toThrow('Check the worksheet');
  fetchMock.mockResolvedValueOnce(json({ error: { code: 'rate_limited', message: 'x', retryable: true } }, 429, { 'Retry-After': '30' }));
  await expect(createWorksheet(request)).rejects.toThrow('Wait a minute');
  // Inside the Retry-After window nothing is sent.
  await expect(createWorksheet(request)).rejects.toThrow('wait a moment');
  expect(fetchMock).toHaveBeenCalledTimes(4);
});

it('downloads the PDF with the server filename', async () => {
  fetchMock.mockResolvedValueOnce(new Response(new Blob(['%PDF-1.5'], { type: 'application/pdf' }), {
    status: 200, headers: { 'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename="practiceloop-worksheet-2026-10-22.pdf"' } }));
  const pdf = await fetchWorksheetPdf('w 1');
  expect(fetchMock.mock.calls[0][0]).toBe('/api/worksheets/w%201/pdf');
  expect(pdf.filename).toBe('practiceloop-worksheet-2026-10-22.pdf');
  expect(pdf.blob.type).toBe('application/pdf');
});

const catalogue: Catalogue = {
  areas: [{ slug: 'mathematical-analysis', name: 'Mathematical Analysis', mixed: { availableDifficulties: [1, 2, 3], weights: { 'basic-integrals': 1, substitution: 2 }, worksheetCapacity: { 1: 30, 2: 30, 3: 30 } } }],
  topics: [
    { slug: 'basic-integrals', name: 'Basic integrals', area: 'mathematical-analysis', availableDifficulties: [1, 2, 3], worksheetCapacity: { 1: 12, 2: 12, 3: 12 } },
    { slug: 'substitution', name: 'Substitution', area: 'mathematical-analysis', availableDifficulties: [1, 2, 3], worksheetCapacity: { 1: 3, 2: 8, 3: 8 } },
  ],
};
const group = (key: number, rest: Partial<DraftGroup>): DraftGroup => ({ key, area: 'mathematical-analysis', topic: 'basic-integrals', difficulty: 1, count: 5, ...rest });

it('caps a group to its cell and sends the capped count', () => {
  const plan = planWorksheet(catalogue, [group(0, { topic: 'substitution', count: 10 }), group(1, { topic: 'mixed', difficulty: 3, count: 4 })]);
  expect(plan.groups[0]).toMatchObject({ capacity: 3, count: 3, capped: true, label: 'Substitution, level 1' });
  expect(plan.groups[1]).toMatchObject({ count: 4, capped: false, label: 'Mixed mathematical analysis, level 3' });
  expect(plan.total).toBe(7);
  expect(plan.blocked).toBeNull();
  expect(groupRequests(plan)).toEqual([{ topic: 'substitution', difficulty: 1, count: 3 },
    { topic: 'mixed:mathematical-analysis', difficulty: 3, count: 4 }]);
});

it('blocks more than 40 problems or 8 groups, a level the topic lacks and an empty worksheet', () => {
  expect(planWorksheet(catalogue, []).blocked).toContain('at least one');
  const many = ([1, 2, 3] as const).map(level => group(level, { count: 20, topic: 'mixed', difficulty: level }));
  expect(planWorksheet(catalogue, many)).toMatchObject({ total: 60 });
  expect(planWorksheet(catalogue, many).blocked).toContain('Remove 20');
  expect(planWorksheet(catalogue, Array.from({ length: 9 }, (_, key) => group(key, { count: 1 }))).blocked).toContain('8 groups');
  expect(planWorksheet(catalogue, [group(0, { difficulty: 5 })]).blocked).toContain('level');
  // Counts are whole numbers from 1 to 20.
  expect(planWorksheet(catalogue, [group(0, { count: 99, topic: 'mixed' })]).groups[0].count).toBe(20);
});

it('shares a cell between groups, since a worksheet never repeats a problem', () => {
  const plan = planWorksheet(catalogue, [group(0, { topic: 'substitution', count: 2 }), group(1, { topic: 'substitution', count: 2 }),
    group(2, { topic: 'substitution', count: 1 })]);
  expect(plan.groups.map(g => [g.count, g.capped, g.shared])).toEqual([[2, false, false], [1, true, true], [0, true, true]]);
  expect(plan.blocked).toContain('no problems left');
  // Topic groups at a level use up room in that area's mixed group at the same level.
  const mixed = planWorksheet({ ...catalogue, areas: [{ ...catalogue.areas[0], mixed: { ...catalogue.areas[0].mixed!, worksheetCapacity: { 1: 15 } } }] },
    [group(0, { count: 12 }), group(1, { topic: 'mixed', count: 5 }), group(2, { topic: 'mixed', difficulty: 1, count: 1 })]);
  expect(mixed.groups.map(g => g.count)).toEqual([12, 3, 0]);
});

it('does not cap when the API publishes no cell sizes', () => {
  const bare: Catalogue = { ...catalogue, topics: catalogue.topics.map(t => ({ ...t, worksheetCapacity: undefined })) };
  expect(planWorksheet(bare, [group(0, { topic: 'substitution', count: 10 })]).groups[0]).toMatchObject({ count: 10, capped: false });
});
