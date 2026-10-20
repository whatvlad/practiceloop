import { Link } from '../router';
import { Button, ButtonLink } from './Button';
import { LoopMark } from './icons';

export function Logo({ to = '/' }: { to?: string }) {
  return (
    <Link className="pl-logo" to={to}>
      <LoopMark />
      PracticeLoop
    </Link>
  );
}

const APP_ROUTES = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/practice', label: 'Practice' },
  { to: '/history', label: 'History' },
  { to: '/profile', label: 'Profile' },
] as const;

interface AppNavProps {
  current: string;
  initial: string;
  onLogOut: () => void;
  busy?: boolean;
}

/** Signed-in app bar: wordmark, the four routes and the account area. */
export function AppNav({ current, initial, onLogOut, busy = false }: AppNavProps) {
  return (
    <header className="pl-nav">
      <Logo to="/dashboard" />
      <nav aria-label="Primary">
        {APP_ROUTES.map((route) => (
          <Link key={route.to} to={route.to} aria-current={route.to === current ? 'page' : undefined}>
            {route.label}
          </Link>
        ))}
      </nav>
      <div className="pl-row pl-nav-account">
        <Button variant="ghost" size="sm" onClick={onLogOut} disabled={busy} aria-busy={busy}>
          {busy ? 'Logging out…' : 'Log out'}
        </Button>
        <span className="pl-avatar" aria-hidden="true">
          {initial}
        </span>
      </div>
    </header>
  );
}

/** Signed-out bar: logo, How it works (Home away from the landing page) and Sign in. */
export function PublicNav({ landing = false }: { landing?: boolean }) {
  return (
    <header className="pl-nav pl-nav--bare">
      <Logo />
      <div className="pl-row">
        {landing ? (
          <a className="pl-btn pl-btn--ghost pl-btn--sm" href="#how">
            How it works
          </a>
        ) : (
          <ButtonLink to="/" variant="ghost" size="sm">
            Home
          </ButtonLink>
        )}
        <ButtonLink to="/login" variant="secondary" size="sm" pill>
          Sign in
        </ButtonLink>
      </div>
    </header>
  );
}
