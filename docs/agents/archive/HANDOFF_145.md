# HANDOFF — Analysis I (#145)

Agent: Codex (existing shiro chat, explicitly authorized by Vlad).
Accountable human: Vlad / whatvlad.
Issue: #145. Branch: `codex/issue-145-analysis-i`.
Exact base commit: `50fb658ad4d8650774bb042436b9dafb876139e0`.
Head commit: see the linked PR's immutable head and CI runs.
Final status: **Done**, merged and deployed on 2026-11-03. The following sections
preserve the implementation-stage checkpoints. Final authoritative HANDOFF:
[issue #145 completion comment](https://github.com/whatvlad/practiceloop/issues/145#issuecomment-6602711263).
Merge: `bca9bee50150ad47f2a4d67cca43f8267d1cd54d`; verified head:
`6fe5ec2587be4545175a799f85bb0e010c98eb27`. Ready CI 41626017264 passed 3,392 backend,
368 DB, 612 frontend and all expanded E2E checks. All deploys and 33 live public
code openings passed; project Done, Order cleared and remaining queue verified.

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
The catalogue was rebuilt; its full replay regression passed in 19.76 seconds. Linux
worker behavior must be judged by hosted Linux CI, not by Windows failures.

Hosted first ready run: migrations applied successfully; SQL isolation stopped
on an old 35-topic count. Updated it to 36 (17 in Mathematical Analysis) and
added an explicit assertion for the new topic's area. No production schema fix
was needed. A fresh ready run must pass after this fixture correction.

Final scope check changed the unshipped bisection equation from exp(x)+x=a+1
(expressible through Lambert W) to exp(x)+x²=a+1, for which the bounded symbolic
solver has no supported closed form. Its monotonicity proof, rational sign
certificates and error bound remain explicit; only the new bisection golden
samples change. Focused final tests: 41 passed, 33 Linux-only skips, 1.86 seconds.

Second hosted run: Database isolation and expanded HTTP E2E passed. An additional
adversarial check found that generic expression simplification could hide domain
holes in the four new all-real function answers. Added a local specialization of
the existing expression kind, reusing check_domain before cancellation. Existing
answer classes and frozen generator outputs are unchanged. Regression tests cover
0/(x-2), 0*ln(x), and x/x-1 in all four templates, including limited-worker checks.
Scalar templates likewise reject undeclared symbols before cancellation, retaining
pi/e and exact arithmetic. Final focused tests: 46 passed, 33 Linux-only skips,
2.02 seconds. Ruff check/format and mypy (105 sources) pass. Private rendered
outputs and all existing golden entries remain unchanged by these policies.

Both first ready backend runs hit the same existing rational-antiderivative
worker limit (RNI seed 39, combined log|x²+x|); second run otherwise passed
3,385 backend tests, all Database isolation tests and all expanded HTTP E2E.
The blocking case is resolved by a shared exact QQ-rational/log-absolute
certificate used by replay's displayed-step proofs and answer checking. Domain
coverage is still certified exactly; unsupported cases retain the general proof.
After the derivative identity is proved, component constants are compared at
exact interior points before simplifying. Limits remain 2 s CPU/256 MiB/3 s wall.
Cold local runs with five hash seeds improved from 0.891–0.906 to 0.656–0.672 CPU
seconds. Regression run: 1,149 passed, 90 Linux-only skips in 24.99 seconds,
including answer policies and the frozen integral curriculum. Ruff and mypy
(106 sources) pass. Final Linux ready CI is required for this actual fix.

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
