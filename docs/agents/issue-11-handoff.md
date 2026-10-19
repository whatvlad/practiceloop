# Issue #11 coordination and handoff

Agent: Codex
Accountable human: Vlad (whatvlad), availability confirmed in chat
Issue / PR: #11 / pending
Branch: codex/issue-11-saved-practice
Base commit: cc74c4bec351c54dfbef7c316baeeae8012b2ae1
Original claim base: f0d3764e64c4c1fdad77f2f47776c9b5ac1091d7
Head commit (implementation): 3913d4553ec87a53742c4d4b3f63e544f8806a85
The unpublished implementation was rebased onto #73's isolated installer fix;
there was no file overlap. This handoff metadata follows the implementation.
Current status: implementation verified locally; project In Progress; hosted CI pending

Scope: Connect authenticated topic selection, generation, attempts and explicit
reveals to the saved-practice API. Preserve the guest preview data boundary.
Expected files: frontend data boundary/types, dashboard/practice/card state and
focused tests; README/API/status documentation and this handoff.
Explicit exclusions: #12 history/reopen/profile API reads, anonymous demo access
policy (#35), generators, schema, mathematical checking, authentication policy,
dependencies, design system and deployment configuration.
Dependencies: #5 and #10 closed; no open pull requests at claim time.
Potential overlap: #12 and #35 share the frontend data boundary. No other active
implementation was recorded on #11. No other agent branch will be edited.

Completed work: authenticated saved writes and API-driven availability; isolated
guest preview; idempotency/retry/rate-limit handling; safe cache projection;
stale-response guards; saved invalid/missing-constant and reveal state; docs.
Verification commands and exact results (Node 24.19.0, Python 3.14.5):
- `npm run lint`: equivalent direct ESLint invocation, exit 0, no warnings.
- `npm run typecheck`: equivalent direct TypeScript invocation, exit 0.
- `npm test`: equivalent direct Vitest invocation, 17 files / 277 tests passed.
- `npm run build`: direct TypeScript + Vite invocations passed; existing chunk
  size warning remains (KaTeX/MathLive). No dependencies or lockfile changes.
- `python scripts/check_content.py`: 20 templates passed, score >=80, no critical violations.
- `python -m ruff check backend scripts`: passed.
- `python -m ruff format --check backend scripts`: 41 files already formatted.
- `python -m unittest discover -s scripts -p 'test_supabase_*_unit.py'`: 12 passed
  outside sandbox; initial sandbox run blocked loopback connections (WinError 10013).
- `npm audit --audit-level=moderate`: 0 vulnerabilities.
- `python -m pip_audit --no-deps --disable-pip --timeout 10 --progress-spinner off -r backend/requirements.txt`: no known vulnerabilities.
- `python scripts/check_repository.py`: file policy and protected MVP hash passed.
- `git diff --check`: exit 0.
Checks not run successfully and why: Windows shared venv lacks jwt/psycopg and
Linux resource stubs; mypy reported 16 errors and pytest stopped on 5 import
collection errors. Docker Linux engine is not running, so local database,
Linux backend and Gitleaks container checks are unavailable. Hosted Linux CI
must pass before merge; local limitations are not reported as passing checks.
Open findings and risks: #12 read routes are not implemented; current browser
history/counters remain limited to this page session. Graphify executable is
unavailable at the documented Windows path; source inspection is used instead.
Uncommitted changes or recovery instructions: worktree under
D:/PracticeLoop/.worktrees/issue-11-practice; do not reset the original checkout.
Review status: no independent review requested yet.
Merge status: not merged.
Next concrete action: publish the focused PR, wait for hosted CI, merge and update the queue.
Message for the other agent: #11 owns the frontend practice/data integration on
the branch above; coordinate changes to those files before starting #12/#35.
