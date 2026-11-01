import { normalizeCode } from './shares';
import { normalizeProblemCode } from './problemCodes';

const KEY = 'practiceloop:shared-return';

/** Only shared exercise routes may be carried across OAuth, never arbitrary URLs. */
export function sharedReturn(value: string | null): string | null {
  if (!value) return null;
  const permanent = /^\/p\/([^/]+)$/.exec(value);
  if (permanent) {
    try {
      const code = normalizeProblemCode(decodeURIComponent(permanent[1]));
      return code ? `/p/${code}` : null;
    } catch { return null; }
  }
  const token = /^\/(?:s|shared)\/([A-Za-z0-9_-]{43})$/.exec(value);
  if (token) return `/s/${token[1]}`;
  if (!value.startsWith('/shared?')) return null;
  const params = new URLSearchParams(value.slice('/shared?'.length));
  const code = normalizeCode(params.get('code') ?? '');
  return code ? `/shared?code=${code}` : null;
}

export function rememberSharedReturn(value: string | null): void {
  try {
    const path = sharedReturn(value);
    if (path) sessionStorage.setItem(KEY, path);
    else sessionStorage.removeItem(KEY);
  } catch { /* Sign-in still works when browser storage is unavailable. */ }
}

export function takeSharedReturn(): string | null {
  try {
    const path = sessionStorage.getItem(KEY);
    sessionStorage.removeItem(KEY);
    return sharedReturn(path);
  } catch { return null; }
}
