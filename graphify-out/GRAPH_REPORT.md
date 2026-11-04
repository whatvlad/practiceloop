# Graph Report - PracticeLoop  (2026-11-04)

## Corpus Check
- 467 files · ~413,056 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: (none) 10, .css 6, .toml 3)

## Summary
- 4716 nodes · 14936 edges · 227 communities (150 shown, 77 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1294 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d8c0fb2b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- README.md
- package.json
- PracticeLoop — MVP Specification
- api/worksheets.py
- Must-have before production
- test_answer_check.py
- compilerOptions
- auth.test.ts
- API contract
- practice.ts
- integrals.py
- differentiation/single.py
- preview.py
- Prompt for Claude Code: implement the PracticeLoop frontend design
- pull_request_template.md
- system/README.md
- HANDOFF.md
- REVIEW_PROTOCOL.md
- test_auth.py
- ProblemCard.tsx
- test_answer_variables.py
- partial.py
- test_math_worker.py
- setup-graphify.sh
- practiceloop-backend
- TASK_PROTOCOL.md
- typing
- PracticeLoop production roadmap
- 0001-frontend.md
- 0002-data-security.md
- test_practice_api.py
- vite-env.d.ts
- Problem generation intent
- Educational content style intent
- DeterministicRNG
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
- Reader
- HistoryPage.tsx
- owned_records.py
- test_shares_api.py
- Setup
- linear_algebra.py
- InputContract
- types.ts
- App.tsx
- test_engine_complex_numbers.py
- Integration topic generators
- WorksheetBuilder.tsx
- transaction
- services/shares.py
- SyntaxProblem
- test_engine_analysis_two.py
- topics/catalogue.py
- issue-35-handoff.md
- e2e_local.py
- pytest
- [[path]].ts
- build_visual
- react
- shares.ts
- test_reports_api.py
- topics.ts
- Answer
- api/codes.py
- issue
- test_engine_code_opening.py
- test_worksheets_api.py
- parse_answer_input
- DefiniteView.tsx
- Step
- dataclasses
- Canvas
- issue-11-handoff.md
- issue-12-handoff.md
- test_engine_elementary_api.py
- math_worker.py
- AnswerInput
- Routes
- site.ts
- Outcome
- supabase_google_test_login.py
- ADR-005: multiple integrals and derivatives
- main.tsx
- parse_code
- Changelog
- pathlib
- devDependencies
- answerSyntax.test.ts
- dependencies
- ConstantExpressionAnswer
- scripts
- to_tree
- audit.sh
- auth.py
- spec.py
- region2d.test.tsx
- typing
- ExpressionAnswer
- topics/catalogue.py
- DeterministicRNG
- rational_proof.py
- test_preview.py
- dataclasses
- test_archive.py
- test_engine_probability_foundation.py
- _probability_common.py
- registry
- MathNode
- test_worksheet_tex.py
- engine/practice.py
- test_engine_slice.py
- FiniteDistribution
- Probability and Statistics curriculum (#200)
- test_supabase_hosted.py
- ADR-008: composable generator engine
- Computational contracts and Graphify checkpoint
- services/worksheets.py
- MVP end-to-end check (#13)
- geometry.ts
- createAuthStore
- test_engine_probability.py
- CallbackChecks
- mathEditor.ts
- sympy
- test_engine_analysis.py
- subprocess
- test_engine_computational_api.py
- Generator Refactor MVP
- ADR-006: interactive visualizations in solutions
- _probability_inference.py
- Analysis exercise-sheet generator expansion
- TinyAnswer
- spec.ts
- PracticeLoop agent rules
- ReportProblem.tsx
- ADR-007: printable PDF worksheets
- expression.ts
- WorksheetBuilder.test.tsx
- engine_fixtures.py
- answer_text
- test_engine_catalogue.py
- Account completion (#35)
- test_health.py
- Saved practice UI (#11/#12)
- plot2d.py
- 202610150001_initial_schema.sql
- math.ts
- NoRedirect
- test_engine_probability_foundation.py
- os
- 202610220001_worksheets.sql
- Solid3dVisual.tsx
- health.ts
- Elementary functions and logic delivery (#235)
- private.problem_reports
- check_answer
- test_engine_elementary_logic.py
- Optional Graphify tooling
- Analysis source intake handoff
- private.idempotency_keys
- private.problem_shares
- Algebra30: remainder modulo a quadratic
- private.account_exists
- auth_fixture.sql
- 2026-11-02-quadratic-remainders.md
- hosted_fixture.sql

## God Nodes (most connected - your core abstractions)
1. `DeterministicRNG` - 197 edges
2. `Step` - 181 edges
3. `Task` - 181 edges
4. `parse_math_input()` - 115 edges
5. `topics()` - 105 edges
6. `Drawn` - 104 edges
7. `ExpressionAnswer` - 91 edges
8. `MathNode` - 79 edges
9. `TaskGenerator` - 69 edges
10. `encode()` - 67 edges

## Surprising Connections (you probably didn't know these)
- `Automated: `scripts/e2e_local.py`` --references--> `database_unavailable()`  [INFERRED]
  docs/production/MVP_E2E_CHECK.md → backend/app/core/database.py
- `Canonical families and explicit unsupported cases` --references--> `PeriodicSetAnswer`  [INFERRED]
  docs/architecture/COMPUTATIONAL_ANSWERS.md → backend/app/engine/answers/computational.py
- ``POST /api/problems/{id}/report`` --references--> `category()`  [INFERRED]
  docs/api/README.md → backend/app/engine/generators/_elementary_common.py
- `Public input and bounded checking` --references--> `MathNode`  [INFERRED]
  docs/decisions/0008-generator-engine.md → backend/app/math_input/parser.py
- `Check budget` --references--> `test_family_check_fits_the_worker_limits()`  [INFERRED]
  docs/decisions/0005-multiple-integrals-and-derivatives.md → backend/tests/test_answer_check.py

## Import Cycles
- None detected.

## Communities (227 total, 77 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.10
Nodes (7): Completion criteria, Implementation workflow, Algebra30 coverage, Answer checking, Architecture and MVP analysis, Open decisions — resolve before dependent features, Security policy

### Community 1 - "package.json"
Cohesion: 0.11
Nodes (18): engines, node, name, overrides, minimatch, private, type, version (+10 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "api/worksheets.py"
Cohesion: 0.09
Nodes (24): area_topics(), capacity(), _mixed(), mixed_topics(), _not_found(), topics(), _check_group(), create_worksheet() (+16 more)

### Community 4 - "Must-have before production"
Cohesion: 0.12
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "test_answer_check.py"
Cohesion: 0.17
Nodes (19): answer_for(), native_record(), family(), _learner_text(), outcome(), record(), test_check_answer_end_to_end(), test_classification() (+11 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.18
Nodes (14): AuthCallback, AuthClient, AuthOptions, INITIAL, none, setup(), start(), stops (+6 more)

### Community 8 - "API contract"
Cohesion: 0.08
Nodes (22): _error(), internal_error(), invalid_request(), request_boundary(), _secure(), API contract, `GET /api/shares/{token}` and `GET /api/shares/code/{code}`, `GET /api/worksheets/{id}/pdf` (+14 more)

### Community 9 - "practice.ts"
Cohesion: 0.09
Nodes (69): authStore, client, accessToken(), accountRequest(), authorize(), base, cache(), capacity() (+61 more)

### Community 10 - "integrals.py"
Cohesion: 0.13
Nodes (22): _evaluate(), IntegralData, IntegralForm, BasicIntegrals, DefiniteBasicIntegrals, DefinitePartsIntegrals, DefiniteRationalIntegrals, DefiniteSubstitutionIntegrals (+14 more)

### Community 11 - "differentiation/single.py"
Cohesion: 0.12
Nodes (12): _chain(), _components(), _d(), DerivativeData, DerivativeStep, DerivativeTemplate, _evaluate(), _rewrite() (+4 more)

### Community 12 - "preview.py"
Cohesion: 0.22
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
Cohesion: 0.15
Nodes (22): install_error_handlers(), assert_rejected(), bearer(), claims(), client(), FakeJwksClient, jwk(), jwks() (+14 more)

### Community 19 - "ProblemCard.tsx"
Cohesion: 0.07
Nodes (52): ApiStatusNotice(), card(), AttemptStatus(), HistoryList(), HistoryListProps, HistoryRow(), RowSelection, SelectableRow() (+44 more)

### Community 20 - "test_answer_variables.py"
Cohesion: 0.14
Nodes (23): check(), _cylindrical(), _log_positive(), _log_real(), _partial_xy(), _polar(), problem(), symbols() (+15 more)

### Community 21 - "partial.py"
Cohesion: 0.13
Nodes (21): Built, _chain_template(), build(), _d(), declared(), _domain(), _evaluate(), _first() (+13 more)

### Community 25 - "test_math_worker.py"
Cohesion: 0.17
Nodes (15): MathWorkerError, _run_worker(), validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker() (+7 more)

### Community 29 - "typing"
Cohesion: 0.11
Nodes (8): BasicStep, build(), MethodStep, MethodTemplate, build(), build(), build(), build()

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 33 - "test_practice_api.py"
Cohesion: 0.08
Nodes (64): close_pool(), AnswerCheck, answer_of(), attempt(), client(), generate(), key(), pin_version() (+56 more)

### Community 50 - "Problem generation intent"
Cohesion: 0.17
Nodes (11): Definite and indefinite integrals, Difficulty, Generation model, Mathematical boundaries, Out of scope for this decision, Outcome, Pedagogically clean values, Practice modes (+3 more)

### Community 51 - "Educational content style intent"
Cohesion: 0.18
Nodes (10): Content in scope, Content outside this policy, Development-time enforcement, Educational content style intent, Out of scope for this decision, Outcome, Success criteria, Template catalogue (+2 more)

### Community 52 - "DeterministicRNG"
Cohesion: 0.06
Nodes (21): Polynomial, PartialFractionRational, DefiniteIntegral, generators(), Derivative, generators(), generators(), IndefiniteIntegral (+13 more)

### Community 53 - "Untracked generated practice (#34)"
Cohesion: 0.33
Nodes (6): Educational content, Mathematical checking and safety, Separate preview boundary, Supported generation, Untracked generated practice (#34), Verification and release

### Community 54 - "ADR-003: bounded real-valued integration answers"
Cohesion: 0.29
Nodes (7): Accepted input language, ADR-003: bounded real-valued integration answers, Amendment: structured probability/statistics answers (#200), Consequences, Fixed parser and worker limits, Integration constants and domains, Topic and difficulty matrix

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
Nodes (39): absBig(), analyseAnswer(), analyseStructuredAnswer(), ANSWER_VARIABLES, AnswerAnalysis, Fraction, FUNCTION_SET, gcd() (+31 more)

### Community 64 - "Oracle backend deploy"
Cohesion: 0.13
Nodes (14): Audit, Backups and restore, Before adding Supabase credentials (human only), Browser path, Capacity and worker isolation, CORS, Logs, On the VM (+6 more)

### Community 65 - "FormulaField.tsx"
Cohesion: 0.07
Nodes (38): AnswerVariable, AnswerInputProps, ADR-0005, answerLatex(), byName(), configureKeyboard(), FormulaField(), FormulaFieldProps (+30 more)

### Community 66 - "Reader"
Cohesion: 0.28
Nodes (4): exponentText(), join(), Reader, wrap()

### Community 67 - "HistoryPage.tsx"
Cohesion: 0.09
Nodes (24): AreaChips(), Chips(), revealNote(), ADR-0007, WorksheetOptions(), WorksheetOptionsProps, ProblemPage, DEFAULT_PAGE_OPTIONS (+16 more)

### Community 68 - "owned_records.py"
Cohesion: 0.09
Nodes (33): attempt_summaries(), AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), insert_problem(), last_attempt(), list_problems() (+25 more)

### Community 69 - "test_shares_api.py"
Cohesion: 0.23
Nodes (26): assert_unavailable(), client(), execute(), generate(), share(), start_copy(), test_concurrent_copy_retries_create_once_and_replay_after_revocation(), test_copy_does_not_inherit_sender_attempts_or_reveals() (+18 more)

### Community 70 - "Setup"
Cohesion: 0.08
Nodes (33): _cartesian(), _disk(), DoubleTemplate, DoubleVariant, _polar(), _same_region(), _statement(), _steps() (+25 more)

### Community 71 - "linear_algebra.py"
Cohesion: 0.05
Nodes (63): bounded(), _cell(), det(), fractions(), linear_form(), minor(), nonzero_rows(), pmatrix() (+55 more)

### Community 72 - "InputContract"
Cohesion: 0.14
Nodes (16): FormulaAnswer, contract_from(), test_categories_and_private_data_never_appear_in_public_contract(), test_domain_holes_before_simplification(), test_empty_singleton_all_reals_and_duplicate_points(), test_integer_parameter_and_ode_constants_are_distinct_from_coordinates(), test_malformed_and_injection_inputs(), test_old_grammars_do_not_gain_new_syntax() (+8 more)

### Community 73 - "types.ts"
Cohesion: 0.06
Nodes (36): splitComputationalParts(), ComputationalAnswerInput(), Props, enter, Harness(), tuple, entries(), LegacyStructuredAnswerInput() (+28 more)

### Community 74 - "App.tsx"
Cohesion: 0.09
Nodes (50): App(), handleDeleted(), handleLogOut(), handleSignIn(), route(), APP_ROUTES, NARROW_ROUTES, NotFoundPage() (+42 more)

### Community 75 - "test_engine_complex_numbers.py"
Cohesion: 0.06
Nodes (40): ComplexAnswer, _angle(), _base(), _cis(), _Complex, ComplexArgument, ComplexLinearEquation, ComplexProduct (+32 more)

### Community 76 - "Integration topic generators"
Cohesion: 0.10
Nodes (17): Basic-integral generator, Definite integrals, Delivery boundary, Derivatives (`derivatives-v1`, #97), Integral engine migration (#193), Integration topic generators, Mathematical and educational verification, Use and persistence boundary (+9 more)

### Community 77 - "WorksheetBuilder.tsx"
Cohesion: 0.08
Nodes (52): DifficultyScale(), DifficultyScaleProps, choices(), GroupRow(), Phase, Start, WorksheetBuilder(), WorksheetForm() (+44 more)

### Community 78 - "transaction"
Cohesion: 0.07
Nodes (39): practice_code(), _archived(), attempt(), AttemptBody, _check(), _decode_cursor(), delete_account(), DeleteBody (+31 more)

### Community 79 - "services/shares.py"
Cohesion: 0.09
Nodes (18): create(), revoke(), active_share(), copy_for_practice(), create_share(), lookup(), new_code(), new_token() (+10 more)

### Community 80 - "SyntaxProblem"
Cohesion: 0.31
Nodes (6): analyseComputationalAnswer(), constantFraction(), numberFraction(), Parser, SyntaxProblem, validateExponent()

### Community 81 - "test_engine_analysis_two.py"
Cohesion: 0.08
Nodes (24): AnalysisTwoData, AnalysisTwoForm, finish(), evaluate(), evaluate(), evaluate(), laplace_table(), evaluate() (+16 more)

### Community 82 - "topics/catalogue.py"
Cohesion: 0.07
Nodes (31): BinomialCoefficient, BinomialConstantTerm, BinomialExponent, CoefficientParams, ConstantTermParams, CubicRemainder, Divisibility, DivisibilityParams (+23 more)

### Community 84 - "e2e_local.py"
Cohesion: 0.16
Nodes (23): check(), combinations(), computational_code_flow(), correct_answer(), cross_user(), database_failure(), derivatives(), engine_answer() (+15 more)

### Community 85 - "pytest"
Cohesion: 0.21
Nodes (15): parse_math_input(), test_bisection_equation_has_no_supported_closed_form(), test_the_imaginary_unit_is_only_accepted_when_declared(), check(), test_global_budgets_and_unchanged_scalar_parser(), test_unselected_boolean_and_undefined_structured_components_are_invalid(), test_exact_boundaries_remain_accepted(), test_function_count_is_bounded() (+7 more)

### Community 86 - "[[path]].ts"
Cohesion: 0.36
Nodes (4): Context, onRequest(), FORWARDED_HEADERS, proxyToApi()

### Community 88 - "build_visual"
Cohesion: 0.19
Nodes (14): _loop(), across(), at(), evaluate(), native_data(), assert_definite(), assert_indefinite(), assert_means() (+6 more)

### Community 89 - "react"
Cohesion: 0.06
Nodes (36): harness, renderAt(), signedIn, signedOut, StatTile(), StatTileProps, TopicChips(), AuthSnapshot (+28 more)

### Community 90 - "shares.ts"
Cohesion: 0.12
Nodes (23): expiryDate(), ShareControls(), copy(), base, normalizeProblemCode(), sharedReturn(), takeSharedReturn(), APP_BASE (+15 more)

### Community 91 - "test_reports_api.py"
Cohesion: 0.20
Nodes (11): client(), generate(), stored(), test_invalid_reports_are_refused_without_echoing_them(), test_nobody_reports_someone_elses_or_a_missing_problem(), test_owner_reports_a_problem_with_only_the_approved_fields(), test_reports_are_rate_limited_per_user(), test_reports_go_with_the_account() (+3 more)

### Community 92 - "topics.ts"
Cohesion: 0.12
Nodes (20): AreaChipsProps, ChipOption, ChipsProps, TopicChipsProps, ADR-0005, fetchMock, generate(), publicProblem (+12 more)

### Community 93 - "Answer"
Cohesion: 0.16
Nodes (13): Answer, test_antiderivative_checks_all_domain_components(), test_antiderivative_constant_and_equivalence_rules(), test_derivative_rejects_constants_and_domain_holes(), test_expression_runs_under_worker_limits(), test_expression_uses_declared_variables(), test_number_compares_exact_rationals(), test_number_does_not_guess_about_symbolic_forms() (+5 more)

### Community 94 - "api/codes.py"
Cohesion: 0.04
Nodes (27): canonical(), invalid_code(), lookup(), _opened(), PracticeCodeBody, RateLimiter, _worker_unavailable(), report() (+19 more)

### Community 95 - "issue"
Cohesion: 0.06
Nodes (30): check(), issue(), public_replay(), record_variables(), answer_text(), test_all_algebra_levels_check_in_limited_worker(), test_all_algebra_levels_preserve_public_contracts_and_check_answers(), test_drawn_algebra_parameters_survive_json_and_reject_cross_family() (+22 more)

### Community 96 - "test_engine_code_opening.py"
Cohesion: 0.15
Nodes (8): open_problem_code(), client(), test_code_worker_failure_is_retryable_and_releases_the_shared_slot(), failed(), test_each_version_rebuilds_in_the_limited_worker(), test_every_golden_code_opens_the_exact_shipped_task(), test_invalid_unknown_and_wrong_checksum_codes_fail_before_symbolic_work(), test_public_code_lookup_projects_only_the_statement_without_symbolic_work()

### Community 97 - "test_worksheets_api.py"
Cohesion: 0.17
Nodes (33): client(), Compiled, compiled(), create(), generate(), key(), make_problem(), rows() (+25 more)

### Community 98 - "parse_answer_input"
Cohesion: 0.19
Nodes (14): parse_answer_input(), test_nested_budgets_are_shared_and_kind_comes_from_generator(), certify_canonical(), expression_source(), set_source(), source(), visit(), test_constant_identity_certificates_respect_finite_empty_and_flat_branch_domains() (+6 more)

### Community 99 - "DefiniteView.tsx"
Cohesion: 0.13
Nodes (30): Axes(), DefiniteView(), PAD, RULES, tex(), ADR-0006, IndefiniteView(), NAMES (+22 more)

### Community 100 - "Step"
Cohesion: 0.06
Nodes (44): DiagonalPower, _draw_points(), valid(), EigenParams, EigenvectorValue, _Generator, generators(), LargestEigenvalue (+36 more)

### Community 101 - "dataclasses"
Cohesion: 0.10
Nodes (15): algebraic_form(), _unit_as_x(), check_domain(), classify_expression(), components(), _defined_throughout(), differs(), evaluated_tree() (+7 more)

### Community 102 - "Canvas"
Cohesion: 0.15
Nodes (18): Canvas, _caption(), _curve(), definite(), _finite(), indefinite(), _n(), plot2d() (+10 more)

### Community 105 - "test_engine_elementary_api.py"
Cohesion: 0.08
Nodes (20): generators(), SharedProblem, graph(), _build(), build_visual(), solution_payload(), test_actual_elementary_targets_and_wrong_results_fit_original_worker_limits(), test_large_wrong_constant_never_constructs_an_exponential_root_in_the_worker() (+12 more)

### Community 106 - "math_worker.py"
Cohesion: 0.08
Nodes (25): bisect_exp(), exp_bounds(), generators(), rebuild(), input_variables(), _public(), _registry(), replay() (+17 more)

### Community 107 - "AnswerInput"
Cohesion: 0.19
Nodes (7): AnswerInput(), insert(), move(), replace(), AnswerPreview(), Harness(), render()

### Community 108 - "Routes"
Cohesion: 0.18
Nodes (11): visual(), Archived problems (#190), `GET /api/problems`, `GET /api/problems/{id}`, `GET /api/profile`, `GET /api/topics`, `POST /api/problems`, `POST /api/problems/{id}/attempts` (+3 more)

### Community 109 - "site.ts"
Cohesion: 0.10
Nodes (25): 1. Decisions only the owner can make, 2. Code changes, one PR after step 1, 3. External configuration (owner, in this order), 4. Verification on the domain, 5. Rollback, Launch runbook (#39), applyPageMeta(), crawlerFiles() (+17 more)

### Community 110 - "Outcome"
Cohesion: 0.06
Nodes (17): combine(), ComputationalAnswer, _domain(), _expression(), LimitAnswer, PeriodicSetAnswer, _piece(), _set() (+9 more)

### Community 111 - "supabase_google_test_login.py"
Cohesion: 0.12
Nodes (3): start_server(), collect_google_tokens(), handler_for()

### Community 112 - "ADR-005: multiple integrals and derivatives"
Cohesion: 0.13
Nodes (15): ADR-005: multiple integrals and derivatives, Amendment: practice areas (#144, 2026-10-26), Answers and variables, Areas and topics, Check budget, Consequences, Coordinate systems, Delivery (+7 more)

### Community 113 - "main.tsx"
Cohesion: 0.14
Nodes (9): analyticsAllowed(), BEACON_SRC, startWebAnalytics(), ErrorBoundary, root, @fontsource/geist, @fontsource/geist-mono, @fontsource/instrument-serif (+1 more)

### Community 114 - "parse_code"
Cohesion: 0.09
Nodes (22): build(), Catalogue, write(), format_code(), parse_code(), ProblemCode, Registry, visit() (+14 more)

### Community 115 - "Changelog"
Cohesion: 0.40
Nodes (4): 0.1.0 — MVP (2026-10-20), Changelog, Changes during MVP development, Unreleased

### Community 116 - "pathlib"
Cohesion: 0.29
Nodes (3): inspect(), main(), ContentTests

### Community 117 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, eslint, @eslint/js, jsdom, @types/katex, @types/react, @types/react-dom, @types/three (+4 more)

### Community 118 - "answerSyntax.test.ts"
Cohesion: 0.18
Nodes (10): COMPLEX, CYLINDRICAL, POLAR, REJECTED, SUPPORTED, ADR-0005, VARIABLE_REJECTED, VARIABLE_SUPPORTED (+2 more)

### Community 119 - "dependencies"
Cohesion: 0.20
Nodes (10): dependencies, @fontsource/geist, @fontsource/geist-mono, @fontsource/instrument-serif, katex, mathlive, react, react-dom (+2 more)

### Community 120 - "ConstantExpressionAnswer"
Cohesion: 0.14
Nodes (4): ConstantExpressionAnswer, FullRealExpressionAnswer, canonical_arctangents(), test_arctangent_reciprocal_identity_is_exact_on_the_positive_real_branch()

### Community 121 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, lint:content, test, typecheck

### Community 122 - "to_tree"
Cohesion: 0.14
Nodes (15): bounds_latex(), level(), SetupLike, _interval(), _numeric(), value(), parameter_points(), region2d_setup() (+7 more)

### Community 124 - "auth.py"
Cohesion: 0.09
Nodes (17): _auth_unavailable(), AuthUnavailableError, current_user(), get_token_verifier(), _invalid_token(), token_verifier(), TokenVerifier, _user_from_claims() (+9 more)

### Community 125 - "spec.py"
Cohesion: 0.17
Nodes (14): _bisect(), _changes_sign(), _component(), definite_data(), _distinct(), _f(), indefinite(), _poles() (+6 more)

### Community 126 - "region2d.test.tsx"
Cohesion: 0.16
Nodes (21): annulus, sinc, triangle, Region2dVisual(), ThreeView, compileRegion(), at(), boundary() (+13 more)

### Community 127 - "typing"
Cohesion: 0.04
Nodes (37): ExpressionAnswer, _Invalid, _NonReal, _Unsupported, AlgebraData, AlgebraForm, _evaluate(), AnalysisOneData (+29 more)

### Community 128 - "ExpressionAnswer"
Cohesion: 0.13
Nodes (18): generators(), PolynomialQuotient, QuadraticRemainder, QuadraticRemainderParams, RemainderParams, RemainderTheorem, test_polynomial_answers_are_checked_in_the_limited_worker(), test_polynomial_division_replays_and_checks_1000_draws() (+10 more)

### Community 129 - "topics/catalogue.py"
Cohesion: 0.07
Nodes (33): AlgebraParams, CombinationParams, DefiniteParams, DerivativeParams, PartialDerivativeParams, PartialDerivatives, SingleDerivativeParams, IndefiniteParams (+25 more)

### Community 130 - "DeterministicRNG"
Cohesion: 0.05
Nodes (22): PartialForm, DerivativeForm, IntegerRange, draw_entries(), draw_invertible(), _factorial(), SingleDerivatives, _draw_eigen() (+14 more)

### Community 132 - "test_preview.py"
Cohesion: 0.15
Nodes (14): MathCheckInconclusive, check_answer(), client(), headers(), test_check_failure_is_retryable_not_a_verdict(), fail(), test_fixed_demo_picks_rendered_data_without_symbolic_work(), test_generate_check_and_reveal_through_shared_worker() (+6 more)

### Community 133 - "dataclasses"
Cohesion: 0.09
Nodes (21): OrderedAnswer, RealSetAnswer, DomainFormulaAnswer, FourierAnswer, build_form(), Built, ElementaryParams, expression_set() (+13 more)

### Community 134 - "test_archive.py"
Cohesion: 0.06
Nodes (20): is_archived(), stored_solution(), legacy_code_is_never_run(), migrated(), Saved, owned(), test_an_archived_problem_opens_from_its_stored_rows(), test_an_archived_problem_prints_its_steps_without_a_graph() (+12 more)

### Community 135 - "test_engine_probability_foundation.py"
Cohesion: 0.17
Nodes (10): DensitySegment, ExponentialDistribution, NormalDistribution, PolynomialDensity, UniformDistribution, _cdf(), _density(), evaluate() (+2 more)

### Community 136 - "_probability_common.py"
Cohesion: 0.30
Nodes (13): FiniteSetAnswer, Built, finish(), finite(), joint(), joint_table(), ProbabilityParams, scalar() (+5 more)

### Community 137 - "registry"
Cohesion: 0.07
Nodes (20): registry(), metric(), statistics(), test_new_contract_replays_in_real_limited_child(), test_new_generator_module_registers_without_a_catalogue_edit(), rebuild(), snapshot(), test_dependency_graph_and_topic_views_are_valid() (+12 more)

### Community 138 - "MathNode"
Cohesion: 0.11
Nodes (21): _parse(), parse_computational(), _real_set(), split_parts(), parse_logic(), expression(), node(), _constant_fraction() (+13 more)

### Community 139 - "test_worksheet_tex.py"
Cohesion: 0.08
Nodes (45): compile_pdf(), escape_text(), _log_tail(), _pdflatex(), PrintedGroup, PrintedProblem, PrintedStep, _problem() (+37 more)

### Community 140 - "engine/practice.py"
Cohesion: 0.12
Nodes (14): load(), lookup(), pool(), input_contract(), input_kind(), input_projection(), is_engine_record(), levels() (+6 more)

### Community 141 - "test_engine_slice.py"
Cohesion: 0.09
Nodes (23): AntiderivativeAnswer, DerivativeAnswer, _bounded(), _fraction(), NumberAnswer, test_number_rejects_wrong_undefined_and_nonreal_values(), test_symbolic_constant_and_integer_expected_values(), catalogue() (+15 more)

### Community 142 - "FiniteDistribution"
Cohesion: 0.12
Nodes (12): FiniteDistribution, JointDistribution, test_finite_distribution_and_pushforward_by_independent_enumeration(), test_joint_marginals_conditionals_covariance_independence(), test_polynomial_density_against_symbolic_integration(), Approved release, Delivery and verification after approval, Distribution block design (+4 more)

### Community 143 - "Probability and Statistics curriculum (#200)"
Cohesion: 0.11
Nodes (12): HANDOFF — Analysis I (#145), HANDOFF — Analysis II (#146), HANDOFF — Probability and Statistics (#200), implementation checkpoint, Project status, Analysis I curriculum (#145), Answers, domains and steps, Persistence and verification, Analysis II curriculum (#146) (+4 more)

### Community 144 - "test_supabase_hosted.py"
Cohesion: 0.12
Nodes (12): check_private(), CheckFailure, denied(), main(), require(), rows(), DenialChecks, SingleUserChecks (+4 more)

### Community 145 - "ADR-008: composable generator engine"
Cohesion: 0.25
Nodes (8): ADR-008: composable generator engine, Compatible computational extensions (#234, 2026-11-04), Context and result, Curriculum, visuals and archive, Permanent problem codes, Public input and bounded checking, Verification and remaining work, Verified release catalogue

### Community 146 - "Computational contracts and Graphify checkpoint"
Cohesion: 0.33
Nodes (5): Computational contracts and Graphify checkpoint, Graphify, explicitly delegated by the owner, Observed verification, Review, recovery and next action, Scope and result

### Community 147 - "services/worksheets.py"
Cohesion: 0.10
Nodes (20): catalogue_records(), get_worksheet(), insert_items(), insert_worksheet(), owned_problems(), OwnedProblem, Picker, print_items() (+12 more)

### Community 148 - "MVP end-to-end check (#13)"
Cohesion: 0.50
Nodes (3): Automated: `scripts/e2e_local.py`, Manual: deployed site, MVP end-to-end check (#13)

### Community 149 - "geometry.ts"
Cohesion: 0.17
Nodes (15): Edge, EDGES, axisOrigin(), AxisTick, axisTicks(), Mesh3D, Scene3D, ADR-0006 (+7 more)

### Community 150 - "createAuthStore"
Cohesion: 0.70
Nodes (5): createAuthStore(), accept(), signIn(), signOut(), start()

### Community 151 - "test_engine_probability.py"
Cohesion: 0.09
Nodes (21): BooleanAnswer, IntervalAnswer, _Invalid, RealScalarAnswer, _Unknown, BooleanProbability, _build(), generators() (+13 more)

### Community 153 - "mathEditor.ts"
Cohesion: 0.12
Nodes (17): FUNCTIONS, BARS, COMMAND_FUNCTIONS, CONSTANTS, INVERSE, Item, latexToAnswer(), needsTimes() (+9 more)

### Community 154 - "sympy"
Cohesion: 0.09
Nodes (36): test_radical_exercises_check_equivalent_answers_and_replay(), test_radical_exercises_use_the_limited_worker(), test_integral_curriculum_snapshot(), test_multiple_curriculum_snapshot_and_independent_orders(), test_partial_curriculum_snapshot(), test_scalar_curriculum_snapshots(), test_single_derivative_curriculum_snapshot(), affine_preimage() (+28 more)

### Community 155 - "test_engine_analysis.py"
Cohesion: 0.10
Nodes (19): AnalysisData, AnalysisForm, _evaluate(), analysis_generators(), AnalysisGenerator, AnalysisParams, DifferentialEquations, generators() (+11 more)

### Community 156 - "subprocess"
Cohesion: 0.17
Nodes (10): test_educational_catalogue_and_checker(), test_answer_types_do_not_import_legacy_generators(), test_number_can_be_imported_without_sympy(), test_combination_generation_and_check_do_not_load_sympy(), main(), free_port(), main(), psql() (+2 more)

### Community 157 - "test_engine_computational_api.py"
Cohesion: 0.09
Nodes (19): StoredCell, StoredModel, StoredProblem, StoredStep, _cell(), _historical_views(), OpenedCode, Issued (+11 more)

### Community 158 - "Generator Refactor MVP"
Cohesion: 0.29
Nodes (7): 10. Re-evaluate the generator architecture with GrillMe (#172), Generator Refactor MVP, Goal: Complete the generator refactor, GrillMe gate, Main goal, MVP done when, Rules for every issue

### Community 159 - "ADR-006: interactive visualizations in solutions"
Cohesion: 0.29
Nodes (6): ADR-006: interactive visualizations in solutions, Fallback, mobile and accessibility, Out of scope, Testing, What each kind shows, Where visuals appear

### Community 160 - "_probability_inference.py"
Cohesion: 0.17
Nodes (11): mean_interval(), mean_statistic(), median(), PairedSample, reject(), Sample, _differences(), evaluate() (+3 more)

### Community 161 - "Analysis exercise-sheet generator expansion"
Cohesion: 0.12
Nodes (14): Accepted staging and computational contracts, Analysis exercise-sheet generator expansion, Deliverable, Evidence required before delivery, Existing capability versus source coverage, Reference solutions and visuals are part of generation, Serial delivery, Source mathematics and errata (+6 more)

### Community 163 - "spec.ts"
Cohesion: 0.17
Nodes (13): Tree, DefiniteSpec, finite(), IndefiniteSpec, Interval, Plot2dSpec, POINT_KINDS, PointKind (+5 more)

### Community 164 - "PracticeLoop agent rules"
Cohesion: 0.22
Nodes (7): After a merge, Before starting work, Collaboration rules, GitHub Issue names, Graphify, PracticeLoop agent rules, Claude Code

### Community 165 - "ReportProblem.tsx"
Cohesion: 0.19
Nodes (11): Launch blockers (#39), Production checklist (#38), Running the checks, LABELS, ReportProblem(), submit(), button(), openForm() (+3 more)

### Community 166 - "ADR-007: printable PDF worksheets"
Cohesion: 0.14
Nodes (13): ADR-007: printable PDF worksheets, Amendment to ADR-004 counters, API, Data, Delivery, `GET /api/worksheets/{id}/pdf`, Implementation notes (#116, 2026-10-22), Limits and errors (+5 more)

### Community 167 - "expression.ts"
Cohesion: 0.20
Nodes (12): compile(), build(), Compiled, CONSTANTS, Env, evaluate(), ExpressionError, HEADS (+4 more)

### Community 168 - "WorksheetBuilder.test.tsx"
Cohesion: 0.22
Nodes (7): `POST /api/worksheets`, button(), buttons(), catalogue, groups(), made, shownLevels()

### Community 169 - "engine_fixtures.py"
Cohesion: 0.09
Nodes (25): MultipleForm, DoubleIntegrals, generators(), TripleIntegrals, multiple_record(), native_params(), test_matrix_is_complete_and_reuses_existing_partial_and_multiple_integrals(), test_typed_multiple_parameters_replay_and_reject_wrong_dimensions() (+17 more)

### Community 170 - "answer_text"
Cohesion: 0.17
Nodes (15): primitive(), Analysis source-family contracts (#233), Existing boundary and extension plan for #234, Family gap matrix, Source components and independent mathematical cases, Visual and replay contract, Canonical families and explicit unsupported cases, Computational answer and reference-visual infrastructure (#234) (+7 more)

### Community 171 - "test_engine_catalogue.py"
Cohesion: 0.20
Nodes (7): test_a_new_entry_is_built_without_a_second_registration(), test_catalogue_build_failure_stops_release_before_activation(), test_failed_build_leaves_the_previous_artifact_untouched(), test_incomplete_or_incompatible_catalogue_is_refused(), test_missing_pool_fails_closed_instead_of_generating(), test_picks_do_not_expose_mutable_cached_data(), test_unfillable_cell_aborts_with_a_bounded_candidate_count()

### Community 172 - "Account completion (#35)"
Cohesion: 0.40
Nodes (5): Account completion (#35), Anonymous demo and privacy, Deployment and retention gates, Hard deletion and expired identity, Learning records and metrics

### Community 173 - "test_health.py"
Cohesion: 0.16
Nodes (5): allowed_origins(), _known_origin(), test_allowed_origins_reads_environment(), test_allowed_origins_refuse_plain_http_outside_local_dev(), test_api_responses_carry_security_headers()

### Community 174 - "Saved practice UI (#11/#12)"
Cohesion: 0.40
Nodes (5): Durable history and profile, Public/private boundary, Saved practice UI (#11/#12), Verification, Writes, retries and stale responses

### Community 175 - "plot2d.py"
Cohesion: 0.16
Nodes (5): DiagramModel, PlotDiagram, PlotPath, PlotPoint, test_thousand_inverse_diagrams_preserve_function_branch_and_exact_reflection()

### Community 176 - "202610150001_initial_schema.sql"
Cohesion: 0.29
Nodes (8): attempts_problem_idx, attempts_user_created_idx, private.problem_solutions, problems_user_created_idx, public.attempts, public.problems, public.profiles, public.topics

### Community 177 - "math.ts"
Cohesion: 0.13
Nodes (9): nice_ticks(), _evaluate(), _log(), _pow(), _sqrt(), to_tree(), UnsupportedExpression, test_expression_trees_use_only_the_listed_heads() (+1 more)

### Community 179 - "test_engine_probability_foundation.py"
Cohesion: 0.18
Nodes (7): StandardDistribution, test_new_grammars_reject_invalid_input(), test_shared_structured_syntax_corpus(), test_standard_distribution_normalization_and_moments(), test_strict_bounded_forms_reject_invalid_parameters(), test_structured_answers(), test_supplied_rounded_reference_tables_have_certified_precision()

### Community 181 - "202610220001_worksheets.sql"
Cohesion: 0.33
Nodes (5): problems_user_worksheet_created_idx, public.worksheet_items, public.worksheets, worksheet_items_problem_idx, worksheets_user_created_idx

### Community 183 - "Solid3dVisual.tsx"
Cohesion: 0.36
Nodes (4): Solid3dVisual(), ThreeView, solidScene(), VisualBoundary

### Community 186 - "health.ts"
Cohesion: 0.40
Nodes (3): API_BASE_URL, ApiHealth, checkApiHealth()

### Community 187 - "Elementary functions and logic delivery (#235)"
Cohesion: 0.33
Nodes (5): Coordination and scope, Elementary functions and logic delivery (#235), Implementation, Release gates, Verification

### Community 188 - "private.problem_reports"
Cohesion: 0.47
Nodes (3): private.problem_reports, problem_reports_created_idx, problem_reports_problem_idx

### Community 190 - "check_answer"
Cohesion: 0.12
Nodes (11): check_answer(), test_adversarial_answers_terminate_within_limits(), test_inconclusive_is_a_service_error(), test_invalid_syntax_never_starts_a_worker(), test_original_domain_hole_is_invalid_before_simplification(), test_oversized_answer_is_request_validation(), test_unreplayable_record_is_a_server_fault(), test_worker_output_outside_the_protocol_is_a_service_error() (+3 more)

### Community 191 - "test_engine_elementary_logic.py"
Cohesion: 0.13
Nodes (13): CategoryAnswer, LogicAnswer, render(), truth(), category(), evaluate(), wrong(), parse() (+5 more)

### Community 192 - "Optional Graphify tooling"
Cohesion: 0.40
Nodes (4): Optional Graphify tooling, Query and refresh, Setup on Windows, Verification and limits

### Community 193 - "Analysis source intake handoff"
Cohesion: 0.40
Nodes (4): Analysis source intake handoff, Recovery, review and next action, Scope and completed work, Verification and practical limits

## Knowledge Gaps
- **36 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `@types/three` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1485 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **77 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `vitest` connect `types.ts` to `package.json`, `auth.test.ts`, `ProblemCard.tsx`, `geometry.ts`, `mathEditor.ts`, `ReportProblem.tsx`, `expression.ts`, `WorksheetBuilder.test.tsx`, `math.ts`, `health.ts`, `FormulaField.tsx`, `HistoryPage.tsx`, `App.tsx`, `WorksheetBuilder.tsx`, `[[path]].ts`, `react`, `shares.ts`, `topics.ts`, `AnswerInput`, `site.ts`, `main.tsx`, `answerSyntax.test.ts`, `region2d.test.tsx`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 80 inferred relationships involving `DeterministicRNG` (e.g. with `PartialForm` and `DerivativeForm`) actually correct?**
  _`DeterministicRNG` has 80 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `README.md` be split into smaller, more focused modules?**
  _Cohesion score 0.10114942528735632 - nodes in this community are weakly interconnected._
- **Why does `react` connect `react` to `FormulaField.tsx`, `package.json`, `HistoryPage.tsx`, `DefiniteView.tsx`, `ReportProblem.tsx`, `WorksheetBuilder.test.tsx`, `types.ts`, `App.tsx`, `AnswerInput`, `practice.ts`, `WorksheetBuilder.tsx`, `main.tsx`, `ProblemCard.tsx`, `geometry.ts`, `Solid3dVisual.tsx`, `shares.ts`, `region2d.test.tsx`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 84 inferred relationships involving `Step` (e.g. with `AlgebraData` and `_evaluate()`) actually correct?**
  _`Step` has 84 INFERRED edges - model-reasoned connections that need verification._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._