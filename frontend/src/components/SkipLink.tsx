import type { MouseEvent } from 'react';

/** First focusable element on every page: jumps keyboard users past the navigation. */
export function SkipLink() {
  function skip(event: MouseEvent<HTMLAnchorElement>) {
    const main = document.getElementById('main');
    if (!main) return;
    event.preventDefault();
    main.focus();
    main.scrollIntoView();
  }
  return (
    <a className="pl-skip" href="#main" onClick={skip}>
      Skip to content
    </a>
  );
}
