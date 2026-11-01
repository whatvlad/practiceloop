// @vitest-environment jsdom
import { describe, expect, it } from 'vitest';
import headers from '../public/_headers?raw';
import indexHtml from '../index.html?raw';
import { PUBLIC_PATHS, applyPageMeta, crawlerFiles, pageMeta, pagesHeaders, shellRobots, siteConfig } from './site';

const PREVIEW = siteConfig(undefined, undefined);
const LAUNCHED = siteConfig('https://example.org/', 'true');

function meta(selector: string): string | null {
  return document.head.querySelector(selector)?.getAttribute('content') ?? null;
}

describe('page metadata (#38)', () => {
  it('describes the full range of maths practice on general pages', () => {
    for (const path of ['/', '/practice', '/shared']) {
      expect(pageMeta(path).description).not.toMatch(/integration/i);
    }
    expect(indexHtml).not.toMatch(/Practice integration/);
  });
  it('gives every route its own title and description', () => {
    const paths = ['/', '/privacy', '/login', '/dashboard', '/practice', '/history', '/profile', '/shared', '/nope'];
    const titles = new Set(paths.map((path) => pageMeta(path).title));
    expect(titles.size).toBe(paths.length);
    expect(pageMeta('/s/abc')).toBe(pageMeta('/shared'));
    expect(pageMeta('/shared/abc')).toBe(pageMeta('/shared'));
  });

  it('only lists public pages in the sitemap', () => {
    expect(PUBLIC_PATHS).toEqual(['/', '/privacy']);
  });

  it.each(['/', '/privacy', '/login', '/dashboard', '/practice', '/history', '/profile', '/s/abc', '/shared', '/missing'])(
    'keeps %s noindex on preview, without a canonical URL',
    (path) => {
      applyPageMeta(path, PREVIEW);
      expect(meta('meta[name="robots"]')).toBe('noindex, nofollow');
      expect(document.head.querySelector('link[rel="canonical"]')).toBeNull();
      expect(meta('meta[property="og:url"]')).toBeNull();
      expect(document.title).toBe(pageMeta(path).title);
      expect(meta('meta[name="description"]')).toBe(pageMeta(path).description);
      expect(meta('meta[property="og:title"]')).toBe(pageMeta(path).title);
      expect(meta('meta[name="twitter:card"]')).toBe('summary');
    },
  );

  it.each(['/login', '/dashboard', '/practice', '/history', '/profile', '/s/abc', '/shared', '/missing', '/auth/callback'])(
    'keeps private, shared and error page %s noindex after launch',
    (path) => {
      applyPageMeta(path, LAUNCHED);
      expect(meta('meta[name="robots"]')).toBe('noindex, nofollow');
      expect(document.head.querySelector('link[rel="canonical"]')).toBeNull();
    },
  );

  it('indexes public pages only on an approved HTTPS site', () => {
    applyPageMeta('/privacy', LAUNCHED);
    expect(meta('meta[name="robots"]')).toBe('index, follow');
    expect(document.head.querySelector('link[rel="canonical"]')?.getAttribute('href')).toBe('https://example.org/privacy');
    expect(meta('meta[property="og:url"]')).toBe('https://example.org/privacy');
    expect(siteConfig('http://example.org', 'true').indexable).toBe(false);
    expect(siteConfig('https://example.org', 'false').indexable).toBe(false);
    expect(siteConfig('not a url', 'true')).toEqual({ url: null, indexable: false });
  });

  it('writes crawler files from the route list', () => {
    expect(crawlerFiles(PREVIEW)).toEqual({ robots: 'User-agent: *\nAllow: /\n', sitemap: null });
    const launched = crawlerFiles(LAUNCHED);
    expect(launched.robots).toContain('Sitemap: https://example.org/sitemap.xml');
    expect(launched.sitemap).toContain('<loc>https://example.org/</loc>');
    expect(launched.sitemap).toContain('<loc>https://example.org/privacy</loc>');
    expect(launched.sitemap).not.toContain('/practice');
  });
});

describe('Pages headers (#38)', () => {
  const all = headers.slice(headers.indexOf('/*\n'), headers.indexOf('/graph/*'));
  const csp = /Content-Security-Policy: (.+)/.exec(all)?.[1] ?? '';

  it('keeps the preview noindex and unframeable', () => {
    expect(all).toContain('X-Robots-Tag: noindex');
    expect(all).toContain('X-Frame-Options: DENY');
    expect(all).toContain('X-Content-Type-Options: nosniff');
    expect(all).toContain('Referrer-Policy: no-referrer');
  });

  it('allows scripts only from this site and the analytics beacon', () => {
    const directive = (name: string) => csp.split('; ').find((part) => part.startsWith(`${name} `));
    expect(directive('default-src')).toBe("default-src 'self'");
    expect(directive('script-src')).toBe("script-src 'self' https://static.cloudflareinsights.com");
    expect(directive('object-src')).toBe("object-src 'none'");
    expect(directive('frame-ancestors')).toBe("frame-ancestors 'none'");
    expect(directive('base-uri')).toBe("base-uri 'self'");
    expect(csp).not.toMatch(/unsafe-eval|script-src[^;]*unsafe-inline|\*(?!\.supabase\.co)/);
  });

  it('leaves the preview headers untouched', () => {
    expect(pagesHeaders(headers, PREVIEW)).toBe(headers);
    expect(shellRobots(PREVIEW)).toBe('noindex, nofollow');
  });

  it('indexes only public pages on a launch build (#39)', () => {
    const launched = pagesHeaders(headers, LAUNCHED);
    const rule = (path: string) => launched.slice(launched.lastIndexOf(`\n${path}\n`) + 1).split('\n\n')[0];
    const global = rule('/*');
    expect(global).not.toContain('X-Robots-Tag');
    expect(global).toContain('Strict-Transport-Security: max-age=31536000');
    expect(global).toContain('Content-Security-Policy:');
    for (const path of ['/login', '/dashboard', '/practice', '/history', '/profile', '/shared', '/s/*', '/shared/*', '/auth/*', '/graph/*']) {
      expect(rule(path)).toBe(`${path}\n  X-Robots-Tag: noindex`);
    }
    expect(launched).not.toMatch(/^\/(privacy)?\n {2}X-Robots-Tag/m);
    expect(rule('https://:project.pages.dev/*')).toContain('X-Robots-Tag: noindex');
    expect(launched).toContain('/graph/*\n  ! Content-Security-Policy');
    expect(shellRobots(LAUNCHED)).toBe('index, follow');
    expect(() => pagesHeaders('/*\n  X-Frame-Options: DENY\n', LAUNCHED)).toThrow();
  });

  it('loads nothing from a third party in the page shell', () => {
    expect(indexHtml).not.toMatch(/https?:\/\//);
    expect(indexHtml).toContain('noindex');
  });
});
