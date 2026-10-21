# Graph Report - issue-109-shared-solving  (2026-10-21)

## Corpus Check
- 235 files · ~136,502 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: (none) 10, .toml 3, .css 3)

## Summary
- 2335 nodes · 6280 edges · 125 communities (82 shown, 43 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 240 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `83ec8564`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- README.md
- package.json
- PracticeLoop — MVP Specification
- basic.py
- Must-have before production
- math_worker.py
- compilerOptions
- auth.test.ts
- API contract
- practice.ts
- typing
- test_supabase_hosted.py
- preview.py
- Prompt for Claude Code: implement the PracticeLoop frontend design
- pull_request_template.md
- system/README.md
- HANDOFF.md
- REVIEW_PROTOCOL.md
- test_auth.py
- InternalProblem
- parse_math_input
- test_partial.py
- test_math_worker.py
- setup-graphify.sh
- practiceloop-backend
- TASK_PROTOCOL.md
- test-db.py
- PracticeLoop production roadmap
- 0001-frontend.md
- 0002-data-security.md
- test_practice_api.py
- vite-env.d.ts
- Problem generation intent
- Educational content style intent
- PracticeLoop agent rules
- Untracked generated practice (#34)
- Integration topic generators
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
- owned_records.py
- attempt
- sympy
- core.py
- answer_check.py
- types.ts
- ProblemCard.tsx
- test_definite.py
- DashboardPage.tsx
- App.tsx
- practice.py
- api/shares.py
- Parser
- test_triple.py
- Account completion (#35)
- issue-35-handoff.md
- e2e_local.py
- vitest
- server.ts
- test_double.py
- derivatives.py
- TopicChips.tsx
- test_derivatives.py
- FormulaField.test.tsx
- main.py
- test_health.py
- test_shares_api.py
- ApiError
- ADR-003: bounded real-valued integration answers
- auth.py
- PartialProblem
- test_mistakes.py
- learning_stats.py
- BasicParameters
- issue-11-handoff.md
- issue-12-handoff.md
- SharedProblemPage.tsx
- AnswerInput
- FamilyParameters
- test_reports_api.py
- site.ts
- StubClient
- time
- ADR-005: multiple integrals and derivatives
- main.tsx
- DefiniteParameters
- Changelog
- catalogue.py
- devDependencies
- answerSyntax.test.ts
- dependencies
- CallbackChecks
- scripts
- MultipleParameters
- audit.sh
- STATUS.md

## God Nodes (most connected - your core abstractions)
1. `parse_math_input()` - 58 edges
2. `check_answer()` - 41 edges
3. `replay_problem()` - 37 edges
4. `MathInputError` - 35 edges
5. `replay()` - 32 edges
6. `Button()` - 32 edges
7. `catalogue()` - 31 edges
8. `AnswerCheck` - 31 edges
9. `react` - 31 edges
10. `ApiError` - 30 edges

## Surprising Connections (you probably didn't know these)
- `Automated: `scripts/e2e_local.py`` --references--> `database_unavailable()`  [INFERRED]
  docs/production/MVP_E2E_CHECK.md → backend/app/core/database.py
- `Definite integrals` --references--> `catalogue()`  [INFERRED]
  docs/architecture/TOPIC_GENERATORS.md → backend/app/generators/core.py
- `Delivery boundary` --references--> `replay_problem()`  [INFERRED]
  docs/architecture/TOPIC_GENERATORS.md → backend/app/services/answer_check.py
- `Check budget` --references--> `test_family_check_fits_the_worker_limits()`  [INFERRED]
  docs/decisions/0005-multiple-integrals-and-derivatives.md → backend/tests/test_answer_check.py
- ``GET /api/problems/{id}`` --references--> `share()`  [INFERRED]
  docs/api/README.md → backend/tests/test_shares_api.py

## Import Cycles
- None detected.

## Communities (125 total, 43 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.08
Nodes (14): Completion criteria, Implementation workflow, Architecture and MVP analysis, Durable history and profile, Public/private boundary, Saved practice UI (#11/#12), Verification, Writes, retries and stale responses (+6 more)

### Community 1 - "package.json"
Cohesion: 0.13
Nodes (14): engines, node, name, private, type, version, eslint, @eslint/js (+6 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "basic.py"
Cohesion: 0.15
Nodes (15): generate_basic(), replay_basic(), SolutionStep, _verify(), test_candidate_with_incorrect_step_is_rejected(), test_complete_parameter_corpus(), test_higher_levels_retain_both_intended_rewrites(), test_missing_constant_or_inconsistent_final_answer_is_rejected() (+7 more)

### Community 4 - "Must-have before production"
Cohesion: 0.12
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "math_worker.py"
Cohesion: 0.07
Nodes (40): _check(), declared_variables(), MathInputTooLong, _normalise(), _apply_limits(), check_answer(), _check_child(), _child() (+32 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.13
Nodes (21): AuthCallback, AuthClient, AuthOptions, AuthSnapshot, createAuthStore(), accept(), signIn(), signOut() (+13 more)

### Community 8 - "API contract"
Cohesion: 0.07
Nodes (26): _error(), internal_error(), invalid_request(), request_boundary(), _secure(), API contract, `GET /api/problems`, `GET /api/problems/{id}` (+18 more)

### Community 9 - "practice.ts"
Cohesion: 0.12
Nodes (55): client, accessToken(), accountRequest(), authorize(), base, cache(), configurePracticeAuth(), correctProblems (+47 more)

### Community 10 - "typing"
Cohesion: 0.08
Nodes (18): build(), FamilyProblem, FamilyStep, FamilyTemplate, generate_family(), replay_family(), verify_family(), build() (+10 more)

### Community 11 - "test_supabase_hosted.py"
Cohesion: 0.19
Nodes (10): check_private(), CheckFailure, Client, denied(), main(), NoRedirect, require(), rows() (+2 more)

### Community 12 - "preview.py"
Cohesion: 0.18
Nodes (11): answer(), attempt(), Attempt, generate(), Generate, _problem(), Session, _session() (+3 more)

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
Cohesion: 0.17
Nodes (21): install_error_handlers(), assert_rejected(), bearer(), claims(), client(), FakeJwksClient, jwk(), jwks() (+13 more)

### Community 19 - "InternalProblem"
Cohesion: 0.29
Nodes (3): InternalProblem, PublicProblem, Basic-integral generator

### Community 20 - "parse_math_input"
Cohesion: 0.07
Nodes (42): ExpressionProblem, _constant_fraction(), MathInputError, MathNode, _number_fraction(), parse_math_input(), _Parser, _split_name() (+34 more)

### Community 21 - "test_partial.py"
Cohesion: 0.06
Nodes (37): _build(), Built, _chain_template(), build(), _d(), declared(), _domain(), _first() (+29 more)

### Community 25 - "test_math_worker.py"
Cohesion: 0.18
Nodes (13): validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker(), test_limits_are_active_only_in_child(), test_memory_limit_stops_pathological_allocation() (+5 more)

### Community 29 - "test-db.py"
Cohesion: 0.21
Nodes (7): test_educational_catalogue_and_checker(), main(), free_port(), main(), psql(), run(), wait_ready()

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 33 - "test_practice_api.py"
Cohesion: 0.08
Nodes (61): Topic, close_pool(), AnswerCheck, answer_of(), attempt(), client(), generate(), key() (+53 more)

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

### Community 54 - "Integration topic generators"
Cohesion: 0.21
Nodes (7): Bounded mathematical input, Definite integrals, Delivery boundary, Derivatives (`derivatives-v1`, #97), Integration topic generators, Mathematical and educational verification, Use and persistence boundary

### Community 55 - "ADR-004: backend-owned practice records and distinct-problem counts"
Cohesion: 0.29
Nodes (6): ADR-004: backend-owned practice records and distinct-problem counts, Attempts and counters, Consequences, Private data and profile provisioning, Reveal semantics, Transaction and retry boundaries

### Community 56 - "PracticeLoop"
Cohesion: 0.18
Nodes (11): Collaboration, Known limitations, License, Local setup, Merge gates, PracticeLoop, Product direction, Run (+3 more)

### Community 57 - "Google authentication"
Cohesion: 0.33
Nodes (5): Configuration, Google authentication, Practice data, Session behavior, Verification

### Community 58 - "release.sh"
Cohesion: 0.83
Nodes (3): activate(), healthy(), release.sh script

### Community 61 - "answerSyntax.ts"
Cohesion: 0.08
Nodes (36): analyseAnswer(), ANSWER_VARIABLES, AnswerAnalysis, Fraction, FUNCTION_SET, gcd(), hint(), HINTS (+28 more)

### Community 64 - "Oracle backend deploy"
Cohesion: 0.14
Nodes (13): Audit, Backups and restore, Before adding Supabase credentials (human only), Browser path, Capacity and worker isolation, CORS, Logs, On the VM (+5 more)

### Community 65 - "FormulaField.tsx"
Cohesion: 0.10
Nodes (34): AnswerVariable, AnswerInputProps, ADR-0005, answerLatex(), byName(), configureKeyboard(), FormulaField(), FormulaFieldProps (+26 more)

### Community 66 - "mathEditor.ts"
Cohesion: 0.09
Nodes (30): FUNCTIONS, BARS, COMMAND_FUNCTIONS, CONSTANTS, exponentText(), INVERSE, Item, join() (+22 more)

### Community 67 - "test_preview.py"
Cohesion: 0.26
Nodes (9): client(), headers(), test_check_failure_is_retryable_not_a_verdict(), fail(), test_generate_check_and_reveal_through_shared_worker(), test_one_fixed_demo_requires_login_for_more_and_never_saves_outcomes(), test_request_bounds_expiry_rate_and_unsupported_cells(), test_reveal_is_scoped_and_check_does_not_leak() (+1 more)

### Community 68 - "owned_records.py"
Cohesion: 0.09
Nodes (31): attempt_summaries(), AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), insert_problem(), last_attempt(), list_problems() (+23 more)

### Community 69 - "attempt"
Cohesion: 0.19
Nodes (16): attempt(), generate(), _idempotency_key(), _respond(), practice_shared(), PracticeShareBody, database_unavailable(), claim() (+8 more)

### Community 70 - "sympy"
Cohesion: 0.09
Nodes (28): value_latex(), _cartesian(), _disk(), DoubleProblem, DoubleTemplate, DoubleVariant, _polar(), _same_region() (+20 more)

### Community 71 - "core.py"
Cohesion: 0.11
Nodes (16): BasicTemplate, _basic_records(), catalogue(), _definite_records(), Exercise, _family_records(), replay(), _base() (+8 more)

### Community 72 - "answer_check.py"
Cohesion: 0.09
Nodes (21): DefiniteProblem, ValueProblem, _base_record(), classify(), _classify_definite(), _classify_derivative(), _classify_expression(), _components() (+13 more)

### Community 73 - "types.ts"
Cohesion: 0.07
Nodes (41): Launch blockers (#39), Production checklist (#38), Running the checks, card(), DifficultyScaleProps, LABELS, ReportProblem(), submit() (+33 more)

### Community 74 - "ProblemCard.tsx"
Cohesion: 0.09
Nodes (50): route(), NotFoundPage(), APP_ROUTES, AppNav(), AppNavProps, Logo(), PublicNav(), Button() (+42 more)

### Community 75 - "test_definite.py"
Cohesion: 0.16
Nodes (16): base_record(), DefiniteStep, replay_definite(), verify_definite(), record(), source(), test_base_records_are_complete_basic_or_family_records(), test_bounds_never_touch_a_singularity() (+8 more)

### Community 76 - "DashboardPage.tsx"
Cohesion: 0.12
Nodes (21): DifficultyScale(), StatTile(), StatTileProps, getDisplayName(), mixedShares(), AccountSettings(), NameForm(), DashboardPage() (+13 more)

### Community 77 - "App.tsx"
Cohesion: 0.09
Nodes (32): App(), handleDeleted(), handleLogOut(), handleSignIn(), APP_ROUTES, SITE, harness, renderAt() (+24 more)

### Community 78 - "practice.py"
Cohesion: 0.09
Nodes (26): area_topics(), AttemptBody, _decode_cursor(), delete_account(), DeleteBody, _encode_cursor(), _feedback(), GenerateBody (+18 more)

### Community 79 - "api/shares.py"
Cohesion: 0.08
Nodes (23): by_code(), by_token(), create(), _invalid_share(), revoke(), _shared(), active_share(), copy_for_practice() (+15 more)

### Community 80 - "Parser"
Cohesion: 0.30
Nodes (6): absBig(), constantFraction(), numberFraction(), Parser, SyntaxProblem, validateExponent()

### Community 81 - "test_triple.py"
Cohesion: 0.09
Nodes (30): is_clean_value(), _box(), _cartesian(), _lookup(), _over_disk(), records(), replay_triple(), replay_value() (+22 more)

### Community 82 - "Account completion (#35)"
Cohesion: 0.40
Nodes (5): Account completion (#35), Anonymous demo and privacy, Deployment and retention gates, Hard deletion and expired identity, Learning records and metrics

### Community 84 - "e2e_local.py"
Cohesion: 0.14
Nodes (18): check(), correct_answer(), cross_user(), database_failure(), derivatives(), full_flow(), key(), LocalKeys (+10 more)

### Community 85 - "vitest"
Cohesion: 0.12
Nodes (10): fetchMock, generate(), publicProblem, response(), savedProblem(), storedProblem, renderMath(), THEMES (+2 more)

### Community 86 - "server.ts"
Cohesion: 0.09
Nodes (32): Context, onRequest(), BANK, MockTemplate, balanced(), check(), isReadable(), normalise() (+24 more)

### Community 88 - "test_double.py"
Cohesion: 0.13
Nodes (18): _lookup(), replay_double(), replay_value(), check_and_diagnose(), check_tree(), replay_problem(), _build_sympy(), test_unknown_record_version_is_rejected() (+10 more)

### Community 89 - "derivatives.py"
Cohesion: 0.09
Nodes (9): _chain(), _components(), _d(), DerivativeParameters, DerivativeTemplate, _rewrite(), _step(), _StepPrinter (+1 more)

### Community 90 - "TopicChips.tsx"
Cohesion: 0.12
Nodes (20): HistoryList(), HistoryListProps, AreaChips(), AreaChipsProps, ChipOption, Chips(), ChipsProps, TopicChips() (+12 more)

### Community 91 - "test_derivatives.py"
Cohesion: 0.13
Nodes (22): DerivativeStep, generate_derivative(), records(), replay_derivative(), verify_derivative(), learner(), _mistake_cases(), outcome() (+14 more)

### Community 92 - "FormulaField.test.tsx"
Cohesion: 0.15
Nodes (6): changes, Fake, FakeMathfield, Harness(), Layout, render()

### Community 93 - "main.py"
Cohesion: 0.06
Nodes (7): report(), ReportBody, DatabaseNotConfigured, get_pool(), _api_error_response(), health(), lifespan()

### Community 94 - "test_health.py"
Cohesion: 0.16
Nodes (5): allowed_origins(), _known_origin(), test_allowed_origins_reads_environment(), test_allowed_origins_refuse_plain_http_outside_local_dev(), test_api_responses_carry_security_headers()

### Community 95 - "test_shares_api.py"
Cohesion: 0.23
Nodes (25): assert_unavailable(), client(), execute(), generate(), share(), start_copy(), test_concurrent_copy_retries_create_once_and_replay_after_revocation(), test_copy_does_not_inherit_sender_attempts_or_reveals() (+17 more)

### Community 96 - "ApiError"
Cohesion: 0.14
Nodes (8): RateLimiter, _worker_unavailable(), ApiError, delete_user(), unavailable(), test_hard_delete_uses_server_key_and_no_redirects(), test_missing_deletion_config_never_contacts_auth(), test_uncertain_auth_failure_is_safe_and_closes_connection()

### Community 97 - "ADR-003: bounded real-valued integration answers"
Cohesion: 0.33
Nodes (6): Accepted input language, ADR-003: bounded real-valued integration answers, Consequences, Fixed parser and worker limits, Integration constants and domains, Topic and difficulty matrix

### Community 98 - "auth.py"
Cohesion: 0.10
Nodes (12): _auth_unavailable(), AuthUnavailableError, current_user(), get_token_verifier(), _invalid_token(), token_verifier(), TokenVerifier, _user_from_claims() (+4 more)

### Community 99 - "PartialProblem"
Cohesion: 0.13
Nodes (10): DerivativeProblem, PartialProblem, _derivative_mistakes(), diagnose(), classify(), _declared(), diagnose(), _differs() (+2 more)

### Community 100 - "test_mistakes.py"
Cohesion: 0.13
Nodes (11): _basic(), declared(), _without_absolute(), _indefinite_cases(), learner(), outcome(), test_correct_missing_constant_and_invalid_answers_get_no_diagnosis(), test_diagnosis_fits_the_worker_limits() (+3 more)

### Community 105 - "SharedProblemPage.tsx"
Cohesion: 0.14
Nodes (21): expiryDate(), ShareControls(), copy(), APP_BASE, base, CONFUSABLE, lookupShare(), normalizeCode() (+13 more)

### Community 106 - "AnswerInput"
Cohesion: 0.19
Nodes (7): AnswerInput(), insert(), move(), replace(), AnswerPreview(), Harness(), render()

### Community 108 - "test_reports_api.py"
Cohesion: 0.18
Nodes (11): client(), generate(), stored(), test_invalid_reports_are_refused_without_echoing_them(), test_nobody_reports_someone_elses_or_a_missing_problem(), test_owner_reports_a_problem_with_only_the_approved_fields(), test_reports_are_rate_limited_per_user(), test_reports_go_with_the_account() (+3 more)

### Community 109 - "site.ts"
Cohesion: 0.14
Nodes (15): applyPageMeta(), crawlerFiles(), isSharedPath(), NOT_FOUND, pageMeta, PAGES, PUBLIC_PATHS, setCanonical() (+7 more)

### Community 110 - "StubClient"
Cohesion: 0.18
Nodes (4): DenialChecks, SingleUserChecks, SingleUserClient, StubClient

### Community 112 - "ADR-005: multiple integrals and derivatives"
Cohesion: 0.14
Nodes (14): ADR-005: multiple integrals and derivatives, Answers and variables, Areas and topics, Check budget, Consequences, Coordinate systems, Delivery, Derivatives (`derivatives-v1`) (+6 more)

### Community 113 - "main.tsx"
Cohesion: 0.15
Nodes (8): analyticsAllowed(), BEACON_SRC, startWebAnalytics(), ErrorBoundary, root, @fontsource/geist, @fontsource/geist-mono, @fontsource/instrument-serif

### Community 115 - "Changelog"
Cohesion: 0.40
Nodes (4): 0.1.0 — MVP (2026-10-20), Changelog, Changes during MVP development, Unreleased

### Community 116 - "catalogue.py"
Cohesion: 0.27
Nodes (3): inspect(), main(), ContentTests

### Community 117 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, @eslint/js, jsdom, @types/katex, @types/react, @types/react-dom, typescript (+3 more)

### Community 118 - "answerSyntax.test.ts"
Cohesion: 0.20
Nodes (9): CYLINDRICAL, POLAR, REJECTED, SUPPORTED, ADR-0005, VARIABLE_REJECTED, VARIABLE_SUPPORTED, XY (+1 more)

### Community 119 - "dependencies"
Cohesion: 0.22
Nodes (9): dependencies, @fontsource/geist, @fontsource/geist-mono, @fontsource/instrument-serif, katex, mathlive, react, react-dom (+1 more)

### Community 121 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, lint:content, test, typecheck

## Knowledge Gaps
- **19 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `eslint` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 834 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Declared answer variables (ADR-005, Issue #96)` connect `math_worker.py` to `AnswerInput`, `parse_math_input`, `test_partial.py`, `Integration topic generators`?**
  _High betweenness centrality (0.294) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `check_answer()` (e.g. with `MathInputError` and `MathInputTooLong`) actually correct?**
  _`check_answer()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _19 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `README.md` be split into smaller, more focused modules?**
  _Cohesion score 0.08465608465608465 - nodes in this community are weakly interconnected._
- **Why does `AnswerInput()` connect `AnswerInput` to `FormulaField.tsx`, `math_worker.py`, `ProblemCard.tsx`, `FormulaField.test.tsx`, `answerSyntax.ts`?**
  _High betweenness centrality (0.294) - this node is a cross-community bridge._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Why does `MathWorkerError` connect `math_worker.py` to `test_practice_api.py`, `test_preview.py`, `preview.py`, `practice.py`, `test_math_worker.py`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._