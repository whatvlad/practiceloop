import { useRef, useState } from 'react';
import { shareCode, shareLink, shareProblem, stopSharing } from '../data/api';
import type { ProblemShare } from '../data/types';
import { Button } from './Button';
import text from '../../../backend/app/content/en.json';

function expiryDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

/** The owner's share card (#37): one link and one code for the statement only, revocable. */
export function ShareControls({ problemId, initial }: { problemId: string; initial: ProblemShare | null }) {
  const [share, setShare] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const link = useRef<HTMLInputElement>(null);

  async function run(task: () => Promise<void>) {
    setBusy(true);
    setError('');
    setCopied(false);
    try {
      await task();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : text.service_error);
    } finally {
      setBusy(false);
    }
  }

  async function copy() {
    if (!share) return;
    try {
      await navigator.clipboard.writeText(shareLink(share));
      setCopied(true);
    } catch {
      link.current?.select();
      setError('Copy the selected link with your keyboard.');
    }
  }

  return (
    <section className="pl-card pl-stack pl-gap-3 pl-share" aria-label="Share this problem">
      <div className="pl-row pl-share-head">
        <span className="pl-label">Share</span>
        <span className="pl-small pl-muted">Only the problem is shared. Your answers, results and solutions stay private.</span>
      </div>
      {share ? (
        <>
          <label className="pl-field">
            <span className="pl-small pl-muted">Link</span>
            <input ref={link} className="pl-input pl-share-link" readOnly value={shareLink(share)} onFocus={(event) => event.currentTarget.select()} />
          </label>
          <p className="pl-small pl-m-0">
            Or enter the code <strong className="pl-mono">{shareCode(share.code)}</strong> on the shared problem page. Works until {expiryDate(share.expiresAt)}.
          </p>
          <div className="pl-actions">
            <Button variant="secondary" onClick={() => void copy()} disabled={busy}>
              Copy link
            </Button>
            <Button variant="ghost" onClick={() => void run(async () => { await stopSharing(problemId); setShare(null); })} disabled={busy}>
              Stop sharing
            </Button>
          </div>
        </>
      ) : (
        <div>
          <Button variant="secondary" onClick={() => void run(async () => setShare(await shareProblem(problemId)))} disabled={busy}>
            Share problem
          </Button>
        </div>
      )}
      {copied && <p className="pl-small pl-muted pl-m-0" role="status">Link copied.</p>}
      {error && <p className="pl-small pl-m-0" role="alert">{error}</p>}
    </section>
  );
}
