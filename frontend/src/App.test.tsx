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

  it('disables repeated sign-in attempts while opening Google', async () => {
    await renderAt('/login', { ...signedOut, working: true });
    const button = element.querySelector('button')!;
    expect(button.disabled).toBe(true);
    expect(button.textContent).toContain('Opening Google');
    await act(async () => button.click());
    expect(harness.store.signIn).not.toHaveBeenCalled();
  });
});
