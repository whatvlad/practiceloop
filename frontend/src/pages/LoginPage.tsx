import { Logo } from '../components/AppNav';
import { Button } from '../components/Button';

export function LoginPage({ onSignIn }: { onSignIn: () => void }) {
  return (
    <div className="pl-page pl-login">
      <main className="pl-problem pl-login-panel">
        <div className="pl-center">
          <Logo />
        </div>
        <div className="pl-center">
          <h1 className="pl-display-md">
            Welcome <em>back.</em>
          </h1>
          <p className="pl-muted pl-login-text">Sign in to save every problem you generate.</p>
        </div>
        <Button size="lg" block onClick={onSignIn}>
          <span className="pl-g-icon pl-g-letter" aria-hidden="true">
            G
          </span>{' '}
          Continue with Google
        </Button>
        <p className="pl-small pl-subtle pl-m-0 pl-center">Google is the only sign-in method for now.</p>
      </main>
    </div>
  );
}
