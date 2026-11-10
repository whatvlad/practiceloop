// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, expect, it } from 'vitest';
import { ThemeToggle } from './ThemeToggle';
import { setTheme } from '../theme';

afterEach(() => {
  localStorage.clear();
  document.documentElement.removeAttribute('data-theme');
});

it('switches between the dark and the light theme', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  setTheme('dark');
  const host = document.createElement('div');
  document.body.append(host);
  const root = createRoot(host);
  await act(async () => root.render(<ThemeToggle />));
  const button = host.querySelector('button')!;
  expect(button.getAttribute('aria-label')).toBe('Switch to light theme');
  await act(async () => button.click());
  expect(document.documentElement.getAttribute('data-theme')).toBe('paper');
  expect(button.getAttribute('aria-label')).toBe('Switch to dark theme');
  await act(async () => root.unmount());
  host.remove();
});
