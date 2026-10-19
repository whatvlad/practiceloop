import type { Session, SupabaseClient } from '@supabase/supabase-js';
import type { Account } from './types';

export type AuthClient = Pick<SupabaseClient['auth'],
  'getSession' | 'onAuthStateChange' | 'exchangeCodeForSession' | 'signInWithOAuth' | 'signOut'>;

export interface AuthSnapshot {
  status: 'loading' | 'authenticated' | 'unauthenticated';
  account: Account | null;
  error: string | null;
  working: boolean;
}

export interface AuthCallback {
  isCallback: boolean;
  code: string | null;
  failed: boolean;
}

interface AuthOptions {
  redirectTo: string;
  takeCallback: () => AuthCallback;
  onIdentityChange: (id: string | null) => void;
}

const INITIAL: AuthSnapshot = { status: 'loading', account: null, error: null, working: false };
const RESTORE_ERROR = 'Could not restore your session. Please sign in again.';
const CALLBACK_ERROR = 'Google sign-in did not finish. Please try again in this browser.';
const CONFIG_ERROR = 'Sign-in is not configured yet. Please try again later.';

export function createAuthStore(client: AuthClient | null, options: AuthOptions) {
  let snapshot = INITIAL;
  let generation = 0;
  let identity: string | null = null;
  let expiry: ReturnType<typeof setTimeout> | undefined;
  let callback: AuthCallback | undefined;
  let exchange: ReturnType<AuthClient['exchangeCodeForSession']> | undefined;
  const listeners = new Set<() => void>();
  const publish = (next: AuthSnapshot) => {
    snapshot = next;
    listeners.forEach(listener => listener());
  };

  function accept(session: Session | null, error: string | null = null) {
    clearTimeout(expiry);
    const valid = session && session.expires_at && session.expires_at * 1000 > Date.now()
      && session.user.app_metadata.provider === 'google' && !session.user.is_anonymous;
    const user = valid ? session.user : null;
    const nextIdentity = user?.id ?? null;
    if (identity !== nextIdentity) {
      options.onIdentityChange(nextIdentity);
      identity = nextIdentity;
    }
    const name = user?.user_metadata.full_name ?? user?.user_metadata.name;
    const account: Account | null = user ? {
      id: user.id,
      name: typeof name === 'string' && name.trim() ? name.trim() : user.email?.split('@')[0] || 'Learner',
      email: user.email ?? '',
      provider: 'Google',
    } : null;
    publish({ status: account ? 'authenticated' : 'unauthenticated', account, error, working: false });
    if (valid) {
      const current = generation;
      expiry = setTimeout(() => {
        if (current !== generation) return;
        // Hide protected content immediately if refresh has not replaced the expiring session.
        accept(null, 'Your session expired. Please sign in again.');
      }, Math.min(session.expires_at! * 1000 - Date.now(), 2_147_483_647));
    }
  }

  function start(): () => void {
    const current = ++generation;
    let restoring = true;
    let pendingEvent: { session: Session | null } | undefined;
    publish({ ...INITIAL });
    callback ??= options.takeCallback();
    const currentCallback = callback;
    if (!client) {
      accept(null, CONFIG_ERROR);
      return () => { generation++; };
    }
    const { data: { subscription } } = client.onAuthStateChange((event, session) => {
      if (current !== generation || event === 'INITIAL_SESSION') return;
      const next = event === 'SIGNED_OUT' ? null : session;
      if (restoring) pendingEvent = { session: next };
      else accept(next);
    });
    void (async () => {
      try {
        if (currentCallback.failed || (currentCallback.isCallback && !currentCallback.code)) {
          if (current === generation) accept(null, CALLBACK_ERROR);
          return;
        }
        const result = currentCallback.code
          ? await (exchange ??= client.exchangeCodeForSession(currentCallback.code))
          : await client.getSession();
        if (current !== generation) return;
        if (result.error) accept(null, currentCallback.isCallback ? CALLBACK_ERROR : RESTORE_ERROR);
        else accept(pendingEvent ? pendingEvent.session : result.data.session);
        callback = { isCallback: false, code: null, failed: false };
      } catch {
        if (current === generation) accept(null, currentCallback.isCallback ? CALLBACK_ERROR : RESTORE_ERROR);
      } finally {
        restoring = false;
      }
    })();
    return () => {
      generation++;
      subscription.unsubscribe();
      clearTimeout(expiry);
    };
  }

  async function signIn(): Promise<void> {
    if (snapshot.working || snapshot.status === 'loading') return;
    if (!client) { accept(null, CONFIG_ERROR); return; }
    publish({ ...snapshot, error: null, working: true });
    try {
      const { error } = await client.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: options.redirectTo, queryParams: { prompt: 'select_account' } },
      });
      if (error) publish({ ...snapshot, error: CALLBACK_ERROR });
    } catch {
      publish({ ...snapshot, error: CALLBACK_ERROR });
    } finally {
      // The SDK has only initiated navigation. It may be cancelled, or this
      // document may return from browser history, so do not leave it locked.
      publish({ ...snapshot, working: false });
    }
  }

  async function signOut(): Promise<void> {
    if (!client || snapshot.working) return;
    publish({ ...snapshot, error: null, working: true });
    try {
      const { error } = await client.signOut({ scope: 'local' });
      if (error) publish({ ...snapshot, error: 'Could not log out. Please try again.', working: false });
      else accept(null);
    } catch {
      publish({ ...snapshot, error: 'Could not log out. Please try again.', working: false });
    }
  }

  return {
    start, signIn, signOut,
    completeDeletion: async () => {
      try { await client?.signOut({ scope: 'local' }); } catch { /* Backend already denies the deleted identity. */ }
      finally { accept(null); }
    },
    configured: client !== null,
    getSnapshot: () => snapshot,
    getServerSnapshot: () => INITIAL,
    subscribe: (listener: () => void) => { listeners.add(listener); return () => { listeners.delete(listener); }; },
  };
}
