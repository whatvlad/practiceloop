import { Logo } from '../components/AppNav';
import { Button } from '../components/Button';
import { Link } from '../router';

export function LoginPage({ onSignIn, disabled = false, busy = false, error = null }: {
  onSignIn: () => void; disabled?: boolean; busy?: boolean; error?: string | null;
}) {
  return (
    <div className="pl-page pl-login">
      <main id="main" tabIndex={-1} className="pl-problem pl-login-panel">
        <div className="pl-center">
          <Logo />
        </div>
        <div className="pl-center">
          <h1 className="pl-display-md">Sign in</h1>
          <p className="pl-muted pl-login-text">Sign in to save your practice, history and progress.</p>
        </div>
        {error && <p className="pl-result pl-result--invalid" role="alert">{error}</p>}
        <Button size="lg" block onClick={onSignIn} disabled={disabled} aria-busy={busy}>
          <span className="pl-g-icon pl-g-letter" aria-hidden="true">
            G
          </span>{' '}
          {busy ? 'Opening Google…' : 'Continue with Google'}
        </Button>
        <p className="pl-small pl-subtle pl-m-0 pl-center">Google is the only sign-in method. Accounts are for learners aged 16 and over. By continuing, you agree to the <Link to="/terms">Terms</Link> and can read the <Link to="/privacy">Privacy</Link> page.</p>
      </main>
    </div>
  );
}
