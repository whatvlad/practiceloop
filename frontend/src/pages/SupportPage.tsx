import { useState } from 'react';
import { PublicNav } from '../components/AppNav';
import { Button } from '../components/Button';
import { Link } from '../router';
import { SUPPORT_PROVIDER, SUPPORT_URL, supportPanelUrl } from '../support';

/**
 * Voluntary support. The Ko-fi panel is a third-party frame that can set its own
 * cookies, so it loads only after the visitor asks for it.
 */
export function SupportPage({ url = SUPPORT_URL }: { url?: string }) {
  const [open, setOpen] = useState(false);
  const panel = supportPanelUrl(url);
  return (
    <div className="pl-page">
      <PublicNav />
      <main id="main" tabIndex={-1} className="pl-wrap pl-wrap--narrow pl-app-main pl-stack pl-gap-5">
        <div>
          <h1 className="pl-display-md">Support MathLoop</h1>
          <p className="pl-lead">
            MathLoop is free and has no ads or paid features. If it helps you study, a small tip helps pay for the
            servers and new topics. Supporting is voluntary and does not unlock anything.
          </p>
        </div>
        {panel && (open
          ? <iframe className="pl-support-frame" src={panel} title={`Support MathLoop on ${SUPPORT_PROVIDER}`} allow="payment" />
          : <section className="pl-card pl-stack pl-gap-3" aria-label="Donation form">
            <p className="pl-m-0">
              The form is provided by {SUPPORT_PROVIDER}, which handles the payment. Loading it connects to {SUPPORT_PROVIDER}{' '}
              and its payment providers, which may set their own cookies. See <Link to="/privacy">Privacy</Link>.
            </p>
            <div className="pl-actions">
              <Button onClick={() => setOpen(true)}>Show the donation form</Button>
            </div>
          </section>)}
        {url && <p className="pl-small pl-muted pl-m-0">
          Prefer a new tab? <a href={url} target="_blank" rel="noopener noreferrer">Open our {SUPPORT_PROVIDER} page</a>.
        </p>}
      </main>
    </div>
  );
}
