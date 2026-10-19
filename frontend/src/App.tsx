import { useEffect, useState, useSyncExternalStore } from 'react';
import { ApiStatusNotice } from './components/ApiStatusNotice';
import { AppNav, Logo } from './components/AppNav';
import { ButtonLink } from './components/Button';
import { type ApiHealth, authStore, checkApiHealth } from './data/api';
import { DashboardPage } from './pages/DashboardPage';
import { HistoryPage } from './pages/HistoryPage';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { PracticePage } from './pages/PracticePage';
import { ProfilePage } from './pages/ProfilePage';
import { navigate, useLocation } from './router';

const TITLES: Record<string, string> = {
  '/': 'PracticeLoop',
  '/login': 'Sign in · PracticeLoop',
  '/dashboard': 'Dashboard · PracticeLoop',
  '/practice': 'Practice · PracticeLoop',
  '/history': 'History · PracticeLoop',
  '/profile': 'Profile · PracticeLoop',
};

const APP_ROUTES = new Set(['/dashboard', '/practice', '/history', '/profile']);

function NotFoundPage() {
  return (
    <div className="pl-page pl-login">
      <main className="pl-card pl-card--lg pl-stack pl-gap-5 pl-center pl-login-panel">
        <div>
          <Logo />
        </div>
        <h1 className="pl-display-md">
          Nothing <em>here.</em>
        </h1>
        <p className="pl-muted pl-m-0">There is no page at this address.</p>
        <div>
          <ButtonLink to="/" arrow>
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

  const [apiHealth, setApiHealth] = useState<ApiHealth | undefined>(undefined);

  useEffect(() => {
    void checkApiHealth().then(setApiHealth);
  }, []);
  useEffect(() => authStore.start(), []);

  useEffect(() => {
    document.title = TITLES[pathname] ?? 'PracticeLoop';
  }, [pathname]);

  const needsAccount = APP_ROUTES.has(pathname);
  useEffect(() => {
    if (auth.status === 'loading') return;
    if (!account && (needsAccount || pathname === '/auth/callback')) navigate('/login', { replace: true });
    if (account && (pathname === '/login' || pathname === '/auth/callback')) navigate('/dashboard', { replace: true });
  }, [auth.status, account, needsAccount, pathname]);

  async function handleSignIn() {
    if (account) navigate('/dashboard');
    else await authStore.signIn();
  }

  async function handleLogOut() {
    await authStore.signOut();
    if (!authStore.getSnapshot().account) navigate('/');
  }

  const authDisabled = auth.working || auth.status === 'loading' || !authStore.configured;
  if (pathname === '/') return <LandingPage onSignIn={handleSignIn} disabled={authDisabled} busy={auth.working} error={auth.error} signedIn={!!account} />;
  if (pathname === '/login') return <LoginPage onSignIn={handleSignIn} disabled={authDisabled} busy={auth.working} error={auth.error} />;
  if (pathname === '/auth/callback' || (needsAccount && auth.status === 'loading')) {
    return <div className="pl-page pl-login"><p role="status">Restoring your session…</p></div>;
  }
  if (!needsAccount) return <NotFoundPage />;
  if (!account) return <div className="pl-page" />;

  return (
    <div className="pl-page" key={account.id}>
      <AppNav current={pathname} initial={account.name.charAt(0).toUpperCase()} onLogOut={handleLogOut} busy={auth.working} />
      <ApiStatusNotice health={apiHealth} />
      <div className="pl-wrap pl-api-notice">
        <p className="pl-small pl-muted" role="status">Problems, attempts and reveals are saved to your account.</p>
        {auth.error && <p className="pl-result pl-result--invalid" role="alert">{auth.error}</p>}
      </div>
      {pathname === '/dashboard' && <DashboardPage />}
      {pathname === '/practice' && <PracticePage key={params.get('id') ?? 'latest'} id={params.get('id')} />}
      {pathname === '/history' && <HistoryPage />}
      {pathname === '/profile' && <ProfilePage account={account} onLogOut={handleLogOut} busy={auth.working} />}
    </div>
  );
}
