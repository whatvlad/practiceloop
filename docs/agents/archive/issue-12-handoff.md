# Issue #12 coordination and handoff

Agent: Codex
Accountable human: Vlad (whatvlad), availability confirmed in chat
Issue / PR: #12 / pending
Branch: codex/issue-12-history-profile
Base commit: 0e3fa0f878dda5b9299e0b6297c84e3543e6e30a
Head commit: pending
Current status: In Progress (project updated)

Scope: Paginated owner-scoped history, persisted reopen with latest attempt and
previously authorized reveals, ADR-004 profile counts, and connected frontend.
Expected files: backend owned_records/practice API and focused tests; frontend
practice data/types/history/dashboard/profile/practice and tests; API/README/status
documentation; reviewed Graphify outputs if update succeeds.
Explicit exclusions: migrations, auth policy, mathematical logic/generators,
account deletion/statistics in #35, dependencies/lockfiles and design-system changes.
Dependencies: #2/#5/#10 closed; #11 merged and deployed. No open PRs at claim time.
Potential overlap: #35 shares profile/history/auth boundaries. Coordinate before
editing those files; no other agent branch or original working tree is modified.

Completed work: owner-filtered GET history/reopen/profile; batched latest attempt
and count summaries; bounded validated cursors; 50+1 overfetch; read-only
repeatable-read history/reopen; single-snapshot ADR-004 counts. Frontend durable
reads, pagination/retry/empty/loading states and restored reveals. Focused tests
and docs; no migrations, dependencies or auth policy changes.
Verification commands and exact results:
- Node 24.19.0 direct equivalents of npm lint/typecheck/test/build passed;
  18 test files / 287 tests passed, existing bundle-size warning retained.
- `python -m mypy --platform linux`: no issues in 24 source files.
- Windows-supported pytest selection excluding the two Linux-worker preview
  test groups: 516 passed, 35 explicitly Linux-skipped, 70 deselected. The full
  Windows run had 16 expected Linux-worker preview failures (503 fail-closed);
  do not report that full run as passing. Hosted Linux CI must run everything.
- Ruff check passed; format check: 41 files already formatted.
- Content check: 20 templates, score >=80, no critical violations.
- 12 offline script tests passed outside sandbox for loopback access.
- Frontend audit: 0 vulnerabilities; backend pip_audit: no known vulnerabilities.
- Repository policy and protected MVP hash passed; diff whitespace check passed.
- Scoped Graphify query and `update .` succeeded via the root's installed
  launcher outside sandbox. Reviewed graph/report contain relative source paths;
  generated timestamp-only manifest changes excluded. SQL extractor is not
  installed, so SQL invariants are verified by database tests, not graph output.
Checks not run and why: hosted CI, disposable Postgres and live browser checks
await publication/deployment. Docker Desktop start was attempted, but the Linux
engine pipe remained unavailable; no fixtures were pointed at shared Supabase.
Open findings and risks: root checkout has unrelated uncommitted Graphify outputs;
they are preserved. Graphify's launcher needs execution outside the sandbox.
Uncommitted changes or recovery instructions: own worktree
D:/MathLoop/.worktrees/issue-12-history; preserve all other worktrees.
Review status: owner-scoped database queries will be highlighted for optional review.
Merge status: not merged.
Next concrete action: publish the PR, offer optional review of SQL changes,
complete hosted Linux/database CI, merge, renumber queue and verify deployment.
Message for the other agent: #12 owns backend history/profile reads and the
frontend practice data boundary on the branch above; coordinate overlapping work.
