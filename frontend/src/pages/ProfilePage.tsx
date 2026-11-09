import { useState } from 'react';
import { Button } from '../components/Button';
import { getDisplayName, getProfileCounts } from '../data/api';
import { Link } from '../router';
import type { Account } from '../data/types';
import { useLoad } from '../useLoad';
import { AccountSettings } from './AccountSettings';

// The "+ C" omission statistics (LearningStatistics) are hidden from the profile for now, at the owner's request.
export function ProfilePage({ account, onLogOut, onDeleted = async () => {}, busy = false }: { account: Account; onLogOut: () => void; onDeleted?: () => Promise<void>; busy?: boolean }) {
  const [revision, setRevision] = useState(0);
  const counts = useLoad(getProfileCounts, String(revision));
  const displayName = useLoad(getDisplayName, String(revision));
  const name = displayName.status === 'ready' ? displayName.data || 'Learner' : 'Learner';
  const rate = counts.status === 'ready' && counts.data.attempted > 0 ? Math.round((counts.data.correct / counts.data.attempted) * 100) : null;
  return (
    <main id="main" tabIndex={-1} className="pl-wrap pl-app-main">
      <h1 className="pl-display-md pl-page-title">Profile</h1>
      <div className="pl-profile-grid">
        <div className="pl-stack pl-gap-4">
          <section className="pl-card pl-card--lg pl-profile-account" aria-label="Account">
            <span className="pl-avatar pl-avatar--lg" aria-hidden="true">
              {name.charAt(0).toUpperCase()}
            </span>
            <div className="pl-profile-who">
              <div className="pl-h-md">{name}</div>
              <div className="pl-muted">{account.email}</div>
              <div className="pl-small pl-subtle">Signed in with {account.provider}</div>
            </div>
            <Button variant="secondary" block onClick={onLogOut} disabled={busy} aria-busy={busy}>
              {busy ? 'Logging out…' : 'Log out'}
            </Button>
          </section>
          <section className="pl-card pl-card--lg pl-stack pl-gap-4" aria-labelledby="stats-title">
            <h2 id="stats-title" className="pl-h-md pl-m-0">Statistics</h2>
            {counts.status === 'ready' && <>
              <dl className="pl-home-stats pl-profile-stats">
                <div><dt>Generated</dt><dd>{counts.data.generated}</dd></div>
                <div><dt>Attempted</dt><dd>{counts.data.attempted}</dd></div>
                <div><dt>Correct</dt><dd>{counts.data.correct}</dd></div>
                <div><dt>Success rate</dt><dd>{rate === null ? '—' : `${rate}%`}</dd></div>
              </dl>
              <p className="pl-small pl-muted pl-m-0">Each problem is counted once. Correct includes any successful attempt.</p>
            </>}
            {counts.status === 'loading' && <p role="status">Loading your statistics…</p>}
            {counts.status === 'error' && <div role="alert"><p>Your statistics could not be loaded.</p><Button variant="secondary" onClick={() => setRevision(value => value + 1)}>Retry loading statistics</Button></div>}
          </section>
        </div>
        <div className="pl-stack pl-gap-4">
          <AccountSettings onDeleted={onDeleted} onNameSaved={() => setRevision(value => value + 1)} />
          <p className="pl-small pl-muted pl-m-0">
            What we store and how deletion works: <Link to="/privacy">Privacy</Link>.
          </p>
        </div>
      </div>
    </main>
  );
}
