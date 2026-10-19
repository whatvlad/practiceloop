import type { Session } from '@supabase/supabase-js';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { createAuthStore, type AuthCallback, type AuthClient } from './auth';
import { parseCallback, validPublicConfig } from './supabase';

const none: AuthCallback = { isCallback: false, code: null, failed: false };
function session(id = 'user-a', expires = Math.floor(Date.now() / 1000) + 3600): Session {
  return {
    access_token: 'synthetic', refresh_token: 'synthetic', token_type: 'bearer', expires_in: 3600,
    expires_at: expires,
    user: { id, app_metadata: { provider: 'google' }, user_metadata: { full_name: 'Real Learner' },
      email: 'learner@example.invalid', aud: 'authenticated', created_at: '', is_anonymous: false },
  };
}

function setup(initial: Session | null = null, callback = none) {
  let listener: ((event: string, session: Session | null) => void) | undefined;
  const unsubscribe = vi.fn();
  const client = {
    getSession: vi.fn().mockResolvedValue({ data: { session: initial }, error: null }),
    exchangeCodeForSession: vi.fn().mockResolvedValue({ data: { session: initial }, error: null }),
    onAuthStateChange: vi.fn(fn => {
      listener = fn;
      return { data: { subscription: { unsubscribe } } };
    }),
    signInWithOAuth: vi.fn().mockResolvedValue({ data: { url: 'https://example.invalid' }, error: null }),
    signOut: vi.fn().mockResolvedValue({ error: null }),
  };
  const identityChange = vi.fn();
  const takeCallback = vi.fn(() => callback);
  const store = createAuthStore(client as unknown as AuthClient, {
    redirectTo: 'https://app.example.invalid/auth/callback', takeCallback, onIdentityChange: identityChange,
  });
  return { store, client, identityChange, takeCallback, unsubscribe,
    event: (event: string, value: Session | null) => listener?.(event, value) };
}

const stops: Array<() => void> = [];
async function start(store: ReturnType<typeof createAuthStore>) {
  stops.push(store.start());
  await Promise.resolve();
  await Promise.resolve();
}
afterEach(() => { stops.splice(0).forEach(stop => stop()); vi.useRealTimers(); });

describe('real auth lifecycle', () => {
  it('removes a deleted identity even when local sign-out fails', async () => {
    const { store, client, identityChange } = setup(session());
    await start(store);
    client.signOut.mockRejectedValueOnce(new Error('network'));
    await store.completeDeletion();
    expect(store.getSnapshot().account).toBeNull();
    expect(store.getSnapshot().status).toBe('unauthenticated');
    expect(identityChange).toHaveBeenLastCalledWith(null);
  });
  it('restores the real account and clears it on cross-tab logout', async () => {
    const { store, event, identityChange } = setup(session());
    await start(store);
    expect(store.getSnapshot().account).toEqual({
      id: 'user-a', name: 'Real Learner', email: 'learner@example.invalid', provider: 'Google',
    });
    event('SIGNED_OUT', null);
    expect(store.getSnapshot().status).toBe('unauthenticated');
    expect(identityChange.mock.calls).toEqual([['user-a'], [null]]);
  });

  it('uses Google and the fixed same-origin callback, preventing duplicate submits', async () => {
    const { store, client } = setup();
    await start(store);
    await Promise.all([store.signIn(), store.signIn()]);
    expect(client.signInWithOAuth).toHaveBeenCalledTimes(1);
    expect(client.signInWithOAuth).toHaveBeenCalledWith({ provider: 'google', options: {
      redirectTo: 'https://app.example.invalid/auth/callback', queryParams: { prompt: 'select_account' },
    } });
  });

  it('exchanges a PKCE code once under StrictMode setup/cleanup/setup', async () => {
    const { store, client, takeCallback, unsubscribe } = setup(session(), {
      isCallback: true, code: 'synthetic-once-only-code', failed: false,
    });
    const stop = store.start();
    stop();
    await start(store);
    expect(client.exchangeCodeForSession).toHaveBeenCalledTimes(1);
    expect(takeCallback).toHaveBeenCalledTimes(1);
    expect(unsubscribe).toHaveBeenCalledTimes(1);
    expect(store.getSnapshot().status).toBe('authenticated');
  });

  it('unlocks sign-in when navigation is interrupted, including after logout', async () => {
    const { store, client, event } = setup(session());
    await start(store);
    await store.signOut();
    let finish!: () => void;
    client.signInWithOAuth.mockImplementationOnce(() => new Promise(resolve => {
      finish = () => resolve({ data: { url: 'https://example.invalid' }, error: null });
    }));
    const pending = store.signIn();
    expect(store.getSnapshot().working).toBe(true);
    await store.signIn();
    expect(client.signInWithOAuth).toHaveBeenCalledTimes(1);
    // SDK initiation succeeds, but the browser never leaves this document.
    finish();
    await pending;
    expect(store.getSnapshot().working).toBe(false);
    expect(store.getSnapshot().account).toBeNull();
    await store.signIn();
    expect(client.signInWithOAuth).toHaveBeenCalledTimes(2);
    event('SIGNED_IN', session());
    await store.signOut();
    await store.signIn();
    expect(client.signInWithOAuth).toHaveBeenCalledTimes(3);
    expect(store.getSnapshot().working).toBe(false);
  });

  it('unlocks failed sign-in and allows a retry without exposing provider details', async () => {
    const { store, client } = setup();
    await start(store);
    client.signInWithOAuth.mockRejectedValueOnce(new Error('private provider details'));
    await store.signIn();
    expect(store.getSnapshot().working).toBe(false);
    expect(store.getSnapshot().error).toContain('did not finish');
    expect(store.getSnapshot().error).not.toContain('private');
    await store.signIn();
    expect(client.signInWithOAuth).toHaveBeenCalledTimes(2);
    expect(store.getSnapshot().error).toBeNull();
  });

  it('does not let a stale initial session undo a newer logout', async () => {
    const { store, client, event } = setup();
    let finish!: (value: unknown) => void;
    client.getSession.mockReturnValue(new Promise(resolve => { finish = resolve; }));
    stops.push(store.start());
    event('SIGNED_OUT', null);
    finish({ data: { session: session() }, error: null });
    await Promise.resolve();
    expect(store.getSnapshot().account).toBeNull();
  });

  it('updates refreshed sessions and hides protected content on expiry', async () => {
    vi.useFakeTimers();
    const { store, event } = setup(session('user-a', Math.floor(Date.now() / 1000) + 10));
    await start(store);
    event('TOKEN_REFRESHED', session('user-a', Math.floor(Date.now() / 1000) + 60));
    vi.advanceTimersByTime(11_000);
    expect(store.getSnapshot().status).toBe('authenticated');
    vi.advanceTimersByTime(50_000);
    expect(store.getSnapshot().status).toBe('unauthenticated');
  });

  it('fails closed on expired sessions and restore/network errors without exposing error details', async () => {
    const expired = setup(session('user-a', 1));
    await start(expired.store);
    expect(expired.store.getSnapshot().account).toBeNull();
    const failed = setup();
    failed.client.getSession.mockRejectedValue(new Error('sensitive error details'));
    await start(failed.store);
    expect(failed.store.getSnapshot().status).toBe('unauthenticated');
    expect(failed.store.getSnapshot().error).not.toContain('sensitive');
  });

  it('reports provider cancellation without calling an exchange or exposing the callback', async () => {
    const { store, client } = setup(null, { isCallback: true, code: null, failed: true });
    await start(store);
    expect(client.exchangeCodeForSession).not.toHaveBeenCalled();
    expect(store.getSnapshot().error).toContain('did not finish');
  });

  it('logs out only this session and preserves the account when logout fails', async () => {
    const { store, client } = setup(session());
    await start(store);
    client.signOut.mockResolvedValueOnce({ error: new Error('raw provider detail') });
    await store.signOut();
    expect(store.getSnapshot().account?.id).toBe('user-a');
    expect(store.getSnapshot().error).toBe('Could not log out. Please try again.');
    await store.signOut();
    expect(client.signOut).toHaveBeenCalledWith({ scope: 'local' });
    expect(store.getSnapshot().account).toBeNull();
  });

  it('fails closed without public config and never falls back to a mock account', async () => {
    const store = createAuthStore(null, { redirectTo: '', takeCallback: () => none, onIdentityChange: vi.fn() });
    await start(store);
    await store.signIn();
    expect(store.configured).toBe(false);
    expect(store.getSnapshot().account).toBeNull();
    expect(store.getSnapshot().error).toContain('not configured');
  });
});

describe('public configuration and callback hygiene', () => {
  it('rejects backend/legacy credentials, URL passwords and unencrypted remote projects', () => {
    expect(validPublicConfig('https://example.supabase.co', 'sb_publishable_fixture')).toBe(true);
    for (const key of ['sb_secret_fixture', 'legacy-jwt', undefined]) {
      expect(validPublicConfig('https://example.supabase.co', key)).toBe(false);
    }
    expect(validPublicConfig('https://user:password@example.invalid', 'sb_publishable_fixture')).toBe(false);
    expect(validPublicConfig('http://example.invalid', 'sb_publishable_fixture')).toBe(false);
  });

  it('only consumes codes on the fixed callback and strips auth data without interpreting redirects', () => {
    const parsed = parseCallback('https://app.invalid/auth/callback?code=once&next=https://evil.invalid', '/auth/callback');
    expect(parsed).toMatchObject({ code: 'once', isCallback: true, failed: false });
    expect(parsed.cleanUrl).toBe('/auth/callback?next=https%3A%2F%2Fevil.invalid');
    expect(parseCallback('https://app.invalid/?code=ignore', '/auth/callback').code).toBeNull();
    expect(parseCallback('https://app.invalid/?code=ignore', '/auth/callback').failed).toBe(true);
    const error = parseCallback('https://app.invalid/auth/callback#error=cancel&access_token=private', '/auth/callback');
    expect(error.failed).toBe(true);
    expect(error.cleanUrl).toBe('/auth/callback');
    expect(parseCallback('https://app.invalid/#how', '/auth/callback').cleanUrl).toBe('/#how');
  });
});
