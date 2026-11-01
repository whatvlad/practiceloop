// Page metadata for every route, in one place (#38). Indexing needs both an
// approved site URL (VITE_SITE_URL) and VITE_SITE_INDEXABLE=true; until the
// custom domain launches (#39) every page is noindex. No og:image yet: there is
// no approved source logo or sharing image.

export const SITE_NAME = 'PracticeLoop';
const DESCRIPTION =
  'Practice mathematics with generated problems, checked answers, full solutions and a saved history.';

export interface PageMeta {
  title: string;
  description: string;
  /** Public content a search engine may list once the site is indexable. */
  indexable: boolean;
}

function page(title: string, description: string, indexable = false): PageMeta {
  return { title: title === SITE_NAME ? title : `${title} · ${SITE_NAME}`, description, indexable };
}

const PAGES: Record<string, PageMeta> = {
  '/': page(SITE_NAME, DESCRIPTION, true),
  '/privacy': page('Privacy', 'What PracticeLoop stores, why, who processes it and how to delete it.', true),
  '/login': page('Sign in', 'Sign in with Google to save problems, attempts and statistics.'),
  '/dashboard': page('Dashboard', 'Your practice overview.'),
  '/practice': page('Practice', 'Solve a generated mathematics problem.'),
  '/history': page('History', 'Every problem you have generated.'),
  '/profile': page('Profile', 'Your account, statistics and data.'),
  '/shared': page('Shared problem', 'A mathematics problem shared from PracticeLoop.'),
  '/auth/callback': page('Signing in', 'Finishing Google sign-in.'),
};
const NOT_FOUND = page('Page not found', 'There is no page at this address.');

/** Routes a sitemap lists. */
export const PUBLIC_PATHS = Object.keys(PAGES).filter((path) => PAGES[path].indexable);

export function isSharedPath(pathname: string): boolean {
  return pathname === '/shared' || /^\/(s|shared)\/[^/]+$/.test(pathname);
}

export function pageMeta(pathname: string): PageMeta {
  if (/^\/p\/[^/]+$/.test(pathname)) return page('Problem from code', 'Open a mathematics problem by its code.');
  if (isSharedPath(pathname)) return PAGES['/shared'];
  return Object.hasOwn(PAGES, pathname) ? PAGES[pathname] : NOT_FOUND;
}

export interface SiteConfig {
  /** Approved origin plus deploy base, without a trailing slash; null on preview. */
  url: string | null;
  indexable: boolean;
}

export function siteConfig(rawUrl: string | undefined, rawIndexable: string | undefined): SiteConfig {
  let url: string | null = null;
  try {
    const parsed = new URL(rawUrl ?? '');
    if (parsed.protocol === 'https:' && !parsed.username && !parsed.password && !parsed.search && !parsed.hash) {
      url = parsed.origin + parsed.pathname.replace(/\/+$/, '');
    }
  } catch {
    url = null;
  }
  return { url, indexable: url !== null && rawIndexable === 'true' };
}

function setMeta(attribute: 'name' | 'property', key: string, content: string | null): void {
  let tag = document.head.querySelector<HTMLMetaElement>(`meta[${attribute}="${key}"]`);
  if (content === null) {
    tag?.remove();
    return;
  }
  if (!tag) {
    tag = document.createElement('meta');
    tag.setAttribute(attribute, key);
    document.head.append(tag);
  }
  tag.content = content;
}

function setCanonical(href: string | null): void {
  let link = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
  if (href === null) {
    link?.remove();
    return;
  }
  if (!link) {
    link = document.createElement('link');
    link.rel = 'canonical';
    document.head.append(link);
  }
  link.href = href;
}

/** Writes title, description, robots, canonical, Open Graph and Twitter tags for a route. */
export function applyPageMeta(pathname: string, config: SiteConfig): void {
  const meta = pageMeta(pathname);
  const indexed = config.indexable && meta.indexable;
  const canonical = indexed && config.url ? config.url + (pathname === '/' ? '/' : pathname) : null;
  document.title = meta.title;
  setMeta('name', 'description', meta.description);
  setMeta('name', 'robots', indexed ? 'index, follow' : 'noindex, nofollow');
  setMeta('property', 'og:site_name', SITE_NAME);
  setMeta('property', 'og:type', 'website');
  setMeta('property', 'og:title', meta.title);
  setMeta('property', 'og:description', meta.description);
  setMeta('property', 'og:url', canonical);
  setMeta('name', 'twitter:card', 'summary');
  setMeta('name', 'twitter:title', meta.title);
  setMeta('name', 'twitter:description', meta.description);
  setCanonical(canonical);
}

/** robots.txt and, once indexable, sitemap.xml for the build output. */
export function crawlerFiles(config: SiteConfig): { robots: string; sitemap: string | null } {
  if (!config.indexable || !config.url) {
    // Crawling stays allowed so crawlers see the noindex header and meta tag.
    return { robots: 'User-agent: *\nAllow: /\n', sitemap: null };
  }
  const urls = PUBLIC_PATHS.map((path) => `  <url><loc>${config.url}${path === '/' ? '/' : path}</loc></url>`);
  return {
    robots: `User-agent: *\nAllow: /\n\nSitemap: ${config.url}/sitemap.xml\n`,
    sitemap: `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`,
  };
}

/** Paths that stay noindex after launch; the app's own 404 sets its meta tag at runtime. */
export const NOINDEX_PATHS = [
  ...Object.keys(PAGES).filter((path) => !PAGES[path].indexable && !path.startsWith('/auth/')),
  '/s/*',
  '/shared/*',
  '/p/*',
  '/auth/*',
  '/graph/*',
];

/** robots meta tag in index.html, read before the app runs. */
export function shellRobots(config: SiteConfig): string {
  return config.indexable ? 'index, follow' : 'noindex, nofollow';
}

const GLOBAL_NOINDEX = '/*\n  X-Robots-Tag: noindex\n';

/**
 * Cloudflare Pages `_headers` for a build (#39). Preview keeps public/_headers
 * as is. A launch build drops the global noindex, adds HSTS, keeps every
 * non-public route noindex and keeps the *.pages.dev addresses out of search.
 */
export function pagesHeaders(preview: string, config: SiteConfig): string {
  if (!config.indexable) return preview;
  if (!preview.includes(GLOBAL_NOINDEX)) throw new Error('public/_headers no longer starts the /* rule with X-Robots-Tag: noindex.');
  const rules = [
    ...NOINDEX_PATHS.map((path) => `${path}\n  X-Robots-Tag: noindex`),
    'https://:project.pages.dev/*\n  X-Robots-Tag: noindex',
    'https://:version.:project.pages.dev/*\n  X-Robots-Tag: noindex',
  ];
  return `${preview.replace(GLOBAL_NOINDEX, '/*\n  Strict-Transport-Security: max-age=31536000\n').trimEnd()}

# Launch build (${config.url}): only public pages are indexable.
${rules.join('\n\n')}
`;
}
