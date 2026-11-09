import { useEffect, useState } from 'react';
import { buttonClass } from './Button';
import { CrossIcon } from './icons';
import { SOLVED_EVENT, SUPPORT_URL, dismissSupportNotice, supportNoticeDue } from '../support';

/** A small closable toast in the corner of app pages asking for voluntary support. */
export function SupportNotice({ url = SUPPORT_URL }: { url?: string }) {
  const [visible, setVisible] = useState(() => supportNoticeDue(url));
  // The third correct answer usually happens on the same page, so listen rather than wait for navigation.
  useEffect(() => {
    const update = () => setVisible(supportNoticeDue(url));
    window.addEventListener(SOLVED_EVENT, update);
    return () => window.removeEventListener(SOLVED_EVENT, update);
  }, [url]);
  if (!visible) return null;
  function close() {
    dismissSupportNotice();
    setVisible(false);
  }
  return (
    <aside className="pl-support-toast pl-fade" aria-label="Support MathLoop">
      <button type="button" className="pl-support-close" aria-label="Close" onClick={close}><CrossIcon /></button>
      <p className="pl-support-title">Enjoying MathLoop?</p>
      <p className="pl-small pl-muted pl-m-0">It is free and has no ads. If it helps you, you can support the project.</p>
      <div className="pl-support-actions">
        <a className={buttonClass({ size: 'sm' })} href={url} target="_blank" rel="noopener noreferrer" onClick={close}>Support</a>
        <button type="button" className={buttonClass({ variant: 'ghost', size: 'sm' })} onClick={close}>Not now</button>
      </div>
    </aside>
  );
}
