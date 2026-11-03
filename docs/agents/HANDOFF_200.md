# HANDOFF — Probability and Statistics (#200), design stage

Agent: Codex (existing shiro chat).
Accountable human: Vlad / whatvlad.
Issue: #200. Branch: `codex/issue-200-probability-statistics`.
Exact base: `b8130b8bf499e9d56a8c9a2e676fffa56eef562b`.
Head commit: see the planning PR's exact head.
Current status: claimed/In Progress; concrete curriculum and input/block design
prepared for the explicit owner-approval criterion. Not Done.

Scope: proposed nine topics, five structural levels each (45 cells), with the
Distribution block and actual boolean/finite-set/interval answer classes and UI.
The complete reviewable proposal is
[PROBABILITY_STATISTICS.md](../architecture/PROBABILITY_STATISTICS.md).

Files changed: this English handoff and the proposal only. Runtime, schema,
goldens, dependencies, lockfiles, original MVP and existing frozen output remain
unchanged. No implementation has started ahead of curriculum approval.

Completed: read all mandatory repository instructions; inspected issue body,
dependencies, project, open PRs and remote state. #200 is the lowest Order (1),
previously Todo/unclaimed, with no comments or competing PR. Vlad explicitly
instructed this chat to start it. Dependencies #189/#191/#192 are CLOSED. Project
status is now In Progress. Ownership/base/scope record is issue comment 6604588955.

Graphify: graph.json exists, but the worktree CLI is absent. A scoped read-only
JSON graph traversal used actual vocabulary answer/topic/parse/worker/input;
the graph points to obsolete parser locations. Current parser, frozen models,
worker, input component, topic declarations and API types were verified directly
in source. No graph output or machine-specific cache was fabricated/committed.

Verification commands and exact results: git status/remote/fetch/worktree checks
completed; base verified. Documentation diff and repository-policy checks are
recorded in the planning PR. No implementation tests are claimed for a proposal.

Checks not run: runtime, PostgreSQL and live tests await approved scope and code.
TeX remains intentionally disabled under #181. Hosted planning CI is distinct
from the required full ready-for-review CI after implementation.

Open decision: issue #200 explicitly says "Vlad agrees the topic list and levels
first" and requires approved topics/levels. General authorization to start does
not approve an unspecified curriculum. A concrete matrix and design have been
prepared before requesting this decision; do not implement its dependent code
until Vlad answers. Scope exclusions and inference/table conventions are included
in the proposal rather than silently assumed.

Potential overlap: shared answer grammar/API metadata/frontend input, areas and
catalogue, serial topic migration; no other open PR observed. Original checkout
and other worktrees are preserved. No new agents/chats were started.

Uncommitted/recovery: before publication these two documentation files only;
after publication use the planning branch/PR. No environment secrets are needed.
Review status: owner curriculum decision pending; advisory math/database review
will be requested on the implementation. Merge status: pending implementation
and full hosted CI; do not merge the planning draft as completion of #200.

Next concrete action: obtain the explicit topic/level decision, update this
proposal if requested, then implement the approved matrix and all verification
through merge/project/deployed checks. No message to another chat is required.
