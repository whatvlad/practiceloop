# Graph Report - PracticeLoop  (2026-10-20)

## Corpus Check
- 190 files · ~85,720 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: (none) 8, .toml 3, .css 3)

## Summary
- 1505 nodes · 3643 edges · 108 communities (67 shown, 41 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 125 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `54644bc5`
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
- test_families.py
- test_supabase_hosted.py
- preview.py
- Prompt for Claude Code: implement the PracticeLoop frontend design
- pull_request_template.md
- system/README.md
- HANDOFF.md
- REVIEW_PROTOCOL.md
- test_auth.py
- basic.py
- MathNode
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
- attempt
- ProblemCard.tsx
- core.py
- sympy
- types.ts
- App.tsx
- practice.py
- Button
- DashboardPage.tsx
- history
- math_worker.py
- HistoryRow.tsx
- [[path]].ts
- Account completion (#35)
- issue-35-handoff.md
- HistoryPage.tsx
- vitest
- server.ts
- MathInputError
- typing
- check_content.py
- PracticePage.tsx
- FormulaField.test.tsx
- database.py
- Implementation stages
- subprocess
- ApiError
- PracticeLoop production readiness plan
- health.ts
- Saved practice UI (#11/#12)
- practice.test.ts
- learning_stats.py
- checker.ts
- issue-11-handoff.md
- issue-12-handoff.md
- RateLimiter
- AnswerInput.test.tsx
- FamilyParameters

## God Nodes (most connected - your core abstractions)
1. `MathInputError` - 30 edges
2. `MathWorkerError` - 29 edges
3. `parse_math_input()` - 27 edges
4. `ApiError` - 26 edges
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
- `Basic-integral generator` --references--> `InternalProblem`  [INFERRED]
  docs/architecture/BASIC_GENERATOR.md → backend/app/generators/basic.py
- `How it decides` --references--> `classify()`  [INFERRED]
  docs/architecture/ANSWER_CHECK.md → backend/app/services/answer_check.py

## Import Cycles
- None detected.

## Communities (108 total, 41 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.13
Nodes (8): Changelog, Unreleased, Completion criteria, Implementation workflow, Architecture and MVP analysis, Decision index, Open decisions — resolve before dependent features, Security policy

### Community 1 - "package.json"
Cohesion: 0.05
Nodes (39): dependencies, katex, mathlive, react, react-dom, @supabase/supabase-js, devDependencies, eslint (+31 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "test_basic.py"
Cohesion: 0.16
Nodes (15): generate_basic(), replay_basic(), SolutionStep, _verify(), test_candidate_with_incorrect_step_is_rejected(), test_complete_parameter_corpus(), test_higher_levels_retain_both_intended_rewrites(), test_missing_constant_or_inconsistent_final_answer_is_rejected() (+7 more)

### Community 4 - "Must-have before production"
Cohesion: 0.20
Nodes (10): Authentication and personal data, Landing page and CTA, Must-have before production, Practice flow, Privacy and analytics, Problem reports, Routing and public pages, Security, accessibility, and deployment (+2 more)

### Community 5 - "test_answer_check.py"
Cohesion: 0.10
Nodes (25): replay_problem(), check_answer(), MathCheckInconclusive, check_answer(), _learner_text(), outcome(), record(), test_adversarial_answers_terminate_within_limits() (+17 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.13
Nodes (21): AuthCallback, AuthClient, AuthOptions, AuthSnapshot, createAuthStore(), accept(), signIn(), signOut() (+13 more)

### Community 8 - "main.py"
Cohesion: 0.05
Nodes (22): allowed_origins(), _error(), health(), internal_error(), invalid_request(), lifespan(), request_boundary(), test_allowed_origins_reads_environment() (+14 more)

### Community 9 - "practice.ts"
Cohesion: 0.15
Nodes (40): client, accessToken(), accountRequest(), authorize(), base, cache(), correctProblems, credentials() (+32 more)

### Community 10 - "test_families.py"
Cohesion: 0.12
Nodes (14): _families(), FamilyProblem, FamilyStep, generate_family(), replay_family(), verify_family(), test_all_replay_fields_are_required(), test_bad_records_fail_before_symbolic_construction() (+6 more)

### Community 11 - "test_supabase_hosted.py"
Cohesion: 0.11
Nodes (14): check_private(), CheckFailure, Client, denied(), main(), NoRedirect, require(), rows() (+6 more)

### Community 12 - "preview.py"
Cohesion: 0.08
Nodes (14): answer(), attempt(), Attempt, generate(), Generate, _problem(), Session, _session() (+6 more)

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

### Community 19 - "basic.py"
Cohesion: 0.16
Nodes (3): BasicParameters, InternalProblem, PublicProblem

### Community 20 - "MathNode"
Cohesion: 0.28
Nodes (5): _constant_fraction(), MathNode, _number_fraction(), _Parser, _Token

### Community 25 - "MathWorkerError"
Cohesion: 0.17
Nodes (15): MathWorkerError, _run_worker(), validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker() (+7 more)

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.15
Nodes (12): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Launch blockers that must not be guessed, Planned Graphify policy (+4 more)

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
Cohesion: 0.14
Nodes (11): Basic-integral generator, Delivery boundary, Integration topic generators, Mathematical and educational verification, Use and persistence boundary, Accepted input language, ADR-003: bounded real-valued integration answers, Consequences (+3 more)

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
Nodes (36): absBig(), analyseAnswer(), AnswerAnalysis, constantFraction(), Fraction, FUNCTION_SET, gcd(), HINTS (+28 more)

### Community 64 - "Oracle backend deploy"
Cohesion: 0.22
Nodes (8): Before adding Supabase credentials (human only), Browser path, CORS, On the VM, One-time setup, Oracle backend deploy, Rollback and recovery, When the API is down

### Community 65 - "FormulaField.tsx"
Cohesion: 0.11
Nodes (26): AnswerInput(), insert(), move(), replace(), AnswerPreview(), answerLatex(), byName(), configureKeyboard() (+18 more)

### Community 66 - "mathEditor.ts"
Cohesion: 0.09
Nodes (29): FUNCTIONS, BARS, COMMAND_FUNCTIONS, exponentText(), INVERSE, Item, join(), latexToAnswer() (+21 more)

### Community 67 - "test_preview.py"
Cohesion: 0.26
Nodes (9): client(), headers(), test_check_failure_is_retryable_not_a_verdict(), fail(), test_generate_check_and_reveal_through_shared_worker(), test_one_fixed_demo_requires_login_for_more_and_never_saves_outcomes(), test_request_bounds_expiry_rate_and_unsupported_cells(), test_reveal_is_scoped_and_check_does_not_leak() (+1 more)

### Community 68 - "owned_records.py"
Cohesion: 0.09
Nodes (31): attempt_summaries(), AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), insert_problem(), last_attempt(), list_problems() (+23 more)

### Community 69 - "attempt"
Cohesion: 0.26
Nodes (13): attempt(), generate(), _respond(), database_unavailable(), claim(), _conflict(), lookup(), _replay() (+5 more)

### Community 70 - "ProblemCard.tsx"
Cohesion: 0.17
Nodes (16): AnswerInputProps, ApiStatusNotice(), card(), DifficultyDots(), HistoryRow(), WarningIcon(), ProblemCard(), ResultBanner() (+8 more)

### Community 71 - "core.py"
Cohesion: 0.19
Nodes (6): BasicTemplate, catalogue(), Exercise, replay(), test_existing_preview_versions_are_unchanged_and_new_cells_stay_internal(), test_entire_catalogue_has_valid_replay_domain_clean_values_and_answers()

### Community 72 - "sympy"
Cohesion: 0.22
Nodes (8): check_tree(), classify(), _components(), _differs(), _is_primitive(), _not_real(), _same_number_everywhere(), _value()

### Community 73 - "types.ts"
Cohesion: 0.14
Nodes (20): DifficultyScaleProps, ProblemCardProps, ChipOption, ChipsProps, TOPIC_OPTIONS, TopicChipsProps, MockTemplate, State (+12 more)

### Community 74 - "App.tsx"
Cohesion: 0.17
Nodes (22): APP_ROUTES, NotFoundPage(), TITLES, APP_ROUTES, AppNav(), AppNavProps, Logo(), PublicNav() (+14 more)

### Community 75 - "practice.py"
Cohesion: 0.17
Nodes (10): AttemptBody, _decode_cursor(), delete_account(), DeleteBody, _encode_cursor(), GenerateBody, _idempotency_key(), _invalid() (+2 more)

### Community 76 - "Button"
Cohesion: 0.34
Nodes (10): Button(), getDisplayName(), AccountSettings(), NameForm(), LearningStatistics(), rate(), ProfilePage(), Load (+2 more)

### Community 77 - "DashboardPage.tsx"
Cohesion: 0.16
Nodes (20): App(), handleDeleted(), handleLogOut(), handleSignIn(), DifficultyScale(), HistoryList(), StatTile(), StatTileProps (+12 more)

### Community 78 - "history"
Cohesion: 0.18
Nodes (11): history(), learning_statistics(), _not_found(), profile(), ProfileBody, _public_problem(), reopen(), reveal_answer() (+3 more)

### Community 79 - "math_worker.py"
Cohesion: 0.36
Nodes (4): _apply_limits(), _build_sympy(), _check_child(), _child()

### Community 80 - "HistoryRow.tsx"
Cohesion: 0.20
Nodes (15): AttemptStatus(), HistoryListProps, CheckIcon(), ChevronIcon(), CrossIcon(), DashIcon(), Icon(), IconProps (+7 more)

### Community 81 - "[[path]].ts"
Cohesion: 0.36
Nodes (4): Context, onRequest(), FORWARDED_HEADERS, proxyToApi()

### Community 82 - "Account completion (#35)"
Cohesion: 0.40
Nodes (5): Account completion (#35), Anonymous demo and privacy, Deployment and retention gates, Hard deletion and expired identity, Learning records and metrics

### Community 84 - "HistoryPage.tsx"
Cohesion: 0.11
Nodes (12): harness, renderAt(), signedIn, signedOut, Chips(), root, Filter, FILTERS (+4 more)

### Community 85 - "vitest"
Cohesion: 0.17
Nodes (7): REJECTED, SUPPORTED, BANK, PUBLIC_KEYS, renderMath(), THEMES, vitest

### Community 86 - "server.ts"
Cohesion: 0.26
Nodes (17): copy(), find(), generateProblem(), getLastSelection(), getProblem(), getProfileCounts(), listProblems(), load() (+9 more)

### Community 88 - "MathInputError"
Cohesion: 0.19
Nodes (15): MathInputError, MathInputTooLong, _normalise(), parse_math_input(), _tokenise(), test_exact_boundaries_remain_accepted(), test_function_count_is_bounded(), test_group_nesting_is_bounded() (+7 more)

### Community 89 - "typing"
Cohesion: 0.13
Nodes (5): build(), FamilyTemplate, build(), build(), build()

### Community 90 - "check_content.py"
Cohesion: 0.26
Nodes (3): inspect(), main(), ContentTests

### Community 91 - "PracticePage.tsx"
Cohesion: 0.17
Nodes (8): OpenedProblem, latestOrNewId(), PracticePage(), PracticeSession(), practiceUrl(), calls, fetchMock, saved

### Community 92 - "FormulaField.test.tsx"
Cohesion: 0.16
Nodes (5): changes, Fake, FakeMathfield, Harness(), render()

### Community 93 - "database.py"
Cohesion: 0.23
Nodes (3): DatabaseNotConfigured, get_pool(), transaction()

### Community 94 - "Implementation stages"
Cohesion: 0.25
Nodes (8): Implementation stages, Issue #33: working preview infrastructure, Issue #34: usable core integration practice, Issue #35: accounts, private history and learning statistics, Issue #36: advanced integration generator, Issue #37: privacy-safe problem sharing, Issue #38: production readiness on the preview domain, Issue #39: custom-domain public launch

### Community 96 - "ApiError"
Cohesion: 0.17
Nodes (8): _check(), _worker_unavailable(), ApiError, delete_user(), unavailable(), test_hard_delete_uses_server_key_and_no_redirects(), test_missing_deletion_config_never_contacts_auth(), test_uncertain_auth_failure_is_safe_and_closes_connection()

### Community 97 - "PracticeLoop production readiness plan"
Cohesion: 0.25
Nodes (7): Expected implementation surface, Optional or deferred, PracticeLoop production readiness plan, Product decisions, Recommended, Unresolved production blockers, Verification and publication rules

### Community 98 - "health.ts"
Cohesion: 0.40
Nodes (3): API_BASE_URL, ApiHealth, checkApiHealth()

### Community 99 - "Saved practice UI (#11/#12)"
Cohesion: 0.40
Nodes (5): Durable history and profile, Public/private boundary, Saved practice UI (#11/#12), Verification, Writes, retries and stale responses

### Community 100 - "practice.test.ts"
Cohesion: 0.32
Nodes (7): configurePracticeAuth(), fetchMock, generate(), publicProblem, response(), savedProblem(), storedProblem

### Community 102 - "checker.ts"
Cohesion: 0.52
Nodes (5): balanced(), check(), isReadable(), normalise(), ACCEPTED

## Knowledge Gaps
- **10 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `eslint` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 578 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Basic-integral generator` connect `ADR-003: bounded real-valued integration answers` to `basic.py`, `server.ts`?**
  _High betweenness centrality (0.234) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `MathInputError` (e.g. with `check_answer()` and `test_function_count_is_bounded()`) actually correct?**
  _`MathInputError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `README.md` be split into smaller, more focused modules?**
  _Cohesion score 0.12631578947368421 - nodes in this community are weakly interconnected._
- **Why does `seed()` connect `server.ts` to `ADR-003: bounded real-valued integration answers`?**
  _High betweenness centrality (0.218) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `MathWorkerError` (e.g. with `_check()` and `attempt()`) actually correct?**
  _`MathWorkerError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._