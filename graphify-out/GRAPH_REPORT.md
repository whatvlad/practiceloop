# Graph Report - PracticeLoop  (2026-10-20)

## Corpus Check
- 190 files · ~87,220 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 7, .toml 3, .css 3)

## Summary
- 1517 nodes · 3700 edges · 110 communities (63 shown, 47 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 127 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `93b17517`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- README.md
- package.json
- PracticeLoop — MVP Specification
- generate_basic
- Must-have before production
- test_answer_check.py
- compilerOptions
- auth.test.ts
- Routes
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
- InternalProblem
- test_owned_records.py
- MathInputError
- setup-graphify.sh
- practiceloop-backend
- TASK_PROTOCOL.md
- PracticeLoop production roadmap
- 0001-frontend.md
- 0002-data-security.md
- test_basic.py
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
- practice.py
- test_practice_api.py
- MathWorkerError
- answer_check.py
- math_worker.py
- App.tsx
- types.ts
- DashboardPage.tsx
- test_supabase_hosted.py
- HistoryRow.tsx
- math_worker.py
- Parser
- supabase_google_test_login.py
- json
- test_health.py
- HistoryPage.tsx
- vitest
- PracticeLoop production readiness plan
- CallbackChecks
- BasicParameters
- check_repository.py
- CallbackChecks
- FormulaField.test.tsx
- database.py
- FamilyProblem
- check_repository.py
- ApiError
- ADR-003: bounded real-valued integration answers
- health.ts
- Saved practice UI (#11/#12)
- savedPracticeFlow.test.tsx
- learning_stats.py
- BasicParameters
- issue-11-handoff.md
- issue-12-handoff.md
- RateLimiter
- AnswerInput
- FamilyParameters
- WORKFLOW.md
- build

## God Nodes (most connected - your core abstractions)
1. `MathInputError` - 30 edges
2. `MathWorkerError` - 29 edges
3. `parse_math_input()` - 28 edges
4. `ApiError` - 26 edges
5. `Button()` - 25 edges
6. `check_answer()` - 24 edges
7. `react` - 24 edges
8. `Reader` - 24 edges
9. `generate()` - 23 edges
10. `attempt()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Delivery boundary` --references--> `replay_problem()`  [INFERRED]
  docs/architecture/TOPIC_GENERATORS.md → backend/app/services/answer_check.py
- `Project status` --references--> `current_user()`  [INFERRED]
  docs/agents/STATUS.md → backend/app/core/auth.py
- `API contract` --references--> `current_user()`  [INFERRED]
  docs/api/README.md → backend/app/core/auth.py
- `HTTP failures and retry behavior` --references--> `database_unavailable()`  [INFERRED]
  docs/api/README.md → backend/app/core/database.py
- `Basic-integral generator` --references--> `InternalProblem`  [INFERRED]
  docs/architecture/BASIC_GENERATOR.md → backend/app/generators/basic.py

## Import Cycles
- None detected.

## Communities (110 total, 47 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.15
Nodes (6): Changelog, Unreleased, Architecture and MVP analysis, Decision index, Open decisions — resolve before dependent features, Security policy

### Community 1 - "package.json"
Cohesion: 0.05
Nodes (39): dependencies, katex, mathlive, react, react-dom, @supabase/supabase-js, devDependencies, eslint (+31 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "generate_basic"
Cohesion: 0.15
Nodes (15): generate_basic(), replay_basic(), SolutionStep, _verify(), test_candidate_with_incorrect_step_is_rejected(), test_complete_parameter_corpus(), test_higher_levels_retain_both_intended_rewrites(), test_missing_constant_or_inconsistent_final_answer_is_rejected() (+7 more)

### Community 4 - "Must-have before production"
Cohesion: 0.11
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "test_answer_check.py"
Cohesion: 0.12
Nodes (26): replay_problem(), MathInputTooLong, check_answer(), MathCheckInconclusive, family(), _learner_text(), outcome(), record() (+18 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.13
Nodes (21): AuthCallback, AuthClient, AuthOptions, AuthSnapshot, createAuthStore(), accept(), signIn(), signOut() (+13 more)

### Community 8 - "Routes"
Cohesion: 0.05
Nodes (22): allowed_origins(), _error(), health(), internal_error(), invalid_request(), lifespan(), request_boundary(), test_allowed_origins_reads_environment() (+14 more)

### Community 9 - "PracticePage.tsx"
Cohesion: 0.13
Nodes (44): client, accessToken(), accountRequest(), authorize(), base, cache(), correctProblems, credentials() (+36 more)

### Community 10 - "server.ts"
Cohesion: 0.13
Nodes (15): build(), _families(), FamilyStep, generate_family(), replay_family(), verify_family(), build(), test_all_replay_fields_are_required() (+7 more)

### Community 11 - "test_supabase_hosted.py"
Cohesion: 0.14
Nodes (5): CheckFailure, DenialChecks, SingleUserChecks, SingleUserClient, StubClient

### Community 12 - "preview.py"
Cohesion: 0.19
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
Cohesion: 0.06
Nodes (34): _auth_unavailable(), AuthUnavailableError, current_user(), get_token_verifier(), _invalid_token(), token_verifier(), TokenVerifier, _user_from_claims() (+26 more)

### Community 20 - "test_owned_records.py"
Cohesion: 0.19
Nodes (9): _constant_fraction(), MathInputError, MathNode, _normalise(), _number_fraction(), _Parser, _Token, _tokenise() (+1 more)

### Community 25 - "MathInputError"
Cohesion: 0.17
Nodes (13): validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker(), test_limits_are_active_only_in_child(), test_memory_limit_stops_pathological_allocation() (+5 more)

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 33 - "test_basic.py"
Cohesion: 0.11
Nodes (45): close_pool(), AnswerCheck, attempt(), client(), generate(), key(), primitive_of(), rows() (+37 more)

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
Cohesion: 0.27
Nodes (5): Basic-integral generator, Delivery boundary, Integration topic generators, Mathematical and educational verification, Use and persistence boundary

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
Cohesion: 0.09
Nodes (33): absBig(), analyseAnswer(), AnswerAnalysis, Fraction, FUNCTION_SET, gcd(), HINTS, isDigit() (+25 more)

### Community 64 - "Oracle backend deploy"
Cohesion: 0.22
Nodes (8): Before adding Supabase credentials (human only), Browser path, CORS, On the VM, One-time setup, Oracle backend deploy, Rollback and recovery, When the API is down

### Community 65 - "FormulaField.tsx"
Cohesion: 0.13
Nodes (22): AnswerPreview(), answerLatex(), byName(), configureKeyboard(), FormulaField(), FormulaFieldProps, keycap(), loadMathLive() (+14 more)

### Community 66 - "mathEditor.ts"
Cohesion: 0.09
Nodes (29): FUNCTIONS, BARS, COMMAND_FUNCTIONS, exponentText(), INVERSE, Item, join(), latexToAnswer() (+21 more)

### Community 67 - "test_preview.py"
Cohesion: 0.14
Nodes (15): MathWorkerError, check_answer(), client(), headers(), test_check_failure_is_retryable_not_a_verdict(), fail(), test_entire_catalogue_has_valid_replay_domain_clean_values_and_answers(), test_generate_check_and_reveal_through_shared_worker() (+7 more)

### Community 68 - "InternalProblem"
Cohesion: 0.09
Nodes (31): attempt_summaries(), AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), insert_problem(), last_attempt(), list_problems() (+23 more)

### Community 69 - "practice.py"
Cohesion: 0.28
Nodes (12): attempt(), generate(), _respond(), claim(), _conflict(), lookup(), _replay(), request_hash() (+4 more)

### Community 70 - "test_practice_api.py"
Cohesion: 0.13
Nodes (27): AnswerInputProps, ApiStatusNotice(), DifficultyDots(), AttemptStatus(), HistoryRow(), CheckIcon(), ChevronIcon(), CrossIcon() (+19 more)

### Community 71 - "MathWorkerError"
Cohesion: 0.20
Nodes (7): BasicTemplate, _basic_records(), catalogue(), Exercise, _family_records(), replay(), test_existing_preview_versions_are_unchanged_and_new_cells_are_offered()

### Community 72 - "answer_check.py"
Cohesion: 0.23
Nodes (9): classify(), _components(), _defined_throughout(), _differs(), _domain(), _is_primitive(), _not_real(), _same_number_everywhere() (+1 more)

### Community 73 - "math_worker.py"
Cohesion: 0.11
Nodes (25): card(), DifficultyScale(), DifficultyScaleProps, ProblemCardProps, ChipOption, Chips(), ChipsProps, TOPIC_OPTIONS (+17 more)

### Community 74 - "App.tsx"
Cohesion: 0.12
Nodes (37): App(), handleDeleted(), handleLogOut(), handleSignIn(), APP_ROUTES, NotFoundPage(), TITLES, APP_ROUTES (+29 more)

### Community 75 - "types.ts"
Cohesion: 0.16
Nodes (13): AttemptBody, _check(), _decode_cursor(), delete_account(), DeleteBody, _encode_cursor(), GenerateBody, _idempotency_key() (+5 more)

### Community 76 - "DashboardPage.tsx"
Cohesion: 0.26
Nodes (11): StatTile(), StatTileProps, getDisplayName(), AccountSettings(), NameForm(), LearningStatistics(), rate(), ProfilePage() (+3 more)

### Community 77 - "test_supabase_hosted.py"
Cohesion: 0.24
Nodes (9): check_private(), Client, denied(), main(), NoRedirect, require(), rows(), verify() (+1 more)

### Community 78 - "HistoryRow.tsx"
Cohesion: 0.18
Nodes (11): history(), learning_statistics(), _not_found(), profile(), _public_problem(), reopen(), reveal_answer(), reveal_solution() (+3 more)

### Community 79 - "math_worker.py"
Cohesion: 0.16
Nodes (7): check_tree(), _apply_limits(), _build_sympy(), _check_child(), _child(), _run_worker(), test_educational_catalogue_and_checker()

### Community 80 - "Parser"
Cohesion: 0.32
Nodes (5): constantFraction(), numberFraction(), Parser, SyntaxProblem, validateExponent()

### Community 82 - "json"
Cohesion: 0.40
Nodes (5): Account completion (#35), Anonymous demo and privacy, Deployment and retention gates, Hard deletion and expired identity, Learning records and metrics

### Community 84 - "HistoryPage.tsx"
Cohesion: 0.23
Nodes (9): HistoryList(), HistoryListProps, StoredProblem, ProblemPage, PublicProblem, Filter, FILTERS, HistoryPage() (+1 more)

### Community 85 - "vitest"
Cohesion: 0.07
Nodes (16): Context, onRequest(), harness, renderAt(), signedIn, signedOut, BANK, PUBLIC_KEYS (+8 more)

### Community 86 - "PracticeLoop production readiness plan"
Cohesion: 0.18
Nodes (22): balanced(), check(), isReadable(), normalise(), ACCEPTED, copy(), find(), generateProblem() (+14 more)

### Community 88 - "CallbackChecks"
Cohesion: 0.35
Nodes (10): parse_math_input(), test_exact_boundaries_remain_accepted(), test_function_count_is_bounded(), test_group_nesting_is_bounded(), test_input_length_is_bounded_before_tokenisation(), test_node_count_is_bounded(), test_numeric_literal_length_is_bounded(), test_supported_notation() (+2 more)

### Community 89 - "BasicParameters"
Cohesion: 0.18
Nodes (3): FamilyTemplate, build(), PublicProblem

### Community 90 - "check_repository.py"
Cohesion: 0.25
Nodes (3): inspect(), main(), ContentTests

### Community 92 - "FormulaField.test.tsx"
Cohesion: 0.16
Nodes (5): changes, Fake, FakeMathfield, Harness(), render()

### Community 93 - "database.py"
Cohesion: 0.20
Nodes (3): database_unavailable(), DatabaseNotConfigured, get_pool()

### Community 96 - "ApiError"
Cohesion: 0.21
Nodes (6): ApiError, delete_user(), unavailable(), test_hard_delete_uses_server_key_and_no_redirects(), test_missing_deletion_config_never_contacts_auth(), test_uncertain_auth_failure_is_safe_and_closes_connection()

### Community 97 - "ADR-003: bounded real-valued integration answers"
Cohesion: 0.33
Nodes (6): Accepted input language, ADR-003: bounded real-valued integration answers, Consequences, Fixed parser and worker limits, Integration constants and domains, Topic and difficulty matrix

### Community 98 - "health.ts"
Cohesion: 0.40
Nodes (3): API_BASE_URL, ApiHealth, checkApiHealth()

### Community 99 - "Saved practice UI (#11/#12)"
Cohesion: 0.40
Nodes (5): Durable history and profile, Public/private boundary, Saved practice UI (#11/#12), Verification, Writes, retries and stale responses

### Community 100 - "savedPracticeFlow.test.tsx"
Cohesion: 0.15
Nodes (10): configurePracticeAuth(), fetchMock, generate(), publicProblem, response(), savedProblem(), storedProblem, calls (+2 more)

### Community 106 - "AnswerInput"
Cohesion: 0.23
Nodes (6): AnswerInput(), insert(), move(), replace(), Harness(), render()

## Knowledge Gaps
- **10 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `eslint` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 580 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **47 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Basic-integral generator` connect `ADR-003: bounded real-valued integration answers` to `InternalProblem`, `PracticeLoop production readiness plan`?**
  _High betweenness centrality (0.236) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `MathInputError` (e.g. with `check_answer()` and `test_function_count_is_bounded()`) actually correct?**
  _`MathInputError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Why does `seed()` connect `PracticeLoop production readiness plan` to `ADR-003: bounded real-valued integration answers`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `MathWorkerError` (e.g. with `_check()` and `attempt()`) actually correct?**
  _`MathWorkerError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Should `PracticeLoop — MVP Specification` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._