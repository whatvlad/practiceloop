# Graph Report - PracticeLoop  (2026-11-04)

## Corpus Check
- 442 files · ~378,727 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: (none) 10, .css 6, .toml 3)

## Summary
- 4533 nodes · 14192 edges · 217 communities (141 shown, 76 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1212 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `67f3372e`
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
- test-db.py
- PracticeLoop production roadmap
- 0001-frontend.md
- 0002-data-security.md
- test_practice_api.py
- vite-env.d.ts
- Problem generation intent
- Educational content style intent
- engine/models.py
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
- vitest
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
- differentiation/single.py
- test_engine_polynomials.py
- issue-35-handoff.md
- e2e_local.py
- react-dom
- [[path]].ts
- test_engine_analysis_two.py
- react
- differentiation.py
- test_shares_api.py
- FormulaField.test.tsx
- api/practice.py
- test_health.py
- issue
- test_engine_code_opening.py
- test_worksheets_api.py
- auth.py
- DefiniteView.tsx
- topics/catalogue.py
- build_expression
- worksheet_graphs.py
- issue-11-handoff.md
- issue-12-handoff.md
- types.ts
- AnswerInput
- integrals.py
- topics.ts
- site.ts
- _scalar
- supabase_google_test_login.py
- ADR-005: multiple integrals and derivatives
- main.tsx
- parse_code
- Changelog
- typing
- devDependencies
- answerSyntax.test.ts
- dependencies
- sympy
- scripts
- spec.py
- audit.sh
- Analysis II curriculum (#146)
- evaluate
- region2d.test.tsx
- test_engine_algebra.py
- test_engine_algebra_expansion.py
- invalid_request
- engine/practice.py
- test_engine_computational_api.py
- AnalysisTwo
- InputContract
- _worked
- Parameters
- answers/structured.py
- .kind
- MathInputError
- test_worksheet_tex.py
- DeterministicRNG
- test_engine_probability_foundation.py
- FiniteDistribution
- Probability and Statistics curriculum (#200)
- StubClient
- algebra_expressions.py
- Computational contracts and Graphify checkpoint
- catalogue_records
- MVP end-to-end check (#13)
- geometry.ts
- WORKFLOW.md
- test_engine_probability.py
- mathEditor.ts
- test_engine_curriculum.py
- generators/analysis.py
- test_engine_answers.py
- test_engine_catalogue.py
- test_engine_integrals.py
- Sample
- Analysis exercise-sheet generator expansion
- math.ts
- spec.ts
- PracticeLoop agent rules
- ADR-007: printable PDF worksheets
- expression.ts
- test_region2d.py
- Account completion (#35)
- Routes
- Saved practice UI (#11/#12)
- test_solid3d.py
- 202610150001_initial_schema.sql
- number.py
- StandardDistribution
- Launch runbook (#39)
- 202610220001_worksheets.sql
- test_supplied_rounded_reference_tables_have_certified_precision
- ADR-006: interactive visualizations in solutions
- ADR-008: composable generator engine
- private.problem_reports
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
- `Registration and extension` --references--> `Drawn`  [INFERRED]
  docs/decisions/0008-generator-engine.md → backend/app/engine/models.py
- `Public input and bounded checking` --references--> `MathNode`  [INFERRED]
  docs/decisions/0008-generator-engine.md → backend/app/math_input/parser.py
- `Check budget` --references--> `test_family_check_fits_the_worker_limits()`  [INFERRED]
  docs/decisions/0005-multiple-integrals-and-derivatives.md → backend/tests/test_answer_check.py
- ``GET /api/problems/{id}`` --references--> `share()`  [INFERRED]
  docs/api/README.md → backend/tests/test_shares_api.py

## Import Cycles
- None detected.

## Communities (217 total, 76 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.11
Nodes (6): Algebra30 coverage, Answer checking, Basic-integral generator, Architecture and MVP analysis, Open decisions — resolve before dependent features, Security policy

### Community 1 - "package.json"
Cohesion: 0.11
Nodes (17): engines, node, name, overrides, minimatch, private, type, version (+9 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "test_engine_catalogue.py"
Cohesion: 0.13
Nodes (13): _print_order(), _worked(), graph(), get_worksheet(), insert_items(), insert_worksheet(), owned_problems(), OwnedProblem (+5 more)

### Community 4 - "Must-have before production"
Cohesion: 0.12
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "check_answer"
Cohesion: 0.08
Nodes (34): _check(), check_answer(), MathCheckInconclusive, MathWorkerError, _run_worker(), answer_for(), check(), native_record() (+26 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.15
Nodes (19): AuthCallback, AuthClient, AuthOptions, createAuthStore(), accept(), signIn(), signOut(), start() (+11 more)

### Community 8 - "API contract"
Cohesion: 0.13
Nodes (15): API contract, `GET /api/shares/{token}` and `GET /api/shares/code/{code}`, `GET /api/worksheets/{id}/pdf`, Ownership and atomicity, Permanent problem codes (#198), `POST /api/problems/{id}/report`, `POST /api/problems/{id}/share`, `POST /api/problems/{id}/share/revoke` (+7 more)

### Community 9 - "practice.ts"
Cohesion: 0.07
Nodes (75): WorksheetBuilder(), authStore, client, accessToken(), accountRequest(), authorize(), base, cache() (+67 more)

### Community 10 - "_symbolic.py"
Cohesion: 0.06
Nodes (24): check_domain(), classify_expression(), components(), _defined_throughout(), differs(), is_primitive(), _not_real(), same_number_everywhere() (+16 more)

### Community 11 - "test_supabase_hosted.py"
Cohesion: 0.26
Nodes (9): check_private(), Client, denied(), main(), NoRedirect, require(), rows(), verify() (+1 more)

### Community 12 - "preview.py"
Cohesion: 0.11
Nodes (20): answer(), attempt(), Attempt, generate(), Generate, _problem(), Session, _session() (+12 more)

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
Cohesion: 0.13
Nodes (23): _api_error_response(), install_error_handlers(), assert_rejected(), bearer(), claims(), client(), FakeJwksClient, jwk() (+15 more)

### Community 20 - "pytest"
Cohesion: 0.08
Nodes (34): declared_variables(), parse_math_input(), test_domain_check_avoids_repeating_sum_domains_and_preserves_holes(), _cylindrical(), _log_positive(), _log_real(), _partial_xy(), _polar() (+26 more)

### Community 21 - "partial.py"
Cohesion: 0.07
Nodes (36): Built, _chain_template(), build(), _d(), declared(), _domain(), _evaluate(), _first() (+28 more)

### Community 25 - "MathWorkerError"
Cohesion: 0.19
Nodes (13): validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker(), test_limits_are_active_only_in_child(), test_memory_limit_stops_pathological_allocation() (+5 more)

### Community 29 - "test-db.py"
Cohesion: 0.42
Nodes (5): free_port(), main(), psql(), run(), wait_ready()

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 33 - "test_practice_api.py"
Cohesion: 0.08
Nodes (65): close_pool(), AnswerCheck, answer_of(), attempt(), client(), generate(), key(), pin_version() (+57 more)

### Community 50 - "Problem generation intent"
Cohesion: 0.17
Nodes (11): Definite and indefinite integrals, Difficulty, Generation model, Mathematical boundaries, Out of scope for this decision, Outcome, Pedagogically clean values, Practice modes (+3 more)

### Community 51 - "Educational content style intent"
Cohesion: 0.18
Nodes (10): Content in scope, Content outside this policy, Development-time enforcement, Educational content style intent, Out of scope for this decision, Outcome, Success criteria, Template catalogue (+2 more)

### Community 52 - "engine/models.py"
Cohesion: 0.04
Nodes (37): Polynomial, PartialFractionRational, _check(), encode(), generators(), generators(), DefiniteIntegral, DefiniteParams (+29 more)

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

### Community 67 - "vitest"
Cohesion: 0.09
Nodes (17): enter, Harness(), tuple, entries(), LegacyStructuredAnswerInput(), Props, StructuredAnswerInput(), Harness() (+9 more)

### Community 68 - "owned_records.py"
Cohesion: 0.09
Nodes (31): attempt_summaries(), AttemptRecord, ensure_profile(), get_problem(), insert_attempt(), insert_problem(), last_attempt(), list_problems() (+23 more)

### Community 69 - "api/worksheets.py"
Cohesion: 0.08
Nodes (35): practice_code(), PracticeCodeBody, area_topics(), attempt(), capacity(), generate(), _idempotency_key(), _invalid() (+27 more)

### Community 70 - "Setup"
Cohesion: 0.08
Nodes (34): _cartesian(), _disk(), DoubleTemplate, DoubleVariant, _polar(), _same_region(), _statement(), _steps() (+26 more)

### Community 71 - "topics"
Cohesion: 0.05
Nodes (63): ExpressionAnswer, det(), _factorial(), fractions(), linear_form(), minor(), nonzero_rows(), row_echelon() (+55 more)

### Community 72 - "Step"
Cohesion: 0.09
Nodes (23): _cell(), pmatrix(), Combinations, EigenParams, _line(), _m(), _plane(), _plane_point() (+15 more)

### Community 73 - "types.ts"
Cohesion: 0.06
Nodes (58): analyseComputationalAnswer(), ANSWER_VARIABLES, splitComputationalParts(), card(), ComputationalAnswerInput(), Props, DifficultyDots(), DifficultyScale() (+50 more)

### Community 74 - "App.tsx"
Cohesion: 0.07
Nodes (63): App(), handleDeleted(), handleLogOut(), handleSignIn(), route(), APP_ROUTES, NARROW_ROUTES, NotFoundPage() (+55 more)

### Community 75 - "test_engine_complex_numbers.py"
Cohesion: 0.06
Nodes (41): ComplexAnswer, _angle(), _base(), _cis(), _Complex, ComplexArgument, ComplexLinearEquation, ComplexProduct (+33 more)

### Community 76 - "HistoryPage.tsx"
Cohesion: 0.13
Nodes (15): Launch blockers (#39), Production checklist (#38), Running the checks, ReportProblem(), submit(), button(), openForm(), report (+7 more)

### Community 77 - "WorksheetBuilder.tsx"
Cohesion: 0.07
Nodes (62): DifficultyScaleProps, choices(), GroupRow(), Phase, Start, WorksheetForm(), addGroup(), generate() (+54 more)

### Community 78 - "transaction"
Cohesion: 0.06
Nodes (25): AttemptBody, delete_account(), DeleteBody, _encode_cursor(), _feedback(), GenerateBody, history(), learning_statistics() (+17 more)

### Community 79 - "api/shares.py"
Cohesion: 0.11
Nodes (21): by_code(), by_token(), _invalid_share(), _shared(), active_share(), copy_for_practice(), create_share(), lookup() (+13 more)

### Community 80 - "SyntaxProblem"
Cohesion: 0.32
Nodes (5): constantFraction(), numberFraction(), Parser, SyntaxProblem, validateExponent()

### Community 81 - "differentiation/single.py"
Cohesion: 0.06
Nodes (28): AnalysisTwoData, AnalysisTwoForm, finish(), _chain(), _components(), _d(), DerivativeData, DerivativeStep (+20 more)

### Community 82 - "test_engine_polynomials.py"
Cohesion: 0.06
Nodes (36): CombinationParams, BinomialCoefficient, BinomialConstantTerm, BinomialExponent, CoefficientParams, ConstantTermParams, CubicRemainder, Divisibility (+28 more)

### Community 84 - "e2e_local.py"
Cohesion: 0.14
Nodes (21): check(), combinations(), correct_answer(), cross_user(), database_failure(), derivatives(), full_flow(), key() (+13 more)

### Community 85 - "react-dom"
Cohesion: 0.09
Nodes (18): `POST /api/worksheets`, button(), buttons(), catalogue, groups(), made, shownLevels(), algebraSections (+10 more)

### Community 86 - "[[path]].ts"
Cohesion: 0.36
Nodes (4): Context, onRequest(), FORWARDED_HEADERS, proxyToApi()

### Community 88 - "test_engine_analysis_two.py"
Cohesion: 0.07
Nodes (22): MultipleData, MultipleForm, generators(), MatrixCombination, MatrixCommutator, MatrixProduct, DoubleIntegrals, generators() (+14 more)

### Community 89 - "react"
Cohesion: 0.13
Nodes (19): StatTile(), StatTileProps, AreaChips(), TopicChips(), getDisplayName(), mixedShares(), ProblemPage, AccountSettings() (+11 more)

### Community 90 - "differentiation.py"
Cohesion: 0.14
Nodes (7): DerivativeAnswer, DerivativeForm, generators(), PartialDerivativeParams, PartialDerivatives, SingleDerivativeParams, SingleDerivatives

### Community 91 - "test_shares_api.py"
Cohesion: 0.10
Nodes (39): client(), generate(), stored(), test_invalid_reports_are_refused_without_echoing_them(), test_nobody_reports_someone_elses_or_a_missing_problem(), test_owner_reports_a_problem_with_only_the_approved_fields(), test_reports_are_rate_limited_per_user(), test_reports_go_with_the_account() (+31 more)

### Community 92 - "FormulaField.test.tsx"
Cohesion: 0.15
Nodes (6): changes, Fake, FakeMathfield, Harness(), Layout, render()

### Community 93 - "api/practice.py"
Cohesion: 0.06
Nodes (14): _archived(), _decode_cursor(), listed_topics(), RateLimiter, Topic, ApiError, health(), lifespan() (+6 more)

### Community 94 - "test_health.py"
Cohesion: 0.16
Nodes (5): allowed_origins(), _known_origin(), test_allowed_origins_reads_environment(), test_allowed_origins_refuse_plain_http_outside_local_dev(), test_api_responses_carry_security_headers()

### Community 95 - "issue"
Cohesion: 0.05
Nodes (34): check(), is_engine_record(), issue(), levels(), is_archived(), stored_solution(), record_variables(), test_record_variables_are_read_and_validated() (+26 more)

### Community 96 - "test_engine_code_opening.py"
Cohesion: 0.09
Nodes (15): invalid_code(), lookup(), _opened(), _worker_unavailable(), OpenedCode, statement_latex(), _text(), open_problem_code() (+7 more)

### Community 97 - "test_worksheets_api.py"
Cohesion: 0.17
Nodes (33): client(), Compiled, compiled(), create(), generate(), key(), make_problem(), rows() (+25 more)

### Community 98 - "auth.py"
Cohesion: 0.06
Nodes (21): _auth_unavailable(), AuthUnavailableError, current_user(), get_token_verifier(), _invalid_token(), token_verifier(), TokenVerifier, _user_from_claims() (+13 more)

### Community 99 - "DefiniteView.tsx"
Cohesion: 0.10
Nodes (35): Axes(), DefiniteView(), PAD, RULES, tex(), ADR-0006, IndefiniteView(), NAMES (+27 more)

### Community 100 - "topics/catalogue.py"
Cohesion: 0.08
Nodes (44): AnalysisParams, DiagonalPower, EigenvectorValue, _Generator, generators(), LargestEigenvalue, LinePlaneIntersection, LinePlaneParams (+36 more)

### Community 101 - "build_expression"
Cohesion: 0.15
Nodes (5): algebraic_form(), _unit_as_x(), evaluated_tree(), build_expression(), test_global_budgets_and_unchanged_scalar_parser()

### Community 102 - "worksheet_graphs.py"
Cohesion: 0.14
Nodes (19): Canvas, _caption(), _curve(), definite(), _finite(), indefinite(), _n(), nice_ticks() (+11 more)

### Community 105 - "types.ts"
Cohesion: 0.08
Nodes (31): LABELS, expiryDate(), ShareControls(), copy(), APP_BASE, base, CONFUSABLE, shareCode() (+23 more)

### Community 106 - "AnswerInput"
Cohesion: 0.19
Nodes (7): AnswerInput(), insert(), move(), replace(), AnswerPreview(), Harness(), render()

### Community 107 - "integrals.py"
Cohesion: 0.28
Nodes (13): BasicIntegrals, DefiniteBasicIntegrals, DefinitePartsIntegrals, DefiniteRationalIntegrals, DefiniteSubstitutionIntegrals, DefiniteTrigonometricIntegrals, generators(), integral_generators() (+5 more)

### Community 108 - "topics.ts"
Cohesion: 0.12
Nodes (19): AreaChipsProps, ChipOption, ChipsProps, TopicChipsProps, ADR-0005, fetchMock, generate(), publicProblem (+11 more)

### Community 109 - "site.ts"
Cohesion: 0.12
Nodes (20): 2. Code changes, one PR after step 1, applyPageMeta(), crawlerFiles(), isSharedPath(), NOINDEX_PATHS, NOT_FOUND, page(), pageMeta (+12 more)

### Community 111 - "supabase_google_test_login.py"
Cohesion: 0.12
Nodes (3): collect_google_tokens(), handler_for(), CallbackChecks

### Community 112 - "ADR-005: multiple integrals and derivatives"
Cohesion: 0.13
Nodes (15): ADR-005: multiple integrals and derivatives, Amendment: practice areas (#144, 2026-10-26), Answers and variables, Areas and topics, Check budget, Consequences, Coordinate systems, Delivery (+7 more)

### Community 113 - "main.tsx"
Cohesion: 0.14
Nodes (9): analyticsAllowed(), BEACON_SRC, startWebAnalytics(), ErrorBoundary, root, @fontsource/geist, @fontsource/geist-mono, @fontsource/instrument-serif (+1 more)

### Community 114 - "parse_code"
Cohesion: 0.06
Nodes (37): canonical(), format_code(), parse_code(), ProblemCode, registry(), Registry, visit(), test_blocks_do_not_import_topics_generators_or_content() (+29 more)

### Community 115 - "Changelog"
Cohesion: 0.40
Nodes (4): 0.1.0 — MVP (2026-10-20), Changelog, Changes during MVP development, Unreleased

### Community 116 - "typing"
Cohesion: 0.10
Nodes (7): test_educational_catalogue_and_checker(), imported_modules(), test_new_engine_never_imports_the_old_generators(), test_old_saved_problem_opens_with_its_stored_statement(), inspect(), main(), ContentTests

### Community 117 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, eslint, @eslint/js, jsdom, @types/katex, @types/react, @types/react-dom, @types/three (+4 more)

### Community 118 - "answerSyntax.test.ts"
Cohesion: 0.18
Nodes (10): COMPLEX, CYLINDRICAL, POLAR, REJECTED, SUPPORTED, ADR-0005, VARIABLE_REJECTED, VARIABLE_SUPPORTED (+2 more)

### Community 119 - "dependencies"
Cohesion: 0.20
Nodes (10): dependencies, @fontsource/geist, @fontsource/geist-mono, @fontsource/instrument-serif, katex, mathlive, react, react-dom (+2 more)

### Community 120 - "sympy"
Cohesion: 0.07
Nodes (22): ConstantExpressionAnswer, FullRealExpressionAnswer, AnalysisOneData, AnalysisOneForm, bisect_exp(), evaluate(), exp_bounds(), canonical_arctangents() (+14 more)

### Community 121 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, lint:content, test, typecheck

### Community 122 - "spec.py"
Cohesion: 0.13
Nodes (14): level(), SetupLike, _interval(), _numeric(), value(), parameter_points(), region2d_setup(), to_xy() (+6 more)

### Community 124 - "Analysis II curriculum (#146)"
Cohesion: 0.13
Nodes (10): HANDOFF — Analysis I (#145), HANDOFF — Analysis II (#146), Project status, Analysis I curriculum (#145), Persistence and verification, Analysis II curriculum (#146), Integration and verification, Issuing matrix (+2 more)

### Community 125 - "evaluate"
Cohesion: 0.17
Nodes (14): _bisect(), _changes_sign(), _component(), definite_data(), _distinct(), _f(), indefinite(), _poles() (+6 more)

### Community 126 - "region2d.test.tsx"
Cohesion: 0.16
Nodes (20): annulus, sinc, triangle, Region2dVisual(), ThreeView, compileRegion(), at(), boundary() (+12 more)

### Community 127 - "test_engine_algebra.py"
Cohesion: 0.21
Nodes (9): algebra_generators(), AlgebraGenerator, AlgebraParams, ComplexNumbers, generators(), Matrices, PracticePartialFractions, RootSum (+1 more)

### Community 128 - "test_engine_algebra_expansion.py"
Cohesion: 0.12
Nodes (19): generators(), PolynomialQuotient, QuadraticRemainder, QuadraticRemainderParams, RemainderParams, RemainderTheorem, rebuild(), test_polynomial_answers_are_checked_in_the_limited_worker() (+11 more)

### Community 129 - "invalid_request"
Cohesion: 0.20
Nodes (6): _error(), internal_error(), invalid_request(), request_boundary(), _secure(), HTTP failures and retry behavior

### Community 130 - "engine/practice.py"
Cohesion: 0.08
Nodes (27): build(), Catalogue, load(), lookup(), pool(), StoredCell, StoredModel, StoredProblem (+19 more)

### Community 131 - "test_engine_computational_api.py"
Cohesion: 0.07
Nodes (22): render(), DiagramModel, PlotDiagram, PlotPath, PlotPoint, validate_plot(), _build(), build_visual() (+14 more)

### Community 132 - "AnalysisTwo"
Cohesion: 0.28
Nodes (3): AnalysisTwo, AnalysisTwoParams, SymbolicAnalysisTwo

### Community 133 - "InputContract"
Cohesion: 0.05
Nodes (40): CategoryAnswer, combine(), ComputationalAnswer, _domain(), _expression(), FormulaAnswer, LimitAnswer, OrderedAnswer (+32 more)

### Community 134 - "_worked"
Cohesion: 0.17
Nodes (9): legacy_code_is_never_run(), migrated(), Saved, owned(), test_an_archived_problem_opens_from_its_stored_rows(), test_an_archived_problem_prints_its_steps_without_a_graph(), test_an_archived_problem_reveals_its_stored_solution(), test_checking_an_archived_problem_is_an_archived_error() (+1 more)

### Community 135 - "Parameters"
Cohesion: 0.15
Nodes (11): DensitySegment, ExponentialDistribution, NormalDistribution, PolynomialDensity, UniformDistribution, _cdf(), _density(), evaluate() (+3 more)

### Community 136 - "answers/structured.py"
Cohesion: 0.17
Nodes (19): FiniteSetAnswer, RealScalarAnswer, BooleanProbability, _build(), Built, finish(), finite(), joint() (+11 more)

### Community 137 - ".kind"
Cohesion: 0.31
Nodes (3): metric(), statistics(), Structured answer instructions (#200)

### Community 138 - "MathInputError"
Cohesion: 0.11
Nodes (18): _parse(), parse_computational(), _real_set(), split_parts(), _constant_fraction(), MathInputError, MathInputTooLong, MathNode (+10 more)

### Community 139 - "test_worksheet_tex.py"
Cohesion: 0.06
Nodes (50): download_pdf(), label(), _space_cm(), compile_pdf(), escape_text(), filename(), _log_tail(), _pdflatex() (+42 more)

### Community 140 - "DeterministicRNG"
Cohesion: 0.05
Nodes (21): IntegerRange, bounded(), draw_entries(), draw_invertible(), _draw_eigen(), candidate(), valid(), _draw_planes() (+13 more)

### Community 141 - "test_engine_probability_foundation.py"
Cohesion: 0.20
Nodes (11): mean_interval(), mean_statistic(), reject(), _differences(), evaluate(), paired(), test_inference_boundaries_and_center_width(), test_new_grammars_reject_invalid_input() (+3 more)

### Community 142 - "FiniteDistribution"
Cohesion: 0.19
Nodes (5): FiniteDistribution, JointDistribution, test_finite_distribution_and_pushforward_by_independent_enumeration(), test_joint_marginals_conditionals_covariance_independence(), Distribution block design

### Community 143 - "Probability and Statistics curriculum (#200)"
Cohesion: 0.22
Nodes (7): HANDOFF — Probability and Statistics (#200), implementation checkpoint, Approved release, Delivery and verification after approval, Mathematical conventions and bounded records, New answer kinds and input UI, Probability and Statistics curriculum (#200), Reference conventions

### Community 144 - "StubClient"
Cohesion: 0.13
Nodes (5): CheckFailure, DenialChecks, SingleUserChecks, SingleUserClient, StubClient

### Community 145 - "algebra_expressions.py"
Cohesion: 0.14
Nodes (12): generators(), RadicalParams, RadicandParams, RationalizedAnswer, RationalizeDenominator, RationalizeParams, SimplifiedRadicalAnswer, SimplifyRadicals (+4 more)

### Community 146 - "Computational contracts and Graphify checkpoint"
Cohesion: 0.33
Nodes (5): Computational contracts and Graphify checkpoint, Graphify, explicitly delegated by the owner, Observed verification, Review, recovery and next action, Scope and result

### Community 147 - "catalogue_records"
Cohesion: 0.17
Nodes (10): catalogue_records(), Picker, record_key(), test_cold_symbolic_issuing_and_worksheet_preparation_call_no_sympy(), test_combinations_worksheet_picker_exhausts_the_pool_without_duplicate_codes(), picker(), test_a_cell_is_used_up_without_repeats_and_then_capped(), test_capacity_is_the_cell_size() (+2 more)

### Community 148 - "MVP end-to-end check (#13)"
Cohesion: 0.50
Nodes (3): Automated: `scripts/e2e_local.py`, Manual: deployed site, MVP end-to-end check (#13)

### Community 149 - "geometry.ts"
Cohesion: 0.18
Nodes (14): axisOrigin(), AxisTick, axisTicks(), Mesh3D, Scene3D, ADR-0006, Vec3, canvasHeight() (+6 more)

### Community 151 - "test_engine_probability.py"
Cohesion: 0.15
Nodes (14): BooleanAnswer, IntervalAnswer, generators(), scalar(), source(), test_all_45_approved_cells_and_74_distinct_frozen_identities_are_issued(), test_boolean_templates_have_both_outcomes_and_inference_boundary_examples(), test_event_set_operations_include_disjoint_intersections_and_empty_differences() (+6 more)

### Community 153 - "mathEditor.ts"
Cohesion: 0.12
Nodes (17): FUNCTIONS, BARS, COMMAND_FUNCTIONS, CONSTANTS, INVERSE, Item, latexToAnswer(), needsTimes() (+9 more)

### Community 154 - "test_engine_curriculum.py"
Cohesion: 0.18
Nodes (8): AlgebraData, AlgebraForm, _evaluate(), test_integral_curriculum_snapshot(), test_multiple_curriculum_snapshot_and_independent_orders(), test_partial_curriculum_snapshot(), test_scalar_curriculum_snapshots(), test_single_derivative_curriculum_snapshot()

### Community 155 - "generators/analysis.py"
Cohesion: 0.14
Nodes (16): AnalysisData, AnalysisForm, _evaluate(), analysis_generators(), AnalysisGenerator, DifferentialEquations, generators(), ImproperIntegrals (+8 more)

### Community 156 - "test_engine_answers.py"
Cohesion: 0.05
Nodes (43): AntiderivativeAnswer, NumberAnswer, Answer, test_answer_types_do_not_import_legacy_generators(), test_antiderivative_checks_all_domain_components(), test_antiderivative_constant_and_equivalence_rules(), test_derivative_rejects_constants_and_domain_holes(), test_expression_runs_under_worker_limits() (+35 more)

### Community 157 - "test_engine_catalogue.py"
Cohesion: 0.10
Nodes (8): main(), test_a_new_entry_is_built_without_a_second_registration(), test_catalogue_build_failure_stops_release_before_activation(), test_failed_build_leaves_the_previous_artifact_untouched(), test_incomplete_or_incompatible_catalogue_is_refused(), test_missing_pool_fails_closed_instead_of_generating(), test_picks_do_not_expose_mutable_cached_data(), test_unfillable_cell_aborts_with_a_bounded_candidate_count()

### Community 158 - "test_engine_integrals.py"
Cohesion: 0.24
Nodes (7): IntegralForm, answer_text(), test_each_cell_checks_its_own_answer_and_builds_the_existing_visual(), test_each_migrated_cell_checks_inside_the_limited_worker(), test_forms_have_exact_primitives_and_valid_bounds(), test_malformed_parameters_are_refused(), test_native_indefinite_answers_keep_the_constant_policy()

### Community 160 - "Sample"
Cohesion: 0.26
Nodes (4): median(), PairedSample, Sample, test_sample_statistics_against_standard_library_and_normal_equations()

### Community 161 - "Analysis exercise-sheet generator expansion"
Cohesion: 0.12
Nodes (14): primitive(), Analysis source-family contracts (#233), Existing boundary and extension plan for #234, Family gap matrix, Source components and independent mathematical cases, Accepted staging and computational contracts, Analysis exercise-sheet generator expansion, Deliverable (+6 more)

### Community 162 - "math.ts"
Cohesion: 0.10
Nodes (23): _loop(), across(), at(), evaluate(), _evaluate(), _log(), _pow(), _sqrt() (+15 more)

### Community 163 - "spec.ts"
Cohesion: 0.10
Nodes (23): Tree, isRegion(), box, cylinder, halfCone, simplex, Edge, EDGES (+15 more)

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
Cohesion: 0.29
Nodes (10): native_params(), _name(), solution_setup(), _spec(), test_every_record_builds_a_small_valid_spec(), test_every_template_is_covered(), test_the_spec_follows_the_coefficient(), test_the_window_contains_the_region() (+2 more)

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
Cohesion: 0.35
Nodes (8): solid3d(), solution_setup(), test_every_record_builds_a_small_valid_spec(), test_every_template_is_covered(), test_the_integrand_is_not_in_the_spec(), test_the_spec_ignores_the_coefficient(), test_the_window_contains_the_solid(), test_trees_round_trip_against_sympy()

### Community 176 - "202610150001_initial_schema.sql"
Cohesion: 0.29
Nodes (8): attempts_problem_idx, attempts_user_created_idx, private.problem_solutions, problems_user_created_idx, public.attempts, public.problems, public.profiles, public.topics

### Community 178 - "number.py"
Cohesion: 0.31
Nodes (5): _bounded(), _fraction(), _Invalid, _NonReal, _Unsupported

### Community 180 - "Launch runbook (#39)"
Cohesion: 0.40
Nodes (5): 1. Decisions only the owner can make, 3. External configuration (owner, in this order), 4. Verification on the domain, 5. Rollback, Launch runbook (#39)

### Community 181 - "202610220001_worksheets.sql"
Cohesion: 0.33
Nodes (5): problems_user_worksheet_created_idx, public.worksheet_items, public.worksheets, worksheet_items_problem_idx, worksheets_user_created_idx

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

## Knowledge Gaps
- **36 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `@types/three` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1438 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **76 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `vitest` connect `vitest` to `package.json`, `auth.test.ts`, `practice.ts`, `geometry.ts`, `mathEditor.ts`, `spec.ts`, `expression.ts`, `types.ts`, `App.tsx`, `HistoryPage.tsx`, `WorksheetBuilder.tsx`, `react-dom`, `[[path]].ts`, `react`, `FormulaField.test.tsx`, `DefiniteView.tsx`, `AnswerInput`, `topics.ts`, `site.ts`, `main.tsx`, `answerSyntax.test.ts`, `region2d.test.tsx`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 79 inferred relationships involving `DeterministicRNG` (e.g. with `PartialForm` and `DerivativeForm`) actually correct?**
  _`DeterministicRNG` has 79 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `README.md` be split into smaller, more focused modules?**
  _Cohesion score 0.10591133004926108 - nodes in this community are weakly interconnected._
- **Why does `definite_data()` connect `evaluate` to `sympy`, `math.ts`, `test_engine_computational_api.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 83 inferred relationships involving `Step` (e.g. with `AlgebraData` and `_evaluate()`) actually correct?**
  _`Step` has 83 INFERRED edges - model-reasoned connections that need verification._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._