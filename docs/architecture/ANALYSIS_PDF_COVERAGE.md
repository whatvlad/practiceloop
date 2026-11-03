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

**This is a draft intake, not a coverage certificate.** The index currently
enumerates 830 positional references (536 AM1, including 84 exam questions;
294 AM2A). Source numbering, graph labels and extraction ambiguities require
visual reconciliation before #233 closes. Every row initially has empty
`verified_versions`; implementation must populate evidence rather than treating
an existing topic name as full coverage. Exam rows initially route to an issue;
their precise family deduplication is still pending.

AM1 13 and 68 have duplicate labels, visually confirmed on pages 3 and 12; positional
suffixes keep references unique rather than silently losing a part. AM1 59's
nonconsecutive labels are retained. AM2A 14.1 includes three graph-defined
functions as well as the six written formulas. The three level-set panels in
AM2A 5.2 form a matching exercise, not three unrelated scalar questions.

Text from all 27 pages has been extracted. AM1 pages 1, 3, 12 and AM2A pages 3, 9
were visually inspected in this checkpoint. AM2A 14.1's unlettered plots are
identified as graph-f, graph-g and graph-h by the functions actually labelled in
the source, rather than inventing subpart letters. Remaining ambiguous pages are not
represented as visually verified.

## Serial delivery

| Issue | Scope | Source references |
|---|---|---|
| #233 | Reconcile source inventory and checking contracts | All source/exam references |
| #234 | Reusable exact structured answers and visual/self-review task mode | Shared prerequisites |
| #235 | Logic, elementary functions, domains, equations, inequalities, trigonometry | AM1 1–23 |
| #236 | Sequences, limits, asymptotes, continuity, root certificates | AM1 24–39 |
| #237 | Derivatives, complete function analysis, optimization, Taylor/error bounds | AM1 40–49, 51, 69–73 |
| #238 | Single integrals and geometric/physical applications | AM1 50, 52–68 |
| #239 | Improper integrals, numerical/power series, Maclaurin operations | AM2A 1–4 |
| #240 | Multivariable functions, regions/surfaces, derivatives and extrema | AM2A 5–9 |
| #241 | Double integrals, region geometry, surface patches, centroids/inertia | AM2A 10–12 |
| #242 | ODE models/general solutions/IVPs and direct/inverse Laplace transforms | AM2A 13–14 |
| #232 | Final source coverage and deployment audit | All children, including exam-only/starred families |

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

Source checked against `generators/analysis_one.py`'s MATRIX,
`generators/analysis_two.py`'s SPECS, the current answer classes and structured
parser; details are also in ANALYSIS_I.md and ANALYSIS_II.md.

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

## Answer and interaction proposal

The owner has been asked to choose self-review versus structured step checking
for proof/sketch tasks, or to stage those after computations. The self-review
contract below is the recommended proposal, not recorded owner acceptance.
Do not start dependent task-mode implementation before that answer arrives.

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
5. **Proof and sketch tasks remain proof and sketch tasks.** Generate a new
   mathematically certified statement/figure and a parameter-specific reference
   proof/sketch, hidden until the learner requests it. Present these clearly as
   self-review tasks, with no fabricated Correct/Incorrect score for free-form
   reasoning/drawing. They must not inflate checked/correct counters. Where a
   faithful intermediate calculation or graph-matching question is generated,
   label that narrower interaction explicitly rather than claiming unrestricted
   proof/drawing assessment. The worksheet can include the generated prompt and
   optionally the reference proof/diagram under existing reveal semantics.
6. Generated task diagrams are built from the sampled mathematical model, never
   cropped from the PDF. Separate task-visible data from solution-only graphs
   and private expected values. A graph used in the question must not leak the
   answer through metadata or accessibility text.

The proposed self-review choice preserves the source's mathematical request while
avoiding unreliable free-form proof/drawing grading. It does not exclude those
families from this expansion. #234 must implement an explicit public task mode,
UI behavior, API response for unsupported auto-check attempts, history/statistics
behavior and privacy/worker tests before these templates are issued.

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

## Evidence required before delivery

For each reconciled source family, record the implementing immutable versions,
method-specific structural levels, actual answer/task mode, independent worked
examples, parameter bounds and excluded degeneracies. Follow existing golden
replay, seed sweeps, private catalogue verification and Linux worker caps.

For computations, exercise correct/equivalent/wrong/invalid inputs and ownership,
history, codes/shares/copies, mixed practice and generated worksheets. For
self-review, verify no false grading, no unintended counter updates and hidden
reference solutions before authorized reveal. Inspect rendered question/solution
graphs. New private catalogue/proofs/source text never enter browser assets.

Do not close #232 because the intake document exists, a topic appears in the UI,
or a few scalar representatives work. It closes only after source-family
reconciliation, all mathematical deliveries, hosted CI, deployment and actual
live checks, with explicit remaining gaps or owner-accepted exclusions.
