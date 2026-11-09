import { useRef, useState } from 'react';
import { Button } from '../components/Button';
import { deleteAccount, getDisplayName, saveDisplayName } from '../data/api';
import { useLoad } from '../useLoad';

function NameForm({ initial, onSaved }: { initial: string | null; onSaved: () => void }) {
  const [name, setName] = useState(initial ?? '');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const pending = useRef(false);
  return <form className="pl-stack pl-gap-3" onSubmit={async event => {
    event.preventDefault();
    if (pending.current) return;
    pending.current = true; setBusy(true); setMessage('');
    try { await saveDisplayName(name); setMessage(name.trim() ? 'Display name saved.' : 'Display name removed.'); onSaved(); }
    catch { setMessage('Your name could not be saved. Try again.'); }
    finally { pending.current = false; setBusy(false); }
  }}>
    <label htmlFor="display-name">Display name (optional)</label>
    <input id="display-name" className="pl-input" maxLength={80} value={name} disabled={busy} onChange={event => setName(event.target.value)} aria-describedby="name-help" />
    <p id="name-help" className="pl-small pl-muted pl-m-0">Private to you. Leave blank and save to remove it. This does not change your Google name.</p>
    <div><Button type="submit" variant="secondary" disabled={busy}>{busy ? 'Saving…' : 'Save display name'}</Button></div>
    {message && <p role="status">{message}</p>}
  </form>;
}

export function AccountSettings({ onDeleted, onNameSaved }: { onDeleted: () => Promise<void>; onNameSaved: () => void }) {
  const [revision, setRevision] = useState(0);
  const displayName = useLoad(getDisplayName, String(revision));
  const [confirming, setConfirming] = useState(false);
  const [confirmation, setConfirmation] = useState('');
  const [busy, setBusy] = useState(false);
  const [deleted, setDeleted] = useState(false);
  const [error, setError] = useState('');
  const pending = useRef(false);
  return <section className="pl-card pl-card--lg pl-stack pl-gap-4" aria-labelledby="settings-title">
    <h2 id="settings-title" className="pl-h-lg">Account settings</h2>
    {displayName.status === 'ready' && <NameForm initial={displayName.data} onSaved={onNameSaved} />}
    {displayName.status === 'loading' && <p role="status">Loading your display name…</p>}
    {displayName.status === 'error' && <div role="alert"><p>Your display name could not be loaded.</p><Button variant="secondary" onClick={() => setRevision(value => value + 1)}>Retry loading name</Button></div>}
    <hr className="pl-sep" />
    <h3 className="pl-h-md">Delete your account</h3>
    <p className="pl-small pl-muted pl-m-0">Permanently delete your MathLoop account, problems, answers, results and profile. This cannot be undone. Your Google account is unaffected.</p>
    <p className="pl-small pl-muted pl-m-0">Active data is removed immediately. Our retention policy requires recovery backups to expire within 30 days.</p>
    {!confirming ? <div><Button variant="secondary" onClick={() => setConfirming(true)}>Delete account…</Button></div> :
      <form className="pl-stack pl-gap-3" onSubmit={async event => {
        event.preventDefault();
        if (pending.current || confirmation !== 'DELETE') return;
        pending.current = true; setBusy(true); setError('');
        try { if (!deleted) { await deleteAccount(); setDeleted(true); } await onDeleted(); }
        catch { setError(deleted ? 'Your account was deleted. Reload this page to finish signing out.' : 'Deletion could not be completed. Try again; you will stay signed in.'); }
        finally { pending.current = false; setBusy(false); }
      }}>
        <label htmlFor="delete-confirmation">Type DELETE to confirm permanent deletion</label>
        <input id="delete-confirmation" className="pl-input" value={confirmation} onChange={event => setConfirmation(event.target.value)} disabled={busy} autoComplete="off" />
        <div className="pl-actions"><Button type="submit" disabled={busy || confirmation !== 'DELETE'}>{busy ? 'Deleting…' : 'Permanently delete account'}</Button><Button variant="ghost" disabled={busy} onClick={() => { setConfirming(false); setConfirmation(''); setError(''); }}>Cancel</Button></div>
      </form>}
    {error && <p role="alert">{error}</p>}
  </section>;
}
