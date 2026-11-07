// Cookiebot consent banner. Off until VITE_COOKIEBOT_ID holds the public domain
// group ID. It stays off where the URL carries something private (see analytics.ts).
import { analyticsAllowed } from './analytics';

export const COOKIEBOT_SRC = 'https://consent.cookiebot.com/uc.js';
const CBID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

declare global {
  interface Window {
    Cookiebot?: { renew?: () => void };
  }
}

export function cookiebotEnabled(id: string | undefined = import.meta.env.VITE_COOKIEBOT_ID): boolean {
  return !!id && CBID.test(id);
}

/** Adds the banner script once, when an ID is configured and the path is safe. */
export function startCookiebot(id: string | undefined, pathname: string, doc: Document = document): boolean {
  if (!cookiebotEnabled(id) || !analyticsAllowed(pathname)) return false;
  if (doc.getElementById('Cookiebot')) return true;
  const script = doc.createElement('script');
  script.id = 'Cookiebot';
  script.src = COOKIEBOT_SRC;
  script.async = true;
  script.dataset.cbid = id;
  doc.head.append(script);
  return true;
}

/** Reopens the banner so a visitor can change or withdraw their choice; false if it has not loaded. */
export function openCookieSettings(win: Window = window): boolean {
  if (!win.Cookiebot?.renew) return false;
  win.Cookiebot.renew();
  return true;
}
