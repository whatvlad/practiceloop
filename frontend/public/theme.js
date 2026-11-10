/* global window, document, localStorage */
// Runs before the page paints (a blocking script in <head>), so a saved or system
// light theme never flashes the dark one first. src/theme.ts owns the same key.
(function () {
  var theme;
  try { theme = localStorage.getItem('practiceloop:theme'); } catch { theme = null; }
  if (theme !== 'light' && theme !== 'dark') {
    theme = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }
  var root = document.documentElement;
  root.setAttribute('data-theme', theme === 'light' ? 'paper' : 'ink');
  root.style.colorScheme = theme;
})();
