import { useState } from 'react';
import { Button } from '../components/Button';
import { StatTile } from '../components/StatTile';
import { getProfileCounts } from '../data/api';
import type { Account } from '../data/types';
import { useLoad } from '../useLoad';

export function ProfilePage({ account, onLogOut, busy = false }: { account: Account; onLogOut: () => void; busy?: boolean }) {
  const [revision, setRevision] = useState(0);
  const counts = useLoad(getProfileCounts, String(revision));
  return (
    <main className="pl-wrap pl-wrap--narrow pl-app-main">
      <div className="pl-label">Profile</div>
      <h1 className="pl-display-md pl-page-title">
        Your <em>account.</em>
      </h1>
      <div className="pl-card pl-card--lg pl-row pl-account">
        <div className="pl-row pl-gap-4">
          <span className="pl-avatar pl-avatar--lg" aria-hidden="true">
            {account.name.charAt(0).toUpperCase()}
          </span>
          <div>
            <div className="pl-h-md">{account.name}</div>
            <div className="pl-muted pl-small">
              {account.email} · Signed in with {account.provider}
            </div>
          </div>
        </div>
        <Button variant="secondary" onClick={onLogOut} disabled={busy} aria-busy={busy}>
          {busy ? 'Logging out…' : 'Log out'}
        </Button>
      </div>
      {counts.status === 'ready' && (
        <>
        <div className="pl-grid-3">
          <StatTile label="Generated" value={counts.data.generated} />
          <StatTile label="Attempted" value={counts.data.attempted} />
          <StatTile label="Correct" value={counts.data.correct} />
        </div>
        <p className="pl-small pl-muted">Each problem is counted once. Correct includes any successful attempt.</p>
        </>
      )}
      {counts.status === 'loading' && <p role="status">Loading your statistics…</p>}
      {counts.status === 'error' && <div role="alert"><p>Your statistics could not be loaded.</p><Button variant="secondary" onClick={() => setRevision(value => value + 1)}>Retry loading statistics</Button></div>}
    </main>
  );
}
