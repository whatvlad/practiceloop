import { useState } from 'react';
import { Button } from '../components/Button';
import { StatTile } from '../components/StatTile';
import { getDisplayName, getProfileCounts } from '../data/api';
import { CookieSettingsLink } from '../components/CookieSettingsLink';
import { FEEDBACK_HREF } from '../legal';
import { Link } from '../router';
import type { Account } from '../data/types';
import { useLoad } from '../useLoad';
import { AccountSettings } from './AccountSettings';
import { LearningStatistics } from './LearningStatistics';

export function ProfilePage({ account, onLogOut, onDeleted = async () => {}, busy = false }: { account: Account; onLogOut: () => void; onDeleted?: () => Promise<void>; busy?: boolean }) {
  const [revision, setRevision] = useState(0);
  const counts = useLoad(getProfileCounts, String(revision));
  const displayName = useLoad(getDisplayName, String(revision));
  const name = displayName.status === 'ready' ? displayName.data || 'Learner' : 'Learner';
  return (
    <main id="main" tabIndex={-1} className="pl-wrap pl-wrap--narrow pl-app-main">
      <div className="pl-label">Profile</div>
      <h1 className="pl-display-md pl-page-title">
        Your <em>account.</em>
      </h1>
      <div className="pl-card pl-card--lg pl-row pl-account">
        <div className="pl-row pl-gap-4">
          <span className="pl-avatar pl-avatar--lg" aria-hidden="true">
            {name.charAt(0).toUpperCase()}
          </span>
          <div>
            <div className="pl-h-md">{name}</div>
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
      <LearningStatistics />
      <AccountSettings onDeleted={onDeleted} onNameSaved={() => setRevision(value => value + 1)} />
      <p className="pl-small pl-muted">
        What we store and how deletion works: <Link to="/privacy">Privacy</Link>. Rules for using PracticeLoop: <Link to="/terms">Terms</Link>. Questions or ideas: <a href={FEEDBACK_HREF}>send feedback</a>. <CookieSettingsLink />
      </p>
    </main>
  );
}
