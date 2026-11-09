import { FEEDBACK_PATH } from '../legal';
import { Link } from '../router';
import { Logo } from './AppNav';
import { CookieSettingsLink } from './CookieSettingsLink';
import { SUPPORT_PATH, SUPPORT_URL } from '../support';

/** The footer on every page: legal pages, feedback, support and cookie settings. */
export function SiteFooter({ supportUrl = SUPPORT_URL }: { supportUrl?: string }) {
  return (
    <footer className="pl-site-footer">
      <div className="pl-wrap pl-footer">
        <div className="pl-footer-brand">
          <Logo />
          <span>Generated mathematics problems with checked answers.</span>
        </div>
        <nav className="pl-footer-links" aria-label="Footer">
          <Link to="/privacy">Privacy</Link>
          <Link to="/terms">Terms</Link>
          <Link to={FEEDBACK_PATH}>Feedback</Link>
          {supportUrl && <Link to={SUPPORT_PATH}>Support us</Link>}
          <CookieSettingsLink />
        </nav>
      </div>
    </footer>
  );
}
