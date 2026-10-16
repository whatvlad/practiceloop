import { useEffect, useState } from 'react';
import { AppNav, Logo } from './components/AppNav';
import { ButtonLink } from './components/Button';
import { getAccount, signIn, signOut } from './data/api';
import type { Account } from './data/types';
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
  // undefined while the session is being restored.
  const [account, setAccount] = useState<Account | null | undefined>(undefined);

  useEffect(() => {
    void getAccount().then(setAccount);
  }, []);

  useEffect(() => {
    document.title = TITLES[pathname] ?? 'PracticeLoop';
  }, [pathname]);

  const needsAccount = APP_ROUTES.has(pathname);
  useEffect(() => {
    if (account === null && needsAccount) navigate('/login', { replace: true });
    if (account && pathname === '/login') navigate('/dashboard', { replace: true });
  }, [account, needsAccount, pathname]);

  async function handleSignIn() {
    setAccount(await signIn());
    navigate('/dashboard');
  }

  async function handleLogOut() {
    await signOut();
    setAccount(null);
    navigate('/');
  }

  if (pathname === '/') return <LandingPage onSignIn={handleSignIn} />;
  if (pathname === '/login') return <LoginPage onSignIn={handleSignIn} />;
  if (!needsAccount) return <NotFoundPage />;
  if (!account) return <div className="pl-page" />;

  return (
    <div className="pl-page">
      <AppNav current={pathname} initial={account.name.charAt(0).toUpperCase()} onLogOut={handleLogOut} />
      {pathname === '/dashboard' && <DashboardPage />}
      {pathname === '/practice' && <PracticePage id={params.get('id')} />}
      {pathname === '/history' && <HistoryPage />}
      {pathname === '/profile' && <ProfilePage account={account} onLogOut={handleLogOut} />}
    </div>
  );
}
