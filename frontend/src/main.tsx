import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
// Self-hosted fonts (#38): no request to Google Fonts, so no third party sees visitors.
import '@fontsource/geist/400.css';
import '@fontsource/geist/500.css';
import '@fontsource/geist/600.css';
import '@fontsource/geist-mono/400.css';
import '@fontsource/geist-mono/500.css';
import 'katex/dist/katex.min.css';
import './styles/tokens.css';
import './styles/components.css';
import './styles/app.css';
import { App } from './App';
import { startWebAnalytics } from './analytics';
import { cookiebotEnabled, startCookiebot, whenStatisticsAllowed } from './cookieConsent';
import { ErrorBoundary } from './components/ErrorBoundary';
import { startTheme } from './theme';

// public/theme.js already set the theme before the first paint; this keeps it in step with the system.
startTheme();

const path = () => window.location.pathname.slice(import.meta.env.BASE_URL.length - 1);
// The banner loads before the app renders, so it is in place before anything else
// runs; App.tsx adds it later for a visitor who landed on a private URL.
startCookiebot(import.meta.env.VITE_COOKIEBOT_ID, path());

const root = document.getElementById('root');
if (!root) throw new Error('Missing application root');

createRoot(root).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);

// With a consent banner the beacon waits for statistics consent; without one it is
// cookieless and needs none.
const analytics = () => startWebAnalytics(import.meta.env.VITE_CF_WEB_ANALYTICS_TOKEN, path());
if (cookiebotEnabled()) whenStatisticsAllowed(analytics);
else analytics();
