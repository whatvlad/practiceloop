# Generator Refactor MVP

Plan for #162, agreed by Vlad on 2026-10-30 (see `docs/decisions/DECISIONS.md`).
Each MVP step below is its own Issue; their order is the `Order` field of the
Implementation Queue project. Stack stays Python + SymPy.

The MVP is one vertical slice: the new engine, a few generators that overlap
across areas, and one topic served through the real API. It ends with the
GrillMe review, and no further topic migration starts before that review is
accepted.

## Rules for every issue

- One issue is one PR from the latest `main`, with green CI.
- Old generator code is not changed during the MVP; the new engine lives next
  to it.
- New generators (including Feijhoaaaaa's Codex work) are written only against
  the new interfaces once #163 is merged (agreed between Vlad and Feijhoaaaaa
  on 2026-10-30). The Algebra and Analysis Issues #145-#147 depend on #172.

## Small issues: generator foundation

### 1. Core engine: models, protocols, registry, dependency graph (#163)

**Depends on:** none

Create the package structure (`app/engine/`: `blocks`, `generators`, `answers`,
`topics`, `registry`) and, in the same PR:

- `Task`: statement, structured `Step`s, answer, metadata, code, generator
  version.
- `Step`: a structured solution step (text key + LaTeX), not plain text.
- Parameter models: strict, immutable Pydantic models.
- `TaskGenerator` protocol: `version`, `params`, `answer`, `requires`,
  `draw(seed)`, `build(params)`.
- `Answer` protocol: `kind`, `latex()`, `check(tree) -> Outcome`.
- Registry: register and look up by version; reject duplicate versions,
  unknown generators, invalid metadata.
- Dependency graph: validate `requires`; tests detect missing, duplicate and
  circular dependencies and unknown versions.

Includes one tiny test-only generator, so the interfaces are exercised by a
real consumer from the first PR.

### 2. Deterministic PRNG and problem codes (#164)

**Depends on:** 1

- Local hash-based PRNG on `hashlib` (seed + counter); no global `random`.
- Deterministic rejection and redraw, with a hard cap on redraws (e.g. 64).
  A generator that hits the cap fails its tests, so every shipped seed
  gives a valid problem.
- Code format `<TYPE>-<VERSION>-<16_DIGIT_SEED>-<CHECK>`, with a two-digit
  check. The owner approved two digits for #164: they detect any one-digit
  substitution and any swap of two different seed digits; one decimal digit cannot
  guarantee all such swaps across 16 positions. Parsing is case-insensitive,
  accepts spaces and dashes, and rejects unknown types and versions.
- A table of task-type prefixes (`INT`, `DEF`, `PFR`, `CMB`, ...) owned by the
  registry; a prefix is never reused.

The v1 PRNG hashes the domain tag `PracticeLoop PRNG v1` followed by a NUL,
the seed as eight big-endian bytes and a counter as eight big-endian bytes.
It uses rejection sampling for bounded values. Candidate redraw stops after at
most 64 attempts. The code check uses position-weighted version and seed digits
modulo 97, with a prefix-derived salt; two decimal digits store the residue.
The registry binds each prefix to one family and each numeric version to an
existing generator version. Do not reassign a shipped prefix or change a
shipped version's output.

### 3. Typed answers (#165)

**Depends on:** 1

One `Answer` type per kind, each with its own `check`, no `isinstance` chain:

- `NumberAnswer`: exact numbers and fractions (definite integral values,
  counts), compared exactly, no symbolic simplification.
- `ExpressionAnswer`: SymPy equivalence with variables and domains.
- `AntiderivativeAnswer`: up to a constant, `+ C` required (ADR-003).
- `DerivativeAnswer`: equal on every component, no added constant (ADR-005).

Shared SymPy helpers sit underneath (sampling points, domain components).
The new types apply the ADR-003/005 rules without importing legacy generator
implementations.

For #165, `NumberAnswer` checks exact rational arithmetic without importing
SymPy. Expressions outside that bounded rational subset are inconclusive;
the caller selects `ExpressionAnswer` for answers requiring symbolic forms,
including symbolic numeric values. There is no automatic symbolic fallback.
Symbolic answer checks must run inside the resource-limited math worker; the
new types do not connect themselves to the practice API in this issue. The
owner does not require replay compatibility with older generator versions.

### 4. Math blocks (#166)

**Depends on:** 1

Pure math objects with integer parameters, no topic or text knowledge:

- coefficients and domain-safe integer parameters;
- `Polynomial` (integer coefficients / roots);
- `PartialFractionRational` (a rational function built from its
  decomposition, with its poles).

Each block validates its parameters and can be drawn from the PRNG.

`IntegerRange` draws from a range within -12…12 after excluding forbidden
values. `Polynomial` stores coefficients in ascending power order, supports
degrees 0–5 and coefficients up to 100,000 in magnitude, and can be built
from integer roots in -6…6. `PartialFractionRational` represents one to four
simple fractions with distinct integer poles and nonzero integer numerators in
-6…6. Its combined expression and decomposition use the same exact terms;
the poles remain available to the generator for domain construction.
Draws use the supplied deterministic PRNG and do not import topic or generator
code. Other denominator families are outside this slice.

### 5. Generators for the slice (#167)

**Depends on:** 2, 3, 4

Build natively on the new interfaces:

- **Partial fractions** (Algebra): decompose a rational function.
- **Indefinite integral**: polynomial and rational integrands; rational
  integrals reuse the partial-fractions generator for their decomposition
  step (Algebra inside Analysis). Verification by differentiation;
  invalid cases rejected.
- **Definite integral**: wraps the indefinite generator, adds bounds inside
  the domain and an exact `NumberAnswer`.
- **Derivative**: polynomial and rational functions, `DerivativeAnswer`.
- **Combinations** (Combinatorics): `C(n, k)` with an integer
  `NumberAnswer`, to prove the engine works with no SymPy answer and for the
  future Probability and Statistics topics.

The first version draws polynomials of degrees 1–4 and rational functions with
two simple symmetric poles at ±2…±6 and equal nonzero numerators. The latter
allows the definite generator to wrap the same indefinite task on [-1, 1]
without crossing a pole; the exact rational value is zero. This is a limited
vertical slice, not the eventual curriculum catalogue. Combinations use
integer arithmetic. Codes PFR, INT, DEF, DRV and CMB identify the respective
version-1 generators. Symbolic answer checking remains inside the limited worker
when the slice is later connected to the API.

### 6. Topic registration (#168)

**Depends on:** 5

Topics as views over generators: each topic level is a list of generators
with parameter filters. Register partial fractions, derivatives, indefinite
integrals, definite integrals and combinations. One generator may appear in
several topics.

### 7. One topic through the real API (#169)

**Depends on:** 6

Serve one new-engine topic (e.g. `combinatorics`, a new topic so no
existing topic changes) through the practice API: issue, check, reveal. It
stores the problem code. The end-to-end API check covers it. Other topics
stay on the old engine.

### 8. Deterministic, golden and isolation tests (#170)

**Depends on:** 5, 6, 7

- The same code produces the same task (statement, steps, answer).
- Golden problems: sample codes per generator version pinned to their
  statement and answer, so a SymPy or Python upgrade that changes output
  fails CI.
- Every topic level yields a valid problem for many seeds; no seed hits the
  redraw cap.
- The dependency graph is valid.
- Isolation: old saved problems still open (statement from
  `problems.problem_latex`), old generator code is unchanged, and new topics
  use only the new engine.

### 9. Architecture handoff package (#171)

**Depends on:** 1–8

ADR-008 draft with: architecture, dependency diagram, package structure,
generator lifecycle (draw, verify, build, check), an extension example
("add a task type in one file"), known limitations, and unresolved design
decisions.

## GrillMe gate

### 10. Re-evaluate the generator architecture with GrillMe (#172)

**Depends on:** 1–9

GrillMe reviews the whole slice and decides:

- which abstractions stay, which are simplified;
- whether the interfaces are stable;
- whether the architecture fits Algebra, Analysis, Probability and Statistics
  (backed by partial fractions → integrals and combinations in the slice);
- how the rest of the refactor is split into issues.

Accepted when its findings are written down and Vlad accepts them. No
other topic migration starts before this issue is accepted.

## MVP done when

- [ ] Adding a task type is one new generator file plus its topic entry, with
      no edits to the engine, `answer_check.py` or other generators.
- [ ] One generator composes another (rational integral via partial
      fractions) and one wraps another (definite via indefinite).
- [ ] Answers are checked through `Answer.check`, including one non-SymPy
      answer (combinations).
- [ ] The same code rebuilds the same problem; golden tests pass.
- [ ] One new-engine topic works end to end through the API, covered by the
      end-to-end check.
- [ ] All existing tests pass; old topics behave as before.

## Main goal

### Goal: Complete the generator refactor

Starts only after #172 is accepted.

- Migrate the remaining topics, one family per issue.
- Add matrix and algebra generators (`IntegerDetMatrix` block,
  `MatrixAnswer`/`VectorAnswer` with input UI).
- Add functions and analysis generators.
- Add Probability and Statistics generators (`Distribution` block,
  interval/set/bool answers as needed).
- Connect every topic to the new engine.
- Build the topic catalogue at deploy (verified seeds), so issuing a problem
  runs no SymPy.
- `/p/<code>` page to open a problem from a code.
- Keep the legacy archive read-only (old problems show their statement,
  checks return "archived", not 500).
- Remove obsolete generator code.
- Final ADR-008.
