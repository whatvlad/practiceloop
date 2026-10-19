# Graph Report - issue-12-history  (2026-10-19)

## Corpus Check
- 174 files · ~77,787 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: (none) 8, .toml 3, .css 3)

## Summary
- 1388 nodes · 3296 edges · 105 communities (59 shown, 46 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0e3fa0f8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- README.md
- package.json
- PracticeLoop — MVP Specification
- test_basic.py
- Must-have before production
- MathWorkerError
- compilerOptions
- auth.test.ts
- Routes
- practice.ts
- server.ts
- test_supabase_hosted.py
- preview.py
- Prompt for Claude Code: implement the PracticeLoop frontend design
- pull_request_template.md
- system/README.md
- HANDOFF.md
- REVIEW_PROTOCOL.md
- test_auth.py
- App
- test_owned_records.py
- MathInputError
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
- attempt
- answer_check.py
- ProblemCard.tsx
- App.tsx
- types.ts
- DashboardPage.tsx
- test_math_worker.py
- HistoryRow.tsx
- math_worker.py
- test_answer_check.py
- [[path]].ts
- supabase_google_test_login.py
- StubClient
- savedPracticeFlow.test.tsx
- vitest
- typing
- main.py
- invalid_request
- database.py
- test_health.py
- PracticePage.tsx
- test_supabase_hosted_unit.py
- CallbackChecks
- checker.ts
- RateLimiter
- components.test.tsx
- health.ts
- Saved practice UI (#11/#12)
- check_repository.py
- AttemptBody
- CHANGELOG.md
- issue-11-handoff.md
- issue-12-handoff.md

## God Nodes (most connected - your core abstractions)
1. `MathInputError` - 30 edges
2. `MathWorkerError` - 29 edges
3. `parse_math_input()` - 25 edges
4. `Reader` - 24 edges
5. `check_answer()` - 23 edges
6. `attempt()` - 22 edges
7. `react` - 21 edges
8. `generate()` - 20 edges
9. `vitest` - 20 edges
10. `Button()` - 20 edges

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

## Communities (105 total, 46 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.21
Nodes (4): Architecture and MVP analysis, Decision index, Open decisions — resolve before dependent features, Security policy

### Community 1 - "package.json"
Cohesion: 0.05
Nodes (39): dependencies, katex, mathlive, react, react-dom, @supabase/supabase-js, devDependencies, eslint (+31 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "test_basic.py"
Cohesion: 0.06
Nodes (28): BasicParameters, generate_basic(), InternalProblem, replay_basic(), SolutionStep, _verify(), PublicProblem, test_candidate_with_incorrect_step_is_rejected() (+20 more)

### Community 4 - "Must-have before production"
Cohesion: 0.11
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "MathWorkerError"
Cohesion: 0.14
Nodes (17): check_answer(), MathCheckInconclusive, MathWorkerError, check_answer(), test_adversarial_answers_terminate_within_limits(), test_inconclusive_is_a_service_error(), test_invalid_syntax_never_starts_a_worker(), test_original_domain_hole_is_invalid_before_simplification() (+9 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.13
Nodes (21): AuthCallback, AuthClient, AuthOptions, AuthSnapshot, createAuthStore(), accept(), signIn(), signOut() (+13 more)

### Community 8 - "Routes"
Cohesion: 0.14
Nodes (14): API contract, `GET /api/problems`, `GET /api/problems/{id}`, `GET /api/profile`, `GET /api/topics`, HTTP failures and retry behavior, Ownership and atomicity, `POST /api/problems` (+6 more)

### Community 9 - "practice.ts"
Cohesion: 0.19
Nodes (30): client, accessToken(), authorize(), base, cache(), correctProblems, credentials(), find() (+22 more)

### Community 10 - "server.ts"
Cohesion: 0.26
Nodes (17): copy(), find(), generateProblem(), getLastSelection(), getProblem(), getProfileCounts(), listProblems(), load() (+9 more)

### Community 11 - "test_supabase_hosted.py"
Cohesion: 0.24
Nodes (9): check_private(), Client, denied(), main(), NoRedirect, require(), rows(), verify() (+1 more)

### Community 12 - "preview.py"
Cohesion: 0.11
Nodes (15): _pick(), answer(), attempt(), Attempt, generate(), Generate, _problem(), Session (+7 more)

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
Nodes (33): _auth_unavailable(), AuthUnavailableError, current_user(), get_token_verifier(), _invalid_token(), token_verifier(), TokenVerifier, _user_from_claims() (+25 more)

### Community 19 - "App"
Cohesion: 0.11
Nodes (18): App(), handleLogOut(), handleSignIn(), harness, renderAt(), signedIn, signedOut, root (+10 more)

### Community 20 - "test_owned_records.py"
Cohesion: 0.17
Nodes (15): add_problem(), flags(), test_attempts_are_scoped_to_owner(), test_cannot_attempt_someone_elses_problem(), test_ensure_profile_is_idempotent(), test_history_lists_only_own_problems_with_stable_cursor(), test_other_users_problem_is_indistinguishable_from_missing(), test_owner_reads_own_problem() (+7 more)

### Community 25 - "MathInputError"
Cohesion: 0.13
Nodes (20): _constant_fraction(), MathInputError, MathInputTooLong, MathNode, _normalise(), _number_fraction(), parse_math_input(), _Parser (+12 more)

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 33 - "test_practice_api.py"
Cohesion: 0.13
Nodes (40): close_pool(), AnswerCheck, attempt(), client(), generate(), key(), primitive_of(), rows() (+32 more)

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
Cohesion: 0.09
Nodes (35): absBig(), AnswerAnalysis, constantFraction(), Fraction, FUNCTION_SET, gcd(), HINTS, isDigit() (+27 more)

### Community 64 - "Oracle backend deploy"
Cohesion: 0.22
Nodes (8): Before adding Supabase credentials (human only), Browser path, CORS, On the VM, One-time setup, Oracle backend deploy, Rollback and recovery, When the API is down

### Community 65 - "FormulaField.tsx"
Cohesion: 0.06
Nodes (37): analyseAnswer(), AnswerInput(), insert(), move(), replace(), AnswerInputProps, AnswerPreview(), Harness() (+29 more)

### Community 66 - "mathEditor.ts"
Cohesion: 0.12
Nodes (20): FUNCTIONS, BARS, COMMAND_FUNCTIONS, exponentText(), INVERSE, Item, join(), latexToAnswer() (+12 more)

### Community 67 - "test_preview.py"
Cohesion: 0.29
Nodes (9): replay(), client(), headers(), test_entire_catalogue_has_valid_replay_domain_clean_values_and_answers(), test_generate_check_and_reveal_through_shared_worker(), test_no_repeats_until_pool_exhausted_and_no_adjacent_repeat_across_cycle(), test_request_bounds_expiry_rate_and_unsupported_cells(), test_reveal_is_scoped_and_check_does_not_leak() (+1 more)

### Community 68 - "owned_records.py"
Cohesion: 0.14
Nodes (16): attempt_summaries(), AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), insert_problem(), last_attempt(), list_problems() (+8 more)

### Community 69 - "practice.py"
Cohesion: 0.16
Nodes (12): _decode_cursor(), _encode_cursor(), history(), _not_found(), profile(), _public_problem(), reopen(), reveal_answer() (+4 more)

### Community 71 - "attempt"
Cohesion: 0.18
Nodes (18): attempt(), _check(), generate(), _idempotency_key(), _invalid(), _respond(), _worker_unavailable(), database_unavailable() (+10 more)

### Community 72 - "answer_check.py"
Cohesion: 0.26
Nodes (7): classify(), _components(), _differs(), _is_primitive(), _not_real(), _same_number_everywhere(), _value()

### Community 73 - "ProblemCard.tsx"
Cohesion: 0.24
Nodes (15): DifficultyDots(), ProblemCard(), ProblemCardProps, ResultBanner(), ResultBannerProps, RESULTS, RevealedAnswer(), SolutionSteps() (+7 more)

### Community 74 - "App.tsx"
Cohesion: 0.18
Nodes (18): APP_ROUTES, NotFoundPage(), TITLES, APP_ROUTES, AppNav(), AppNavProps, Logo(), PublicNav() (+10 more)

### Community 75 - "types.ts"
Cohesion: 0.15
Nodes (18): DifficultyScaleProps, ChipOption, ChipsProps, TOPIC_OPTIONS, TopicChipsProps, MockTemplate, State, DIFFICULTIES (+10 more)

### Community 76 - "DashboardPage.tsx"
Cohesion: 0.17
Nodes (17): Button(), DifficultyScale(), HistoryList(), StatTile(), StatTileProps, Chips(), TopicChips(), getProfileCounts() (+9 more)

### Community 77 - "test_math_worker.py"
Cohesion: 0.19
Nodes (13): validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker(), test_limits_are_active_only_in_child(), test_memory_limit_stops_pathological_allocation() (+5 more)

### Community 78 - "HistoryRow.tsx"
Cohesion: 0.18
Nodes (17): AttemptStatus(), HistoryListProps, HistoryRow(), ArrowIcon(), CheckIcon(), ChevronIcon(), CrossIcon(), DashIcon() (+9 more)

### Community 79 - "math_worker.py"
Cohesion: 0.16
Nodes (7): check_tree(), _apply_limits(), _build_sympy(), _check_child(), _child(), _run_worker(), test_educational_catalogue_and_checker()

### Community 80 - "test_answer_check.py"
Cohesion: 0.20
Nodes (11): replay_problem(), _learner_text(), outcome(), record(), test_check_answer_end_to_end(), test_classification(), test_every_generated_answer_is_accepted(), test_oversized_answer_is_request_validation() (+3 more)

### Community 81 - "[[path]].ts"
Cohesion: 0.36
Nodes (4): Context, onRequest(), FORWARDED_HEADERS, proxyToApi()

### Community 83 - "StubClient"
Cohesion: 0.21
Nodes (3): DenialChecks, SingleUserClient, StubClient

### Community 84 - "savedPracticeFlow.test.tsx"
Cohesion: 0.15
Nodes (10): configurePracticeAuth(), fetchMock, generate(), publicProblem, response(), savedProblem(), storedProblem, calls (+2 more)

### Community 85 - "vitest"
Cohesion: 0.17
Nodes (7): REJECTED, SUPPORTED, BANK, PUBLIC_KEYS, renderMath(), THEMES, vitest

### Community 86 - "typing"
Cohesion: 0.24
Nodes (3): inspect(), main(), ContentTests

### Community 89 - "invalid_request"
Cohesion: 0.23
Nodes (4): _error(), internal_error(), invalid_request(), request_boundary()

### Community 92 - "PracticePage.tsx"
Cohesion: 0.33
Nodes (6): getLastSelection(), OpenedProblem, latestOrNewId(), PracticePage(), PracticeSession(), practiceUrl()

### Community 95 - "checker.ts"
Cohesion: 0.52
Nodes (5): balanced(), check(), isReadable(), normalise(), ACCEPTED

### Community 97 - "components.test.tsx"
Cohesion: 0.47
Nodes (3): ApiStatusNotice(), card(), WarningIcon()

### Community 98 - "health.ts"
Cohesion: 0.40
Nodes (3): API_BASE_URL, ApiHealth, checkApiHealth()

### Community 99 - "Saved practice UI (#11/#12)"
Cohesion: 0.40
Nodes (5): Durable history and profile, Public/private boundary, Saved practice UI (#11/#12), Verification, Writes, retries and stale responses

## Knowledge Gaps
- **10 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `eslint` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 538 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Basic-integral generator` connect `test_basic.py` to `server.ts`, `ADR-003: bounded real-valued integration answers`?**
  _High betweenness centrality (0.236) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `MathInputError` (e.g. with `check_answer()` and `test_function_count_is_bounded()`) actually correct?**
  _`MathInputError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Why does `seed()` connect `server.ts` to `test_basic.py`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `MathWorkerError` (e.g. with `_check()` and `attempt()`) actually correct?**
  _`MathWorkerError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Should `PracticeLoop — MVP Specification` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._