import { Link } from '../router';
import { Button, ButtonLink } from './Button';
import { LoopMark } from './icons';

export function Logo({ to = '/' }: { to?: string }) {
  return (
    <Link className="pl-logo" to={to}>
      <LoopMark />
      MathLoop
    </Link>
  );
}

const APP_ROUTES = [
  { to: '/dashboard', label: 'Home', also: ['/practice', '/random', '/algebra-random'] },
  { to: '/history', label: 'History', also: [] },
  { to: '/profile', label: 'Profile', also: [] },
] as const;

interface AppNavProps {
  current: string;
  initial: string;
  onLogOut: () => void;
  busy?: boolean;
}

/** Signed-in app bar: wordmark, the three routes and the account area. */
export function AppNav({ current, initial, onLogOut, busy = false }: AppNavProps) {
  return (
    <header className="pl-nav">
      <Logo />
      <nav aria-label="Primary">
        {APP_ROUTES.map((route) => (
          <Link key={route.to} to={route.to} aria-current={route.to === current || (route.also as readonly string[]).includes(current) ? 'page' : undefined}>
            {route.label}
          </Link>
        ))}
      </nav>
      <div className="pl-row pl-nav-account">
        <Button variant="ghost" size="sm" onClick={onLogOut} disabled={busy} aria-busy={busy}>
          {busy ? 'Logging out…' : 'Log out'}
        </Button>
        <Link className="pl-avatar pl-avatar-link" to="/profile" aria-label="Profile" aria-current={current === '/profile' ? 'page' : undefined}>
          <span aria-hidden="true">{initial}</span>
        </Link>
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
          <a className="pl-btn pl-btn--ghost pl-btn--sm pl-nav-secondary" href="#how">
            How it works
          </a>
        ) : (
          <ButtonLink className="pl-nav-secondary" to="/" variant="ghost" size="sm">
            Home
          </ButtonLink>
        )}
        <ButtonLink to="/login" variant="secondary" size="sm">
          Sign in
        </ButtonLink>
      </div>
    </header>
  );
}
