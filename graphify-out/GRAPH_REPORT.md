# Graph Report - PracticeLoop  (2026-11-04)

## Corpus Check
- 467 files · ~412,452 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: (none) 10, .css 6, .toml 3)

## Summary
- 4714 nodes · 14920 edges · 231 communities (156 shown, 75 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1292 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `58e25f84`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- README.md
- package.json
- PracticeLoop — MVP Specification
- api/worksheets.py
- Must-have before production
- check_answer
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
- test_shares_api.py
- topics.ts
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
- Reader
- tokens.test.ts
- owned_records.py
- attempt
- Setup
- linear_algebra.py
- InputContract
- types.ts
- App.tsx
- test_engine_complex_numbers.py
- Issue #3 delivery and first-project procedure
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
- FormulaField.test.tsx
- reports.py
- main.py
- issue
- test_engine_code_opening.py
- test_worksheets_api.py
- test_engine_elementary_api.py
- DefiniteView.tsx
- Step
- dataclasses
- Canvas
- issue-11-handoff.md
- issue-12-handoff.md
- test_worksheet_graphs.py
- test_engine_analysis_one.py
- parse_code
- generators/probability.py
- site.ts
- Outcome
- supabase_google_test_login.py
- ADR-005: multiple integrals and derivatives
- main.tsx
- Registry
- Changelog
- pathlib
- devDependencies
- answerSyntax.test.ts
- dependencies
- ExpressionAnswer
- scripts
- to_tree
- audit.sh
- math_worker.py
- spec.py
- region2d.test.tsx
- TaskGenerator
- ExpressionAnswer
- topics/catalogue.py
- DeterministicRNG
- test_engine_computational_api.py
- test_preview.py
- dataclasses
- Saved
- test_engine_probability_foundation.py
- _probability_common.py
- registry
- MathNode
- test_worksheet_tex.py
- engine/practice.py
- pytest
- FiniteDistribution
- Probability and Statistics curriculum (#200)
- test_supabase_hosted.py
- encode
- Computational contracts and Graphify checkpoint
- test_worksheets.py
- MVP end-to-end check (#13)
- geometry.ts
- createAuthStore
- test_engine_probability.py
- test_engine_curriculum.py
- mathEditor.ts
- sympy
- generators/analysis.py
- subprocess
- test_engine_computational_api.py
- pydantic
- StubClient
- _probability_inference.py
- Analysis exercise-sheet generator expansion
- test_engine_analysis.py
- spec.ts
- PracticeLoop agent rules
- ReportProblem.tsx
- ADR-007: printable PDF worksheets
- expression.ts
- WorksheetBuilder.test.tsx
- test_solid3d.py
- answer_text
- test_engine_catalogue.py
- Account completion (#35)
- test_health.py
- Saved practice UI (#11/#12)
- plot2d.py
- 202610150001_initial_schema.sql
- math.ts
- test_region2d.py
- test_engine_probability_foundation.py
- database.py
- 202610220001_worksheets.sql
- learning_stats.py
- solid3d.test.tsx
- input_projection
- to_tree
- health.ts
- Elementary functions and logic delivery (#235)
- private.problem_reports
- Launch runbook (#39)
- test_answers_are_parsed_with_the_record_variables
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

## Communities (231 total, 75 thin omitted)

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
Nodes (24): create_worksheet(), download_pdf(), _from_history(), _generate(), GroupBody, label(), _limit(), _prepare() (+16 more)

### Community 4 - "Must-have before production"
Cohesion: 0.12
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "check_answer"
Cohesion: 0.10
Nodes (27): check_answer(), MathCheckInconclusive, answer_for(), native_record(), family(), _learner_text(), outcome(), record() (+19 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.16
Nodes (16): AuthCallback, AuthClient, AuthOptions, AuthSnapshot, INITIAL, none, setup(), start() (+8 more)

### Community 8 - "API contract"
Cohesion: 0.07
Nodes (29): visual(), API contract, Archived problems (#190), `GET /api/problems`, `GET /api/problems/{id}`, `GET /api/profile`, `GET /api/shares/{token}` and `GET /api/shares/code/{code}`, `GET /api/topics` (+21 more)

### Community 9 - "practice.ts"
Cohesion: 0.07
Nodes (76): WorksheetBuilder(), authStore, client, accessToken(), accountRequest(), authorize(), base, cache() (+68 more)

### Community 10 - "integrals.py"
Cohesion: 0.10
Nodes (30): _evaluate(), IntegralData, IntegralForm, BasicIntegrals, DefiniteBasicIntegrals, DefinitePartsIntegrals, DefiniteRationalIntegrals, DefiniteSubstitutionIntegrals (+22 more)

### Community 11 - "differentiation/single.py"
Cohesion: 0.10
Nodes (13): _chain(), _components(), _d(), DerivativeData, DerivativeForm, DerivativeStep, DerivativeTemplate, _evaluate() (+5 more)

### Community 12 - "preview.py"
Cohesion: 0.18
Nodes (12): answer(), attempt(), Attempt, generate(), Generate, _problem(), Session, _session() (+4 more)

### Community 13 - "Prompt for Claude Code: implement the PracticeLoop frontend design"
Cohesion: 0.29
Nodes (6): Definition of done, Goal, Prompt for Claude Code: implement the PracticeLoop frontend design, Rules, Source of truth, What to build

### Community 14 - "pull_request_template.md"
Cohesion: 0.40
Nodes (4): How it was tested, Risks, What changed, Why

### Community 15 - "system/README.md"
Cohesion: 0.33
Nodes (5): Content fundamentals, Directions, Iconography, Using the components, Visual foundations

### Community 18 - "test_shares_api.py"
Cohesion: 0.07
Nodes (54): _auth_unavailable(), current_user(), get_token_verifier(), token_verifier(), TokenVerifier, install_error_handlers(), assert_rejected(), bearer() (+46 more)

### Community 19 - "topics.ts"
Cohesion: 0.06
Nodes (48): ApiStatusNotice(), DifficultyScale(), DifficultyScaleProps, AttemptStatus(), HistoryList(), HistoryListProps, HistoryRow(), RowSelection (+40 more)

### Community 20 - "test_answer_variables.py"
Cohesion: 0.12
Nodes (24): declared_variables(), check(), _cylindrical(), _log_positive(), _log_real(), _partial_xy(), _polar(), problem() (+16 more)

### Community 21 - "partial.py"
Cohesion: 0.13
Nodes (21): Built, _chain_template(), build(), _d(), declared(), _domain(), _evaluate(), _first() (+13 more)

### Community 25 - "test_math_worker.py"
Cohesion: 0.19
Nodes (13): validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker(), test_limits_are_active_only_in_child(), test_memory_limit_stops_pathological_allocation() (+5 more)

### Community 29 - "typing"
Cohesion: 0.09
Nodes (10): BasicStep, build(), MethodStep, MethodTemplate, build(), build(), build(), build() (+2 more)

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
Cohesion: 0.05
Nodes (24): IntegerRange, Polynomial, PartialFractionRational, Derivative, generators(), generators(), IndefiniteIntegral, IndefiniteParams (+16 more)

### Community 53 - "Untracked generated practice (#34)"
Cohesion: 0.33
Nodes (6): Educational content, Mathematical checking and safety, Separate preview boundary, Supported generation, Untracked generated practice (#34), Verification and release

### Community 54 - "Integration topic generators"
Cohesion: 0.11
Nodes (15): Basic-integral generator, Definite integrals, Delivery boundary, Derivatives (`derivatives-v1`, #97), Integration topic generators, Mathematical and educational verification, Partial derivatives (`partial-v1`, #101), Use and persistence boundary (+7 more)

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
Cohesion: 0.08
Nodes (33): AnswerInput(), insert(), move(), replace(), answerLatex(), byName(), configureKeyboard(), FormulaField() (+25 more)

### Community 66 - "Reader"
Cohesion: 0.28
Nodes (4): exponentText(), join(), Reader, wrap()

### Community 68 - "owned_records.py"
Cohesion: 0.10
Nodes (29): attempt_summaries(), AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), insert_problem(), last_attempt(), list_problems() (+21 more)

### Community 69 - "attempt"
Cohesion: 0.13
Nodes (22): invalid_code(), _opened(), practice_code(), PracticeCodeBody, attempt(), _check(), generate(), _idempotency_key() (+14 more)

### Community 70 - "Setup"
Cohesion: 0.07
Nodes (34): _cartesian(), _disk(), DoubleTemplate, DoubleVariant, _polar(), _same_region(), _statement(), _steps() (+26 more)

### Community 71 - "linear_algebra.py"
Cohesion: 0.04
Nodes (68): bounded(), _cell(), det(), _factorial(), fractions(), linear_form(), minor(), nonzero_rows() (+60 more)

### Community 72 - "InputContract"
Cohesion: 0.09
Nodes (23): CategoryAnswer, FormulaAnswer, RealSetAnswer, describe(), InputContract, ContractExample, generators(), contract_from() (+15 more)

### Community 73 - "types.ts"
Cohesion: 0.04
Nodes (77): AnswerVariable, AnswerInputProps, AnswerPreview(), ADR-0005, card(), ComputationalAnswerInput(), Props, enter (+69 more)

### Community 74 - "App.tsx"
Cohesion: 0.10
Nodes (40): route(), APP_ROUTES, NARROW_ROUTES, NotFoundPage(), SITE, APP_ROUTES, AppNav(), AppNavProps (+32 more)

### Community 75 - "test_engine_complex_numbers.py"
Cohesion: 0.06
Nodes (40): ComplexAnswer, _angle(), _base(), _cis(), _Complex, ComplexArgument, ComplexLinearEquation, ComplexProduct (+32 more)

### Community 76 - "Issue #3 delivery and first-project procedure"
Cohesion: 0.20
Nodes (9): Backup and rollback, Current verification status, Database preparation, Hosted Auth and PostgREST verification (human only), Human-only Google test helper (no token copying), Human provisioning, without sharing credentials, Issue #3 delivery and first-project procedure, Migration workflow (+1 more)

### Community 77 - "WorksheetBuilder.tsx"
Cohesion: 0.07
Nodes (61): choices(), GroupRow(), Phase, Start, WorksheetForm(), addGroup(), generate(), render() (+53 more)

### Community 78 - "transaction"
Cohesion: 0.08
Nodes (30): area_topics(), AttemptBody, capacity(), _decode_cursor(), delete_account(), DeleteBody, _encode_cursor(), _feedback() (+22 more)

### Community 79 - "services/shares.py"
Cohesion: 0.08
Nodes (25): _public_share(), by_code(), by_token(), create(), _invalid_share(), PracticeShareBody, revoke(), _shared() (+17 more)

### Community 80 - "SyntaxProblem"
Cohesion: 0.29
Nodes (7): analyseComputationalAnswer(), constantFraction(), numberFraction(), Parser, splitComputationalParts(), SyntaxProblem, validateExponent()

### Community 81 - "test_engine_analysis_two.py"
Cohesion: 0.11
Nodes (21): AnalysisTwoData, AnalysisTwoForm, finish(), canonical_arctangents(), evaluate(), evaluate(), evaluate(), laplace_table() (+13 more)

### Community 82 - "topics/catalogue.py"
Cohesion: 0.07
Nodes (32): BinomialCoefficient, BinomialConstantTerm, BinomialExponent, CoefficientParams, ConstantTermParams, CubicRemainder, Divisibility, DivisibilityParams (+24 more)

### Community 84 - "e2e_local.py"
Cohesion: 0.15
Nodes (22): check(), computational_code_flow(), correct_answer(), cross_user(), database_failure(), derivatives(), engine_answer(), full_flow() (+14 more)

### Community 85 - "pytest"
Cohesion: 0.11
Nodes (22): parse_math_input(), test_domain_check_avoids_repeating_sum_domains_and_preserves_holes(), test_radical_exercises_check_equivalent_answers_and_replay(), test_radical_exercises_use_the_limited_worker(), test_radical_parameters_reject_noncanonical_radicands(), test_partial_fraction_grammar_declares_only_x_and_checks_equivalent_rational_form(), test_arctangent_reciprocal_identity_is_exact_on_the_positive_real_branch(), test_the_imaginary_unit_is_only_accepted_when_declared() (+14 more)

### Community 86 - "[[path]].ts"
Cohesion: 0.36
Nodes (4): Context, onRequest(), FORWARDED_HEADERS, proxyToApi()

### Community 88 - "build_visual"
Cohesion: 0.16
Nodes (15): build_visual(), solution_payload(), native_data(), assert_definite(), assert_indefinite(), assert_means(), heads(), single_records() (+7 more)

### Community 89 - "react"
Cohesion: 0.09
Nodes (16): harness, renderAt(), signedIn, signedOut, Harness(), render(), algebraSections, analysisSections (+8 more)

### Community 90 - "shares.ts"
Cohesion: 0.08
Nodes (42): App(), handleDeleted(), handleLogOut(), handleSignIn(), topicReturn(), DifficultyDots(), expiryDate(), ShareControls() (+34 more)

### Community 91 - "test_reports_api.py"
Cohesion: 0.23
Nodes (11): client(), generate(), stored(), test_invalid_reports_are_refused_without_echoing_them(), test_nobody_reports_someone_elses_or_a_missing_problem(), test_owner_reports_a_problem_with_only_the_approved_fields(), test_reports_are_rate_limited_per_user(), test_reports_go_with_the_account() (+3 more)

### Community 92 - "FormulaField.test.tsx"
Cohesion: 0.15
Nodes (6): changes, Fake, FakeMathfield, Harness(), Layout, render()

### Community 93 - "reports.py"
Cohesion: 0.15
Nodes (3): RateLimiter, report(), ReportBody

### Community 94 - "main.py"
Cohesion: 0.07
Nodes (15): _archived(), _api_error_response(), ApiError, _error(), health(), internal_error(), invalid_request(), lifespan() (+7 more)

### Community 95 - "issue"
Cohesion: 0.04
Nodes (35): check(), is_engine_record(), issue(), levels(), is_archived(), stored_solution(), record_variables(), test_record_variables_are_read_and_validated() (+27 more)

### Community 96 - "test_engine_code_opening.py"
Cohesion: 0.11
Nodes (11): OpenedCode, statement_latex(), _text(), open_problem_code(), client(), test_code_worker_failure_is_retryable_and_releases_the_shared_slot(), failed(), test_each_version_rebuilds_in_the_limited_worker() (+3 more)

### Community 97 - "test_worksheets_api.py"
Cohesion: 0.17
Nodes (33): client(), Compiled, compiled(), create(), generate(), key(), make_problem(), rows() (+25 more)

### Community 98 - "test_engine_elementary_api.py"
Cohesion: 0.08
Nodes (23): PeriodicSetAnswer, DomainFormulaAnswer, generators(), parse_answer_input(), test_actual_elementary_targets_and_wrong_results_fit_original_worker_limits(), test_public_descriptors_and_pooled_visuals_do_not_rebuild_symbolic_tasks(), test_saved_generation_reopen_history_owner_copy_reveal_and_share_are_consistent(), checked() (+15 more)

### Community 99 - "DefiniteView.tsx"
Cohesion: 0.14
Nodes (30): Axes(), DefiniteView(), PAD, RULES, tex(), ADR-0006, IndefiniteView(), NAMES (+22 more)

### Community 100 - "Step"
Cohesion: 0.07
Nodes (42): DiagonalPower, _draw_points(), valid(), EigenParams, EigenvectorValue, _Generator, generators(), LargestEigenvalue (+34 more)

### Community 101 - "dataclasses"
Cohesion: 0.10
Nodes (15): algebraic_form(), _unit_as_x(), check_domain(), classify_expression(), components(), _defined_throughout(), differs(), evaluated_tree() (+7 more)

### Community 102 - "Canvas"
Cohesion: 0.11
Nodes (25): Canvas, _caption(), _curve(), definite(), _finite(), indefinite(), _n(), nice_ticks() (+17 more)

### Community 105 - "test_worksheet_graphs.py"
Cohesion: 0.24
Nodes (7): graph(), first_records(), literals(), test_a_graph_is_a_picture_of_pdf_operators_and_math_labels(), test_every_served_visual_kind_has_a_drawer(), test_no_visual_means_no_graph(), test_ticks_are_round_numbers_inside_the_window()

### Community 106 - "test_engine_analysis_one.py"
Cohesion: 0.15
Nodes (13): AnalysisOneData, AnalysisOneForm, bisect_exp(), evaluate(), exp_bounds(), generators(), test_bisection_equation_has_no_supported_closed_form(), test_bisection_has_exact_sign_certificates_error_bound_and_unique_root() (+5 more)

### Community 107 - "parse_code"
Cohesion: 0.21
Nodes (11): canonical(), format_code(), parse_code(), ProblemCode, registry(), test_a_generator_writes_the_same_code_without_a_registry(), test_codes_round_trip_and_normalise_separators(), test_every_single_digit_change_is_rejected() (+3 more)

### Community 108 - "generators/probability.py"
Cohesion: 0.15
Nodes (8): _Invalid, RealScalarAnswer, _Unknown, BooleanProbability, _build(), IntervalProbability, Probability, SetProbability

### Community 109 - "site.ts"
Cohesion: 0.12
Nodes (20): 2. Code changes, one PR after step 1, applyPageMeta(), crawlerFiles(), isSharedPath(), NOINDEX_PATHS, NOT_FOUND, page(), pageMeta (+12 more)

### Community 110 - "Outcome"
Cohesion: 0.08
Nodes (11): combine(), ComputationalAnswer, _domain(), _expression(), LimitAnswer, _piece(), _set(), _validate_set() (+3 more)

### Community 111 - "supabase_google_test_login.py"
Cohesion: 0.12
Nodes (3): collect_google_tokens(), handler_for(), CallbackChecks

### Community 112 - "ADR-005: multiple integrals and derivatives"
Cohesion: 0.13
Nodes (15): ADR-005: multiple integrals and derivatives, Amendment: practice areas (#144, 2026-10-26), Answers and variables, Areas and topics, Check budget, Consequences, Coordinate systems, Delivery (+7 more)

### Community 113 - "main.tsx"
Cohesion: 0.15
Nodes (9): analyticsAllowed(), BEACON_SRC, startWebAnalytics(), ErrorBoundary, root, @fontsource/geist, @fontsource/geist-mono, @fontsource/instrument-serif (+1 more)

### Community 114 - "Registry"
Cohesion: 0.14
Nodes (9): Registry, visit(), extension(), test_dependency_graph_accepts_shared_dependency_and_rejects_missing_and_cycles(), test_generator_consumer_and_parameter_validation(), test_registry_rejects_duplicate_unknown_and_invalid_metadata(), TinyAnswer, TinyGenerator (+1 more)

### Community 115 - "Changelog"
Cohesion: 0.40
Nodes (4): 0.1.0 — MVP (2026-10-20), Changelog, Changes during MVP development, Unreleased

### Community 116 - "pathlib"
Cohesion: 0.27
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

### Community 120 - "ExpressionAnswer"
Cohesion: 0.09
Nodes (12): ExpressionAnswer, ConstantExpressionAnswer, FullRealExpressionAnswer, AnalysisOne, AnalysisOneParams, SymbolicAnalysisOne, AnalysisTwo, AnalysisTwoParams (+4 more)

### Community 121 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, lint:content, test, typecheck

### Community 122 - "to_tree"
Cohesion: 0.13
Nodes (15): bounds_latex(), level(), SetupLike, _interval(), _numeric(), value(), parameter_points(), region2d_setup() (+7 more)

### Community 124 - "math_worker.py"
Cohesion: 0.06
Nodes (17): AuthUnavailableError, _invalid_token(), _user_from_claims(), VerifiedUser, _apply_limits(), _child(), _code_child(), test_delete_requires_exact_confirmation_and_uses_only_verified_identity() (+9 more)

### Community 125 - "spec.py"
Cohesion: 0.15
Nodes (14): _bisect(), _changes_sign(), _component(), definite_data(), _distinct(), _f(), indefinite(), _poles() (+6 more)

### Community 126 - "region2d.test.tsx"
Cohesion: 0.16
Nodes (20): annulus, sinc, triangle, Region2dVisual(), ThreeView, compileRegion(), at(), boundary() (+12 more)

### Community 127 - "TaskGenerator"
Cohesion: 0.11
Nodes (11): algebra_generators(), AlgebraGenerator, ComplexNumbers, generators(), Matrices, PracticePartialFractions, RootSum, TaskGenerator (+3 more)

### Community 128 - "ExpressionAnswer"
Cohesion: 0.08
Nodes (29): generators(), PolynomialQuotient, QuadraticRemainder, QuadraticRemainderParams, RemainderParams, RemainderTheorem, rebuild(), input_variables() (+21 more)

### Community 129 - "topics/catalogue.py"
Cohesion: 0.05
Nodes (39): _check(), encode(), AlgebraParams, CombinationParams, Combinations, generators(), DefiniteIntegral, DefiniteParams (+31 more)

### Community 130 - "DeterministicRNG"
Cohesion: 0.07
Nodes (14): draw_entries(), draw_invertible(), _draw_eigen(), candidate(), _draw_planes(), vector(), root(), DeterministicRNG (+6 more)

### Community 131 - "test_engine_computational_api.py"
Cohesion: 0.16
Nodes (12): build(), Catalogue, load(), pool(), StoredCell, StoredModel, StoredProblem, StoredStep (+4 more)

### Community 132 - "test_preview.py"
Cohesion: 0.13
Nodes (15): MathWorkerError, _run_worker(), check_answer(), client(), headers(), test_check_failure_is_retryable_not_a_verdict(), fail(), test_generate_check_and_reveal_through_shared_worker() (+7 more)

### Community 133 - "dataclasses"
Cohesion: 0.10
Nodes (20): OrderedAnswer, FourierAnswer, build_form(), Built, ElementaryParams, expression_set(), finish(), set_diagram() (+12 more)

### Community 134 - "Saved"
Cohesion: 0.20
Nodes (8): legacy_code_is_never_run(), migrated(), Saved, owned(), test_an_archived_problem_opens_from_its_stored_rows(), test_an_archived_problem_prints_its_steps_without_a_graph(), test_an_archived_problem_reveals_its_stored_solution(), test_checking_an_archived_problem_is_an_archived_error()

### Community 135 - "test_engine_probability_foundation.py"
Cohesion: 0.16
Nodes (11): DensitySegment, ExponentialDistribution, NormalDistribution, PolynomialDensity, UniformDistribution, _cdf(), _density(), evaluate() (+3 more)

### Community 136 - "_probability_common.py"
Cohesion: 0.30
Nodes (13): FiniteSetAnswer, Built, finish(), finite(), joint(), joint_table(), ProbabilityParams, scalar() (+5 more)

### Community 137 - "registry"
Cohesion: 0.10
Nodes (15): registry(), test_new_generator_module_registers_without_a_catalogue_edit(), rebuild(), snapshot(), test_dependency_graph_and_topic_views_are_valid(), test_every_generator_version_has_golden_problems(), test_every_topic_level_gives_a_valid_problem_for_every_swept_seed(), test_golden_code_rebuilds_its_pinned_problem() (+7 more)

### Community 138 - "MathNode"
Cohesion: 0.10
Nodes (20): _parse(), parse_computational(), _real_set(), split_parts(), parse_logic(), expression(), node(), _constant_fraction() (+12 more)

### Community 139 - "test_worksheet_tex.py"
Cohesion: 0.10
Nodes (32): compile_pdf(), escape_text(), _log_tail(), _pdflatex(), PrintedGroup, PrintedProblem, _problem(), render_tex() (+24 more)

### Community 140 - "engine/practice.py"
Cohesion: 0.17
Nodes (13): lookup(), input_contract(), input_kind(), pooled(), _public(), public_replay(), _registry(), _check_child() (+5 more)

### Community 141 - "pytest"
Cohesion: 0.05
Nodes (46): AntiderivativeAnswer, DerivativeAnswer, _bounded(), _fraction(), _Invalid, _NonReal, NumberAnswer, _Unsupported (+38 more)

### Community 142 - "FiniteDistribution"
Cohesion: 0.15
Nodes (5): FiniteDistribution, JointDistribution, test_finite_distribution_and_pushforward_by_independent_enumeration(), test_joint_marginals_conditionals_covariance_independence(), Distribution block design

### Community 143 - "Probability and Statistics curriculum (#200)"
Cohesion: 0.09
Nodes (16): HANDOFF — Analysis I (#145), HANDOFF — Analysis II (#146), HANDOFF — Probability and Statistics (#200), implementation checkpoint, Project status, Analysis I curriculum (#145), Persistence and verification, Analysis II curriculum (#146), Integration and verification (+8 more)

### Community 144 - "test_supabase_hosted.py"
Cohesion: 0.19
Nodes (10): check_private(), CheckFailure, Client, denied(), main(), NoRedirect, require(), rows() (+2 more)

### Community 145 - "encode"
Cohesion: 0.18
Nodes (9): generators(), RadicalParams, RadicandParams, RationalizedAnswer, RationalizeDenominator, RationalizeParams, SimplifiedRadicalAnswer, SimplifyRadicals (+1 more)

### Community 146 - "Computational contracts and Graphify checkpoint"
Cohesion: 0.33
Nodes (5): Computational contracts and Graphify checkpoint, Graphify, explicitly delegated by the owner, Observed verification, Review, recovery and next action, Scope and result

### Community 147 - "test_worksheets.py"
Cohesion: 0.14
Nodes (23): _space_cm(), PrintedStep, catalogue_records(), record_key(), group(), picker(), test_a_cell_is_used_up_without_repeats_and_then_capped(), test_answers_start_on_a_new_page_and_only_with_the_key() (+15 more)

### Community 148 - "MVP end-to-end check (#13)"
Cohesion: 0.50
Nodes (3): Automated: `scripts/e2e_local.py`, Manual: deployed site, MVP end-to-end check (#13)

### Community 149 - "geometry.ts"
Cohesion: 0.20
Nodes (13): axisOrigin(), AxisTick, axisTicks(), Mesh3D, Scene3D, ADR-0006, Vec3, canvasHeight() (+5 more)

### Community 150 - "createAuthStore"
Cohesion: 0.70
Nodes (5): createAuthStore(), accept(), signIn(), signOut(), start()

### Community 151 - "test_engine_probability.py"
Cohesion: 0.12
Nodes (16): BooleanAnswer, IntervalAnswer, generators(), test_first_generation_response_already_includes_safe_input_instructions(), test_public_and_saved_input_instructions_are_safe_without_building(), test_wrong_kind_is_invalid_before_worker_admission(), scalar(), source() (+8 more)

### Community 152 - "test_engine_curriculum.py"
Cohesion: 0.15
Nodes (8): AlgebraData, AlgebraForm, _evaluate(), test_integral_curriculum_snapshot(), test_multiple_curriculum_snapshot_and_independent_orders(), test_partial_curriculum_snapshot(), test_scalar_curriculum_snapshots(), test_single_derivative_curriculum_snapshot()

### Community 153 - "mathEditor.ts"
Cohesion: 0.12
Nodes (17): FUNCTIONS, BARS, COMMAND_FUNCTIONS, CONSTANTS, INVERSE, Item, latexToAnswer(), needsTimes() (+9 more)

### Community 154 - "sympy"
Cohesion: 0.12
Nodes (28): affine_preimage(), angle_solutions(), composition_certificate(), equation_angles(), equation_roots(), inequality_set(), inverse_certificate(), logarithmic_image() (+20 more)

### Community 155 - "generators/analysis.py"
Cohesion: 0.23
Nodes (10): analysis_generators(), AnalysisGenerator, AnalysisParams, DifferentialEquations, generators(), ImproperIntegrals, Limits, MultivariableFunctions (+2 more)

### Community 156 - "subprocess"
Cohesion: 0.18
Nodes (9): test_educational_catalogue_and_checker(), test_answer_types_do_not_import_legacy_generators(), test_number_can_be_imported_without_sympy(), main(), free_port(), main(), psql(), run() (+1 more)

### Community 157 - "test_engine_computational_api.py"
Cohesion: 0.16
Nodes (8): render(), validate_plot(), diagram(), test_catalogue_replay_copy_projection_and_reveal_use_same_variant(), test_contract_mismatch_fails_before_catalogue_publication(), test_contract_used_before_worker_and_checked_inside(), test_new_contract_replays_in_real_limited_child(), test_visual_payload_is_bounded_and_strict()

### Community 158 - "pydantic"
Cohesion: 0.17
Nodes (10): _coefficient(), _entry_task(), generators(), MatrixCombination, MatrixCommutator, MatrixProduct, OperationParams, _shape() (+2 more)

### Community 159 - "StubClient"
Cohesion: 0.18
Nodes (4): DenialChecks, SingleUserChecks, SingleUserClient, StubClient

### Community 160 - "_probability_inference.py"
Cohesion: 0.17
Nodes (11): mean_interval(), mean_statistic(), median(), PairedSample, reject(), Sample, _differences(), evaluate() (+3 more)

### Community 161 - "Analysis exercise-sheet generator expansion"
Cohesion: 0.12
Nodes (14): Accepted staging and computational contracts, Analysis exercise-sheet generator expansion, Deliverable, Evidence required before delivery, Existing capability versus source coverage, Reference solutions and visuals are part of generation, Serial delivery, Source mathematics and errata (+6 more)

### Community 162 - "test_engine_analysis.py"
Cohesion: 0.22
Nodes (9): AnalysisData, AnalysisForm, _evaluate(), answer_text(), test_analysis_drawn_parameters_survive_json_and_reject_other_templates(), test_every_analysis_level_checks_in_limited_worker(), test_geometric_sum_matches_infinite_sum_and_rejects_previous_wrong_formula(), test_invalid_analysis_forms_are_rejected() (+1 more)

### Community 163 - "spec.ts"
Cohesion: 0.13
Nodes (17): Tree, spec, isRegion(), DefiniteSpec, finite(), IndefiniteSpec, Interval, parseVisual() (+9 more)

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

### Community 169 - "test_solid3d.py"
Cohesion: 0.29
Nodes (10): multiple_record(), _name(), solid3d(), solution_setup(), test_every_record_builds_a_small_valid_spec(), test_every_template_is_covered(), test_the_integrand_is_not_in_the_spec(), test_the_spec_ignores_the_coefficient() (+2 more)

### Community 170 - "answer_text"
Cohesion: 0.19
Nodes (15): category(), primitive(), Analysis source-family contracts (#233), Existing boundary and extension plan for #234, Family gap matrix, Source components and independent mathematical cases, Canonical families and explicit unsupported cases, Computational answer and reference-visual infrastructure (#234) (+7 more)

### Community 171 - "test_engine_catalogue.py"
Cohesion: 0.13
Nodes (10): Picker, test_a_new_entry_is_built_without_a_second_registration(), test_catalogue_build_failure_stops_release_before_activation(), test_cold_symbolic_issuing_and_worksheet_preparation_call_no_sympy(), test_combinations_worksheet_picker_exhausts_the_pool_without_duplicate_codes(), test_failed_build_leaves_the_previous_artifact_untouched(), test_incomplete_or_incompatible_catalogue_is_refused(), test_missing_pool_fails_closed_instead_of_generating() (+2 more)

### Community 172 - "Account completion (#35)"
Cohesion: 0.40
Nodes (5): Account completion (#35), Anonymous demo and privacy, Deployment and retention gates, Hard deletion and expired identity, Learning records and metrics

### Community 173 - "test_health.py"
Cohesion: 0.15
Nodes (5): allowed_origins(), _known_origin(), test_allowed_origins_reads_environment(), test_allowed_origins_refuse_plain_http_outside_local_dev(), test_api_responses_carry_security_headers()

### Community 174 - "Saved practice UI (#11/#12)"
Cohesion: 0.40
Nodes (5): Durable history and profile, Public/private boundary, Saved practice UI (#11/#12), Verification, Writes, retries and stale responses

### Community 175 - "plot2d.py"
Cohesion: 0.24
Nodes (4): DiagramModel, PlotDiagram, PlotPath, PlotPoint

### Community 176 - "202610150001_initial_schema.sql"
Cohesion: 0.29
Nodes (8): attempts_problem_idx, attempts_user_created_idx, private.problem_solutions, problems_user_created_idx, public.attempts, public.problems, public.profiles, public.topics

### Community 177 - "math.ts"
Cohesion: 0.23
Nodes (9): _loop(), across(), at(), evaluate(), _evaluate(), _log(), _pow(), _sqrt() (+1 more)

### Community 178 - "test_region2d.py"
Cohesion: 0.32
Nodes (9): native_params(), _name(), solution_setup(), _spec(), test_every_record_builds_a_small_valid_spec(), test_every_template_is_covered(), test_the_spec_follows_the_coefficient(), test_the_window_contains_the_region() (+1 more)

### Community 179 - "test_engine_probability_foundation.py"
Cohesion: 0.20
Nodes (7): StandardDistribution, test_new_grammars_reject_invalid_input(), test_shared_structured_syntax_corpus(), test_standard_distribution_normalization_and_moments(), test_strict_bounded_forms_reject_invalid_parameters(), test_structured_answers(), test_supplied_rounded_reference_tables_have_certified_precision()

### Community 180 - "database.py"
Cohesion: 0.18
Nodes (3): DatabaseNotConfigured, get_pool(), main()

### Community 181 - "202610220001_worksheets.sql"
Cohesion: 0.33
Nodes (5): problems_user_worksheet_created_idx, public.worksheet_items, public.worksheets, worksheet_items_problem_idx, worksheets_user_created_idx

### Community 183 - "solid3d.test.tsx"
Cohesion: 0.22
Nodes (8): box, cylinder, halfCone, simplex, Edge, EDGES, solidScene(), polyline()

### Community 184 - "input_projection"
Cohesion: 0.25
Nodes (3): lookup(), input_projection(), test_archived_records_have_no_new_input_projection()

### Community 185 - "to_tree"
Cohesion: 0.33
Nodes (3): to_tree(), UnsupportedExpression, test_expression_trees_use_only_the_listed_heads()

### Community 186 - "health.ts"
Cohesion: 0.40
Nodes (3): API_BASE_URL, ApiHealth, checkApiHealth()

### Community 187 - "Elementary functions and logic delivery (#235)"
Cohesion: 0.33
Nodes (5): Coordination and scope, Elementary functions and logic delivery (#235), Implementation, Release gate, Verification observed before publication

### Community 188 - "private.problem_reports"
Cohesion: 0.47
Nodes (3): private.problem_reports, problem_reports_created_idx, problem_reports_problem_idx

### Community 189 - "Launch runbook (#39)"
Cohesion: 0.40
Nodes (5): 1. Decisions only the owner can make, 3. External configuration (owner, in this order), 4. Verification on the domain, 5. Rollback, Launch runbook (#39)

### Community 191 - "test_engine_elementary_logic.py"
Cohesion: 0.18
Nodes (8): LogicAnswer, render(), truth(), evaluate(), parse(), test_every_operator_matches_an_independent_truth_table(), test_negations_accept_equivalence_over_every_assignment(), test_shared_logic_syntax()

### Community 192 - "Optional Graphify tooling"
Cohesion: 0.40
Nodes (4): Optional Graphify tooling, Query and refresh, Setup on Windows, Verification and limits

### Community 193 - "Analysis source intake handoff"
Cohesion: 0.40
Nodes (4): Analysis source intake handoff, Recovery, review and next action, Scope and completed work, Verification and practical limits

## Knowledge Gaps
- **36 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `@types/three` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1486 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **75 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `vitest` connect `types.ts` to `package.json`, `auth.test.ts`, `practice.ts`, `topics.ts`, `geometry.ts`, `mathEditor.ts`, `spec.ts`, `ReportProblem.tsx`, `expression.ts`, `WorksheetBuilder.test.tsx`, `solid3d.test.tsx`, `health.ts`, `tokens.test.ts`, `App.tsx`, `WorksheetBuilder.tsx`, `[[path]].ts`, `react`, `shares.ts`, `FormulaField.test.tsx`, `site.ts`, `main.tsx`, `answerSyntax.test.ts`, `region2d.test.tsx`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 80 inferred relationships involving `DeterministicRNG` (e.g. with `PartialForm` and `DerivativeForm`) actually correct?**
  _`DeterministicRNG` has 80 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `README.md` be split into smaller, more focused modules?**
  _Cohesion score 0.10344827586206896 - nodes in this community are weakly interconnected._
- **Why does `assert_means()` connect `build_visual` to `test_engine_analysis_two.py`, `math.ts`, `pytest`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 84 inferred relationships involving `Step` (e.g. with `AlgebraData` and `_evaluate()`) actually correct?**
  _`Step` has 84 INFERRED edges - model-reasoned connections that need verification._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._