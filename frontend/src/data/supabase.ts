import { createClient } from '@supabase/supabase-js';
import type { AuthCallback, GoogleRedirect } from './auth';

export function validPublicConfig(rawUrl: string | undefined, key: string | undefined): boolean {
  if (!rawUrl || !key?.startsWith('sb_publishable_')) return false;
  try {
    const url = new URL(rawUrl);
    const local = ['localhost', '127.0.0.1'].includes(url.hostname);
    return (url.protocol === 'https:' || (url.protocol === 'http:' && local))
      && !url.username && !url.password && url.pathname === '/' && !url.search && !url.hash;
  } catch { return false; }
}

export function createBrowserClient() {
  const url = import.meta.env.VITE_SUPABASE_URL;
  const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;
  if (!validPublicConfig(url, key)) return null;
  return createClient(url!, key!, {
    auth: { flowType: 'pkce', detectSessionInUrl: false, persistSession: true, autoRefreshToken: true },
  });
}

/** A Google OAuth web client ID is public, but only this shape is accepted. */
export function validGoogleClientId(id: string | undefined): id is string {
  return !!id && /^[0-9]+-[0-9a-z]+\.apps\.googleusercontent\.com$/.test(id);
}

const GOOGLE_AUTHORIZE = 'https://accounts.google.com/o/oauth2/v2/auth';
const GOOGLE_PENDING = 'mathloop.google-sign-in';
const PENDING_MAX_AGE = 10 * 60_000;

function randomToken(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/** Google gets SHA-256(nonce) in hex; Supabase hashes the raw nonce the same way and compares. */
export async function hashNonce(nonce: string): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(nonce));
  return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('');
}

export function googleAuthorizeUrl(clientId: string, redirectUri: string, state: string, hashedNonce: string): string {
  const url = new URL(GOOGLE_AUTHORIZE);
  url.search = new URLSearchParams({
    client_id: clientId, redirect_uri: redirectUri, response_type: 'id_token',
    scope: 'openid email profile', nonce: hashedNonce, state, prompt: 'select_account',
  }).toString();
  return url.href;
}

export function googleRedirect(clientId: string, redirectUri: string, storage: () => Storage,
  navigate: (url: string) => void, now: () => number = Date.now): GoogleRedirect {
  return {
    begin: async () => {
      const state = randomToken();
      const nonce = randomToken();
      storage().setItem(GOOGLE_PENDING, JSON.stringify({ state, nonce, at: now() }));
      navigate(googleAuthorizeUrl(clientId, redirectUri, state, await hashNonce(nonce)));
    },
    takeNonce: state => {
      try {
        const raw = storage().getItem(GOOGLE_PENDING);
        storage().removeItem(GOOGLE_PENDING);
        const pending: unknown = raw ? JSON.parse(raw) : null;
        if (!state || !pending || typeof pending !== 'object') return null;
        const { state: saved, nonce, at } = pending as Record<string, unknown>;
        const fresh = typeof at === 'number' && now() - at >= 0 && now() - at < PENDING_MAX_AGE;
        return saved === state && typeof nonce === 'string' && fresh ? nonce : null;
      } catch { return null; }
    },
  };
}

const AUTH_PARAMS = ['code', 'error', 'error_code', 'error_description', 'access_token', 'refresh_token',
  'provider_token', 'provider_refresh_token', 'expires_in', 'expires_at', 'token_type'];

export function parseCallback(href: string, callbackPath: string): AuthCallback & { cleanUrl: string } {
  const url = new URL(href);
  const fragment = new URLSearchParams(url.hash.slice(1));
  const isCallback = url.pathname === callbackPath;
  // /shared?code=... is an exercise reference, including under a deploy prefix.
  const isSharedCode = url.pathname === callbackPath.replace(/\/auth\/callback$/, '/shared');
  const code = isCallback ? url.searchParams.get('code') : null;
  const idToken = isCallback ? fragment.get('id_token') : null;
  const state = isCallback ? fragment.get('state') : null;
  const failed = ['error', 'error_description', 'error_code', 'access_token', 'refresh_token']
    .some(key => url.searchParams.has(key) || fragment.has(key))
    || (!isCallback && !isSharedCode && url.searchParams.has('code')) || (code !== null && code.length > 2048)
    || (idToken !== null && idToken.length > 16_384);
  for (const key of AUTH_PARAMS) {
    if (key !== 'code' || !isSharedCode) url.searchParams.delete(key);
  }
  if (AUTH_PARAMS.some(key => fragment.has(key)) || (isCallback && url.hash)) url.hash = '';
  return { isCallback, code, failed, idToken, state, cleanUrl: url.pathname + url.search + url.hash };
}

export function callbackOptions() {
  const callbackPath = `${import.meta.env.BASE_URL}auth/callback`;
  const redirectTo = typeof window === 'undefined' ? '' : new URL(callbackPath, window.location.origin).href;
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  return {
    redirectTo,
    // Without a client ID, sign-in keeps the Supabase-hosted Google redirect.
    google: typeof window !== 'undefined' && validGoogleClientId(clientId)
      ? googleRedirect(clientId, redirectTo, () => window.sessionStorage, url => window.location.assign(url))
      : null,
    takeCallback: (): AuthCallback => {
      if (typeof window === 'undefined') return { isCallback: false, code: null, failed: false };
      const result = parseCallback(window.location.href, callbackPath);
      window.history.replaceState(null, '', result.cleanUrl);
      window.dispatchEvent(new Event('popstate'));
      return result;
    },
  };
}
