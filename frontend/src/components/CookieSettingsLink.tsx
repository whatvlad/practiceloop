import { cookiebotEnabled, openCookieSettings } from '../cookieConsent';
import { navigate } from '../router';

/**
 * Reopens the consent banner, so withdrawing is as easy as agreeing. The banner stays
 * off on share and sign-in URLs, so there it opens Privacy, where the banner loads.
 */
export function CookieSettingsLink() {
  if (!cookiebotEnabled()) return null;
  return <button type="button" className="pl-link-button" onClick={() => { if (!openCookieSettings()) navigate('/privacy'); }}>Cookie settings</button>;
}
