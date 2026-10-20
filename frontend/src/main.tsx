import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
// Self-hosted fonts (#38): no request to Google Fonts, so no third party sees visitors.
import '@fontsource/geist/400.css';
import '@fontsource/geist/500.css';
import '@fontsource/geist/600.css';
import '@fontsource/geist-mono/400.css';
import '@fontsource/geist-mono/500.css';
import '@fontsource/instrument-serif/400.css';
import '@fontsource/instrument-serif/400-italic.css';
import 'katex/dist/katex.min.css';
import './styles/tokens.css';
import './styles/components.css';
import './styles/app.css';
import { App } from './App';
import { startWebAnalytics } from './analytics';
import { ErrorBoundary } from './components/ErrorBoundary';

const root = document.getElementById('root');
if (!root) throw new Error('Missing application root');

createRoot(root).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);

startWebAnalytics(import.meta.env.VITE_CF_WEB_ANALYTICS_TOKEN, window.location.pathname.slice(import.meta.env.BASE_URL.length - 1));
