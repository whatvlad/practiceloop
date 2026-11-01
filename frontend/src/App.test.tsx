// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { AuthSnapshot } from './data/auth';

const harness = vi.hoisted(() => {
  let snapshot: AuthSnapshot = { status: 'loading', account: null, error: null, working: false };
  const listeners = new Set<() => void>();
  const store = {
    configured: true,
    getSnapshot: () => snapshot,
    getServerSnapshot: () => snapshot,
    start: vi.fn(() => () => {}),
    signIn: vi.fn(async () => {}),
    signOut: vi.fn(async () => {}),
    subscribe: (fn: () => void) => { listeners.add(fn); return () => { listeners.delete(fn); }; },
  };
  return { store, set: (next: AuthSnapshot) => { snapshot = next; listeners.forEach(fn => fn()); } };
});

vi.mock('./data/api', async importOriginal => ({
  ...await importOriginal<typeof import('./data/api')>(),
  authStore: harness.store,
  checkApiHealth: vi.fn(async () => 'ok'),
}));

import { App } from './App';

const signedOut: AuthSnapshot = { status: 'unauthenticated', account: null, working: false, error: null };
const signedIn: AuthSnapshot = { ...signedOut, status: 'authenticated', account: {
  id: 'real-user', name: 'A Learner', email: 'learner@example.invalid', provider: 'Google',
} };
let root: Root;
let element: HTMLDivElement;

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  harness.set(signedOut);
  sessionStorage.clear();
  vi.clearAllMocks();
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
  element = document.createElement('div');
  document.body.append(element);
  root = createRoot(element);
});
afterEach(async () => {
  await act(async () => root.unmount());
  element.remove();
  vi.restoreAllMocks();
});

async function renderAt(path: string, state = signedOut) {
  window.history.replaceState(null, '', path);
  harness.set(state);
  await act(async () => root.render(<App />));
}

describe('client route protection and auth UI', () => {
  it.each([signedOut, signedIn])('opens shared problems without redirecting (#37)', async state => {
    await renderAt('/shared', state);
    expect(window.location.pathname).toBe('/shared');
    expect(element.querySelector('h1')?.textContent).toBe('Open a shared problem');
    expect(document.title).toBe('Shared problem · PracticeLoop');
    await renderAt('/s/short', state);
    expect(window.location.pathname).toBe('/s/short');
    expect(element.textContent).toContain('That link or code is not valid.');
  });

  it('handles malformed URL escapes on permanent-code pages without crashing', async () => {
    await renderAt('/p/%E0%A4%A', signedOut);
    expect(element.querySelector('h1')?.textContent).toContain('not valid or is unknown');
    expect(window.location.pathname).toBe('/p/%E0%A4%A');
  });

  it('does not render a protected profile while restoring the session', async () => {
    await renderAt('/profile', { ...signedOut, status: 'loading' });
    expect(element.textContent).toContain('Restoring your session');
    expect(element.textContent).not.toContain('Your account');
    expect(window.location.pathname).toBe('/profile');
    await act(async () => harness.set(signedOut));
    expect(window.location.pathname).toBe('/login');
    expect(element.textContent).toContain('Continue with Google');
  });

  it('renders real account details and removes them immediately on a cross-tab sign-out', async () => {
    await renderAt('/profile', signedIn);
    expect(element.textContent).toContain('learner@example.invalid');
    expect(element.textContent).toContain('Learner');
    expect(element.textContent).not.toContain('Alex Morgan');
    expect(element.textContent).toContain('Problems, attempts and reveals are saved to your account');
    await act(async () => harness.set(signedOut));
    expect(window.location.pathname).toBe('/login');
    expect(element.textContent).not.toContain('learner@example.invalid');
  });

  it('puts the account notice in the column of the page below it (#128)', async () => {
    const column = () => {
      const notice = element.querySelector('[aria-label="Account status"]');
      const main = element.querySelector('main');
      return [notice?.classList.contains('pl-wrap--narrow'), main?.classList.contains('pl-wrap--narrow')];
    };
    await renderAt('/profile', signedIn);
    expect(column()).toEqual([true, true]);
    await renderAt('/history', signedIn);
    expect(column()).toEqual([false, false]);
  });

  it('returns a successful callback to the dashboard and a rejected callback to sign-in', async () => {
    await renderAt('/auth/callback', signedIn);
    expect(window.location.pathname).toBe('/dashboard');
    await act(async () => {
      window.history.replaceState(null, '', '/auth/callback');
      window.dispatchEvent(new Event('popstate'));
      harness.set({ ...signedOut, error: 'Google sign-in did not finish.' });
    });
    expect(window.location.pathname).toBe('/login');
    expect(element.querySelector('[role="alert"]')?.textContent).toBe('Google sign-in did not finish.');
  });

  it.each([`/s/${'a'.repeat(43)}`, '/shared?code=K7M2QX9P', '/p/CMB-1-0000000000000000-32'])('returns from Google to the selected shared problem: %s', async path => {
    await renderAt(`/login?next=${encodeURIComponent(path)}`);
    await act(async () => element.querySelector('button')!.click());
    expect(harness.store.signIn).toHaveBeenCalledOnce();
    // OAuth returns to a fresh callback URL without the original query string.
    await renderAt('/auth/callback', signedIn);
    expect(window.location.pathname + window.location.search).toBe(path);
    expect(sessionStorage.getItem('practiceloop:shared-return')).toBeNull();
  });

  it('preserves the shared exercise after a rejected sign-in and retry', async () => {
    const path = `/s/${'b'.repeat(43)}`;
    await renderAt(`/login?next=${encodeURIComponent(path)}`);
    await act(async () => element.querySelector('button')!.click());
    await renderAt('/auth/callback', { ...signedOut, error: 'Try again.' });
    expect(window.location.pathname).toBe('/login');
    await act(async () => element.querySelector('button')!.click());
    await renderAt('/auth/callback', signedIn);
    expect(window.location.pathname).toBe(path);
  });

  it.each(['https://example.invalid', '//example.invalid', '/practice?id=someone-else', '/s/short'])('ignores unsafe auth destinations: %s', async next => {
    await renderAt(`/login?next=${encodeURIComponent(next)}`, signedIn);
    expect(window.location.pathname).toBe('/dashboard');
  });

  it('disables repeated sign-in attempts while opening Google', async () => {
    await renderAt('/login', { ...signedOut, working: true });
    const button = element.querySelector('button')!;
    expect(button.disabled).toBe(true);
    expect(button.textContent).toContain('Opening Google');
    await act(async () => button.click());
    expect(harness.store.signIn).not.toHaveBeenCalled();
  });
});

describe('routes and public pages (#38)', () => {
  it.each(['/', '/login', '/privacy', '/practice', '/missing', '/shared'])('starts %s with a skip link to the main content', async path => {
    await renderAt(path);
    const skip = element.querySelector<HTMLAnchorElement>('a.pl-skip')!;
    expect(element.querySelector('a')).toBe(skip);
    expect(skip.getAttribute('href')).toBe('#main');
    expect(element.querySelector('main#main')).not.toBeNull();
    expect(document.head.querySelector('meta[name="robots"]')?.getAttribute('content')).toBe('noindex, nofollow');
  });

  it.each([signedOut, signedIn])('puts a practice CTA first in the hero', async state => {
    await renderAt('/', state);
    const cta = element.querySelector<HTMLAnchorElement>('.pl-hero-actions a, .pl-hero-actions button')!;
    expect(cta.getAttribute('href')).toBe('/practice');
  });

  it('serves the privacy draft without an account, naming processors and no invented operator', async () => {
    await renderAt('/privacy');
    expect(window.location.pathname).toBe('/privacy');
    expect(element.querySelector('h1')?.textContent).toBe('Privacy');
    for (const name of ['Supabase', 'Google', 'Cloudflare', 'Oracle Cloud']) expect(element.textContent).toContain(name);
    expect(element.textContent).toContain('Not decided yet');
    expect(element.textContent).not.toMatch(/@|sp\. z o\.o\.|ul\./);
    expect(document.title).toBe('Privacy · PracticeLoop');
  });

  it('opens /shared/<token> like /s/<token>', async () => {
    await renderAt('/shared/short');
    expect(element.textContent).toContain('That link or code is not valid.');
  });

  it('shows a branded 404 with links home and to practice', async () => {
    await renderAt('/nowhere');
    expect(element.textContent).toContain('There is no page at this address.');
    const links = [...element.querySelectorAll('main a')].map(link => link.getAttribute('href'));
    expect(links).toEqual(expect.arrayContaining(['/', '/practice']));
    expect(document.title).toBe('Page not found · PracticeLoop');
  });

  it.each(['/dashboard', '/history', '/profile'])('sends a signed-out visitor from %s to sign-in', async path => {
    await renderAt(path);
    expect(window.location.pathname).toBe('/login');
  });
});
