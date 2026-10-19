# Graph Report - issue-35-account  (2026-10-19)

## Corpus Check
- 183 files · ~82,192 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: (none) 8, .toml 3, .css 3)

## Summary
- 1446 nodes · 3497 edges · 101 communities (57 shown, 44 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 127 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9c66a1f7`
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
- practice.ts
- auth.py
- test_supabase_hosted.py
- preview.py
- Prompt for Claude Code: implement the PracticeLoop frontend design
- pull_request_template.md
- system/README.md
- HANDOFF.md
- REVIEW_PROTOCOL.md
- test_auth.py
- InternalProblem
- MathInputError
- MathWorkerError
- setup-graphify.sh
- practiceloop-backend
- TASK_PROTOCOL.md
- PracticeLoop production roadmap
- 0001-frontend.md
- 0002-data-security.md
- test_practice_api.py
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
- owned_records.py
- practice.py
- WORKFLOW.md
- typing
- answer_check.py
- types.ts
- App.tsx
- supabase_google_test_login.py
- DashboardPage.tsx
- HistoryPage.tsx
- StubClient
- math_worker.py
- BasicParameters
- [[path]].ts
- Account completion (#35)
- issue-35-handoff.md
- vitest
- tokens.test.ts
- MathCheckInconclusive
- parse_math_input
- Routes
- check_content.py
- test_health.py
- test_supabase_hosted_unit.py
- math_parser.py
- CallbackChecks
- check_repository.py
- ApiError
- health.ts
- Saved practice UI (#11/#12)
- issue-11-handoff.md
- issue-12-handoff.md

## God Nodes (most connected - your core abstractions)
1. `MathInputError` - 30 edges
2. `MathWorkerError` - 29 edges
3. `ApiError` - 26 edges
4. `parse_math_input()` - 25 edges
5. `Button()` - 25 edges
6. `react` - 24 edges
7. `Reader` - 24 edges
8. `check_answer()` - 23 edges
9. `attempt()` - 22 edges
10. `generate()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Project status` --references--> `current_user()`  [INFERRED]
  docs/agents/STATUS.md → backend/app/core/auth.py
- `API contract` --references--> `current_user()`  [INFERRED]
  docs/api/README.md → backend/app/core/auth.py
- `HTTP failures and retry behavior` --references--> `database_unavailable()`  [INFERRED]
  docs/api/README.md → backend/app/core/database.py
- `HTTP failures and retry behavior` --references--> `invalid_request()`  [INFERRED]
  docs/api/README.md → backend/app/main.py
- `Cost and limits` --references--> `replay_problem()`  [INFERRED]
  docs/architecture/ANSWER_CHECK.md → backend/app/services/answer_check.py

## Import Cycles
- None detected.

## Communities (101 total, 44 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.15
Nodes (6): Changelog, Unreleased, Architecture and MVP analysis, Decision index, Open decisions — resolve before dependent features, Security policy

### Community 1 - "package.json"
Cohesion: 0.05
Nodes (39): dependencies, katex, mathlive, react, react-dom, @supabase/supabase-js, devDependencies, eslint (+31 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "test_basic.py"
Cohesion: 0.18
Nodes (13): generate_basic(), replay_basic(), test_candidate_with_incorrect_step_is_rejected(), test_complete_parameter_corpus(), test_higher_levels_retain_both_intended_rewrites(), test_missing_constant_or_inconsistent_final_answer_is_rejected(), test_numeric_coefficients_stay_pedagogically_small(), test_rejects_bad_records_before_symbolic_construction() (+5 more)

### Community 4 - "Must-have before production"
Cohesion: 0.11
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "test_answer_check.py"
Cohesion: 0.13
Nodes (18): MathInputTooLong, check_answer(), _learner_text(), outcome(), record(), test_adversarial_answers_terminate_within_limits(), test_check_answer_end_to_end(), test_classification() (+10 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.13
Nodes (21): AuthCallback, AuthClient, AuthOptions, AuthSnapshot, createAuthStore(), accept(), signIn(), signOut() (+13 more)

### Community 8 - "main.py"
Cohesion: 0.11
Nodes (6): _error(), health(), internal_error(), invalid_request(), lifespan(), request_boundary()

### Community 9 - "practice.ts"
Cohesion: 0.12
Nodes (44): authStore, client, accessToken(), accountRequest(), authorize(), base, cache(), correctProblems (+36 more)

### Community 10 - "auth.py"
Cohesion: 0.09
Nodes (12): _auth_unavailable(), AuthUnavailableError, current_user(), get_token_verifier(), _invalid_token(), token_verifier(), TokenVerifier, _user_from_claims() (+4 more)

### Community 11 - "test_supabase_hosted.py"
Cohesion: 0.23
Nodes (9): check_private(), Client, denied(), main(), NoRedirect, require(), rows(), verify() (+1 more)

### Community 12 - "preview.py"
Cohesion: 0.23
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
Cohesion: 0.18
Nodes (20): assert_rejected(), bearer(), claims(), client(), FakeJwksClient, jwk(), jwks(), make_client() (+12 more)

### Community 19 - "InternalProblem"
Cohesion: 0.26
Nodes (4): InternalProblem, SolutionStep, _verify(), Basic-integral generator

### Community 20 - "MathInputError"
Cohesion: 0.28
Nodes (6): _constant_fraction(), MathInputError, MathNode, _number_fraction(), _Parser, Bounded mathematical input

### Community 25 - "MathWorkerError"
Cohesion: 0.18
Nodes (14): MathWorkerError, validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker(), test_limits_are_active_only_in_child() (+6 more)

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 33 - "test_practice_api.py"
Cohesion: 0.11
Nodes (44): close_pool(), AnswerCheck, attempt(), client(), generate(), key(), primitive_of(), rows() (+36 more)

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
Nodes (32): AnswerInput(), insert(), move(), replace(), Harness(), render(), answerLatex(), byName() (+24 more)

### Community 66 - "mathEditor.ts"
Cohesion: 0.09
Nodes (29): FUNCTIONS, BARS, COMMAND_FUNCTIONS, exponentText(), INVERSE, Item, join(), latexToAnswer() (+21 more)

### Community 67 - "test_preview.py"
Cohesion: 0.21
Nodes (13): catalogue(), replay(), replay_problem(), client(), headers(), test_check_failure_is_retryable_not_a_verdict(), fail(), test_entire_catalogue_has_valid_replay_domain_clean_values_and_answers() (+5 more)

### Community 68 - "owned_records.py"
Cohesion: 0.09
Nodes (31): attempt_summaries(), AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), insert_problem(), last_attempt(), list_problems() (+23 more)

### Community 69 - "practice.py"
Cohesion: 0.06
Nodes (40): attempt(), AttemptBody, _decode_cursor(), delete_account(), DeleteBody, _encode_cursor(), generate(), GenerateBody (+32 more)

### Community 71 - "typing"
Cohesion: 0.15
Nodes (3): BasicTemplate, Exercise, PublicProblem

### Community 72 - "answer_check.py"
Cohesion: 0.22
Nodes (8): check_tree(), classify(), _components(), _differs(), _is_primitive(), _not_real(), _same_number_everywhere(), _value()

### Community 73 - "types.ts"
Cohesion: 0.05
Nodes (76): AnswerInputProps, AnswerPreview(), card(), DifficultyDots(), DifficultyScale(), DifficultyScaleProps, AttemptStatus(), HistoryListProps (+68 more)

### Community 74 - "App.tsx"
Cohesion: 0.12
Nodes (33): App(), handleDeleted(), handleLogOut(), handleSignIn(), APP_ROUTES, NotFoundPage(), TITLES, APP_ROUTES (+25 more)

### Community 76 - "DashboardPage.tsx"
Cohesion: 0.23
Nodes (16): Button(), StatTile(), StatTileProps, TopicChips(), getDisplayName(), getProfileCounts(), saveDisplayName(), AccountSettings() (+8 more)

### Community 77 - "HistoryPage.tsx"
Cohesion: 0.26
Nodes (9): HistoryList(), Chips(), listProblemPage(), ProblemPage, PublicProblem, Filter, FILTERS, HistoryPage() (+1 more)

### Community 78 - "StubClient"
Cohesion: 0.21
Nodes (3): DenialChecks, SingleUserClient, StubClient

### Community 79 - "math_worker.py"
Cohesion: 0.19
Nodes (6): _apply_limits(), _build_sympy(), _check_child(), _child(), _run_worker(), test_educational_catalogue_and_checker()

### Community 81 - "[[path]].ts"
Cohesion: 0.36
Nodes (4): Context, onRequest(), FORWARDED_HEADERS, proxyToApi()

### Community 82 - "Account completion (#35)"
Cohesion: 0.40
Nodes (5): Account completion (#35), Anonymous demo and privacy, Deployment and retention gates, Hard deletion and expired identity, Learning records and metrics

### Community 84 - "vitest"
Cohesion: 0.08
Nodes (18): harness, renderAt(), signedIn, signedOut, configurePracticeAuth(), fetchMock, generate(), publicProblem (+10 more)

### Community 86 - "MathCheckInconclusive"
Cohesion: 0.19
Nodes (9): _check(), _worker_unavailable(), MathCheckInconclusive, check_answer(), test_worker_saturation_does_not_queue_and_slot_is_released(), inconclusive(), Answer checking, Cost and limits (+1 more)

### Community 88 - "parse_math_input"
Cohesion: 0.35
Nodes (10): parse_math_input(), test_exact_boundaries_remain_accepted(), test_function_count_is_bounded(), test_group_nesting_is_bounded(), test_input_length_is_bounded_before_tokenisation(), test_node_count_is_bounded(), test_numeric_literal_length_is_bounded(), test_supported_notation() (+2 more)

### Community 89 - "Routes"
Cohesion: 0.14
Nodes (14): API contract, `GET /api/problems`, `GET /api/problems/{id}`, `GET /api/profile`, `GET /api/topics`, HTTP failures and retry behavior, Ownership and atomicity, `POST /api/problems` (+6 more)

### Community 90 - "check_content.py"
Cohesion: 0.26
Nodes (3): inspect(), main(), ContentTests

### Community 93 - "math_parser.py"
Cohesion: 0.32
Nodes (3): _normalise(), _Token, _tokenise()

### Community 96 - "ApiError"
Cohesion: 0.14
Nodes (8): _api_error_response(), ApiError, install_error_handlers(), delete_user(), unavailable(), test_hard_delete_uses_server_key_and_no_redirects(), test_missing_deletion_config_never_contacts_auth(), test_uncertain_auth_failure_is_safe_and_closes_connection()

### Community 98 - "health.ts"
Cohesion: 0.28
Nodes (4): ApiStatusNotice(), API_BASE_URL, ApiHealth, checkApiHealth()

### Community 99 - "Saved practice UI (#11/#12)"
Cohesion: 0.40
Nodes (5): Durable history and profile, Public/private boundary, Saved practice UI (#11/#12), Verification, Writes, retries and stale responses

## Knowledge Gaps
- **10 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `eslint` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 550 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **44 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Basic-integral generator` connect `InternalProblem` to `types.ts`, `ADR-003: bounded real-valued integration answers`?**
  _High betweenness centrality (0.234) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `MathInputError` (e.g. with `check_answer()` and `test_function_count_is_bounded()`) actually correct?**
  _`MathInputError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Why does `seed()` connect `types.ts` to `InternalProblem`?**
  _High betweenness centrality (0.221) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `MathWorkerError` (e.g. with `_check()` and `attempt()`) actually correct?**
  _`MathWorkerError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Should `PracticeLoop — MVP Specification` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._