import { PublicNav, Logo } from '../components/AppNav';
import { Button } from '../components/Button';
import { DifficultyDots } from '../components/DifficultyScale';
import { ResultBanner } from '../components/ResultBanner';
import { Tex } from '../components/Tex';

const STEPS = [
  { title: 'Choose a topic', text: 'Basic integrals, substitution, by parts, rational and trigonometric.' },
  { title: 'Set the difficulty', text: 'Five levels, from Basic to Advanced.' },
  { title: 'Type your answer', text: 'Write 3pi, sqrt(3) or pi/4 + 2. Equivalent forms all count.' },
  { title: 'Learn, then loop', text: 'Reveal the answer or the full solution, then generate the next problem.' },
];

const PRINCIPLES = [
  {
    title: 'Generated from structures',
    text: 'Problems are built from predefined mathematical rules, not written freehand by a language model.',
  },
  {
    title: 'Verified symbolically',
    text: 'Every answer is calculated and checked by a symbolic mathematics engine before you see the problem.',
  },
  { title: 'Checked by equivalence', text: '1/2 and 2/4 are the same answer. We compare mathematics, not text.' },
];

/** A static ProblemCard in its Correct state, as the product demo. */
function DemoCard() {
  return (
    <figure className="pl-landing-demo">
      <figcaption className="pl-sr-only">
        Example: the integral of 2x cos(x squared) dx, answered sin(x squared) + C, marked Correct.
      </figcaption>
      <div className="pl-problem pl-problem--compact" inert>
        <div className="pl-problem-head">
          <div className="meta">
            <span className="pl-tag">Integration — Substitution</span>
            <span className="pl-small pl-muted">
              <DifficultyDots level={3} />
            </span>
          </div>
          <span className="pl-label">Generated just now</span>
        </div>
        <div className="pl-expr">
          <Tex latex={'\\int 2x\\cos(x^2)\\,dx'} />
        </div>
        <div className="pl-row pl-landing-demo-answer">
          <input className="pl-input" value="sin(x^2) + C" aria-label="Your answer" readOnly tabIndex={-1} />
          <Button tabIndex={-1}>Check answer</Button>
        </div>
        <ResultBanner state="correct" message="Equivalent to the solution." live={false} />
      </div>
    </figure>
  );
}

export function LandingPage({ onSignIn }: { onSignIn: () => void }) {
  return (
    <div className="pl-page">
      <PublicNav />
      <main>
        <section className="pl-wrap pl-hero">
          <div className="pl-label pl-hero-eyebrow">Calculus · Integration</div>
          <h1 className="pl-display-xl">
            Practice until
            <br />
            it <em>clicks.</em>
          </h1>
          <p className="pl-lead pl-hero-lead">
            Fresh integration problems, built from mathematical rules and verified by a symbolic engine. Check your
            answer, reveal the solution, go again.
          </p>
          <div className="pl-actions pl-hero-actions">
            <Button size="lg" pill arrow onClick={onSignIn}>
              Continue with Google
            </Button>
            <a className="pl-btn pl-btn--secondary pl-btn--lg pl-btn--pill" href="#how">
              See how it works
            </a>
          </div>
        </section>

        <section className="pl-wrap pl-wrap--narrow pl-section">
          <DemoCard />
        </section>

        <section id="how" className="pl-wrap pl-section">
          <div className="pl-label">How it works</div>
          <h2 className="pl-display-lg pl-how-title">
            Four taps from a topic to a <em>solved</em> problem.
          </h2>
          <ol className="pl-grid-4">
            {STEPS.map((step, index) => (
              <li key={step.title} className="pl-card">
                <div className="pl-display-md" aria-hidden="true">
                  {index + 1}
                </div>
                <h3 className="pl-h-md pl-how-step-title">{step.title}</h3>
                <p className="pl-muted pl-small pl-m-0">{step.text}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className="pl-wrap pl-section">
          <div className="pl-principles">
            <div>
              <div className="pl-label">The difference</div>
              <h2 className="pl-display-lg pl-mt-4">
                Rules, not <em>guesses.</em>
              </h2>
            </div>
            <div className="pl-stack pl-gap-5">
              {PRINCIPLES.map((item, index) => (
                <div key={item.title} className="pl-stack pl-gap-5">
                  {index > 0 && <hr className="pl-sep" />}
                  <div>
                    <h3 className="pl-h-md">{item.title}</h3>
                    <p className="pl-muted pl-principle-text">{item.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="pl-wrap pl-section">
          <div className="pl-card pl-card--lg pl-cta">
            <h2 className="pl-display-lg">Ready for problem one?</h2>
            <p className="pl-lead pl-cta-lead">Sign in and every problem you generate is saved to your history.</p>
            <Button size="lg" pill arrow onClick={onSignIn}>
              Continue with Google
            </Button>
          </div>
        </section>
      </main>
      <footer className="pl-wrap pl-row pl-small pl-subtle pl-footer">
        <Logo />
        <span>Math practice, on loop.</span>
      </footer>
    </div>
  );
}
