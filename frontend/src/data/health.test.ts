import { describe, expect, it } from 'vitest';
import { checkApiHealth } from './health';

const respond = (status: number, body: unknown) => (async () => new Response(JSON.stringify(body), { status })) as typeof fetch;

describe('checkApiHealth', () => {
  it('is unconfigured without an API address', async () => {
    expect(await checkApiHealth('', respond(200, { status: 'ok' }))).toBe('unconfigured');
  });

  it('is ok only for a 200 with status ok', async () => {
    expect(await checkApiHealth('https://api.test', respond(200, { status: 'ok' }))).toBe('ok');
    expect(await checkApiHealth('https://api.test', respond(200, { status: 'starting' }))).toBe('unreachable');
    expect(await checkApiHealth('https://api.test', respond(503, { status: 'ok' }))).toBe('unreachable');
  });

  it('is unreachable when the request fails', async () => {
    const fail = (async () => {
      throw new TypeError('Failed to fetch');
    }) as typeof fetch;
    expect(await checkApiHealth('https://api.test', fail)).toBe('unreachable');
  });

  it('calls /health under the configured address', async () => {
    let url = '';
    const capture = (async (input: RequestInfo | URL) => {
      url = String(input);
      return new Response('{"status":"ok"}');
    }) as typeof fetch;
    await checkApiHealth('https://api.test', capture);
    expect(url).toBe('https://api.test/health');
  });
});
