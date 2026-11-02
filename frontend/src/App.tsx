import { useEffect, useState, useSyncExternalStore } from 'react';
import { ApiStatusNotice } from './components/ApiStatusNotice';
import { AppNav, Logo, PublicNav } from './components/AppNav';
import { ButtonLink } from './components/Button';
import { SkipLink } from './components/SkipLink';
import { type ApiHealth, authStore, checkApiHealth } from './data/api';
import { rememberSharedReturn, sharedReturn, takeSharedReturn } from './data/sharedReturn';
import { CurriculumPage } from './pages/CurriculumPage';
import { HistoryPage } from './pages/HistoryPage';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { PrivacyPage } from './pages/PrivacyPage';
import { ProfilePage } from './pages/ProfilePage';
import { SharedProblemPage } from './pages/SharedProblemPage';
import { navigate, useLocation } from './router';
import { applyPageMeta, siteConfig } from './site';

const SITE = siteConfig(import.meta.env.VITE_SITE_URL, import.meta.env.VITE_SITE_INDEXABLE);

const APP_ROUTES = new Set(['/dashboard', '/practice', '/history', '/profile']);
// Pages whose main column is .pl-wrap--narrow (760px) instead of the full 1120px.
const NARROW_ROUTES = new Set(['/practice', '/profile']);

function NotFoundPage() {
  return (
    <div className="pl-page pl-login">
      <main id="main" tabIndex={-1} className="pl-card pl-card--lg pl-stack pl-gap-5 pl-center pl-login-panel">
        <div>
          <Logo />
        </div>
        <h1 className="pl-display-md">
          Nothing <em>here.</em>
        </h1>
        <p className="pl-muted pl-m-0">There is no page at this address.</p>
        <div className="pl-actions pl-center">
          <ButtonLink to="/practice" arrow>
            Practice a problem
          </ButtonLink>
          <ButtonLink to="/" variant="secondary">
            Go to the home page
          </ButtonLink>
        </div>
      </main>
    </div>
  );
}

export function App() {
  const { pathname, params } = useLocation();
  const auth = useSyncExternalStore(authStore.subscribe, authStore.getSnapshot, authStore.getServerSnapshot);
  const account = auth.account;
  const nextShare = sharedReturn(params.get('next'));

  const [apiHealth, setApiHealth] = useState<ApiHealth | undefined>(undefined);

  useEffect(() => {
    void checkApiHealth().then(setApiHealth);
  }, []);
  useEffect(() => authStore.start(), []);

  useEffect(() => {
    applyPageMeta(pathname, SITE);
  }, [pathname]);

  const needsAccount = APP_ROUTES.has(pathname) && pathname !== '/practice';
  useEffect(() => {
    if (auth.status === 'loading') return;
    if (!account && (needsAccount || pathname === '/auth/callback')) navigate('/login', { replace: true });
    if (account && (pathname === '/login' || pathname === '/auth/callback')) {
      const remembered = takeSharedReturn();
      navigate(nextShare ?? remembered ?? '/dashboard', { replace: true });
    }
  }, [auth.status, account, needsAccount, pathname, nextShare]);

  async function handleSignIn() {
    if (account) navigate('/dashboard');
    else {
      // A rejected callback returns to /login; keep its pending exercise for retry.
      if (nextShare || pathname !== '/login') rememberSharedReturn(nextShare);
      await authStore.signIn();
    }
  }

  async function handleLogOut() {
    await authStore.signOut();
    if (!authStore.getSnapshot().account) navigate('/');
  }

  async function handleDeleted() {
    await authStore.completeDeletion();
    navigate('/');
  }

  const authDisabled = auth.working || auth.status === 'loading' || !authStore.configured;
  return <><SkipLink />{route()}</>;

  function route() {
    if (pathname === '/') return <LandingPage onSignIn={handleSignIn} disabled={authDisabled} busy={auth.working} error={auth.error} signedIn={!!account} />;
    // Shared problems (#37) open the same way signed in or not.
    const coded = /^\/p\/([^/]+)$/.exec(pathname);
    if (coded) {
      let code = coded[1];
      try { code = decodeURIComponent(code); } catch { /* The page displays an invalid-code message. */ }
      return <SharedProblemPage key={`${account?.id ?? auth.status}:code:${code}`} token={null} code={null} problemCode={code} signedIn={!!account} authLoading={auth.status === 'loading'} inactive />;
    }
    if (pathname === '/shared') return <SharedProblemPage key={`${account?.id ?? auth.status}:${params.get('code')}`} token={null} code={params.get('code')} signedIn={!!account} authLoading={auth.status === 'loading'} inactive />;
    const shared = /^\/(?:s|shared)\/([^/]+)$/.exec(pathname);
    if (shared) return <SharedProblemPage key={`${account?.id ?? auth.status}:${shared[1]}`} token={decodeURIComponent(shared[1])} code={null} signedIn={!!account} authLoading={auth.status === 'loading'} inactive />;
    if (pathname === '/privacy') return <PrivacyPage />;
    if (pathname === '/login') return <LoginPage onSignIn={handleSignIn} disabled={authDisabled} busy={auth.working} error={auth.error} />;
    if (pathname === '/auth/callback' || (needsAccount && auth.status === 'loading')) {
      return <div className="pl-page pl-login"><p role="status">Restoring your session…</p></div>;
    }
    if (!account && pathname === '/practice' && auth.status !== 'loading') return <div className="pl-page"><PublicNav /><CurriculumPage /></div>;
    if (!APP_ROUTES.has(pathname)) return <NotFoundPage />;
    if (!account) return <div className="pl-page" />;

    // Notices share the column of the page below them, so their left edges line up.
    const wrap = NARROW_ROUTES.has(pathname) ? 'pl-wrap pl-wrap--narrow' : 'pl-wrap';
    return (
      <div className="pl-page" key={account.id}>
        <AppNav current={pathname} initial={account.name.charAt(0).toUpperCase()} onLogOut={handleLogOut} busy={auth.working} />
        <ApiStatusNotice health={apiHealth} wrap={wrap} />
        <section className={`${wrap} pl-api-notice`} aria-label="Account status">
          <p className="pl-small pl-muted" role="status">Problems, attempts and reveals are saved to your account.</p>
          {auth.error && <p className="pl-result pl-result--invalid" role="alert">{auth.error}</p>}
        </section>
        {pathname === '/dashboard' && <CurriculumPage />}
        {pathname === '/practice' && (params.has('id')
          ? <main id="main" tabIndex={-1} className="pl-wrap pl-app-main"><h1 className="pl-display-md">In develop</h1><p>Saved problems are currently inactive.</p><ButtonLink to="/history">View history</ButtonLink></main>
          : <CurriculumPage />)}
        {pathname === '/history' && <HistoryPage inactive />}
        {pathname === '/profile' && <ProfilePage account={account} onLogOut={handleLogOut} onDeleted={handleDeleted} busy={auth.working} />}
      </div>
    );
  }
}
