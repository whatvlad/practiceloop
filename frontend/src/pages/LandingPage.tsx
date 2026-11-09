import { PublicNav } from '../components/AppNav';
import { Button, ButtonLink } from '../components/Button';
import { Link } from '../router';

export function LandingPage({ onSignIn, disabled = false, busy = false, error = null, signedIn = false }: {
  onSignIn: () => void; disabled?: boolean; busy?: boolean; error?: string | null; signedIn?: boolean;
}) {
  const label = busy ? 'Opening Google…' : signedIn ? 'Open MathLoop' : 'Continue with Google';
  return (
    <div className="pl-page">
      <PublicNav landing />
      <main id="main" tabIndex={-1}>
        <section className="pl-wrap pl-hero">
          <h1 className="pl-display-xl">Practice mathematics, one problem at a time</h1>
          <p className="pl-lead pl-hero-lead">Generated problems in algebra, analysis and probability, with instant answer checks and full solutions.</p>
          <div className="pl-actions pl-hero-actions">
            {signedIn
              ? <ButtonLink to="/dashboard" size="lg" arrow>Go to home</ButtonLink>
              : <ButtonLink to="/demo" size="lg" arrow>Try a problem</ButtonLink>}
            <Button variant="secondary" size="lg" onClick={onSignIn} disabled={disabled} aria-busy={busy}>{label}</Button>
          </div>
          {error && <p className="pl-result pl-result--invalid" role="alert">{error}</p>}
        </section>
        <section id="how" className="pl-wrap pl-section">
          <h2 className="pl-h-lg">Explore the curriculum</h2>
          <p className="pl-muted">The demo needs no account. Sign in with Google to generate problems in every available topic, print worksheets and keep your history. <Link to="/practice">Browse topics</Link>.</p>
        </section>
      </main>
    </div>
  );
}
