# Issue #35 coordination and handoff

Agent: Codex
Accountable human: Vlad (whatvlad), confirmed in chat
Issue / PR: #35 / pending
Branch: codex/issue-35-account-completion
Base commit: 9c66a1f73caac58f8f7e7614e3c2087021c6ed33
Head commit: pending
Status: In Progress; Implementation Queue Order 1

Scope: finish the approved account stage after #11/#12: one untracked anonymous
demo, private constant-omission statistics, optional removable display name,
learning timing, explicit self-service hard deletion and retention documentation.
Reverify existing Google login/session/logout, history and ownership boundaries.
Dependency #34 is closed; no open PRs at claim time. Human approved availability.
Expected overlap: auth, practice/profile UI and data boundary, backend account and
practice routes, additive migration, focused tests and documentation. No other
agent is started and no other branch/worktree is edited. The original checkout's
uncommitted graph outputs are preserved.
Exclusions: original MVP specification, advanced generators, sharing, public
launch, new providers, analytics vendors and unrelated design/dependency changes.

Verification: frontend 292 tests pass; lint, typecheck and production build pass.
Backend Ruff/format and strict Linux-targeted mypy (26 files) pass. Supported
Windows selection: 521 passed, 35 Linux skips, 72 deselected (before one additional
timeout regression). Offline Supabase scripts: 12 passed; repository policy and
original MVP hash pass. Scoped Graphify query/update succeeded; SQL extractor is
missing, so SQL is verified by hosted database tests. Graph/report reviewed and
manifest-only timestamps excluded. Local browser rendered the fixed demo,
explicit solution reveal and sign-in-for-more action; screenshot is in ignored
.local/issue-35-demo.png. No live owner data was changed. Hosted Linux CI and
disposable database tests are required; shared Supabase must never receive disposable CI fixtures.
Deletion live verification must use an explicitly disposable account, never the
owner's existing account. Confirm actual backup configuration before claiming
the 30-day retention requirement is verified.
Review: offer optional database/auth review on the concrete PR per AGENTS.md.
Merge: allowed after green hosted CI, followed by queue maintenance and deployment
verification. Do not report Done with unverified external acceptance criteria.
Next action: publish the concrete PR and obtain green hosted CI. Before merge,
verify populated-project backup/restore and <=30-day recovery-copy retention;
provision the missing server-only Auth admin key. Then deploy and verify deletion
with an explicitly disposable account. Until then #35 is In Progress, not Done.
