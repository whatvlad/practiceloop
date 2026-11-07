// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';
import { COOKIEBOT_SRC, cookiebotEnabled, openCookieSettings, startCookiebot } from './cookieConsent';

const ID = '01234567-89ab-cdef-0123-456789abcdef';

afterEach(() => document.head.querySelectorAll('script').forEach((script) => script.remove()));

describe('Cookiebot', () => {
  it('loads one script with the domain group ID', () => {
    expect(startCookiebot(ID, '/')).toBe(true);
    expect(startCookiebot(ID, '/practice')).toBe(true);
    const scripts = document.head.querySelectorAll<HTMLScriptElement>(`script[src="${COOKIEBOT_SRC}"]`);
    expect(scripts).toHaveLength(1);
    expect(scripts[0].id).toBe('Cookiebot');
    expect(scripts[0].dataset.cbid).toBe(ID);
  });

  it.each(['/auth/callback', '/s/abc', '/shared', '/shared/abc'])('stays off where the URL is private: %s', (path) => {
    expect(startCookiebot(ID, path)).toBe(false);
    expect(document.head.querySelector('script')).toBeNull();
  });

  it.each([undefined, '', 'not-an-id', `${ID}"onload="x`])('stays off without a valid ID: %s', (id) => {
    expect(cookiebotEnabled(id)).toBe(false);
    expect(startCookiebot(id, '/')).toBe(false);
    expect(document.head.querySelector('script')).toBeNull();
  });

  it('reopens the banner when Cookiebot has loaded and does nothing otherwise', () => {
    const renew = vi.fn();
    expect(openCookieSettings({ Cookiebot: { renew } } as unknown as Window)).toBe(true);
    expect(renew).toHaveBeenCalledOnce();
    expect(openCookieSettings({} as Window)).toBe(false);
  });
});
