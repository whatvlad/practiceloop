// Cloudflare Web Analytics (#38): anonymous page views and Web Vitals, no cookies
// or storage. The beacon reports the page URL, so it is not loaded where the URL
// carries something private: the OAuth callback (?code=) and share links (tokens).
// Other paths hold no email, account ID or answer; /practice?id= is a random
// problem ID. Learning metrics stay in Supabase.

export const BEACON_SRC = 'https://static.cloudflareinsights.com/beacon.min.js';
const TOKEN = /^[0-9a-f]{32}$/;

export function analyticsAllowed(pathname: string): boolean {
  return !(pathname.startsWith('/auth/') || pathname.startsWith('/s/') || pathname.startsWith('/shared'));
}

/** Adds the beacon once, when a site token is configured and the landing path is safe. */
export function startWebAnalytics(token: string | undefined, pathname: string, doc: Document = document): boolean {
  if (!token || !TOKEN.test(token) || !analyticsAllowed(pathname)) return false;
  if (doc.querySelector(`script[src="${BEACON_SRC}"]`)) return true;
  const script = doc.createElement('script');
  script.defer = true;
  script.src = BEACON_SRC;
  script.dataset.cfBeacon = JSON.stringify({ token, spa: true });
  doc.head.append(script);
  return true;
}
