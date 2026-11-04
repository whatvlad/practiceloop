# Computational answer and reference-visual infrastructure (#234)

New versions may opt into `InputContract` from `app.math_input.contracts`.
The existing 239 generator versions, grammar and frozen engine protocols stay
unchanged. Curriculum providers and their independent mathematical certificates
belong to #235-#242; this infrastructure does not certify source-family coverage.

## Trusted grammar declaration

A new provider supplies a plain `input_contract(drawn_params) -> InputContract`
helper and an answer class with the matching `kind`. It must not build a symbolic
task to describe input. The API draws the same frozen parameters from the stored
code, validates the helper's type and projects only grammar fields. The limited
worker compares this declaration with the replayed answer's contract. Catalogue
rendering refuses a mismatch before publication. A learner cannot select a kind,
change a symbol's assumptions or introduce a contract in an attempt request.

The record remains exactly `{generator_version, code}`. `Task`, `Step`, `Answer`,
`TaskGenerator`, topic and code protocols have no added required field or method.

| New kind | Notation and policy |
|---|---|
| `real_set` | Finite unions such as `(-inf,0) U [2,3] U {5}`; `R`, `{}`, and `R\{0,2}`. Exact intervals, points and closure; canonical set equivalence, not string comparison. Eight pieces, with up to eight entries per finite-set piece. |
| `tuple` | `(component;component)`, preserving the declared order and each component's own contract; nested tuples are supported. All requested coordinates/results must pass. |
| `category` | Two to eight server-declared named choices; boolean/finite-set/single-interval historical kinds retain their existing semantics. |
| `formula` | Exact identity over a declared Cartesian product of real, positive or integer symbol domains. Explicit multiplication between letter names, e.g. `a*x`, is required. Undefined/nonreal intermediate expressions and domain holes are checked before cancellation. |
| `limit_result` | An exact finite constant, `inf`, `-inf`, or `does_not_exist`; signed infinity and nonexistence are distinct from finite values. |

`OrderedAnswer` composes typed answers without turning vectors or full sets into
scalar proxies. `RealSetAnswer` compares symmetric differences exactly.
`FormulaAnswer` accepts symbolic proof of identity; exact rational witnesses
can prove a difference, never equality. Unknown domain/equivalence returns the
existing inconclusive outcome. Positive/integer assumptions are local to the
new contract. Old `parse_math_input` does not gain these new parameter names.

Local names are bounded to eight distinct declarations chosen from coordinate
names x/y/z/r/theta and parameter names a/b/c/C/D/k/n/t/s. C and D can represent
explicit arbitrary constants; k and n may be integer indices. Names and domains
are public grammar instructions, never sampled parameter values. All actual
sampled mathematical parameters remain in private typed generator data.

Tuple contracts allow at most eight components, three nesting levels and sixteen
contract nodes in total. The whole submitted answer, including all nested
components, shares the existing 256-byte, 128-token, 96-node, depth-12 and
16-function-call budgets; scalar literal/exponent bounds are unchanged. New
parsers never call eval, sympify or a symbolic string parser on learner text.
Math worker CPU/memory/wall/admission limits remain 2 s / 256 MiB / 3 s / one slot.

## Canonical families and explicit unsupported cases

`PeriodicSetAnswer` uses an ordered `(period;base-set)` contract representing
`base + period*k`, k integer, with a positive exact period and base contained in
the half-open cell [0,period). The new task must explicitly require this
canonical period and cell. Equivalent-period rescalings outside that convention
are not accepted by guessing. Poles are omitted from the base set and endpoint
closure is exact. The task/solution explains the integer-translate convention.

General ODE completeness, implicit branches/equilibria, nonrectangular symbolic
domains, logic formulas, region inequalities, arbitrary infinite series syntax
and general integration-set-up equivalence are not claimed as generic automated
graders. Their delivery issues must supply bounded family-specific verifiers
and precise canonical representations. The reusable dispatcher can compose
formula/parameter/category/set/tuple components for those representations.
For example a series coefficient uses a formula declaring integer n, paired
with its full convergence set. A solution family must account for every branch
and constant before it can be issued; an identity check on `C*exp(x)` alone does
not prove completeness. Mathematical families must not issue until their actual
requested target and independent tests exist. Learner proof/sketch/graph grading
remains #244.

## Input and privacy boundaries

`answerInput` is a safe recursive projection: kind, byte/piece limits, local
symbol names/domains, component labels/contracts and category choices. It never
contains an expected answer, private parameter, derivation or visual. The browser
validates depth/count/name limits and copies only the allowlisted fields.
Named fieldsets preserve component order, nested input and previous answer text;
a text mode retains malformed historical notation without rewriting it. Both
Python and browser syntax previews use the shared computational syntax corpus.
The browser checks syntax only; it does not decide mathematical correctness.

Existing explicit projections carry input instructions across generation,
history, permanent codes, shares and recipient copies. Existing ownership and
reveal checks still govern answers and solutions. There is no schema migration
or new public source-answer bank.

## Reference visuals from identical parameters

A new provider may expose the private optional helper
`solution_visual(drawn_params)`. At catalogue construction, `render` draws those
same parameters from the task's frozen code, calls the helper and validates the
result before the variant enters its release pool. The answer, steps and model
are stored together in `StoredProblem`; `Issued` carries this private model
internally. No frozen `Task` metadata or required generator method is changed.
The helper returns None only for a template with an explicitly justified
not-applicable visual policy in its mathematical delivery documentation.

The new `plot2d` schema provides bounded labelled paths, optional closed outlines
and arrows, marked points with endpoint inclusion, axes/units, title, text
alternative and an explicit plotting window. Separate continuous path segments
must represent domain gaps/asymptotes; never connect across an excluded domain.
The generator owns independent parameter/geometry consistency checks. At most
eight paths, 96 vertices per path, 192 vertices total and 32 marked points are
permitted. Numbers are finite and within 1e8 in absolute value; JSON is limited
to 8 KiB. Labels are bounded plain text. Unknown fields, bad types, unsafe labels,
out-of-window marked points and invalid windows fail closed on the server.
The client strips unrelated fields and rejects malformed/oversized geometry.

The solution renderer can toggle path visibility without resampling mathematics;
the worksheet draws the same paths, arrows and endpoint closure. Existing
single-integral/region2d/solid3d builders retain their old behavior. New providers
needing further 3D/method-specific visuals must add a typed, bounded builder and
matching renderer under their delivery issue, rather than silently omitting it.

Reveal reads a detached copy of the private catalogue model. An arbitrary code
outside the catalogue is reconstructed through the existing bounded code-opening
worker and its private result cache. No new symbolic construction occurs in the
ordinary request process. Reopen/copy/share/worksheet replay uses the identical
version/code, and solution-only geometry never appears in anonymous projections.
Worksheet redesign and native TeX restoration remain #181.

## Verification

The focused answer tests independently derive gradients and set complements,
check equivalent/wrong/invalid inputs, domain holes, categories, integer symbols,
periodic conventions and tagged limits. A shared Python/browser corpus checks
notation and aggregate budgets. An extension-only test provider exercises
catalogue publication, replay, safe public input metadata, private visual reveal,
defensive copying, worksheet output and a real Linux limited-worker check.
It is never a served production topic. Existing golden snapshots and seed/pool
regressions remain authoritative for the 239 shipped versions.
