import { useState } from 'react';
import { buttonClass } from './Button';
import { SUPPORT_URL, dismissSupportNotice, supportNoticeDue } from '../support';

/** A quiet, closable request for support at the end of an app page. */
export function SupportNotice({ wrap = 'pl-wrap', url = SUPPORT_URL }: { wrap?: string; url?: string }) {
  const [visible, setVisible] = useState(() => supportNoticeDue(url));
  if (!visible) return null;
  function close() {
    dismissSupportNotice();
    setVisible(false);
  }
  return (
    <section className={`${wrap} pl-support-notice`} aria-label="Support MathLoop">
      <div className="pl-support-card">
        <p className="pl-m-0">MathLoop is free. If it helps you, you can support the project.</p>
        <div className="pl-support-actions">
          <a className={buttonClass({ size: 'sm' })} href={url} target="_blank" rel="noopener noreferrer" onClick={close}>Support</a>
          <button type="button" className={buttonClass({ variant: 'ghost', size: 'sm' })} onClick={close}>Not now</button>
        </div>
      </div>
    </section>
  );
}
