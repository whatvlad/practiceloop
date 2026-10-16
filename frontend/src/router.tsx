import { useSyncExternalStore, type AnchorHTMLAttributes, type MouseEvent } from 'react';

// A minimal History API router: six static routes do not need a dependency.
// Routes are written from "/"; BASE is the deploy prefix (e.g. "/practiceloop"
// on GitHub Pages, set with `vite build --base`), empty in dev.

const CHANGE = 'practiceloop:navigate';
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

function withBase(to: string): string {
  return to.startsWith('/') ? BASE + to : to;
}

function subscribe(onChange: () => void): () => void {
  window.addEventListener('popstate', onChange);
  window.addEventListener(CHANGE, onChange);
  return () => {
    window.removeEventListener('popstate', onChange);
    window.removeEventListener(CHANGE, onChange);
  };
}

function snapshot(): string {
  const { pathname, search } = window.location;
  const path = BASE && pathname.startsWith(BASE) ? pathname.slice(BASE.length) || '/' : pathname;
  return path + search;
}

export function useLocation(): { pathname: string; params: URLSearchParams } {
  const href = useSyncExternalStore(subscribe, snapshot, () => '/');
  const url = new URL(href, 'http://local');
  return { pathname: url.pathname, params: url.searchParams };
}

export function navigate(to: string, options: { replace?: boolean } = {}): void {
  if (to === snapshot()) return;
  if (options.replace) window.history.replaceState(null, '', withBase(to));
  else window.history.pushState(null, '', withBase(to));
  window.dispatchEvent(new Event(CHANGE));
  if (!to.includes('#')) window.scrollTo(0, 0);
}

type LinkProps = AnchorHTMLAttributes<HTMLAnchorElement> & { to: string };

export function Link({ to, onClick, ...rest }: LinkProps) {
  function handleClick(event: MouseEvent<HTMLAnchorElement>) {
    onClick?.(event);
    const modified = event.metaKey || event.ctrlKey || event.shiftKey || event.altKey;
    if (event.defaultPrevented || event.button !== 0 || modified || to.startsWith('#')) return;
    event.preventDefault();
    navigate(to);
  }
  return <a href={withBase(to)} onClick={handleClick} {...rest} />;
}
