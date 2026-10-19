import { describe, expect, it, vi } from 'vitest';
import { proxyToApi } from './apiProxy';

const ok = () => vi.fn<typeof fetch>(async () => new Response('{"status":"ok"}', { status: 200 }));

describe('proxyToApi', () => {
  it('strips /api and keeps the path and query', async () => {
    const fetchImpl = ok();
    const response = await proxyToApi(new Request('https://x.pages.dev/api/health?a=1'), 'https://api.example/', fetchImpl);
    expect(response.status).toBe(200);
    expect(fetchImpl.mock.calls[0][0]).toBe('https://api.example/health?a=1');
  });

  it('forwards only the headers the API reads, plus the body', async () => {
    const fetchImpl = ok();
    const request = new Request('https://x.pages.dev/api/attempts', {
      method: 'POST',
      headers: { Authorization: 'Bearer t', 'Content-Type': 'application/json', Cookie: 'c=1' },
      body: '{"a":1}',
    });
    await proxyToApi(request, 'https://api.example', fetchImpl);
    const init = fetchImpl.mock.calls[0][1]!;
    const headers = init.headers as Headers;
    expect(headers.get('authorization')).toBe('Bearer t');
    expect(headers.get('cookie')).toBeNull();
    expect(new TextDecoder().decode(init.body as ArrayBuffer)).toBe('{"a":1}');
  });

  it('answers 503 without an origin and 502 when the API is down', async () => {
    expect((await proxyToApi(new Request('https://x/api/health'), '')).status).toBe(503);
    const down = vi.fn<typeof fetch>(async () => { throw new TypeError('fail'); });
    expect((await proxyToApi(new Request('https://x/api/health'), 'https://api.example', down)).status).toBe(502);
  });
});
