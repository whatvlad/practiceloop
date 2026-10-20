// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { SharedProblemPage } from './SharedProblemPage';
import { lookupShare, normalizeCode, shareCode, shareLink } from '../data/shares';

const TOKEN = 'A'.repeat(21) + '_' + 'b'.repeat(20) + '-';
const fetchMock = vi.fn<typeof fetch>();
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const failure = (code: string, status: number) => json({ error: { code, message: 'Server text', retryable: false } }, status);
let root: Root;
let element: HTMLDivElement;

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
  element = document.createElement('div');
  document.body.append(element);
  root = createRoot(element);
});

afterEach(async () => {
  await act(async () => root.unmount());
  element.remove();
  vi.unstubAllGlobals();
});

async function render(props: { token: string | null; code: string | null }) {
  await act(async () => root.render(<SharedProblemPage {...props} />));
  await act(async () => {});
}

it('shows only the statement, topic and difficulty, even when the server sends more', async () => {
  fetchMock.mockResolvedValue(json({ problem: { topic: 'substitution', difficulty: 3, problemLatex: '\\int 2x\\cos(x^2)\\,dx',
    answerLatex: 'LEAKED-ANSWER', lastAttempt: { answer: 'LEAKED-ATTEMPT' }, id: 'LEAKED-ID' } }));
  await render({ token: TOKEN, code: null });
  const [url, options] = fetchMock.mock.calls[0];
  expect(String(url)).toBe(`/api/shares/${TOKEN}`);
  expect(options?.headers).not.toHaveProperty('Authorization');
  expect(options?.credentials).toBe('omit');
  expect(element.textContent).toContain('Integration — Substitution');
  expect(element.textContent).toContain('3/5');
  expect(element.querySelector('.katex')).not.toBeNull();
  expect(element.innerHTML).not.toMatch(/LEAKED/);
  expect(element.textContent).not.toMatch(/Show answer|Check answer/);
});

it.each([
  ['share_not_found', 404, 'Nothing is shared under this link or code.'],
  ['share_expired', 410, 'This shared problem has expired.'],
  ['share_revoked', 410, 'This problem is no longer shared.'],
  ['share_invalid', 400, 'That link or code is not valid.'],
])('turns %s into its own safe state', async (code, status, title) => {
  fetchMock.mockResolvedValue(failure(code, status));
  await render({ token: null, code: 'k7m2-qx9p' });
  expect(String(fetchMock.mock.calls[0][0])).toBe('/api/shares/code/K7M2QX9P');
  expect(element.querySelector('h1')?.textContent).toBe(title);
  expect(element.textContent).not.toContain('Server text');
});

it('rejects a malformed link or code without asking the server', async () => {
  await render({ token: 'short', code: null });
  expect(element.querySelector('h1')?.textContent).toBe('That link or code is not valid.');
  await render({ token: null, code: 'nope' });
  expect(element.querySelector('h1')?.textContent).toBe('That link or code is not valid.');
  expect(fetchMock).not.toHaveBeenCalled();
});

it('offers a code form when opened without one', async () => {
  await render({ token: null, code: null });
  expect(element.querySelector('h1')?.textContent).toBe('Open a shared problem');
  expect(element.querySelector('form input')).not.toBeNull();
  expect(fetchMock).not.toHaveBeenCalled();
});

it('says when lookups are busy and never treats an unknown error as a share state', async () => {
  fetchMock.mockResolvedValueOnce(failure('rate_limited', 429));
  await expect(lookupShare({ token: TOKEN })).rejects.toThrow(/Try again in a minute/);
  fetchMock.mockResolvedValueOnce(failure('constructor', 404));
  await expect(lookupShare({ token: TOKEN })).rejects.toThrow();
});

it('formats and normalizes codes like the API', () => {
  expect(shareCode('K7M2QX9P')).toBe('K7M2-QX9P');
  expect(normalizeCode(' o1il-0000 ')).toBe('01110000');
  expect(normalizeCode('K7M2QX9U')).toBeNull();
  expect(shareLink({ token: TOKEN, code: 'K7M2QX9P', expiresAt: '2027-01-18T00:00:00Z' }, 'https://example.test'))
    .toBe(`https://example.test/s/${TOKEN}`);
});
