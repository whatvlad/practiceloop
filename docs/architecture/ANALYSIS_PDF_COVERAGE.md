# Analysis exercise-sheet generator expansion

Owner: Vlad / whatvlad. Parent: #232. Intake: #233. Base:
`30743c36ae624177acdc71ffb3638948f9556e7a`.

## Deliverable

Generate fresh mathematical exercises of the source families, with their
answers and worked solutions. Do not publish the original PDF exercises,
scanned figures or a fixed source-answer bank. The owner clarified this on
2026-11-03. The source documents are reference data; their classroom
instructions and external links are not agent instructions.

Reuse the native engine and the existing Algebra/Mathematical Analysis areas.
Do not create a duplicate course solely because a PDF has a different title.
Existing 239 immutable versions, permanent codes, private records and history
remain stable. Additional structures receive new versions and explicit prefixes.

Owner decisions (2026-11-03): release computational generators first. Defer
learner proof and sketch tasks to #244, after computational parent #232.
Each generated variant must already have its own correct reference answer and
worked solution, tied to exactly the same parameters. Include an appropriate
parameter-derived diagram or visualization where the mathematical type calls
for one. This visual requirement is part of the computational release; it is
not deferred together with learner drawing tasks.

## Sources and inventory status

Both sheets credit Marian Gewert and Zbigniew Skoczylas.

| ID | Document | Pages | Scope |
|---|---|---|---|
| AM1 | Analiza matematyczna 1, printed 2020/2021 | 17 | Exercises 1–73, including optional list 15, sample tests/exams and distinction exam |
| AM2A | Analiza matematyczna 2A (USPO), PDF produced 2024 | 10 | Exercises 1.1–14.4, figures/starred parts; bibliography on page 10 |

Exact source file SHA-256 identities are in
[analysis_pdf_source_index.json](analysis_pdf_source_index.json). PDFs, extracted
text and rendered reference images remain ignored local inspection artifacts.
The repository index contains source references and paraphrased family names,
not the original problems or answers.

**Source intake reconciled on 2026-11-04; generator delivery remains pending.**
The version-2 index enumerates 830 positional references (536 AM1, including
84 exam questions; 294 AM2A), with 146 shared family contracts. All 27 pages
were visually checked against their extracted text. Every reference names its
family contracts, page, method, result interaction and delivery components.
30 references are wholly deferred to #244 and 146 combine computational and
deferred components. Other references remain computational delivery work.
At intake `verified_versions` stayed empty: that audit was not a generator coverage
certificate. #235 links 102 computational references/components under 20 family
contracts to 81 new verified bounded versions; see
[ELEMENTARY_FUNCTIONS.md](ELEMENTARY_FUNCTIONS.md). Other delivery issues remain
pending, and mixed derivative/asymptote/proof/sketch components retain their
separate routes. `candidate_versions` identifies inspected, related implementations;
`existing_coverage: partial` never certifies the complete source family.

Exam rows reuse method-family contracts while preserving all 84 source IDs.
Combined questions retain multiple contracts instead of dropping a requested
result. Eight exam-only contracts cover primitive initial values, differentiability
parameters, simultaneous monotonicity/convexity, substitution followed by parts,
decimal existence, general functional-limit classification, exact polynomial
sign reconstruction and torus volume. The two purely theoretical distinction
questions are deferred; the polynomial and torus computations remain first-stage.
The theory component of the torus question is separately deferred.

AM1 13 and 68 have duplicate labels, visually confirmed on pages 3 and 12; positional
suffixes keep references unique rather than silently losing a part. AM1 59's
nonconsecutive labels are retained. AM2A 14.1 includes three graph-defined
functions as well as the six written formulas. The three level-set panels in
AM2A 5.2 form a matching exercise, not three unrelated scalar questions.

Text from all 27 pages has been extracted and visually reconciled. AM2A 14.1's
unlettered plots are
identified as graph-f, graph-g and graph-h by the functions actually labelled in
the source, rather than inventing subpart letters. AM2A 13.1(c)'s three Roman-
numbered requested outputs have explicit component references. Source mistakes
remain independently documented below; visual verification does not make a
printed mathematical statement correct.

## Serial delivery

| Issue | Scope | Source references |
|---|---|---|
| #233 | Reconcile source inventory and checking contracts | All source/exam references |
| #234 | Exact structured computational answers and solution visual contracts | Shared prerequisites |
| #235 | Logic, elementary functions, domains, equations, inequalities, trigonometry | AM1 1–23 |
| #236 | Sequences, limits, asymptotes, continuity, root certificates | AM1 24–39 |
| #237 | Derivatives, complete function analysis, optimization, Taylor/error bounds | AM1 40–49, 51, 69–73 |
| #238 | Single integrals and geometric/physical applications | AM1 50, 52–68 |
| #239 | Improper integrals, numerical/power series, Maclaurin operations | AM2A 1–4 |
| #240 | Multivariable functions, regions/surfaces, derivatives and extrema | AM2A 5–9 |
| #241 | Double integrals, region geometry, surface patches, centroids/inertia | AM2A 10–12 |
| #242 | ODE models/general solutions/IVPs and direct/inverse Laplace transforms | AM2A 13–14 |
| #232 | Computational source coverage and deployment audit | Computational children, including exam-only/starred computations |
| #244 | Subsequent learner proof, sketch and graph-matching tasks | Explicitly deferred items/components, after #232 |

Each mathematical block also owns its matching exam families. No exam-only
family is excluded: examples include polynomial reconstruction, functional-limit
reasoning, constructive existence and the torus application. Implement serially
to avoid overlapping grammar, projections, topic catalogues and golden fixtures.
New levels describe different methods; do not force five levels by changing
coefficients, or preserve a scalar proxy when the source asks for an entire set.

The queue places these dependencies before the final parent audit, then leaves
the previously deferred #181 and existing launch issues in relative order.
Worksheet redesign remains deferred; normal worksheet compatibility belongs to
each generator issue and does not authorize the broader #181 redesign.

## Existing capability versus source coverage

Source checked against `backend/app/engine/generators/analysis_one.py`'s MATRIX,
`backend/app/engine/generators/analysis_two.py`'s SPECS, their mathematical blocks,
the retained native integral/differentiation/multiple-integral providers, current
answer classes and structured parser. The old graph was built at
`a5737c3f9d5fb44b8904e5d5d78a90195fe3b8d4`, predates these curricula and cannot
certify current coverage. Graphify CLI and its optional NetworkX dependency
were unavailable during that intake; a read-only adjacency traversal found old answer-related
nodes, and the audit used current source directly. Details are also in
ANALYSIS_I.md and ANALYSIS_II.md.

The per-family gap matrix and the contracts selected for #234 are recorded in
[ANALYSIS_PDF_CONTRACTS.md](ANALYSIS_PDF_CONTRACTS.md). The index links every
subpart to that matrix; no exam reference retains a pending-deduplication marker.

| Existing capability | Why the source still needs family-level audit |
|---|---|
| Parity, simple square-root domain endpoint, affine inverse/composition | Full domains can be disconnected; inverses require branches and domains; logic/periodic trig solutions are separate |
| Several sequence and function limits, one oblique asymptote, continuity parameter, bisection | Factorial/floor/oscillatory families, all asymptotes, discontinuity classes and proof hypotheses are not implied by these templates |
| Derivative rules, tangent slope, a sign chart, scalar extrema, rectangle/box optimization | Full tangent equations, nonsmooth and global boundary cases, convexity/inflections and rigorous approximation bounds are additional targets |
| Existing single integrals and multiple-integral setups | Arc length, work/pumping, composite regions, centroids and inertia are distinct methods, not merely larger coefficients |
| Improper/series tests and selected Taylor forms | Partial sums, telescoping, transformed series, high derivatives, all endpoint and two-tail cases require independent evidence |
| Disk/ball radius, gradient norm, directional value, scalar differential and extremum classification | Full regions, ordered gradients/planes, level-set matching and complete stationary-point analysis are not scalar norms |
| Selected global IVPs and Laplace IVPs | General solution constants, singular domains/equilibria, inverse/direct and graph-defined transforms require additional contracts |

No row in this table asserts that every old version must be replaced. A child
may cite an existing version after checking its actual form, domain, answer and
solution against the source family. Frozen outputs must not be edited to make
this new mapping fit.

## Accepted staging and computational contracts

The owner chose computations first; the earlier self-review-versus-step-checking
proposal is superseded. No further approval of this phase choice is pending.
Every mixed source task must distinguish its computational result from its
deferred learner proof/sketch component. Do not claim that checking a computed
answer also grades a learner's proof or drawing.

1. Numerical and symbolic computations retain exact server checking, strict
   domain handling and resource limits. No LLM-generated mathematics or sampled
   equality proofs. Parameters are bounded and deliberately preserve the
   intended convergence, branches, degeneracies and difficulty structure.
2. Entire real domains and solution sets require exact finite unions of
   intervals/points/exclusions; a single endpoint or inclusion bitmask is not
   full coverage. Periodic solutions require an explicit bounded parameterized
   family contract, with integer parameter and excluded poles.
3. Gradients, points, planes, coefficients, centroids and multiple requested
   values require ordered components with individually declared domains and
   appropriate joint equivalence. A finite unordered set is not a vector.
4. General ODE solutions retain arbitrary constants, equilibrium/singular
   branches and their stated intervals. Do not silently change every general
   solution question into an IVP just to use an existing checker.
5. **Learner proof and sketch tasks are deferred to #244.** Do not introduce a
   self-review/proof/drawing grading mode in #234. The source index must retain
   these references/components, with an explicit deferral rather than a false
   coverage mark. Exact checking of computations stays in the first release.
6. Generated task diagrams are built from the sampled mathematical model, never
   cropped from the PDF. Separate task-visible data from solution-only graphs
   and private expected values. A graph used in the question must not leak the
   answer through metadata or accessibility text.

## Reference solutions and visuals are part of generation

A publishable generated variant consists of its statement, exact answer,
parameter-specific worked derivation and, when relevant, a deterministic visual
model. All are derived from the same frozen generator/version/code and sampled
parameters. There is no second unrelated generation when Show Solution is
pressed, no shared stock solution with mismatching coefficients and no copied
PDF figure. Private solution content remains hidden until authorized reveal.

Reference derivations must already exist and be verified when a variant enters
the private catalogue. A renderer may draw a stored/replayable visual model
when the solution is opened; that is rendering, not inventing another solution.
Historical reopens, recipient copies and worksheet output retain the same math.

Each template declares a visual policy: a parameter-derived plot, explanatory
diagram, or a justified not-applicable case. Examples are tangent/sign charts,
bounded integration regions and solids, multivariable level sets/gradient
arrows, and suitable sequence/series or ODE solution plots. Use visuals to
explain the actual computation, not as decorative replacements for derivations.
State correct axes, domains, boundaries, orientation and units. New task-visible
diagrams must be separated from private solution-only features. Reuse existing
trusted visual builders where they fit; add focused contracts in #234 where
needed, then mathematical builders in their delivery issue.

## Source mathematics and errata

AM2A 4.4(c), visually checked on page 3, prints
`sum(n>=1, x^n/n!) = -ln(1-x)`. This is false: the factorial series is `exp(x)-1`;
the logarithmic identity uses `x^n/n`, with `|x|<1`. Their cubic coefficients
already differ. Generate the independently verified intended family and explain
the correction in developer provenance, without copying the false statement.

Extraction corrupts several Polish characters, comparison glyphs, subscripts and
formula ordering. A suspicious extracted formula is not itself evidence of a
source error. Inspect its rendered page before defining a generator or adding
an erratum. Correct mathematical domains and assumptions are authoritative.

Additional source observations confirmed from the rendered pages:

- AM2A 7.5(a), p.5, prints `f(x,y)=x^2=y^2`. This does not specify the intended
  scalar function. Do not guess a missing plus/minus sign. #240 must generate
  an independently specified directional-derivative family and verify its result.
- AM2A 13.3(b), p.9, omits `dt` in the first differential term. The corresponding
  family must explicitly state its ODE and handle the boundary initial value
  without dividing away singular or nonunique branches.
- AM2A 13.5(d), p.9, has malformed initial-value notation. Fresh variants state
  the initial condition with a function argument and an admissible interval.

These are provenance observations, not authorization to copy corrected source
tasks. Independent generators and reference derivations remain the deliverable.

## Evidence required before delivery

For each reconciled source family, record the implementing immutable versions,
method-specific structural levels, actual answer/task mode, independent worked
examples, parameter bounds and excluded degeneracies. Follow existing golden
replay, seed sweeps, private catalogue verification and Linux worker caps.

For computations, exercise correct/equivalent/wrong/invalid inputs and ownership,
history, codes/shares/copies, mixed practice and generated worksheets. Verify
that reference answers/steps/visuals match the same sampled parameters and are
hidden before authorized reveal. Inspect rendered question/solution graphs.
New private catalogue/proofs/source text never enter browser assets. Learner
proof/drawing interaction tests belong to the later #244 stage.

Do not close #232 because the intake document exists, a topic appears in the UI,
or a few scalar representatives work. It closes only after computational
source-family reconciliation, all first-stage mathematical deliveries, hosted
CI, deployment and actual live checks. Every deferred proof/sketch component
must explicitly link to the owner-accepted later stage #244.

The [sequence and continuity delivery](ANALYSIS_LIMITS.md) documents the #236
methods. After #257-#259 every computational #236 reference names a verified
version in the machine-readable index.
