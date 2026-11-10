import { setTheme, useTheme } from '../theme';
import { MoonIcon, SunIcon } from './icons';

/** One button in the top bar: switches between the dark and the light look. */
export function ThemeToggle() {
  const theme = useTheme();
  const next = theme === 'dark' ? 'light' : 'dark';
  const label = next === 'light' ? 'Switch to light theme' : 'Switch to dark theme';
  return (
    <button type="button" className="pl-theme-toggle" onClick={() => setTheme(next)} aria-label={label} title={label}>
      {next === 'light' ? <SunIcon /> : <MoonIcon />}
    </button>
  );
}
