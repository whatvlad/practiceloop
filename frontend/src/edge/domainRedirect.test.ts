import { expect, it, vi } from 'vitest';
import { onRequest } from '../../functions/_middleware';

const suffix = '/s/a%2Fb?source=a%2Bb&key=one&key=two';

it.each(['mathloop.pages.dev', 'practiceloop.pages.dev', 'www.mathloop.net'])(
  'redirects %s directly to the apex and preserves the URL',
  async (host) => {
    const next = vi.fn();
    const response = await onRequest({
      request: new Request(`https://${host}${suffix}`), env: { CANONICAL_REDIRECTS: 'true' }, next,
    });
    expect(response.status).toBe(301);
    expect(response.headers.get('location')).toBe(`https://mathloop.net${suffix}`);
    expect(response.headers.get('cache-control')).toBe('no-store');
    expect(next).not.toHaveBeenCalled();
  },
);

it.each([
  ['mathloop.net', 'true'], ['build.mathloop.pages.dev', 'true'],
  ['mathloop.pages.dev', undefined], ['www.mathloop.net', 'false'],
])('serves the existing API or assets at %s when applicable', async (host, enabled) => {
  const upstream = new Response('{"status":"ok"}');
  const next = vi.fn(async () => upstream);
  expect(await onRequest({
    request: new Request(`https://${host}/api/health`), env: { CANONICAL_REDIRECTS: enabled }, next,
  })).toBe(upstream);
  expect(next).toHaveBeenCalledOnce();
});

it('keeps old links working before cutover without letting a path choose the redirect host', async () => {
  const response = await onRequest({
    request: new Request('https://practiceloop.pages.dev//example.org/api/health?'), env: {}, next: vi.fn(),
  });
  expect(response.status).toBe(301);
  expect(response.headers.get('location')).toBe('https://mathloop.pages.dev//example.org/api/health?');
});
