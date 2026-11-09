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
        <section id="how" className="pl-wrap pl-section pl-how" aria-labelledby="how-title">
          <h2 id="how-title" className="pl-display-md">How it works</h2>
          <ul className="pl-how-steps">
            <li><h3 className="pl-h-md">Pick a topic and a level</h3><p className="pl-muted">Matrices, integrals, complex numbers, probability and more, from basic to advanced.</p></li>
            <li><h3 className="pl-h-md">Solve and check</h3><p className="pl-muted">Type your answer as a formula. MathLoop checks it at once, so you know straight away.</p></li>
            <li><h3 className="pl-h-md">See the full solution</h3><p className="pl-muted">Reveal the answer or every step. Each problem stays in your history to retry or print.</p></li>
          </ul>
          <p className="pl-muted pl-how-note">The demo needs no account. Sign in with Google to practise every topic and keep your history. <Link to="/practice">Browse topics</Link></p>
        </section>
      </main>
    </div>
  );
}
