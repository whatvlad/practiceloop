// Cookiebot consent banner. Off until VITE_COOKIEBOT_ID holds the public domain
// group ID. It stays off where the URL carries something private (see analytics.ts).
import { analyticsAllowed } from './analytics';

export const COOKIEBOT_SRC = 'https://consent.cookiebot.com/uc.js';
const CBID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

declare global {
  interface Window {
    Cookiebot?: { renew?: () => void; consent?: { statistics?: boolean } };
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

/**
 * Runs `start` once the visitor has allowed statistics cookies, now or later.
 * Cookiebot fires CookiebotOnConsentReady on load (stored choice) and on every
 * change, so nothing optional runs before consent (Cookiebot "prior consent").
 */
export function whenStatisticsAllowed(start: () => void, win: Window = window): void {
  let started = false;
  const check = () => {
    if (started || !win.Cookiebot?.consent?.statistics) return;
    started = true;
    win.removeEventListener('CookiebotOnConsentReady', check);
    start();
  };
  win.addEventListener('CookiebotOnConsentReady', check);
  check();
}

/** Reopens the banner so a visitor can change or withdraw their choice; false if it has not loaded. */
export function openCookieSettings(win: Window = window): boolean {
  if (!win.Cookiebot?.renew) return false;
  win.Cookiebot.renew();
  return true;
}
