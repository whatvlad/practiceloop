import { Component, type ReactNode } from 'react';
import text from '../../../backend/app/content/en.json';

/** Last resort for a render crash: a safe message instead of a blank page; no error text is shown. */
export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <div className="pl-page pl-login">
        <main id="main" tabIndex={-1} className="pl-card pl-card--lg pl-stack pl-gap-5 pl-center pl-login-panel" role="alert">
          <h1 className="pl-display-md">Something broke.</h1>
          <p className="pl-muted pl-m-0">{text.service_error}</p>
          <div>
            <a className="pl-btn pl-btn--primary" href={import.meta.env.BASE_URL}>
              Reload MathLoop
            </a>
          </div>
        </main>
      </div>
    );
  }
}
