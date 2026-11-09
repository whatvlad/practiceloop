// The data boundary selects saved practice for an account and preview for a guest.
import { createAuthStore } from './auth';
import { configurePracticeAuth, resetPractice } from './practice';
import { callbackOptions, createBrowserClient } from './supabase';
import { resetWorksheets } from './worksheets';

const client = createBrowserClient();
export const authStore = createAuthStore(client?.auth ?? null, {
  ...callbackOptions(), onIdentityChange: () => { resetPractice(); resetWorksheets(); },
});

configurePracticeAuth(async () => {
  const auth = authStore.getSnapshot();
  if (auth.status === 'loading') throw new Error('Wait for your session to finish loading.');
  if (!auth.account) return null;
  const { data, error } = await client!.auth.getSession();
  if (error || !data.session || data.session.user.id !== auth.account.id) {
    throw new Error('Please sign in again to save your practice.');
  }
  return data.session.access_token;
});

export {
  feedbackToken,
  getDisplayName,
  saveDisplayName,
  getLearningStatistics,
  deleteAccount,
  NotFoundError,
  generateProblem,
  getLastSelection,
  getTopics,
  getCatalogue,
  getProblem,
  getProfileCounts,
  listProblems,
  listProblemPage,
  openProblem,
  openDemo,
  revealAnswer,
  revealSolution,
  reportProblem,
  shareProblem,
  practiceSharedProblem,
  practiceCodeProblem,
  stopSharing,
  submitAttempt,
} from './practice';
export { lookupShare, shareCode, shareLink } from './shares';
export { createWorksheet, downloadWorksheetPdf, fetchWorksheetPdf, DEFAULT_PAGE_OPTIONS, WORKSHEET_LIMITS } from './worksheets';
export { checkApiHealth } from './health';
export type { ApiHealth } from './health';
