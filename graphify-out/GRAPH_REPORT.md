# Graph Report - PracticeLoop  (2026-10-19)

## Corpus Check
- 164 files · ~66,522 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: (none) 8, .toml 3, .css 3)

## Summary
- 1204 nodes · 2646 edges · 80 communities (42 shown, 38 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a40db1e5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- README.md
- package.json
- PracticeLoop — MVP Specification
- test_basic.py
- Must-have before production
- test_answer_check.py
- compilerOptions
- auth.test.ts
- main.py
- PracticePage.tsx
- server.ts
- test_supabase_hosted.py
- preview.py
- Prompt for Claude Code: implement the PracticeLoop frontend design
- pull_request_template.md
- system/README.md
- HANDOFF.md
- REVIEW_PROTOCOL.md
- test_auth.py
- main.tsx
- test_owned_records.py
- MathInputError
- setup-graphify.sh
- practiceloop-backend
- TASK_PROTOCOL.md
- PracticeLoop production roadmap
- 0001-frontend.md
- 0002-data-security.md
- basic.py
- vite-env.d.ts
- Problem generation intent
- Educational content style intent
- PracticeLoop agent rules
- Untracked generated practice (#34)
- ADR-003: bounded real-valued integration answers
- ADR-004: backend-owned practice records and distinct-problem counts
- PracticeLoop
- Google authentication
- release.sh
- PracticeLoop domain language
- answerSyntax.ts
- bootstrap.sh
- rollback.sh
- Oracle backend deploy
- FormulaField.tsx
- mathEditor.ts
- test_preview.py
- InternalProblem
- WORKFLOW.md
- answer_check.py
- ProblemCard.tsx
- Button.tsx
- types.ts
- DashboardPage.tsx
- HistoryRow.tsx
- typing
- [[path]].ts
- vitest

## God Nodes (most connected - your core abstractions)
1. `MathInputError` - 30 edges
2. `MathWorkerError` - 26 edges
3. `parse_math_input()` - 25 edges
4. `Reader` - 24 edges
5. `check_answer()` - 21 edges
6. `PracticeLoop — MVP Specification` - 19 edges
7. `replay_basic()` - 18 edges
8. `MathNode` - 18 edges
9. `react` - 18 edges
10. `vitest` - 18 edges

## Surprising Connections (you probably didn't know these)
- ``GET /api/problems/{id}`` --references--> `solution()`  [INFERRED]
  docs/api/README.md → backend/app/api/preview.py
- `API contract` --references--> `current_user()`  [INFERRED]
  docs/api/README.md → backend/app/core/auth.py
- `HTTP failures and retry behavior` --references--> `invalid_request()`  [INFERRED]
  docs/api/README.md → backend/app/main.py
- `How it decides` --references--> `classify()`  [INFERRED]
  docs/architecture/ANSWER_CHECK.md → backend/app/services/answer_check.py
- `Answer checking` --references--> `MathInputTooLong`  [INFERRED]
  docs/architecture/ANSWER_CHECK.md → backend/app/services/math_parser.py

## Import Cycles
- None detected.

## Communities (80 total, 38 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.16
Nodes (6): Changelog, Unreleased, Architecture and MVP analysis, Decision index, Open decisions — resolve before dependent features, Security policy

### Community 1 - "package.json"
Cohesion: 0.05
Nodes (39): dependencies, katex, mathlive, react, react-dom, @supabase/supabase-js, devDependencies, eslint (+31 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "test_basic.py"
Cohesion: 0.17
Nodes (15): generate_basic(), replay_basic(), SolutionStep, _verify(), test_candidate_with_incorrect_step_is_rejected(), test_complete_parameter_corpus(), test_higher_levels_retain_both_intended_rewrites(), test_missing_constant_or_inconsistent_final_answer_is_rejected() (+7 more)

### Community 4 - "Must-have before production"
Cohesion: 0.11
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "test_answer_check.py"
Cohesion: 0.05
Nodes (45): replay_problem(), AnswerCheck, _apply_limits(), _build_sympy(), check_answer(), _check_child(), _child(), MathCheckInconclusive (+37 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.13
Nodes (21): AuthCallback, AuthClient, AuthOptions, AuthSnapshot, createAuthStore(), accept(), signIn(), signOut() (+13 more)

### Community 8 - "main.py"
Cohesion: 0.05
Nodes (18): allowed_origins(), health(), invalid_request(), preview_boundary(), test_allowed_origins_reads_environment(), API contract, `GET /api/problems`, `GET /api/problems/{id}` (+10 more)

### Community 9 - "PracticePage.tsx"
Cohesion: 0.18
Nodes (18): authStore, client, API_BASE_URL, ApiHealth, checkApiHealth(), base, find(), getProblem() (+10 more)

### Community 10 - "server.ts"
Cohesion: 0.16
Nodes (24): balanced(), check(), isReadable(), normalise(), ACCEPTED, copy(), find(), generateProblem() (+16 more)

### Community 11 - "test_supabase_hosted.py"
Cohesion: 0.11
Nodes (14): check_private(), CheckFailure, Client, denied(), main(), NoRedirect, require(), rows() (+6 more)

### Community 12 - "preview.py"
Cohesion: 0.06
Nodes (18): answer(), attempt(), Attempt, generate(), Generate, _problem(), Session, _session() (+10 more)

### Community 13 - "Prompt for Claude Code: implement the PracticeLoop frontend design"
Cohesion: 0.29
Nodes (6): Definition of done, Goal, Prompt for Claude Code: implement the PracticeLoop frontend design, Rules, Source of truth, What to build

### Community 14 - "pull_request_template.md"
Cohesion: 0.40
Nodes (4): How it was tested, Risks, What changed, Why

### Community 15 - "system/README.md"
Cohesion: 0.33
Nodes (5): Content fundamentals, Directions, Iconography, Using the components, Visual foundations

### Community 18 - "test_auth.py"
Cohesion: 0.06
Nodes (34): _auth_unavailable(), AuthUnavailableError, current_user(), get_token_verifier(), _invalid_token(), token_verifier(), TokenVerifier, _user_from_claims() (+26 more)

### Community 20 - "test_owned_records.py"
Cohesion: 0.10
Nodes (26): AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), last_attempt(), list_problems(), PrivateSolution, ProblemRecord (+18 more)

### Community 25 - "MathInputError"
Cohesion: 0.13
Nodes (20): _constant_fraction(), MathInputError, MathInputTooLong, MathNode, _normalise(), _number_fraction(), parse_math_input(), _Parser (+12 more)

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 50 - "Problem generation intent"
Cohesion: 0.17
Nodes (11): Definite and indefinite integrals, Difficulty, Generation model, Mathematical boundaries, Out of scope for this decision, Outcome, Pedagogically clean values, Practice modes (+3 more)

### Community 51 - "Educational content style intent"
Cohesion: 0.18
Nodes (10): Content in scope, Content outside this policy, Development-time enforcement, Educational content style intent, Out of scope for this decision, Outcome, Success criteria, Template catalogue (+2 more)

### Community 52 - "PracticeLoop agent rules"
Cohesion: 0.22
Nodes (7): After a merge, Before starting work, Collaboration rules, GitHub Issue names, Graphify, PracticeLoop agent rules, Claude Code

### Community 53 - "Untracked generated practice (#34)"
Cohesion: 0.33
Nodes (6): Educational content, Mathematical checking and safety, Separate preview boundary, Supported generation, Untracked generated practice (#34), Verification and release

### Community 54 - "ADR-003: bounded real-valued integration answers"
Cohesion: 0.24
Nodes (6): Accepted input language, ADR-003: bounded real-valued integration answers, Consequences, Fixed parser and worker limits, Integration constants and domains, Topic and difficulty matrix

### Community 55 - "ADR-004: backend-owned practice records and distinct-problem counts"
Cohesion: 0.29
Nodes (6): ADR-004: backend-owned practice records and distinct-problem counts, Attempts and counters, Consequences, Private data and profile provisioning, Reveal semantics, Transaction and retry boundaries

### Community 56 - "PracticeLoop"
Cohesion: 0.29
Nodes (7): Collaboration, Local setup, PracticeLoop, Product direction, Run, Stack and structure, Verify

### Community 57 - "Google authentication"
Cohesion: 0.33
Nodes (5): Configuration, Google authentication, Practice remains a demo, Session behavior, Verification

### Community 58 - "release.sh"
Cohesion: 0.83
Nodes (3): activate(), healthy(), release.sh script

### Community 61 - "answerSyntax.ts"
Cohesion: 0.08
Nodes (38): absBig(), analyseAnswer(), AnswerAnalysis, constantFraction(), Fraction, FUNCTION_SET, gcd(), HINTS (+30 more)

### Community 64 - "Oracle backend deploy"
Cohesion: 0.22
Nodes (8): Before adding Supabase credentials (human only), Browser path, CORS, On the VM, One-time setup, Oracle backend deploy, Rollback and recovery, When the API is down

### Community 65 - "FormulaField.tsx"
Cohesion: 0.06
Nodes (33): AnswerInput(), insert(), move(), replace(), Harness(), render(), answerLatex(), byName() (+25 more)

### Community 66 - "mathEditor.ts"
Cohesion: 0.09
Nodes (29): FUNCTIONS, BARS, COMMAND_FUNCTIONS, exponentText(), INVERSE, Item, join(), latexToAnswer() (+21 more)

### Community 67 - "test_preview.py"
Cohesion: 0.21
Nodes (12): catalogue(), replay(), client(), headers(), test_check_failure_is_retryable_not_a_verdict(), fail(), test_entire_catalogue_has_valid_replay_domain_clean_values_and_answers(), test_generate_check_and_reveal_through_shared_worker() (+4 more)

### Community 72 - "answer_check.py"
Cohesion: 0.22
Nodes (8): check_tree(), classify(), _components(), _differs(), _is_primitive(), _not_real(), _same_number_everywhere(), _value()

### Community 73 - "ProblemCard.tsx"
Cohesion: 0.16
Nodes (17): AnswerInputProps, AnswerPreview(), ApiStatusNotice(), card(), DifficultyDots(), WarningIcon(), ProblemCard(), ResultBanner() (+9 more)

### Community 74 - "Button.tsx"
Cohesion: 0.13
Nodes (31): App(), handleLogOut(), handleSignIn(), APP_ROUTES, NotFoundPage(), TITLES, APP_ROUTES, AppNav() (+23 more)

### Community 75 - "types.ts"
Cohesion: 0.15
Nodes (19): DifficultyScaleProps, ProblemCardProps, ChipOption, ChipsProps, TOPIC_OPTIONS, TopicChipsProps, BANK, MockTemplate (+11 more)

### Community 76 - "DashboardPage.tsx"
Cohesion: 0.15
Nodes (25): DifficultyScale(), HistoryList(), StatTile(), StatTileProps, Chips(), TopicChips(), generateProblem(), getLastSelection() (+17 more)

### Community 78 - "HistoryRow.tsx"
Cohesion: 0.19
Nodes (16): AttemptStatus(), HistoryListProps, HistoryRow(), CheckIcon(), ChevronIcon(), CrossIcon(), DashIcon(), Icon() (+8 more)

### Community 81 - "[[path]].ts"
Cohesion: 0.36
Nodes (4): Context, onRequest(), FORWARDED_HEADERS, proxyToApi()

### Community 85 - "vitest"
Cohesion: 0.12
Nodes (10): harness, renderAt(), signedIn, signedOut, fetchMock, generate(), publicProblem, response() (+2 more)

## Knowledge Gaps
- **10 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `eslint` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 490 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Basic-integral generator` connect `InternalProblem` to `server.ts`, `ADR-003: bounded real-valued integration answers`?**
  _High betweenness centrality (0.337) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `MathInputError` (e.g. with `check_answer()` and `test_function_count_is_bounded()`) actually correct?**
  _`MathInputError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Why does `seed()` connect `server.ts` to `InternalProblem`?**
  _High betweenness centrality (0.318) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `MathWorkerError` (e.g. with `attempt()` and `test_adversarial_answers_terminate_within_limits()`) actually correct?**
  _`MathWorkerError` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Should `PracticeLoop — MVP Specification` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._
