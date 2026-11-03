# HANDOFF — Analysis I (#145)

Agent: Codex (existing shiro chat, explicitly authorized by Vlad).
Accountable human: Vlad / whatvlad.
Issue: #145. Branch: `codex/issue-145-analysis-i`.
Exact base commit: `50fb658ad4d8650774bb042436b9dafb876139e0`.
Head commit: see the linked PR's immutable head and CI runs.
Current status: implementation complete; verification in progress; not Done.

Scope: all Analysis I criteria, as mapped in
[ANALYSIS_I.md](../architecture/ANALYSIS_I.md). 33 new frozen generators, 99 new
golden samples, three structural topic matrices (two expanded, one added).
Existing integrals and derivatives are reused. Historical sequence/limit codes
remain openable. No frozen interface, shipped golden output, MVP, dependency,
lockfile or existing database record is changed.

Files changed: mathematical block and generator module, declarative topic and
historical opening views; additive differential-calculus topic migration;
regression/API/E2E tests; curriculum UI and general expression instructions;
README/status/curriculum documentation and this handoff.

Verification observed before the first draft:

- `pytest backend/tests/test_engine_analysis_one.py`: 40 passed, 33 skipped
  (Linux-only limited-worker tests), 1.93 seconds on Python 3.12.10 / Windows.
- `python -m app.engine.catalogue`: 159 cells x 64 codes verified.
- KaTeX strict rendering: all 4,516 new catalogue statements/answers/steps pass.
- Old golden JSON compared semantically: all 85 existing versions unchanged.
- Frontend: 612 tests pass; lint, typecheck and production build pass.
- Ruff check and format: pass, 163 Python files; mypy Linux target: 104 sources pass.
- Repository policy/original MVP hash and content check (95 entries): pass.
- API health tests: 11 pass on the real TestClient.

Additional local results: the mathematical/golden/curriculum/topic selection run
passed 1,282 tests (33 Linux-only skips), in 102.79 seconds. The full Windows run
passed 3,559 tests, with 360 skips and 418 DB/TeX deselections, in 185.38 seconds.
It reported 15 failures: 14 call Linux-only workers without platform markers;
one compared against the local catalogue built before final step-text changes.
The catalogue was rebuilt; its replay regression is rerun separately. Linux
worker behavior must be judged by hosted Linux CI, not by Windows failures.

Checks pending: hosted ready CI including
real Linux worker limits and disposable PostgreSQL/HTTP E2E; deployed checks.
TeX CI remains disabled under #181. Graphify graph exists but the optional CLI is
unavailable in this worktree; no fabricated graph update or runtime dependency.

Open findings: none yet; self-review is not independent review. Bisection uses
rational Taylor sign certificates and a specified six-step midpoint, not a vague
numeric tolerance. Classification exercises state numeric codes explicitly;
endpoint questions display full intervals in the solution.

Dependencies: #144/#147/#172/#189/#191/#192 and #221 verified CLOSED. No open PR
or competing issue claim observed when work started. Project #145 In Progress,
Order 1; stale Order on closed #147 cleared; active queue read back as 1–6.

Potential overlap: shared topic catalogue and curriculum files; no other agent
started. Original checkout and existing worktrees/branches preserved.
Local-only recovery: ignored Python environments, node_modules, rendered private
catalogue and .local logs/scripts. Nothing private is shipped to the browser.

Review: request advisory mathematical review on the ready PR.
Merge: pending green ready-for-review CI. Do not implement #146 before #145 is
merged, project maintenance is verified and deployments pass.

Next action: complete verification, resolve real failures, mark PR ready, inspect
hosted checks/reviews, merge, close issue, Done/clear Order/renumber/read back,
verify live deployment and update this record. Then claim #146 from new main.
Message for the other agent: use merged main after completion; no automatic chat
synchronization is claimed.
