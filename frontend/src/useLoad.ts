import { useEffect, useState } from 'react';

export type Load<T> = { status: 'loading' } | { status: 'ready'; data: T } | { status: 'error'; error: unknown };

/** Runs an async read once per key and ignores results that arrive after unmount. */
export function useLoad<T>(read: () => Promise<T>, key: string = ''): Load<T> {
  const [state, setState] = useState<Load<T>>({ status: 'loading' });
  useEffect(() => {
    let active = true;
    setState({ status: 'loading' });
    read().then(
      (data) => active && setState({ status: 'ready', data }),
      (error: unknown) => active && setState({ status: 'error', error }),
    );
    return () => {
      active = false;
    };
    // `read` is recreated every render; `key` says when to read again.
  }, [key]);
  return state;
}
