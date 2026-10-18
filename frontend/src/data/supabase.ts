import { createClient } from '@supabase/supabase-js';
import type { AuthCallback } from './auth';

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

const AUTH_PARAMS = ['code', 'error', 'error_code', 'error_description', 'access_token', 'refresh_token',
  'provider_token', 'provider_refresh_token', 'expires_in', 'expires_at', 'token_type'];

export function parseCallback(href: string, callbackPath: string): AuthCallback & { cleanUrl: string } {
  const url = new URL(href);
  const fragment = new URLSearchParams(url.hash.slice(1));
  const isCallback = url.pathname === callbackPath;
  const code = isCallback ? url.searchParams.get('code') : null;
  const failed = ['error', 'error_description', 'error_code', 'access_token', 'refresh_token']
    .some(key => url.searchParams.has(key) || fragment.has(key))
    || (!isCallback && url.searchParams.has('code')) || (code !== null && code.length > 2048);
  for (const key of AUTH_PARAMS) url.searchParams.delete(key);
  if (AUTH_PARAMS.some(key => fragment.has(key))) url.hash = '';
  return { isCallback, code, failed, cleanUrl: url.pathname + url.search + url.hash };
}

export function callbackOptions() {
  const callbackPath = `${import.meta.env.BASE_URL}auth/callback`;
  return {
    redirectTo: typeof window === 'undefined' ? '' : new URL(callbackPath, window.location.origin).href,
    takeCallback: (): AuthCallback => {
      if (typeof window === 'undefined') return { isCallback: false, code: null, failed: false };
      const result = parseCallback(window.location.href, callbackPath);
      window.history.replaceState(null, '', result.cleanUrl);
      window.dispatchEvent(new Event('popstate'));
      return result;
    },
  };
}
