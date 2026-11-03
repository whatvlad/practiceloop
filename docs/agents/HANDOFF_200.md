# HANDOFF — Probability and Statistics (#200), implementation checkpoint

Agent: Codex (existing shiro chat).
Accountable human: Vlad / whatvlad.
Issue / PR: #200 / draft #231.
Branch: `codex/issue-200-probability-statistics`.
Exact base: `b8130b8bf499e9d56a8c9a2e676fffa56eef562b`.
Planning head before this implementation: `ce4b1c4dd6c5f65e16bd178e82fe00b32c43f6cf`.
Current status: approved curriculum implemented; integration verification in
progress. Not Done. Exact published implementation head is recorded in the PR.

Owner decision: Vlad answered «Принимаю эту матрицу из 9 тем и уровней 1–5» to
the request linking the entire proposal at the planning head. Recorded in issue
comment 6604843016. Approval is complete; do not ask for it again.

Scope: all nine approved topics and 45 structural cells, implemented as 74 new
frozen versions (PSAA..PSCV), plus Distribution, moments/statistics blocks,
real scalar/boolean/finite-set/interval policies and actual input UI. The complete
matrix, conventions, bounds, exclusions and mathematical references are in
[PROBABILITY_STATISTICS.md](../architecture/PROBABILITY_STATISTICS.md).

Files changed: new blocks/answers/parser and generator providers/helpers/topic
matrix; safe optional input instructions across public codes/shares and saved
history; trusted-kind worker parsing; frontend fields/preview/area/curriculum;
one additive nine-topic migration, tests, fixtures, HTTP E2E and documentation.
Backend CI budget is 25 minutes for 239 versions; Database CI budget is 15
minutes for 563 collected DB tests and 124 HTTP flows;
production worker limits and frozen engine protocol signatures are unchanged.

Completed work:
- All 9,250 mathematical parameter tuples construct/render/parse/check their
  canonical answers. Every template has an independently hand-worked example.
- 222 goldens appended; all 165 baseline golden versions are unchanged.
  Nine public topics appended; all 36 baseline metadata rows/order are unchanged.
- Private catalogue rebuilt: 204 cells x64 verified codes.
- Boolean decisions cover both outcomes; real scalar/set/interval checks reject
  undefined and nonreal intermediate values before cancellation. Closed
  singleton intervals are valid; infinite endpoints must be open.
- API metadata is derived without symbolic construction. The new optional
  descriptor contains only input kind/limits, never expected values or records.
- HTTP E2E covers 124 topic/level/mixed scenarios plus deterministic new-kind
  flows, history, anonymous shares, recipient copies and mixed worksheets.

Observed verification:
- Foundation plus existing parser: 169 passed in 2.20 s before four added
  real-domain/singleton cases. Latest new-generator/foundation run:
  237 passed, 74 Linux-worker skips, 10.07 s.
- Matrix/goldens/seed sweeps/frozen curriculum: 2,021 passed, 74 Linux skips,
  136.75 s. Subsequent real-policy changes preserve rendered snapshots and are
  covered by the latest new-generator run.
- API/privacy/code opening checks: 750 passed, 239 Linux skips, 402 DB
  deselections, 6.91 s. New cases profile parent calls to ensure no SymPy work.
- Frontend full suite: 646 passed in 5.59 s; lint, typecheck and production build
  pass. Saved-kind/curriculum/history checks pass. Content policy: 95 templates,
  no critical violations. npm audit: zero vulnerabilities.
- Latest hardened probability/foundation run: 238 passed, 74 Linux skips,
  10.14 s, including empty event sets and all bounded mathematical values.
- Available full Windows backend suite: 4,818 passed, 602 Linux-only skips,
  636 DB/TeX/platform deselections, 229.52 s; the subsequent focused run above
  covers the final real-domain and event-set refinements.
- Strict KaTeX: 16,883 formulas pass, including all new formulas. Three frozen
  pre-#200 complex-argument statements contain Unicode text that warns in strict
  mode; all three pass the unchanged deployed renderer. No frozen data rewritten.
- Ruff check/format (189 files), mypy (126 app sources), repository file policy
  and original MVP hash pass. Python audit: no known vulnerabilities; all
  12 offline hosted-verification unit tests pass (2.051 s).

- Fresh catalogue/golden/API replay after the formula correction: 998 passed,
  1 Linux release-script skip, 204 seed-sweep deselections, 30.94 s.
- Final focused frontend controls/history/curriculum checks: 20 passed, including
  restored probability area after generation before catalogue loading. Lint,
  typecheck and production build pass.

Checks pending: complete ready-for-review Linux worker/PostgreSQL/E2E CI and
all deployments/live checks. No local Docker CLI; DB isolation runs hosted.
Browser inspection could not run: cua reports "Local browser use is disabled in
Work settings". That setting was not changed or bypassed. No visual or physical
mobile verification is claimed; actual React controls, fallback and API-decoder
flows are covered by the frontend tests. The isolated preview server was stopped.
TeX remains intentionally disabled under #181. Planning CI was green but is
not claimed as implementation acceptance.

Dependencies #189/#191/#192 are CLOSED. #200 is Order 1, In Progress; no competing
open PR observed. Ownership/base record is issue comment 6604588955. Graphify
CLI is absent; the scoped graph was stale (obsolete parser paths), so source
was verified directly. No fabricated graph or machine cache is committed.

Potential overlap: shared grammar, API projections, area types, frontend input,
topic catalogue and serial migration. Original checkout/other worktrees are
untouched. No additional agents or chats were started.

Recovery: implementation changes are in this isolated worktree (published as a
draft checkpoint next). Ignored .venv is Python 3.12.10 and imports this worktree;
frontend/node_modules is isolated. Private catalogue and .local logs/helpers
remain ignored. No secrets are needed or transferred.

Review status: advisory mathematical/database review requested from Feijhoaaaaa
on #231; no independent review claimed. Merge status: pending
full ready CI and resolved blocking findings.

Next concrete action: finish verification/fix failures, keep PR draft while
pushing fixes, mark ready, wait for all mandatory hosted jobs, merge expected
head, immediately close/Done/clear Order/renumber/read back, verify migrations
and both deploys/live codes, then publish the final English HANDOFF. Do not
start another queue issue.
