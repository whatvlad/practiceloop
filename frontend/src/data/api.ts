// The one data boundary for pages: real Supabase Auth, temporary demo practice.
import { createAuthStore } from './auth';
import { setDemoOwner } from './mock/server';
import { callbackOptions, createBrowserClient } from './supabase';

const client = createBrowserClient();
export const authStore = createAuthStore(client?.auth ?? null, {
  ...callbackOptions(), onIdentityChange: setDemoOwner,
});

export {
  NotFoundError,
  generateProblem,
  getLastSelection,
  getProblem,
  getProfileCounts,
  listProblems,
  revealAnswer,
  revealSolution,
  submitAttempt,
} from './mock/server';
export { checkApiHealth } from './health';
export type { ApiHealth } from './health';
