// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';
import { THEME_KEY, currentTheme, setTheme, startTheme } from './theme';

afterEach(() => {
  localStorage.clear();
  document.documentElement.removeAttribute('data-theme');
});

describe('theme', () => {
  it('maps the light and dark themes to the paper and ink tokens and saves the choice', () => {
    setTheme('light');
    expect(document.documentElement.getAttribute('data-theme')).toBe('paper');
    expect(document.documentElement.style.colorScheme).toBe('light');
    expect(localStorage.getItem(THEME_KEY)).toBe('light');
    expect(currentTheme()).toBe('light');
    setTheme('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('ink');
    expect(currentTheme()).toBe('dark');
  });

  it('starts from a saved choice, else from the system setting', () => {
    localStorage.setItem(THEME_KEY, 'light');
    startTheme();
    expect(currentTheme()).toBe('light');
    localStorage.clear();
    startTheme();
    // jsdom has no matchMedia, so there is no system preference: dark.
    expect(currentTheme()).toBe('dark');
  });
});
