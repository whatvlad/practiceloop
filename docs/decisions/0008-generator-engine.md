# ADR-008: composable generator engine

Date: 2026-11-01. Status: **final implementation record** (#199, completing #162).
Owner: Vlad (whatvlad). The four-layer design and frozen interfaces were accepted
in the GrillMe review #172; its decisions are recorded in
[the review](../architecture/generator-engine-review.md). Owner acceptance of
this final record must be recorded in #199's linked pull request before closure.
Future curriculum work (#147, #145, #146, #200) is outside this refactor.

## Context and result

Topic-specific generators and a central problem-type checker made every new
family edit shared dispatch code. Saved legacy records also depended on replay.
The owner chose Python + SymPy, a composable engine, permanent reversible codes,
and a read-only archive for pre-engine problems (#162, 2026-10-30).

All 21 current public topics now use `backend/app/engine/`. The former
`app/generators/`, per-module result types, `core.Exercise`, legacy replay and
checker branches have been removed. Archived problems use their stored statement,
answer and steps; their attempts return `409 problem_archived`. No data migration,
answer rewriting or deletion of saved problems is required.

## Four layers

| Layer | Location | Responsibility |
|---|---|---|
| Mathematical blocks/forms | `app/engine/blocks/` | Strict bounded parameters, exact mathematical data, domains and independently proved transformations; no public topic catalogue or English product copy |
| Typed answers | `app/engine/answers/` | `kind`, `latex()`, `check(MathNode) -> Outcome`; each kind owns its comparison policy |
| Task generators | `app/engine/generators/` | Draw typed parameters, build one immutable `Task`, declare code metadata and English step text; compose blocks and typed generator results |
| Topic views | `app/engine/topics/catalogue.py` | Public slug/title/area, levels with parameter predicates, mixed weight, worksheet space and optional visual |

There is no required generator base class. The `TaskGenerator` protocol permits
composition rather than a deep inheritance hierarchy. `Task` contains statement,
steps, answer, display/test metadata, canonical code and generator version.
`Step` holds a text key and LaTeX; the generator supplies its English explanation.
Metadata is never a hidden composition interface.

### Draw, composition and build

`draw(seed)` makes all PRNG calls and returns a strict frozen `Drawn` subtype
with the drawn values. `build(params)` is pure over those values. Topic filters
read typed parameters, without repeating the random stream or inspecting a
built task. A topic makes at most 64 candidate draws. A build rejection is
logged; the 1,000-seed tests require shipped topic cells to build without one.

The original rational slice demonstrates composition: `IndefiniteParams` holds
`PartialFractionParams | Polynomial`; `PartialFractions.decompose(params)`
returns typed decomposition/domain data. `DefiniteParams` contains the inner
indefinite parameters; `IndefiniteIntegral.integrate(params)` exposes a typed
integrand, primitive, domain and steps that the outer generator evaluates at
its bounds. Neither generator rebuilds an inner task merely to read metadata.
Native curriculum forms similarly expose integral or multiple-integral setup
data. Exact proofs are cached by the drawn mathematical values, excluding seed.

### Registration and extension

Each trusted generator module exports `generators()`, returning its instances.
`generators/catalogue.py` discovers these providers only inside the application
package, registers their immutable metadata and validates the dependency graph.
It rejects duplicate versions/prefix associations, missing dependencies and
cycles. There is no registration list or per-version replay/checking chain.
Private helper modules may omit the provider. This is repository code discovery,
not loading a module, expression or plugin named by a request.

For a task using an existing answer kind and reusable block:

1. Add one generator module with a strict `Drawn` model, frozen version/prefix/
   family/code version, answer class, dependencies, step text, `draw`, `build`
   and a `generators()` provider. Reuse typed blocks/results for composition.
2. Add its declarative topic entry and typed level predicates. A genuinely new
   public slug also needs an additive Supabase `topics` row migration because
   saved problems reference those rows. Existing migrated slugs need none.
3. Add at least three new golden codes, exact mathematical/domain tests and
   own-answer worker tests. The 1,000-seed and release-pool tests discover the
   new version/cells. Never replace existing golden entries.
4. Rebuild the private release catalogue before starting the API or deploying.

No central registry, answer checker, existing generator or frontend topic bank
needs editing. `test_engine_extension.py` adds a temporary provider file and a
topic entry, then generates and checks it without changing central code.
A genuinely new answer kind, block or visual needs its own design and UI when
there is an actual consumer; matrix/vector/interval/set/boolean kinds remain
future curriculum work, as accepted in review decision 11.

## Frozen interfaces and versions

Since #189, `Answer`, `Outcome`, `Task`, `Step`, `TaskGenerator`, `Topic`, `Choice`,
PRNG v1 and the problem-code format are frozen. Changing them needs an ADR
amendment. Adding a generator, block or answer kind is not such a change.
One compatible Topic amendment (#193) permits `mixed_weight = 0`, preserving
the definite-integrals topic's exclusion from mixed practice. Other fields and
protocols are unchanged. Provider discovery adds no generator instance method.

A generator may optionally expose private `input_variables(drawn_params)` for
plain grammar metadata. This does not change the frozen protocol. Partial,
multivariable and ODE generators return fresh allowlisted real/positive variable
mappings from typed parameters. The API derives this from the code without
building a symbolic task; saved records still contain only version and code.

Once shipped, a generator's draw order and mathematical/rendered output are
immutable. Corrections require a new version and new golden entries. Every
shipped engine version remains registered, including the original slice. The
old engine-slice version strings need not be renamed even where a pre-engine
archive used the same string: the presence of a code identifies engine records.

## Permanent problem codes

The canonical format is `<PREFIX>-<VERSION>-<16_DIGIT_SEED>-<TWO_DIGIT_CHECK>`.
PRNG v1 is a SHA-256-based deterministic stream, not Python's `random`.
`codes.py` validates ASCII length/syntax, registered prefix/version and the
position-weighted mod-97 typo check. Case, whitespace and dashes normalize to
one code. A checksum detects typos; it is not authentication or encryption.

The private engine record is exactly `{generator_version, code}`. Replay parses
the registry entry, draws parameters and builds the task, checking that its code
matches. A code is permanent and independent of accounts, attempts and reveals.
It cannot be revoked. Revocable 90-day shares remain a separate feature.

`/p/<code>` opens every golden version, including historical engine slices.
Historical declarative views reuse current public topic metadata; frozen task
output and normal issuing pools stay unchanged. Anonymous `GET /codes?code=...`
returns only statement, topic and difficulty. Google sign-in preserves the route.
Authenticated `POST /codes/practice` uses a canonical idempotency hash and saves
a separate recipient-owned copy with no attempts or reveals. Normal owner-scoped
attempt/reveal endpoints then apply. Invalid/unknown codes are clear 400 errors;
malformed requests are 422. No answer/solution/parameters leave the backend before
an authorized reveal (ADR-002).

## Verified release catalogue

`python -m app.engine.catalogue` builds 64 unique verified codes per declared
topic x level, with rendered statement, answer and steps. The current catalogue
has 101 cells: 99 served public cells and two internal original-slice views.
The private JSON artifact is ignored, release-local and never a browser asset.
Writing is atomic; an incomplete/unfillable catalogue aborts the build. Startup
refuses missing or incompatible cells, versions, codes or pool sizes.

Normal practice and worksheets only read/pick rendered data, even on a cold
cell. They never run symbolic generation or fall back to a legacy generator in
the API. Practice excludes the learner's recent half-pool of records; a worksheet
never repeats a code. Public topic entries supply levels, weights, writing space
and visuals. The fixed untracked guest demo also selects one indefinite example
from the pre-rendered basic level-1 pool; sessions do not unlock extra practice.

Oracle builds and verifies the catalogue before activating a release. A failed
build keeps the previous release; rollback uses that release's own catalogue.
Arbitrary permanent codes need not be in a pool, so code opening reconstructs
in the bounded worker and retains at most 128 private rendered results in the API.
This does not add symbolic work to the normal request process.

## Public input and bounded checking

`app.math_input` is the public bounded-input interface. It exports `MathNode`,
input errors, variable declarations, `parse_math_input(text)` and
`build_expression(validated_tree, evaluate=False)`. The latter builds SymPy
objects from allowlisted AST nodes; it never parses/evaluates a learner string.
Engine answers no longer import a private worker helper or a legacy checker.
The parser/AST/grammar and numeric limits are unchanged by moving the modules.
The frontend's syntax corpus mirrors the backend parser tests.

The shared worker applies 2 s CPU, 256 MiB address-space, 64 KiB combined-output
and 3 s wall limits, with one admission slot. It replays one code, parses the
answer in its declared grammar and calls `task.answer.check(tree)`. There is
no dispatch on legacy versions or problem classes. Failed children are killed
and reaped. Grammar rejection is invalid; a resource limit or undecidable result
is a retryable service error, never evidence of a mathematically wrong answer.
Code reconstruction uses the same resource/admission boundaries.

Current answer kinds are exact number (including non-SymPy combinations), real
expression, antiderivative and derivative. Antiderivatives require one explicit
arbitrary constant and a single numeric offset over all domain components.
Derivatives, scalar definite/multiple integrals and initial-value solutions do
not allow an arbitrary constant. Domain checks inspect unevaluated subexpressions
so cancellation cannot hide a hole. Declared multivariable/positive domains are
retained. Symbolic proof decides equality; numerical samples can certify a
difference only. Native wrong answers use general feedback, with explicit
missing-constant outcomes. Historic feedback codes remain readable in history.

## Curriculum, visuals and archive

Migrations #193-#197 retain every current topic, approved level, coefficient
range, mixed weight and worksheet space. Existing scalar Algebra tasks need
ExpressionAnswer, not new matrix/complex editors. Single/multiple integral
visuals consume typed `IntegralData`/`SetupLike`; derivative topics have none.
Visuals are generated only for authorized solutions. Archive reveals/printing
use saved fields and never regenerate a graph or invoke old mathematical code.

Two errors in pre-engine `symbolic-v1` were corrected in new native versions:
the series with ratio a/(a+1) sums to a+1, and the x derivative of ax^2y+by is
2axy. Saved archive answers are preserved. New regressions independently prove
the corrected results and reject the former wrong answers.

The legacy source and checker modules are removed. The archive boundary depends
only on current served topic metadata, code presence and stored database fields.
No old record is replayed to reopen, reveal, share or print it. Its check returns
409 without invoking a worker. Existing engine codes remain fully checkable.

## Verification and remaining work

Golden snapshots pin every shipped version's code, statement, answer, steps and
metadata. Each topic cell has a 1,000-seed sweep; every pooled code replays its
rendered fields. Frozen curriculum fixtures retain 342 integral parameter sets,
114 single and 84 partial derivatives, 44 geometry variants, 100 Algebra and
175 remaining-analysis forms, plus all public product metadata. Exact native
proofs and independent integration orders complement these regression snapshots.
Tests cover constants/domains, declared variables, adversarial worker limits,
reaping/admission, all golden-code openings, archive ownership/reveals/printing,
PostgreSQL isolation/idempotency and the HTTP end-to-end flow.

The original MVP specification, database/history data, dependencies and frozen
engine outputs are unchanged. TeX verification remains disabled by owner decision
until #181; this refactor does not re-enable it. Graphify is optional development
tooling and has no application/runtime dependency. Future syllabus expansion and
new answer kinds are #147/#145/#146/#200, not unfinished legacy migration.
