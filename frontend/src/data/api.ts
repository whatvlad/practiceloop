// The one data boundary: existing account login and untracked server-generated practice.
import { createAuthStore } from './auth';
import { resetPractice } from './practice';
import { callbackOptions, createBrowserClient } from './supabase';

const client = createBrowserClient();
export const authStore = createAuthStore(client?.auth ?? null, {
  ...callbackOptions(), onIdentityChange: resetPractice,
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
} from './practice';
export { checkApiHealth } from './health';
export type { ApiHealth } from './health';
