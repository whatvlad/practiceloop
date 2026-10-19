# Graph Report - PracticeLoop (2026-10-19)

## Corpus Check
- 139 files · ~55,665 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 7, .toml 3, .css 3)

## Summary
- 910 nodes · 1855 edges · 71 communities (35 shown, 36 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `58bb9f45`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- README.md
- package.json
- PracticeLoop — MVP Specification
- test_basic.py
- Must-have before production
- test_math_worker.py
- compilerOptions
- auth.test.ts
- test_health.py
- server.ts
- types.ts
- test_supabase_hosted.py
- FormulaField.test.tsx
- Prompt for Claude Code: implement the PracticeLoop frontend design
- pull_request_template.md
- system/README.md
- HANDOFF.md
- REVIEW_PROTOCOL.md
- STATUS.md
- MathInputError
- setup-graphify.sh
- practiceloop-backend
- TASK_PROTOCOL.md
- PracticeLoop production roadmap
- 0001-frontend.md
- 0002-data-security.md
- Routes
- vite-env.d.ts
- Problem generation intent
- Educational content style intent
- PracticeLoop agent rules
- MathKeypad.tsx
- ADR-003: bounded real-valued integration answers
- ADR-004: backend-owned practice records and distinct-problem counts
- PracticeLoop
- Google authentication
- release.sh
- AnswerInput.test.tsx
- PracticeLoop domain language
- answerSyntax.ts
- bootstrap.sh
- rollback.sh
- Oracle backend deploy
- FormulaField.tsx
- mathEditor.ts
- AnswerInput
- Issue #3 delivery and first-project procedure
- main.tsx
- WORKFLOW.md

## God Nodes (most connected - your core abstractions)
1. `MathInputError` - 28 edges
2. `Reader` - 24 edges
3. `parse_math_input()` - 19 edges
4. `PracticeLoop — MVP Specification` - 19 edges
5. `App()` - 18 edges
6. `AnswerInput()` - 18 edges
7. `_Parser` - 17 edges
8. `react` - 17 edges
9. `MathNode` - 16 edges
10. `validate_math_input()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Bounded mathematical input` --references--> `MathWorkerError`  [INFERRED]
  docs/architecture/MATH_INPUT.md → backend/app/services/math_worker.py
- `Basic-integral generator` --references--> `seed()`  [INFERRED]
  docs/architecture/BASIC_GENERATOR.md → frontend/src/data/mock/server.ts
- `Basic-integral generator` --references--> `InternalProblem`  [INFERRED]
  docs/architecture/BASIC_GENERATOR.md → backend/app/generators/basic.py
- `Bounded mathematical input` --references--> `MathInputError`  [INFERRED]
  docs/architecture/MATH_INPUT.md → backend/app/services/math_parser.py
- `Bounded mathematical input` --references--> `MathInputTooLong`  [INFERRED]
  docs/architecture/MATH_INPUT.md → backend/app/services/math_parser.py

## Import Cycles
- None detected.

## Communities (71 total, 36 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.15
Nodes (6): Changelog, Unreleased, Architecture and MVP analysis, Decision index, Open decisions — resolve before dependent features, Security policy

### Community 1 - "package.json"
Cohesion: 0.05
Nodes (38): dependencies, katex, mathlive, react, react-dom, @supabase/supabase-js, devDependencies, eslint (+30 more)

### Community 2 - "PracticeLoop — MVP Specification"
Cohesion: 0.09
Nodes (23): 10. Show Solution, 11. History, 12. User Profile, 13. Backend, 14. Database, 15. Frontend, 16. Infrastructure, 17. MVP Scope (+15 more)

### Community 3 - "test_basic.py"
Cohesion: 0.08
Nodes (20): BasicParameters, BasicTemplate, generate_basic(), InternalProblem, replay_basic(), SolutionStep, _verify(), PublicProblem (+12 more)

### Community 4 - "Must-have before production"
Cohesion: 0.11
Nodes (17): Authentication and personal data, Expected implementation surface, Landing page and CTA, Must-have before production, Optional or deferred, Practice flow, PracticeLoop production readiness plan, Privacy and analytics (+9 more)

### Community 5 - "test_math_worker.py"
Cohesion: 0.11
Nodes (15): MathWorkerError, validate_math_input(), _replace_child_computation(), test_combined_stdout_stderr_is_bounded(), test_cpu_limit_stops_pathological_work(), test_interrupted_parent_reaps_worker(), test_invalid_input_does_not_start_a_worker(), test_limits_are_active_only_in_child() (+7 more)

### Community 6 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, jsx, lib, module, moduleResolution, noEmit, noUnusedLocals, noUnusedParameters (+5 more)

### Community 7 - "auth.test.ts"
Cohesion: 0.13
Nodes (21): AuthCallback, AuthClient, AuthOptions, AuthSnapshot, createAuthStore(), accept(), signIn(), signOut() (+13 more)

### Community 8 - "test_health.py"
Cohesion: 0.12
Nodes (3): allowed_origins(), health(), test_allowed_origins_reads_environment()

### Community 9 - "server.ts"
Cohesion: 0.06
Nodes (82): App(), handleLogOut(), handleSignIn(), APP_ROUTES, NotFoundPage(), harness, renderAt(), signedIn (+74 more)

### Community 10 - "types.ts"
Cohesion: 0.06
Nodes (57): AnswerInputProps, AnswerPreview(), ApiStatusNotice(), card(), DifficultyDots(), DifficultyScale(), DifficultyScaleProps, AttemptStatus() (+49 more)

### Community 11 - "test_supabase_hosted.py"
Cohesion: 0.05
Nodes (17): collect_google_tokens(), handler_for(), CallbackChecks, check_private(), CheckFailure, Client, denied(), main() (+9 more)

### Community 12 - "FormulaField.test.tsx"
Cohesion: 0.16
Nodes (5): changes, Fake, FakeMathfield, Harness(), render()

### Community 13 - "Prompt for Claude Code: implement the PracticeLoop frontend design"
Cohesion: 0.29
Nodes (6): Definition of done, Goal, Prompt for Claude Code: implement the PracticeLoop frontend design, Rules, Source of truth, What to build

### Community 14 - "pull_request_template.md"
Cohesion: 0.40
Nodes (4): How it was tested, Risks, What changed, Why

### Community 15 - "system/README.md"
Cohesion: 0.33
Nodes (5): Content fundamentals, Directions, Iconography, Using the components, Visual foundations

### Community 25 - "MathInputError"
Cohesion: 0.11
Nodes (23): _constant_fraction(), MathInputError, MathInputTooLong, MathNode, _normalise(), _number_fraction(), parse_math_input(), _Parser (+15 more)

### Community 30 - "PracticeLoop production roadmap"
Cohesion: 0.10
Nodes (20): Confirmed product direction, Current execution order, Explicitly deferred work, GitHub Issue structure, Implementation stages, Issue #31: publish approved intent documents, Issue #32: publish Graphify agent tooling, Issue #33: working preview infrastructure (+12 more)

### Community 33 - "Routes"
Cohesion: 0.14
Nodes (13): API contract, `GET /api/problems`, `GET /api/problems/{id}`, `GET /api/profile`, `GET /api/topics`, HTTP failures and retry behavior, Ownership and atomicity, `POST /api/problems` (+5 more)

### Community 50 - "Problem generation intent"
Cohesion: 0.17
Nodes (11): Definite and indefinite integrals, Difficulty, Generation model, Mathematical boundaries, Out of scope for this decision, Outcome, Pedagogically clean values, Practice modes (+3 more)

### Community 51 - "Educational content style intent"
Cohesion: 0.18
Nodes (10): Content in scope, Content outside this policy, Development-time enforcement, Educational content style intent, Out of scope for this decision, Outcome, Success criteria, Template catalogue (+2 more)

### Community 52 - "PracticeLoop agent rules"
Cohesion: 0.22
Nodes (7): After a merge, Before starting work, Collaboration rules, GitHub Issue names, Graphify, PracticeLoop agent rules, Claude Code

### Community 53 - "MathKeypad.tsx"
Cohesion: 0.20
Nodes (7): Key, KeypadInsert, KeypadMove, MAIN_KEYS, MathKeypad(), MathKeypadProps, MORE_KEYS

### Community 54 - "ADR-003: bounded real-valued integration answers"
Cohesion: 0.22
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

### Community 59 - "AnswerInput.test.tsx"
Cohesion: 0.33
Nodes (3): Harness(), render(), react-dom

### Community 61 - "answerSyntax.ts"
Cohesion: 0.08
Nodes (38): absBig(), analyseAnswer(), AnswerAnalysis, constantFraction(), Fraction, FUNCTION_SET, gcd(), HINTS (+30 more)

### Community 64 - "Oracle backend deploy"
Cohesion: 0.25
Nodes (7): Before adding Supabase credentials (human only), CORS, On the VM, One-time setup, Oracle backend deploy, Rollback and recovery, When the API is down

### Community 65 - "FormulaField.tsx"
Cohesion: 0.21
Nodes (14): answerLatex(), byName(), configureKeyboard(), FormulaField(), FormulaFieldProps, keycap(), loadMathLive(), MathLive (+6 more)

### Community 66 - "mathEditor.ts"
Cohesion: 0.12
Nodes (20): FUNCTIONS, BARS, COMMAND_FUNCTIONS, exponentText(), INVERSE, Item, join(), latexToAnswer() (+12 more)

### Community 67 - "AnswerInput"
Cohesion: 0.47
Nodes (4): AnswerInput(), insert(), move(), replace()

### Community 68 - "Issue #3 delivery and first-project procedure"
Cohesion: 0.20
Nodes (9): Backup and rollback, Current verification status, Database preparation, Hosted Auth and PostgREST verification (human only), Human-only Google test helper (no token copying), Human provisioning, without sharing credentials, Issue #3 delivery and first-project procedure, Migration workflow (+1 more)

## Knowledge Gaps
- **10 isolated node(s):** `practiceloop-backend`, `@types/katex`, `@types/react`, `@types/react-dom`, `eslint` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 413 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Basic-integral generator` connect `test_basic.py` to `server.ts`, `ADR-003: bounded real-valued integration answers`?**
  _High betweenness centrality (0.357) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `MathInputError` (e.g. with `test_function_count_is_bounded()` and `test_group_nesting_is_bounded()`) actually correct?**
  _`MathInputError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `practiceloop-backend`, `@types/katex`, `@types/react` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05128205128205128 - nodes in this community are weakly interconnected._
- **Why does `seed()` connect `server.ts` to `test_basic.py`?**
  _High betweenness centrality (0.326) - this node is a cross-community bridge._
- **Should `PracticeLoop — MVP Specification` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._
- **Should `test_basic.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0784313725490196 - nodes in this community are weakly interconnected._
