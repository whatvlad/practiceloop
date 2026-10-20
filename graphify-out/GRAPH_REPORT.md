# Graph Report - PracticeLoop  (2026-10-20)

## Corpus Check
- 193 files · ~90,577 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 7, .toml 3, .css 3)

## Summary
- 1575 nodes · 3897 edges · 116 communities (69 shown, 47 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 136 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `97586b32`
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
- HistoryRow.tsx
- definite.py
- answer_check.py
- types.ts
- App.tsx
- test_definite.py
- DashboardPage.tsx
- App
- HistoryRow.tsx
- ProblemCard.tsx
- Parser
- DashboardPage.tsx
- json
- test_health.py
- math_parser.py
- vitest
- PracticeLoop production readiness plan
- CallbackChecks
- BasicParameters
- TopicChips.tsx
- errors.py
- FormulaField.test.tsx
- main.py
- test_health.py
- CheckResult
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
- MathCheckInconclusive
- PracticeLoop production readiness plan
- [[path]].ts
- format.ts
- main.tsx
- DefiniteParameters
- CHANGELOG.md

## God Nodes (most connected - your core abstractions)
1. `parse_math_input()` - 31 edges
2. `MathInputError` - 30 edges
3. `MathWorkerError` - 29 edges
4. `ApiError` - 26 edges
5. `check_answer()` - 26 edges
6. `Button()` - 25 edges
7. `replay_definite()` - 24 edges
8. `generate()` - 24 edges
9. `react` - 24 edges
10. `Reader` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Definite integrals` --references--> `catalogue()`  [INFERRED]
  docs/architecture/TOPIC_GENERATORS.md → backend/app/generators/core.py
- `Delivery boundary` --references--> `replay_problem()`  [INFERRED]
  docs/architecture/TOPIC_GENERATORS.md → backend/app/services/answer_check.py
- `Project status` --references--> `current_user()`  [INFERRED]
  docs/agents/STATUS.md → backend/app/core/auth.py
- `API contract` --references--> `current_user()`  [INFERRED]
  docs/api/README.md → backend/app/core/auth.py
- `HTTP failures and retry behavior` --references--> `database_unavailable()`  [INFERRED]
  docs/api/README.md → backend/app/core/database.py

## Import Cycles
- None detected.

## Communities (116 total, 47 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.20
Nodes (4): Architecture and MVP analysis, Decision index, Open decisions — resolve before dependent features, Security policy

### Community 1 - "package.json"
Cohesion: 0.05
Nodes (39): dependencies, katex, mathlive, react, react-dom, @supabase/supabase-js, devDependencies, eslint (+31 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "generate_basic"
Cohesion: 0.16
Nodes (15): generate_basic(), replay_basic(), SolutionStep, _verify(), test_candidate_with_incorrect_step_is_rejected(), test_complete_parameter_corpus(), test_higher_levels_retain_both_intended_rewrites(), test_missing_constant_or_inconsistent_final_answer_is_rejected() (+7 more)

### Community 4 - "Must-have before production"
Cohesion: 0.20
Nodes (10): Authentication and personal data, Landing page and CTA, Must-have before production, Practice flow, Privacy and analytics, Problem reports, Routing and public pages, Security, accessibility, and deployment (+2 more)

### Community 5 - "test_answer_check.py"
Cohesion: 0.15
Nodes (21): check_answer(), family(), _learner_text(), outcome(), record(), test_adversarial_answers_terminate_within_limits(), test_check_answer_end_to_end(), test_classification() (+13 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.13
Nodes (21): AuthCallback, AuthClient, AuthOptions, AuthSnapshot, createAuthStore(), accept(), signIn(), signOut() (+13 more)

### Community 8 - "Routes"
Cohesion: 0.09
Nodes (18): _error(), internal_error(), invalid_request(), request_boundary(), API contract, `GET /api/problems`, `GET /api/problems/{id}`, `GET /api/profile` (+10 more)

### Community 9 - "PracticePage.tsx"
Cohesion: 0.15
Nodes (40): client, accessToken(), accountRequest(), authorize(), base, cache(), correctProblems, credentials() (+32 more)

### Community 10 - "server.ts"
Cohesion: 0.13
Nodes (14): _families(), FamilyProblem, generate_family(), replay_family(), verify_family(), test_all_replay_fields_are_required(), test_bad_records_fail_before_symbolic_construction(), test_complete_family_corpus() (+6 more)

### Community 11 - "test_supabase_hosted.py"
Cohesion: 0.07
Nodes (19): test_educational_catalogue_and_checker(), inspect(), main(), main(), ContentTests, check_private(), CheckFailure, Client (+11 more)

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
Cohesion: 0.07
Nodes (31): _auth_unavailable(), AuthUnavailableError, current_user(), get_token_verifier(), _invalid_token(), token_verifier(), TokenVerifier, _user_from_claims() (+23 more)

### Community 20 - "test_owned_records.py"
Cohesion: 0.29
Nodes (5): _constant_fraction(), MathInputError, MathNode, _number_fraction(), _Parser

### Community 25 - "MathInputError"
Cohesion: 0.17
Nodes (15): MathWorkerError, _run_worker(), validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker() (+7 more)

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 33 - "test_basic.py"
Cohesion: 0.10
Nodes (49): AnswerCheck, answer_of(), attempt(), client(), generate(), key(), pin_version(), keep() (+41 more)

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
Nodes (6): Basic-integral generator, Definite integrals, Delivery boundary, Integration topic generators, Mathematical and educational verification, Use and persistence boundary

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
Cohesion: 0.10
Nodes (30): analyseAnswer(), AnswerAnalysis, Fraction, FUNCTION_SET, gcd(), HINTS, isDigit(), isLetter() (+22 more)

### Community 64 - "Oracle backend deploy"
Cohesion: 0.22
Nodes (8): Before adding Supabase credentials (human only), Browser path, CORS, On the VM, One-time setup, Oracle backend deploy, Rollback and recovery, When the API is down

### Community 65 - "FormulaField.tsx"
Cohesion: 0.14
Nodes (21): answerLatex(), byName(), configureKeyboard(), FormulaField(), FormulaFieldProps, keycap(), loadMathLive(), MathLive (+13 more)

### Community 66 - "mathEditor.ts"
Cohesion: 0.09
Nodes (29): FUNCTIONS, BARS, COMMAND_FUNCTIONS, exponentText(), INVERSE, Item, join(), latexToAnswer() (+21 more)

### Community 67 - "test_preview.py"
Cohesion: 0.26
Nodes (9): client(), headers(), test_check_failure_is_retryable_not_a_verdict(), fail(), test_generate_check_and_reveal_through_shared_worker(), test_one_fixed_demo_requires_login_for_more_and_never_saves_outcomes(), test_request_bounds_expiry_rate_and_unsupported_cells(), test_reveal_is_scoped_and_check_does_not_leak() (+1 more)

### Community 68 - "InternalProblem"
Cohesion: 0.09
Nodes (31): attempt_summaries(), AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), insert_problem(), last_attempt(), list_problems() (+23 more)

### Community 69 - "practice.py"
Cohesion: 0.24
Nodes (15): attempt(), generate(), _idempotency_key(), _invalid(), _respond(), database_unavailable(), claim(), _conflict() (+7 more)

### Community 70 - "HistoryRow.tsx"
Cohesion: 0.20
Nodes (15): ApiStatusNotice(), AttemptStatus(), HistoryListProps, HistoryRow(), CheckIcon(), ChevronIcon(), CrossIcon(), DashIcon() (+7 more)

### Community 71 - "definite.py"
Cohesion: 0.11
Nodes (11): BasicTemplate, _definite_records(), _family_records(), _base(), base_record(), _basic(), DefiniteStep, DefiniteTemplate (+3 more)

### Community 72 - "answer_check.py"
Cohesion: 0.16
Nodes (12): DefiniteProblem, check_tree(), classify(), _classify_definite(), _components(), _defined_throughout(), _differs(), _domain() (+4 more)

### Community 73 - "types.ts"
Cohesion: 0.24
Nodes (10): DifficultyScaleProps, DIFFICULTIES, AttemptResult, AvailableTopic, Difficulty, ProblemPage, ProfileCounts, RevealedAnswer (+2 more)

### Community 74 - "App.tsx"
Cohesion: 0.15
Nodes (27): APP_ROUTES, NotFoundPage(), TITLES, APP_ROUTES, AppNav(), AppNavProps, Logo(), PublicNav() (+19 more)

### Community 75 - "test_definite.py"
Cohesion: 0.15
Nodes (16): replay(), is_clean_value(), replay_definite(), verify_definite(), replay_problem(), record(), source(), test_bounds_never_touch_a_singularity() (+8 more)

### Community 76 - "DashboardPage.tsx"
Cohesion: 0.18
Nodes (14): StatTile(), StatTileProps, deleteAccount(), getDisplayName(), saveDisplayName(), AccountSettings(), NameForm(), LearningStatistics() (+6 more)

### Community 77 - "App"
Cohesion: 0.14
Nodes (19): App(), handleDeleted(), handleLogOut(), handleSignIn(), harness, renderAt(), signedIn, signedOut (+11 more)

### Community 78 - "HistoryRow.tsx"
Cohesion: 0.13
Nodes (19): AttemptBody, _decode_cursor(), delete_account(), DeleteBody, _encode_cursor(), GenerateBody, history(), learning_statistics() (+11 more)

### Community 79 - "ProblemCard.tsx"
Cohesion: 0.38
Nodes (9): DifficultyDots(), ProblemCard(), ResultBanner(), RevealedAnswer(), SolutionSteps(), Tex(), TexProps, topicName() (+1 more)

### Community 80 - "Parser"
Cohesion: 0.30
Nodes (6): absBig(), constantFraction(), numberFraction(), Parser, SyntaxProblem, validateExponent()

### Community 81 - "DashboardPage.tsx"
Cohesion: 0.20
Nodes (7): DifficultyScale(), resetPractice(), DashboardPage(), generate(), calls, fetchMock, saved

### Community 82 - "json"
Cohesion: 0.40
Nodes (5): Account completion (#35), Anonymous demo and privacy, Deployment and retention gates, Hard deletion and expired identity, Learning records and metrics

### Community 84 - "math_parser.py"
Cohesion: 0.24
Nodes (5): MathInputTooLong, _normalise(), _Token, _tokenise(), Bounded mathematical input

### Community 85 - "vitest"
Cohesion: 0.19
Nodes (5): REJECTED, SUPPORTED, renderMath(), THEMES, vitest

### Community 86 - "PracticeLoop production readiness plan"
Cohesion: 0.16
Nodes (24): ProblemCardProps, BANK, MockTemplate, copy(), find(), generateProblem(), getLastSelection(), getProblem() (+16 more)

### Community 88 - "CallbackChecks"
Cohesion: 0.21
Nodes (14): parse_math_input(), _apply_limits(), _build_sympy(), _check_child(), _child(), test_exact_boundaries_remain_accepted(), test_function_count_is_bounded(), test_group_nesting_is_bounded() (+6 more)

### Community 89 - "BasicParameters"
Cohesion: 0.15
Nodes (6): build(), FamilyStep, FamilyTemplate, build(), build(), build()

### Community 90 - "TopicChips.tsx"
Cohesion: 0.22
Nodes (8): card(), ChipOption, Chips(), ChipsProps, TOPIC_OPTIONS, TopicChips(), TopicChipsProps, TOPICS

### Community 92 - "FormulaField.test.tsx"
Cohesion: 0.16
Nodes (5): changes, Fake, FakeMathfield, Harness(), render()

### Community 93 - "main.py"
Cohesion: 0.10
Nodes (6): close_pool(), DatabaseNotConfigured, get_pool(), transaction(), health(), lifespan()

### Community 95 - "CheckResult"
Cohesion: 0.31
Nodes (8): AnswerInputProps, ResultBannerProps, balanced(), check(), isReadable(), normalise(), ACCEPTED, CheckResult

### Community 96 - "ApiError"
Cohesion: 0.15
Nodes (9): _check(), _worker_unavailable(), ApiError, delete_user(), unavailable(), test_delete_requires_exact_confirmation_and_uses_only_verified_identity(), test_hard_delete_uses_server_key_and_no_redirects(), test_missing_deletion_config_never_contacts_auth() (+1 more)

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
Cohesion: 0.32
Nodes (7): configurePracticeAuth(), fetchMock, generate(), publicProblem, response(), savedProblem(), storedProblem

### Community 106 - "AnswerInput"
Cohesion: 0.21
Nodes (7): AnswerInput(), insert(), move(), replace(), AnswerPreview(), Harness(), render()

### Community 109 - "MathCheckInconclusive"
Cohesion: 0.31
Nodes (7): MathCheckInconclusive, test_worker_saturation_does_not_queue_and_slot_is_released(), inconclusive(), Answer checking, Cost and limits, Definite integrals, How it decides

### Community 110 - "PracticeLoop production readiness plan"
Cohesion: 0.25
Nodes (7): Expected implementation surface, Optional or deferred, PracticeLoop production readiness plan, Product decisions, Recommended, Unresolved production blockers, Verification and publication rules

### Community 111 - "[[path]].ts"
Cohesion: 0.36
Nodes (4): Context, onRequest(), FORWARDED_HEADERS, proxyToApi()

### Community 112 - "format.ts"
Cohesion: 0.43
Nodes (5): formatWhen(), isDefinite(), MONTHS, startOfDay(), NOW

## Knowledge Gaps
- **10 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `eslint` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 598 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **47 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Basic-integral generator` connect `ADR-003: bounded real-valued integration answers` to `InternalProblem`, `PracticeLoop production readiness plan`?**
  _High betweenness centrality (0.247) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `MathInputError` (e.g. with `check_answer()` and `test_function_count_is_bounded()`) actually correct?**
  _`MathInputError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Why does `seed()` connect `PracticeLoop production readiness plan` to `ADR-003: bounded real-valued integration answers`?**
  _High betweenness centrality (0.222) - this node is a cross-community bridge._
- **Should `PracticeLoop — MVP Specification` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._
- **Why does `InternalProblem` connect `InternalProblem` to `generate_basic`, `definite.py`, `answer_check.py`, `test_definite.py`, `ADR-003: bounded real-valued integration answers`, `BasicParameters`?**
  _High betweenness centrality (0.222) - this node is a cross-community bridge._