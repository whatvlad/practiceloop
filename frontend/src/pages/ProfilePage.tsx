import { Button } from '../components/Button';
import { StatTile } from '../components/StatTile';
import { getProfileCounts } from '../data/api';
import type { Account } from '../data/types';
import { useLoad } from '../useLoad';

export function ProfilePage({ account, onLogOut }: { account: Account; onLogOut: () => void }) {
  const counts = useLoad(getProfileCounts);
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
        <Button variant="secondary" onClick={onLogOut}>
          Log out
        </Button>
      </div>
      {counts.status === 'ready' && (
        <div className="pl-grid-3">
          <StatTile label="Generated" value={counts.data.generated} />
          <StatTile label="Attempted" value={counts.data.attempted} />
          <StatTile label="Correct" value={counts.data.correct} />
        </div>
      )}
    </main>
  );
}
