# Graph Report - PracticeLoop  (2026-11-04)

## Corpus Check
- 441 files · ~377,828 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: (none) 10, .css 6, .toml 3)

## Summary
- 4527 nodes · 14187 edges · 229 communities (151 shown, 78 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1212 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `157a662a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- README.md
- package.json
- PracticeLoop — MVP Specification
- test_engine_catalogue.py
- Must-have before production
- check_answer
- compilerOptions
- auth.test.ts
- API contract
- practice.ts
- _symbolic.py
- test_supabase_hosted.py
- preview.py
- Prompt for Claude Code: implement the PracticeLoop frontend design
- pull_request_template.md
- system/README.md
- HANDOFF.md
- REVIEW_PROTOCOL.md
- test_auth.py
- problem.py
- pytest
- partial.py
- MathWorkerError
- setup-graphify.sh
- practiceloop-backend
- TASK_PROTOCOL.md
- subprocess
- PracticeLoop production roadmap
- 0001-frontend.md
- 0002-data-security.md
- test_practice_api.py
- vite-env.d.ts
- Problem generation intent
- Educational content style intent
- engine/models.py
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
- math_worker.py
- owned_records.py
- api/worksheets.py
- Setup
- topics
- Step
- types.ts
- App.tsx
- test_engine_complex_numbers.py
- HistoryPage.tsx
- WorksheetBuilder.tsx
- transaction
- api/shares.py
- SyntaxProblem
- sympy
- test_engine_polynomials.py
- issue-35-handoff.md
- e2e_local.py
- vitest
- [[path]].ts
- engine_fixtures.py
- differentiation/single.py
- HistoryRow.tsx
- test_shares_api.py
- FormulaField.test.tsx
- api/practice.py
- test_health.py
- issue
- test_engine_code_opening.py
- test_worksheets_api.py
- auth.py
- DefiniteView.tsx
- engine/practice.py
- pytest
- worksheet_graphs.py
- issue-11-handoff.md
- issue-12-handoff.md
- shares.ts
- AnswerInput
- integrals.py
- test_reports_api.py
- site.ts
- MathNode
- supabase_google_test_login.py
- ADR-005: multiple integrals and derivatives
- main.tsx
- topics/catalogue.py
- Changelog
- check_content.py
- devDependencies
- answerSyntax.test.ts
- dependencies
- bisect_exp
- scripts
- spec.py
- audit.sh
- Analysis II curriculum (#146)
- evaluate
- region2d.test.tsx
- test_engine_algebra.py
- test_engine_algebra_expansion.py
- Registry
- Issued
- test_engine_computational_api.py
- MethodStep
- InputContract
- _worked
- Parameters
- answers/structured.py
- matrix_operations.py
- MathInputError
- test_worksheet_tex.py
- DeterministicRNG
- test_engine_probability_foundation.py
- FiniteDistribution
- test_visuals.py
- StubClient
- algebra_expressions.py
- parse_code
- test_worksheets.py
- ReportProblem.tsx
- geometry.ts
- SolutionVisual.tsx
- test_engine_probability.py
- Integration topic generators
- mathEditor.ts
- test_engine_curriculum.py
- generators/analysis.py
- test_engine_answers.py
- test_engine_catalogue.py
- test_engine_integrals.py
- triple.py
- Sample
- Analysis exercise-sheet generator expansion
- math.ts
- spec.ts
- PracticeLoop agent rules
- cross_user
- ADR-007: printable PDF worksheets
- expression.ts
- CallbackChecks
- test_region2d.py
- os
- test_worksheet_graphs.py
- Account completion (#35)
- Routes
- Saved practice UI (#11/#12)
- test_solid3d.py
- 202610150001_initial_schema.sql
- plot2d.py
- number.py
- StandardDistribution
- Launch runbook (#39)
- 202610220001_worksheets.sql
- lookup
- test_supplied_rounded_reference_tables_have_certified_precision
- Generator Refactor MVP
- ADR-006: interactive visualizations in solutions
- ADR-008: composable generator engine
- private.problem_reports
- Optional Graphify tooling
- Analysis source intake handoff
- createAuthStore
- private.idempotency_keys
- private.problem_shares
- test_radical_exercises_check_equivalent_answers_and_replay
- Algebra30: remainder modulo a quadratic
- GrillMe review of the generator engine (#172)
- private.account_exists
- auth_fixture.sql
- 2026-11-02-quadratic-remainders.md
- hosted_fixture.sql

## God Nodes (most connected - your core abstractions)
1. `DeterministicRNG` - 194 edges
2. `Step` - 178 edges
3. `Task` - 178 edges
4. `parse_math_input()` - 112 edges
5. `topics()` - 105 edges
6. `Drawn` - 102 edges
7. `ExpressionAnswer` - 91 edges
8. `MathNode` - 69 edges
9. `TaskGenerator` - 67 edges
10. `encode()` - 65 edges

## Surprising Connections (you probably didn't know these)
- `Automated: `scripts/e2e_local.py`` --references--> `database_unavailable()`  [INFERRED]
  docs/production/MVP_E2E_CHECK.md → backend/app/core/database.py
- `Canonical families and explicit unsupported cases` --references--> `PeriodicSetAnswer`  [INFERRED]
  docs/architecture/COMPUTATIONAL_ANSWERS.md → backend/app/engine/answers/computational.py
- `Registration and extension` --references--> `Drawn`  [INFERRED]
  docs/decisions/0008-generator-engine.md → backend/app/engine/models.py
- `Public input and bounded checking` --references--> `MathNode`  [INFERRED]
  docs/decisions/0008-generator-engine.md → backend/app/math_input/parser.py
- `Check budget` --references--> `test_family_check_fits_the_worker_limits()`  [INFERRED]
  docs/decisions/0005-multiple-integrals-and-derivatives.md → backend/tests/test_answer_check.py

## Import Cycles
- None detected.

## Communities (229 total, 78 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.09
Nodes (10): Completion criteria, Implementation workflow, Algebra30 coverage, Answer checking, Architecture and MVP analysis, Open decisions — resolve before dependent features, Automated: `scripts/e2e_local.py`, Manual: deployed site (+2 more)

### Community 1 - "package.json"
Cohesion: 0.11
Nodes (18): engines, node, name, overrides, minimatch, private, type, version (+10 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "test_engine_catalogue.py"
Cohesion: 0.14
Nodes (16): _from_history(), _generate(), _prepare(), _print_order(), _response(), _reveal(), get_worksheet(), insert_items() (+8 more)

### Community 4 - "Must-have before production"
Cohesion: 0.12
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "check_answer"
Cohesion: 0.15
Nodes (23): check_answer(), answer_for(), native_record(), family(), _learner_text(), outcome(), record(), test_adversarial_answers_terminate_within_limits() (+15 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.16
Nodes (16): AuthCallback, AuthClient, AuthOptions, AuthSnapshot, INITIAL, none, setup(), start() (+8 more)

### Community 8 - "API contract"
Cohesion: 0.08
Nodes (22): _error(), internal_error(), invalid_request(), request_boundary(), _secure(), API contract, `GET /api/shares/{token}` and `GET /api/shares/code/{code}`, `GET /api/worksheets/{id}/pdf` (+14 more)

### Community 9 - "practice.ts"
Cohesion: 0.07
Nodes (78): expiryDate(), ShareControls(), copy(), authStore, client, accessToken(), accountRequest(), authorize() (+70 more)

### Community 10 - "_symbolic.py"
Cohesion: 0.08
Nodes (16): check_domain(), classify_expression(), components(), _defined_throughout(), differs(), evaluated_tree(), is_primitive(), _not_real() (+8 more)

### Community 11 - "test_supabase_hosted.py"
Cohesion: 0.17
Nodes (11): check_private(), CheckFailure, Client, denied(), main(), NoRedirect, require(), rows() (+3 more)

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

### Community 18 - "test_auth.py"
Cohesion: 0.15
Nodes (22): install_error_handlers(), assert_rejected(), bearer(), claims(), client(), FakeJwksClient, jwk(), jwks() (+14 more)

### Community 20 - "pytest"
Cohesion: 0.10
Nodes (25): declared_variables(), check(), _cylindrical(), _log_positive(), _log_real(), _partial_xy(), _polar(), problem() (+17 more)

### Community 21 - "partial.py"
Cohesion: 0.15
Nodes (20): Built, _chain_template(), build(), _d(), declared(), _domain(), _evaluate(), _first() (+12 more)

### Community 25 - "MathWorkerError"
Cohesion: 0.17
Nodes (15): MathWorkerError, _run_worker(), validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker() (+7 more)

### Community 29 - "subprocess"
Cohesion: 0.17
Nodes (10): test_educational_catalogue_and_checker(), test_answer_types_do_not_import_legacy_generators(), test_number_can_be_imported_without_sympy(), test_combination_generation_and_check_do_not_load_sympy(), main(), free_port(), main(), psql() (+2 more)

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 33 - "test_practice_api.py"
Cohesion: 0.08
Nodes (66): close_pool(), pool(), metric(), statistics(), AnswerCheck, answer_of(), attempt(), client() (+58 more)

### Community 50 - "Problem generation intent"
Cohesion: 0.17
Nodes (11): Definite and indefinite integrals, Difficulty, Generation model, Mathematical boundaries, Out of scope for this decision, Outcome, Pedagogically clean values, Practice modes (+3 more)

### Community 51 - "Educational content style intent"
Cohesion: 0.18
Nodes (10): Content in scope, Content outside this policy, Development-time enforcement, Educational content style intent, Out of scope for this decision, Outcome, Success criteria, Template catalogue (+2 more)

### Community 52 - "engine/models.py"
Cohesion: 0.03
Nodes (38): DerivativeAnswer, ConstantExpressionAnswer, FullRealExpressionAnswer, AnalysisOneData, AnalysisOneForm, evaluate(), DerivativeTemplate, _check() (+30 more)

### Community 53 - "Untracked generated practice (#34)"
Cohesion: 0.33
Nodes (6): Educational content, Mathematical checking and safety, Separate preview boundary, Supported generation, Untracked generated practice (#34), Verification and release

### Community 54 - "Integration topic generators"
Cohesion: 0.12
Nodes (14): Basic-integral generator, Definite integrals, Delivery boundary, Derivatives (`derivatives-v1`, #97), Integration topic generators, Mathematical and educational verification, Use and persistence boundary, Accepted input language (+6 more)

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
Cohesion: 0.09
Nodes (38): absBig(), analyseAnswer(), analyseStructuredAnswer(), AnswerAnalysis, Fraction, FUNCTION_SET, gcd(), hint() (+30 more)

### Community 64 - "Oracle backend deploy"
Cohesion: 0.13
Nodes (14): Audit, Backups and restore, Before adding Supabase credentials (human only), Browser path, Capacity and worker isolation, CORS, Logs, On the VM (+6 more)

### Community 65 - "FormulaField.tsx"
Cohesion: 0.10
Nodes (32): AnswerVariable, AnswerInputProps, ADR-0005, answerLatex(), byName(), configureKeyboard(), FormulaField(), FormulaFieldProps (+24 more)

### Community 66 - "Reader"
Cohesion: 0.28
Nodes (4): exponentText(), join(), Reader, wrap()

### Community 67 - "math_worker.py"
Cohesion: 0.14
Nodes (16): _apply_limits(), _child(), _code_child(), MathCheckInconclusive, check_answer(), client(), headers(), test_check_failure_is_retryable_not_a_verdict() (+8 more)

### Community 68 - "owned_records.py"
Cohesion: 0.09
Nodes (31): attempt_summaries(), AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), insert_problem(), last_attempt(), list_problems() (+23 more)

### Community 69 - "api/worksheets.py"
Cohesion: 0.13
Nodes (19): practice_code(), PracticeCodeBody, attempt(), generate(), _idempotency_key(), _respond(), practice_shared(), create_worksheet() (+11 more)

### Community 70 - "Setup"
Cohesion: 0.10
Nodes (23): _cartesian(), _disk(), DoubleTemplate, DoubleVariant, _polar(), _same_region(), _statement(), _steps() (+15 more)

### Community 71 - "topics"
Cohesion: 0.05
Nodes (64): bounded(), _cell(), det(), draw_invertible(), _factorial(), fractions(), linear_form(), minor() (+56 more)

### Community 72 - "Step"
Cohesion: 0.05
Nodes (52): Combinations, DefiniteIntegral, DiagonalPower, _draw_eigen(), candidate(), valid(), _draw_planes(), _draw_points() (+44 more)

### Community 73 - "types.ts"
Cohesion: 0.05
Nodes (64): analyseComputationalAnswer(), ANSWER_VARIABLES, splitComputationalParts(), card(), ComputationalAnswerInput(), Props, enter, Harness() (+56 more)

### Community 74 - "App.tsx"
Cohesion: 0.08
Nodes (54): route(), APP_ROUTES, NARROW_ROUTES, NotFoundPage(), SITE, APP_ROUTES, AppNav(), AppNavProps (+46 more)

### Community 75 - "test_engine_complex_numbers.py"
Cohesion: 0.06
Nodes (41): algebraic_form(), ComplexAnswer, _unit_as_x(), _angle(), _base(), _cis(), _Complex, ComplexArgument (+33 more)

### Community 76 - "HistoryPage.tsx"
Cohesion: 0.09
Nodes (23): Chips(), revealNote(), ADR-0007, WorksheetOptions(), WorksheetOptionsProps, ProblemPage, DEFAULT_PAGE_OPTIONS, WorksheetPageOptions (+15 more)

### Community 77 - "WorksheetBuilder.tsx"
Cohesion: 0.06
Nodes (65): DifficultyScale(), DifficultyScaleProps, AreaChipsProps, ChipOption, ChipsProps, TopicChipsProps, ADR-0005, choices() (+57 more)

### Community 78 - "transaction"
Cohesion: 0.10
Nodes (16): delete_account(), _feedback(), history(), learning_statistics(), _not_found(), profile(), _public_problem(), reopen() (+8 more)

### Community 79 - "api/shares.py"
Cohesion: 0.08
Nodes (25): _public_share(), by_code(), by_token(), create(), _invalid_share(), PracticeShareBody, revoke(), _shared() (+17 more)

### Community 80 - "SyntaxProblem"
Cohesion: 0.32
Nodes (5): constantFraction(), numberFraction(), Parser, SyntaxProblem, validateExponent()

### Community 81 - "sympy"
Cohesion: 0.12
Nodes (21): AnalysisTwoData, AnalysisTwoForm, finish(), canonical_arctangents(), evaluate(), evaluate(), evaluate(), laplace_table() (+13 more)

### Community 82 - "test_engine_polynomials.py"
Cohesion: 0.06
Nodes (35): vector(), BinomialCoefficient, BinomialConstantTerm, BinomialExponent, CoefficientParams, ConstantTermParams, CubicRemainder, Divisibility (+27 more)

### Community 84 - "e2e_local.py"
Cohesion: 0.20
Nodes (18): check(), combinations(), correct_answer(), database_failure(), derivatives(), full_flow(), key(), main() (+10 more)

### Community 85 - "vitest"
Cohesion: 0.07
Nodes (19): `POST /api/worksheets`, harness, renderAt(), signedIn, signedOut, button(), buttons(), catalogue (+11 more)

### Community 86 - "[[path]].ts"
Cohesion: 0.36
Nodes (4): Context, onRequest(), FORWARDED_HEADERS, proxyToApi()

### Community 88 - "engine_fixtures.py"
Cohesion: 0.09
Nodes (14): PartialForm, MultipleData, MultipleForm, generators(), PartialDerivativeParams, PartialDerivatives, DoubleIntegrals, generators() (+6 more)

### Community 89 - "differentiation/single.py"
Cohesion: 0.12
Nodes (11): _chain(), _components(), _d(), DerivativeData, DerivativeStep, _evaluate(), _rewrite(), _step() (+3 more)

### Community 90 - "HistoryRow.tsx"
Cohesion: 0.15
Nodes (20): ApiStatusNotice(), AttemptStatus(), HistoryList(), HistoryListProps, HistoryRow(), RowSelection, SelectableRow(), CheckIcon() (+12 more)

### Community 91 - "test_shares_api.py"
Cohesion: 0.22
Nodes (26): assert_unavailable(), client(), execute(), generate(), share(), start_copy(), test_concurrent_copy_retries_create_once_and_replay_after_revocation(), test_copy_does_not_inherit_sender_attempts_or_reveals() (+18 more)

### Community 92 - "FormulaField.test.tsx"
Cohesion: 0.15
Nodes (6): changes, Fake, FakeMathfield, Harness(), Layout, render()

### Community 93 - "api/practice.py"
Cohesion: 0.04
Nodes (39): canonical(), invalid_code(), _opened(), _archived(), area_topics(), AttemptBody, capacity(), _check() (+31 more)

### Community 94 - "test_health.py"
Cohesion: 0.16
Nodes (5): allowed_origins(), _known_origin(), test_allowed_origins_reads_environment(), test_allowed_origins_refuse_plain_http_outside_local_dev(), test_api_responses_carry_security_headers()

### Community 95 - "issue"
Cohesion: 0.06
Nodes (30): check(), is_engine_record(), issue(), levels(), is_archived(), record_variables(), test_record_variables_are_read_and_validated(), test_only_old_records_of_a_migrated_topic_are_archived() (+22 more)

### Community 96 - "test_engine_code_opening.py"
Cohesion: 0.16
Nodes (8): open_problem_code(), client(), test_code_worker_failure_is_retryable_and_releases_the_shared_slot(), failed(), test_each_version_rebuilds_in_the_limited_worker(), test_every_golden_code_opens_the_exact_shipped_task(), test_invalid_unknown_and_wrong_checksum_codes_fail_before_symbolic_work(), test_public_code_lookup_projects_only_the_statement_without_symbolic_work()

### Community 97 - "test_worksheets_api.py"
Cohesion: 0.16
Nodes (34): pooled(), client(), Compiled, compiled(), create(), generate(), key(), make_problem() (+26 more)

### Community 98 - "auth.py"
Cohesion: 0.09
Nodes (17): _auth_unavailable(), AuthUnavailableError, current_user(), get_token_verifier(), _invalid_token(), token_verifier(), TokenVerifier, _user_from_claims() (+9 more)

### Community 99 - "DefiniteView.tsx"
Cohesion: 0.11
Nodes (33): Axes(), DefiniteView(), PAD, RULES, tex(), ADR-0006, IndefiniteView(), NAMES (+25 more)

### Community 100 - "engine/practice.py"
Cohesion: 0.08
Nodes (25): rebuild(), input_contract(), input_kind(), input_variables(), _public(), public_replay(), _registry(), replay() (+17 more)

### Community 101 - "pytest"
Cohesion: 0.13
Nodes (21): parse_math_input(), test_domain_check_avoids_repeating_sum_domains_and_preserves_holes(), answer_text(), test_all_algebra_levels_check_in_limited_worker(), test_all_algebra_levels_preserve_public_contracts_and_check_answers(), test_drawn_algebra_parameters_survive_json_and_reject_cross_family(), test_invalid_algebra_forms_are_rejected(), test_bisection_equation_has_no_supported_closed_form() (+13 more)

### Community 102 - "worksheet_graphs.py"
Cohesion: 0.15
Nodes (18): Canvas, _caption(), _curve(), definite(), _finite(), indefinite(), _n(), plot2d() (+10 more)

### Community 105 - "shares.ts"
Cohesion: 0.10
Nodes (36): App(), handleDeleted(), handleLogOut(), handleSignIn(), topicReturn(), DifficultyDots(), base, lookupProblemCode() (+28 more)

### Community 106 - "AnswerInput"
Cohesion: 0.19
Nodes (7): AnswerInput(), insert(), move(), replace(), AnswerPreview(), Harness(), render()

### Community 107 - "integrals.py"
Cohesion: 0.11
Nodes (21): ExpressionAnswer, _evaluate(), IntegralData, IntegralForm, BasicIntegrals, DefiniteBasicIntegrals, DefinitePartsIntegrals, DefiniteRationalIntegrals (+13 more)

### Community 108 - "test_reports_api.py"
Cohesion: 0.20
Nodes (11): client(), generate(), stored(), test_invalid_reports_are_refused_without_echoing_them(), test_nobody_reports_someone_elses_or_a_missing_problem(), test_owner_reports_a_problem_with_only_the_approved_fields(), test_reports_are_rate_limited_per_user(), test_reports_go_with_the_account() (+3 more)

### Community 109 - "site.ts"
Cohesion: 0.13
Nodes (19): 2. Code changes, one PR after step 1, applyPageMeta(), crawlerFiles(), isSharedPath(), NOINDEX_PATHS, NOT_FOUND, page(), pageMeta (+11 more)

### Community 110 - "MathNode"
Cohesion: 0.07
Nodes (14): combine(), ComputationalAnswer, _domain(), _expression(), LimitAnswer, PeriodicSetAnswer, _piece(), _set() (+6 more)

### Community 111 - "supabase_google_test_login.py"
Cohesion: 0.12
Nodes (3): start_server(), collect_google_tokens(), handler_for()

### Community 112 - "ADR-005: multiple integrals and derivatives"
Cohesion: 0.13
Nodes (15): ADR-005: multiple integrals and derivatives, Amendment: practice areas (#144, 2026-10-26), Answers and variables, Areas and topics, Check budget, Consequences, Coordinate systems, Delivery (+7 more)

### Community 113 - "main.tsx"
Cohesion: 0.14
Nodes (9): analyticsAllowed(), BEACON_SRC, startWebAnalytics(), ErrorBoundary, root, @fontsource/geist, @fontsource/geist-mono, @fontsource/instrument-serif (+1 more)

### Community 114 - "topics/catalogue.py"
Cohesion: 0.05
Nodes (39): load(), lookup(), AlgebraParams, registry(), CombinationParams, DefiniteParams, DerivativeParams, SingleDerivativeParams (+31 more)

### Community 115 - "Changelog"
Cohesion: 0.40
Nodes (4): 0.1.0 — MVP (2026-10-20), Changelog, Changes during MVP development, Unreleased

### Community 116 - "check_content.py"
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

### Community 120 - "bisect_exp"
Cohesion: 0.24
Nodes (5): bisect_exp(), exp_bounds(), test_bisection_has_exact_sign_certificates_error_bound_and_unique_root(), test_every_added_version_opens_and_checks_inside_the_limited_worker(), test_function_answers_preserve_their_full_real_domain_before_cancellation()

### Community 121 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, lint:content, test, typecheck

### Community 122 - "spec.py"
Cohesion: 0.11
Nodes (16): bounds_latex(), level(), SetupLike, _interval(), _numeric(), value(), parameter_points(), region2d_setup() (+8 more)

### Community 124 - "Analysis II curriculum (#146)"
Cohesion: 0.11
Nodes (11): HANDOFF — Analysis I (#145), HANDOFF — Analysis II (#146), HANDOFF — Probability and Statistics (#200), implementation checkpoint, Project status, Analysis I curriculum (#145), Persistence and verification, Analysis II curriculum (#146), Integration and verification (+3 more)

### Community 125 - "evaluate"
Cohesion: 0.17
Nodes (14): _bisect(), _changes_sign(), _component(), definite_data(), _distinct(), _f(), indefinite(), _poles() (+6 more)

### Community 126 - "region2d.test.tsx"
Cohesion: 0.14
Nodes (24): annulus, isRegion(), sinc, triangle, Region2dVisual(), ThreeView, compileRegion(), at() (+16 more)

### Community 127 - "test_engine_algebra.py"
Cohesion: 0.18
Nodes (10): AlgebraData, AlgebraForm, _evaluate(), algebra_generators(), AlgebraGenerator, ComplexNumbers, generators(), Matrices (+2 more)

### Community 128 - "test_engine_algebra_expansion.py"
Cohesion: 0.13
Nodes (18): generators(), PolynomialQuotient, QuadraticRemainder, QuadraticRemainderParams, RemainderParams, RemainderTheorem, test_polynomial_answers_are_checked_in_the_limited_worker(), test_polynomial_division_replays_and_checks_1000_draws() (+10 more)

### Community 129 - "Registry"
Cohesion: 0.16
Nodes (7): visit(), test_dependency_graph_accepts_shared_dependency_and_rejects_missing_and_cycles(), test_generator_consumer_and_parameter_validation(), test_registry_rejects_duplicate_unknown_and_invalid_metadata(), TinyAnswer, TinyGenerator, TinyParams

### Community 130 - "Issued"
Cohesion: 0.15
Nodes (9): build(), StoredCell, StoredModel, StoredProblem, StoredStep, write(), OpenedCode, Issued (+1 more)

### Community 131 - "test_engine_computational_api.py"
Cohesion: 0.15
Nodes (10): render(), statement_latex(), validate_plot(), diagram(), extension(), test_catalogue_replay_copy_projection_and_reveal_use_same_variant(), test_contract_mismatch_fails_before_catalogue_publication(), test_contract_used_before_worker_and_checked_inside() (+2 more)

### Community 132 - "MethodStep"
Cohesion: 0.12
Nodes (8): BasicStep, build(), MethodStep, MethodTemplate, build(), build(), build(), build()

### Community 133 - "InputContract"
Cohesion: 0.08
Nodes (29): CategoryAnswer, FormulaAnswer, OrderedAnswer, RealSetAnswer, InputContract, parse_answer_input(), _split(), ContractExample (+21 more)

### Community 134 - "_worked"
Cohesion: 0.14
Nodes (10): legacy_code_is_never_run(), migrated(), Saved, owned(), test_an_archived_problem_opens_from_its_stored_rows(), test_an_archived_problem_prints_its_steps_without_a_graph(), test_an_archived_problem_reveals_its_stored_solution(), test_checking_an_archived_problem_is_an_archived_error() (+2 more)

### Community 135 - "Parameters"
Cohesion: 0.13
Nodes (10): DensitySegment, ExponentialDistribution, NormalDistribution, PolynomialDensity, UniformDistribution, _cdf(), _density(), evaluate() (+2 more)

### Community 136 - "answers/structured.py"
Cohesion: 0.26
Nodes (14): Built, finish(), finite(), joint(), joint_table(), ProbabilityParams, scalar(), table() (+6 more)

### Community 137 - "matrix_operations.py"
Cohesion: 0.18
Nodes (9): draw_entries(), _coefficient(), generators(), MatrixCombination, MatrixCommutator, MatrixProduct, OperationParams, test_operations_match_pdf_exercises_8_and_9a() (+1 more)

### Community 138 - "MathInputError"
Cohesion: 0.13
Nodes (17): _parse(), parse_computational(), _real_set(), split_parts(), _constant_fraction(), MathInputError, MathInputTooLong, MathNode (+9 more)

### Community 139 - "test_worksheet_tex.py"
Cohesion: 0.09
Nodes (35): download_pdf(), _worked(), compile_pdf(), escape_text(), filename(), _log_tail(), _pdflatex(), PrintedGroup (+27 more)

### Community 140 - "DeterministicRNG"
Cohesion: 0.08
Nodes (18): DerivativeForm, IntegerRange, Polynomial, PartialFractionRational, SingleDerivatives, Parameters, DeterministicRNG, test_integer_range_draw_is_reproducible_and_respects_exclusions() (+10 more)

### Community 141 - "test_engine_probability_foundation.py"
Cohesion: 0.23
Nodes (8): mean_interval(), mean_statistic(), reject(), test_inference_boundaries_and_center_width(), test_new_grammars_reject_invalid_input(), test_shared_structured_syntax_corpus(), test_strict_bounded_forms_reject_invalid_parameters(), test_structured_answers()

### Community 142 - "FiniteDistribution"
Cohesion: 0.15
Nodes (11): FiniteDistribution, JointDistribution, test_finite_distribution_and_pushforward_by_independent_enumeration(), test_joint_marginals_conditionals_covariance_independence(), Approved release, Delivery and verification after approval, Distribution block design, Mathematical conventions and bounded records (+3 more)

### Community 143 - "test_visuals.py"
Cohesion: 0.14
Nodes (17): _build(), build_visual(), solution_payload(), catalogue(), native_data(), assert_definite(), assert_indefinite(), assert_means() (+9 more)

### Community 144 - "StubClient"
Cohesion: 0.21
Nodes (3): DenialChecks, SingleUserClient, StubClient

### Community 145 - "algebra_expressions.py"
Cohesion: 0.17
Nodes (10): generators(), RadicalParams, RadicandParams, RationalizedAnswer, RationalizeDenominator, RationalizeParams, SimplifiedRadicalAnswer, SimplifyRadicals (+2 more)

### Community 146 - "parse_code"
Cohesion: 0.20
Nodes (13): Catalogue, format_code(), parse_code(), ProblemCode, Registry, test_blocks_do_not_import_topics_generators_or_content(), registry(), test_a_generator_writes_the_same_code_without_a_registry() (+5 more)

### Community 147 - "test_worksheets.py"
Cohesion: 0.12
Nodes (24): label(), _space_cm(), WorksheetBody, catalogue_records(), record_key(), group(), picker(), test_a_cell_is_used_up_without_repeats_and_then_capped() (+16 more)

### Community 148 - "ReportProblem.tsx"
Cohesion: 0.19
Nodes (11): Launch blockers (#39), Production checklist (#38), Running the checks, LABELS, ReportProblem(), submit(), button(), openForm() (+3 more)

### Community 149 - "geometry.ts"
Cohesion: 0.16
Nodes (16): Edge, EDGES, axisOrigin(), AxisTick, axisTicks(), Mesh3D, Scene3D, ADR-0006 (+8 more)

### Community 150 - "SolutionVisual.tsx"
Cohesion: 0.15
Nodes (11): box, cylinder, halfCone, simplex, Solid3dVisual(), ThreeView, solidScene(), SolutionVisual() (+3 more)

### Community 151 - "test_engine_probability.py"
Cohesion: 0.10
Nodes (21): BooleanAnswer, FiniteSetAnswer, IntervalAnswer, RealScalarAnswer, BooleanProbability, _build(), generators(), IntervalProbability (+13 more)

### Community 152 - "Integration topic generators"
Cohesion: 0.20
Nodes (9): Backup and rollback, Current verification status, Database preparation, Hosted Auth and PostgREST verification (human only), Human-only Google test helper (no token copying), Human provisioning, without sharing credentials, Issue #3 delivery and first-project procedure, Migration workflow (+1 more)

### Community 153 - "mathEditor.ts"
Cohesion: 0.12
Nodes (17): FUNCTIONS, BARS, COMMAND_FUNCTIONS, CONSTANTS, INVERSE, Item, latexToAnswer(), needsTimes() (+9 more)

### Community 154 - "test_engine_curriculum.py"
Cohesion: 0.12
Nodes (14): AnalysisData, AnalysisForm, _evaluate(), answer_text(), test_analysis_drawn_parameters_survive_json_and_reject_other_templates(), test_every_analysis_level_checks_in_limited_worker(), test_geometric_sum_matches_infinite_sum_and_rejects_previous_wrong_formula(), test_invalid_analysis_forms_are_rejected() (+6 more)

### Community 155 - "generators/analysis.py"
Cohesion: 0.22
Nodes (10): analysis_generators(), AnalysisGenerator, AnalysisParams, DifferentialEquations, generators(), ImproperIntegrals, Limits, MultivariableFunctions (+2 more)

### Community 156 - "test_engine_answers.py"
Cohesion: 0.08
Nodes (28): AntiderivativeAnswer, NumberAnswer, Answer, test_antiderivative_checks_all_domain_components(), test_antiderivative_constant_and_equivalence_rules(), test_derivative_rejects_constants_and_domain_holes(), test_expression_runs_under_worker_limits(), test_expression_uses_declared_variables() (+20 more)

### Community 157 - "test_engine_catalogue.py"
Cohesion: 0.12
Nodes (11): Picker, test_a_new_entry_is_built_without_a_second_registration(), test_catalogue_build_failure_stops_release_before_activation(), test_cold_symbolic_issuing_and_worksheet_preparation_call_no_sympy(), test_combinations_worksheet_picker_exhausts_the_pool_without_duplicate_codes(), test_every_declared_cell_is_full_and_every_code_replays_its_stored_fields(), test_failed_build_leaves_the_previous_artifact_untouched(), test_incomplete_or_incompatible_catalogue_is_refused() (+3 more)

### Community 158 - "test_engine_integrals.py"
Cohesion: 0.27
Nodes (6): answer_text(), test_each_migrated_cell_checks_inside_the_limited_worker(), test_forms_have_exact_primitives_and_valid_bounds(), test_malformed_parameters_are_refused(), test_native_indefinite_answers_keep_the_constant_policy(), test_recent_records_are_excluded_without_rebuilding_a_task()

### Community 159 - "triple.py"
Cohesion: 0.24
Nodes (9): _box(), _cartesian(), _cylindrical(), _over_disk(), _statement(), _steps(), TripleTemplate, TripleVariant (+1 more)

### Community 160 - "Sample"
Cohesion: 0.27
Nodes (5): median(), PairedSample, Sample, evaluate(), test_sample_statistics_against_standard_library_and_normal_equations()

### Community 161 - "Analysis exercise-sheet generator expansion"
Cohesion: 0.12
Nodes (14): primitive(), Analysis source-family contracts (#233), Existing boundary and extension plan for #234, Family gap matrix, Source components and independent mathematical cases, Accepted staging and computational contracts, Analysis exercise-sheet generator expansion, Deliverable (+6 more)

### Community 162 - "math.ts"
Cohesion: 0.15
Nodes (12): _loop(), across(), at(), evaluate(), _evaluate(), _log(), _pow(), _sqrt() (+4 more)

### Community 163 - "spec.ts"
Cohesion: 0.16
Nodes (13): Tree, DefiniteSpec, finite(), IndefiniteSpec, Interval, POINT_KINDS, PointKind, REGION_VARIABLES (+5 more)

### Community 164 - "PracticeLoop agent rules"
Cohesion: 0.22
Nodes (7): After a merge, Before starting work, Collaboration rules, GitHub Issue names, Graphify, PracticeLoop agent rules, Claude Code

### Community 166 - "ADR-007: printable PDF worksheets"
Cohesion: 0.14
Nodes (13): ADR-007: printable PDF worksheets, Amendment to ADR-004 counters, API, Data, Delivery, `GET /api/worksheets/{id}/pdf`, Implementation notes (#116, 2026-10-22), Limits and errors (+5 more)

### Community 167 - "expression.ts"
Cohesion: 0.20
Nodes (12): compile(), build(), Compiled, CONSTANTS, Env, evaluate(), ExpressionError, HEADS (+4 more)

### Community 169 - "test_region2d.py"
Cohesion: 0.32
Nodes (9): native_params(), _name(), solution_setup(), _spec(), test_every_record_builds_a_small_valid_spec(), test_every_template_is_covered(), test_the_spec_follows_the_coefficient(), test_the_window_contains_the_region() (+1 more)

### Community 171 - "test_worksheet_graphs.py"
Cohesion: 0.19
Nodes (9): _text(), graph(), nice_ticks(), first_records(), literals(), test_a_graph_is_a_picture_of_pdf_operators_and_math_labels(), test_every_visual_kind_has_a_drawer(), test_no_visual_means_no_graph() (+1 more)

### Community 172 - "Account completion (#35)"
Cohesion: 0.40
Nodes (5): Account completion (#35), Anonymous demo and privacy, Deployment and retention gates, Hard deletion and expired identity, Learning records and metrics

### Community 173 - "Routes"
Cohesion: 0.18
Nodes (11): visual(), Archived problems (#190), `GET /api/problems`, `GET /api/problems/{id}`, `GET /api/profile`, `GET /api/topics`, `POST /api/problems`, `POST /api/problems/{id}/attempts` (+3 more)

### Community 174 - "Saved practice UI (#11/#12)"
Cohesion: 0.40
Nodes (5): Durable history and profile, Public/private boundary, Saved practice UI (#11/#12), Verification, Writes, retries and stale responses

### Community 175 - "test_solid3d.py"
Cohesion: 0.25
Nodes (9): _name(), solid3d(), solution_setup(), test_every_record_builds_a_small_valid_spec(), test_every_template_is_covered(), test_the_integrand_is_not_in_the_spec(), test_the_spec_ignores_the_coefficient(), test_the_window_contains_the_solid() (+1 more)

### Community 176 - "202610150001_initial_schema.sql"
Cohesion: 0.29
Nodes (8): attempts_problem_idx, attempts_user_created_idx, private.problem_solutions, problems_user_created_idx, public.attempts, public.problems, public.profiles, public.topics

### Community 177 - "plot2d.py"
Cohesion: 0.24
Nodes (4): DiagramModel, PlotDiagram, PlotPath, PlotPoint

### Community 178 - "number.py"
Cohesion: 0.31
Nodes (5): _bounded(), _fraction(), _Invalid, _NonReal, _Unsupported

### Community 180 - "Launch runbook (#39)"
Cohesion: 0.40
Nodes (5): 1. Decisions only the owner can make, 3. External configuration (owner, in this order), 4. Verification on the domain, 5. Rollback, Launch runbook (#39)

### Community 181 - "202610220001_worksheets.sql"
Cohesion: 0.33
Nodes (5): problems_user_worksheet_created_idx, public.worksheet_items, public.worksheets, worksheet_items_problem_idx, worksheets_user_created_idx

### Community 182 - "lookup"
Cohesion: 0.20
Nodes (4): lookup(), input_projection(), test_archived_records_have_no_new_input_projection(), test_public_and_saved_input_instructions_are_safe_without_building()

### Community 184 - "Generator Refactor MVP"
Cohesion: 0.29
Nodes (7): 10. Re-evaluate the generator architecture with GrillMe (#172), Generator Refactor MVP, Goal: Complete the generator refactor, GrillMe gate, Main goal, MVP done when, Rules for every issue

### Community 185 - "ADR-006: interactive visualizations in solutions"
Cohesion: 0.29
Nodes (6): ADR-006: interactive visualizations in solutions, Fallback, mobile and accessibility, Out of scope, Testing, What each kind shows, Where visuals appear

### Community 186 - "ADR-008: composable generator engine"
Cohesion: 0.25
Nodes (8): ADR-008: composable generator engine, Compatible computational extensions (#234, 2026-11-04), Context and result, Curriculum, visuals and archive, Permanent problem codes, Public input and bounded checking, Verification and remaining work, Verified release catalogue

### Community 188 - "private.problem_reports"
Cohesion: 0.47
Nodes (3): private.problem_reports, problem_reports_created_idx, problem_reports_problem_idx

### Community 192 - "Optional Graphify tooling"
Cohesion: 0.40
Nodes (4): Optional Graphify tooling, Query and refresh, Setup on Windows, Verification and limits

### Community 193 - "Analysis source intake handoff"
Cohesion: 0.40
Nodes (4): Analysis source intake handoff, Recovery, review and next action, Scope and completed work, Verification and practical limits

### Community 194 - "createAuthStore"
Cohesion: 0.70
Nodes (5): createAuthStore(), accept(), signIn(), signOut(), start()

### Community 200 - "GrillMe review of the generator engine (#172)"
Cohesion: 0.67
Nodes (3): GrillMe review of the generator engine (#172), Remaining refactor, in Order, Verdict

## Knowledge Gaps
- **36 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `@types/three` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1433 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **78 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `vitest` connect `vitest` to `package.json`, `auth.test.ts`, `practice.ts`, `ReportProblem.tsx`, `geometry.ts`, `SolutionVisual.tsx`, `mathEditor.ts`, `spec.ts`, `expression.ts`, `types.ts`, `App.tsx`, `HistoryPage.tsx`, `WorksheetBuilder.tsx`, `[[path]].ts`, `HistoryRow.tsx`, `FormulaField.test.tsx`, `DefiniteView.tsx`, `shares.ts`, `AnswerInput`, `site.ts`, `main.tsx`, `answerSyntax.test.ts`, `region2d.test.tsx`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 79 inferred relationships involving `DeterministicRNG` (e.g. with `PartialForm` and `DerivativeForm`) actually correct?**
  _`DeterministicRNG` has 79 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `README.md` be split into smaller, more focused modules?**
  _Cohesion score 0.08712121212121213 - nodes in this community are weakly interconnected._
- **Why does `assert_definite()` connect `test_visuals.py` to `sympy`, `math.ts`, `pytest`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 83 inferred relationships involving `Step` (e.g. with `AlgebraData` and `_evaluate()`) actually correct?**
  _`Step` has 83 INFERRED edges - model-reasoned connections that need verification._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._