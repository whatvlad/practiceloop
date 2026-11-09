// Voluntary support for MathLoop (donations through an external page, no perks).
// The notice waits until a learner has solved a few problems, and stays away for a
// while after it is closed. Everything lives in this browser's local storage.

/** The external support page; empty hides every support link and the notice. */
export const SUPPORT_URL = 'https://ko-fi.com/mathloop';
export const SUPPORT_PROVIDER = 'Ko-fi';
export const SUPPORT_AFTER_SOLVED = 3;
export const SUPPORT_SNOOZE_DAYS = 60;

const SOLVED_KEY = 'mathloop:solved-count';
const DISMISSED_KEY = 'mathloop:support-dismissed';
const DAY_MS = 24 * 60 * 60 * 1000;
/** Fired on window after each solved problem, so an open notice can appear without a reload. */
export const SOLVED_EVENT = 'mathloop:solved';

type Store = Pick<Storage, 'getItem' | 'setItem'>;

function browserStore(): Store | null {
  try { return window.localStorage; } catch { return null; }
}

function readNumber(store: Store | null, key: string): number {
  try {
    const value = Number(store?.getItem(key));
    return Number.isFinite(value) && value > 0 ? value : 0;
  } catch { return 0; }
}

function write(store: Store | null, key: string, value: number): void {
  try { store?.setItem(key, String(value)); } catch { /* Storage may be disabled. */ }
}

/** Counts one correctly solved problem on this device. */
export function recordSolved(store: Store | null = browserStore()): void {
  write(store, SOLVED_KEY, readNumber(store, SOLVED_KEY) + 1);
  if (typeof window !== 'undefined') window.dispatchEvent(new Event(SOLVED_EVENT));
}

/** True once enough problems are solved and the notice was not closed recently. */
export function supportNoticeDue(url: string = SUPPORT_URL, now: number = Date.now(), store: Store | null = browserStore()): boolean {
  if (!url || readNumber(store, SOLVED_KEY) < SUPPORT_AFTER_SOLVED) return false;
  const dismissed = readNumber(store, DISMISSED_KEY);
  return !dismissed || now - dismissed >= SUPPORT_SNOOZE_DAYS * DAY_MS;
}

/** Hides the notice for SUPPORT_SNOOZE_DAYS. */
export function dismissSupportNotice(now: number = Date.now(), store: Store | null = browserStore()): void {
  write(store, DISMISSED_KEY, now);
}
