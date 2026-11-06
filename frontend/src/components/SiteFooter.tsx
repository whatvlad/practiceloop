import { FEEDBACK_HREF } from '../legal';
import { Link } from '../router';
import { Logo } from './AppNav';
import { CookieSettingsLink } from './CookieSettingsLink';

/** The footer on every page: legal pages, feedback and cookie settings. */
export function SiteFooter() {
  return (
    <footer className="pl-site-footer">
      <div className="pl-wrap pl-footer">
        <div className="pl-footer-brand">
          <Logo />
          <span>Math practice, on loop.</span>
        </div>
        <nav className="pl-footer-links" aria-label="Footer">
          <Link to="/privacy">Privacy</Link>
          <Link to="/terms">Terms</Link>
          <a href={FEEDBACK_HREF}>Feedback</a>
          <CookieSettingsLink />
        </nav>
      </div>
    </footer>
  );
}
