# Graph Report - practiceloop-issue32  (2026-10-18)

## Corpus Check
- 103 files · ~27,177 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .css 3, .toml 2)

## Summary
- 455 nodes · 831 edges · 51 communities (17 shown, 34 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6a1ff403`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- README.md
- package.json
- PracticeLoop — MVP Specification
- generate_basic
- Must-have before production
- server.ts
- compilerOptions
- types.ts
- test_health.py
- App.tsx
- HistoryRow.tsx
- PracticeLoop
- checker.ts
- Prompt for Claude Code: implement the PracticeLoop frontend design
- pull_request_template.md
- system/README.md
- HANDOFF.md
- REVIEW_PROTOCOL.md
- STATUS.md
- setup-graphify.sh
- practiceloop-backend
- TASK_PROTOCOL.md
- PracticeLoop production roadmap
- 0001-frontend.md
- 0002-data-security.md
- supabase/README.md
- DashboardPage.tsx

## God Nodes (most connected - your core abstractions)
1. `PracticeLoop — MVP Specification` - 19 edges
2. `App()` - 17 edges
3. `Button()` - 16 edges
4. `DashboardPage()` - 16 edges
5. `ButtonLink()` - 14 edges
6. `navigate()` - 14 edges
7. `ProblemCard()` - 13 edges
8. `react` - 12 edges
9. `Tex()` - 12 edges
10. `generateProblem()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Unreleased` --references--> `main()`  [INFERRED]
  CHANGELOG.md → scripts/check_repository.py
- `Run` --references--> `main()`  [INFERRED]
  README.md → scripts/check_repository.py
- `card()` --calls--> `ProblemCard()`  [EXTRACTED]
  frontend/src/components/components.test.tsx → frontend/src/components/ProblemCard.tsx
- `HistoryPage()` --indirect_call--> `listProblems()`  [INFERRED]
  frontend/src/pages/HistoryPage.tsx → frontend/src/data/mock/server.ts
- `DashboardPage()` --indirect_call--> `getLastSelection()`  [INFERRED]
  frontend/src/pages/DashboardPage.tsx → frontend/src/data/mock/server.ts

## Import Cycles
- None detected.

## Communities (51 total, 34 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.04
Nodes (34): Before starting work, Collaboration rules, GitHub Issue names, Graphify, PracticeLoop agent rules, Claude Code, Completion criteria, Implementation workflow (+26 more)

### Community 1 - "package.json"
Cohesion: 0.05
Nodes (38): dependencies, katex, react, react-dom, devDependencies, eslint, @eslint/js, @types/katex (+30 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "generate_basic"
Cohesion: 0.18
Nodes (8): generate_basic(), InternalProblem, PublicProblem, test_all_fixture_parameters_have_correct_antiderivative(), test_deterministic(), test_invalid_parameters(), test_no_string_parameter_evaluation(), test_public_projection_never_contains_solution_or_parameters()

### Community 4 - "Must-have before production"
Cohesion: 0.11
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "server.ts"
Cohesion: 0.20
Nodes (25): HistoryListProps, ACCOUNT, copy(), find(), generateProblem(), getAccount(), getLastSelection(), getProblem() (+17 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "types.ts"
Cohesion: 0.16
Nodes (17): DifficultyScaleProps, ProblemCardProps, TopicChipsProps, BANK, MockTemplate, State, PUBLIC_KEYS, DIFFICULTIES (+9 more)

### Community 9 - "App.tsx"
Cohesion: 0.12
Nodes (34): App(), handleLogOut(), handleSignIn(), APP_ROUTES, NotFoundPage(), TITLES, APP_ROUTES, AppNav() (+26 more)

### Community 10 - "HistoryRow.tsx"
Cohesion: 0.13
Nodes (27): AnswerInput(), AnswerInputProps, DifficultyDots(), AttemptStatus(), HistoryRow(), CheckIcon(), ChevronIcon(), CrossIcon() (+19 more)

### Community 11 - "PracticeLoop"
Cohesion: 0.13
Nodes (10): Changelog, Unreleased, Collaboration, Local setup, PracticeLoop, Product direction, Run, Stack and structure (+2 more)

### Community 12 - "checker.ts"
Cohesion: 0.20
Nodes (7): balanced(), check(), isReadable(), normalise(), ACCEPTED, THEMES, vitest

### Community 13 - "Prompt for Claude Code: implement the PracticeLoop frontend design"
Cohesion: 0.29
Nodes (6): Definition of done, Goal, Prompt for Claude Code: implement the PracticeLoop frontend design, Rules, Source of truth, What to build

### Community 14 - "pull_request_template.md"
Cohesion: 0.40
Nodes (4): How it was tested, Risks, What changed, Why

### Community 15 - "system/README.md"
Cohesion: 0.33
Nodes (5): Content fundamentals, Directions, Iconography, Using the components, Visual foundations

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 50 - "DashboardPage.tsx"
Cohesion: 0.14
Nodes (21): card(), DifficultyScale(), HistoryList(), StatTile(), StatTileProps, ChipOption, Chips(), ChipsProps (+13 more)

## Knowledge Gaps
- **7 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `eslint` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 248 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `DashboardPage.tsx` to `package.json`, `HistoryRow.tsx`, `server.ts`, `App.tsx`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `DashboardPage()` (e.g. with `getLastSelection()` and `getProfileCounts()`) actually correct?**
  _`DashboardPage()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `README.md` be split into smaller, more focused modules?**
  _Cohesion score 0.043478260869565216 - nodes in this community are weakly interconnected._
- **Why does `vitest` connect `checker.ts` to `package.json`, `DashboardPage.tsx`, `HistoryRow.tsx`, `types.ts`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.0463768115942029 - nodes in this community are weakly interconnected._
- **Why does `PracticeLoop — MVP Specification` connect `PracticeLoop — MVP Specification` to `README.md`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._