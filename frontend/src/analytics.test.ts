// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';
import { BEACON_SRC, startWebAnalytics } from './analytics';

const TOKEN = '0123456789abcdef0123456789abcdef';

afterEach(() => document.head.querySelectorAll('script').forEach((script) => script.remove()));

describe('Cloudflare Web Analytics', () => {
  it('loads one beacon with only the site token', () => {
    expect(startWebAnalytics(TOKEN, '/')).toBe(true);
    expect(startWebAnalytics(TOKEN, '/practice')).toBe(true);
    const scripts = document.head.querySelectorAll(`script[src="${BEACON_SRC}"]`);
    expect(scripts).toHaveLength(1);
    expect(JSON.parse((scripts[0] as HTMLScriptElement).dataset.cfBeacon ?? '')).toEqual({ token: TOKEN, spa: true });
  });

  it.each(['/auth/callback', '/s/abc', '/shared', '/shared/abc'])('stays off where the URL is private: %s', (path) => {
    expect(startWebAnalytics(TOKEN, path)).toBe(false);
    expect(document.head.querySelector('script')).toBeNull();
  });

  it.each([undefined, '', 'not-a-token', `${TOKEN}"onload="x`])('stays off without a valid token: %s', (token) => {
    expect(startWebAnalytics(token, '/')).toBe(false);
    expect(document.head.querySelector('script')).toBeNull();
  });
});
