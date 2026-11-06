import { cookiebotEnabled, openCookieSettings } from '../cookieConsent';

/** Reopens the consent banner, so withdrawing is as easy as agreeing. Hidden while the banner is off. */
export function CookieSettingsLink() {
  if (!cookiebotEnabled()) return null;
  return <button type="button" className="pl-link-button" onClick={() => openCookieSettings()}>Cookie settings</button>;
}
