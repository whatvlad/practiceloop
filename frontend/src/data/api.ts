// The one data boundary for pages. Today every call goes to the temporary
// mock in ./mock; swap these exports for authenticated FastAPI calls
// (docs/api/README.md) without changing any page or component.

export {
  NotFoundError,
  generateProblem,
  getAccount,
  getLastSelection,
  getProblem,
  getProfileCounts,
  listProblems,
  revealAnswer,
  revealSolution,
  signIn,
  signOut,
  submitAttempt,
} from './mock/server';
