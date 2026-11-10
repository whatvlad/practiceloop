import { useSyncExternalStore } from 'react';

/** The site's two looks: dark ("ink" tokens) and light ("paper" tokens). */
export type Theme = 'dark' | 'light';

// public/theme.js reads the same key before the first paint.
export const THEME_KEY = 'practiceloop:theme';
const TOKENS: Record<Theme, string> = { dark: 'ink', light: 'paper' };
const listeners = new Set<() => void>();

function systemTheme(): Theme {
  return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}

function savedTheme(): Theme | null {
  try {
    const value = localStorage.getItem(THEME_KEY);
    return value === 'light' || value === 'dark' ? value : null;
  } catch {
    return null;
  }
}

/** The theme on the page now: the saved choice, else the system's. */
export function currentTheme(): Theme {
  return document.documentElement.getAttribute('data-theme') === TOKENS.light ? 'light' : 'dark';
}

function apply(theme: Theme) {
  const root = document.documentElement;
  root.setAttribute('data-theme', TOKENS[theme]);
  root.style.colorScheme = theme;
  listeners.forEach((listener) => listener());
}

/** Saves the visitor's choice; from then on the system setting no longer applies. */
export function setTheme(theme: Theme) {
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    // Private mode: the choice lasts for this page only.
  }
  apply(theme);
}

/** Puts the theme on the page and follows the system setting until the visitor picks one. */
export function startTheme() {
  apply(savedTheme() ?? systemTheme());
  if (typeof window.matchMedia !== 'function') return;
  window.matchMedia('(prefers-color-scheme: light)').addEventListener?.('change', () => {
    if (!savedTheme()) apply(systemTheme());
  });
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

/** The current theme; the component renders again when it changes. */
export function useTheme(): Theme {
  return useSyncExternalStore(subscribe, currentTheme, () => 'dark');
}
