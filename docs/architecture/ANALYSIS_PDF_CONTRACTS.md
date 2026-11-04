# Analysis source-family contracts (#233)

This is the implementation contract selected by the source audit at
`30743c36ae624177acdc71ffb3638948f9556e7a`, not a claim of newly shipped answer
kinds. The [source index](analysis_pdf_source_index.json) schema version 2 is
authoritative for per-reference routing. Its `family_contracts` map records
candidate immutable versions, source evidence, gaps, requested results and
answer interactions. Each `items` row has one or more family links and explicit
delivery components; a component's issue overrides the row's coordinating issue.

## Existing boundary and extension plan for #234

The current `backend/app/math_input/structured.py` only recognizes boolean,
finite-set and single-interval kinds. Its children are constant expressions,
not arbitrary symbolic tuples. `answers/structured.py` limits finite sets to
eight values and compares a single interval's endpoints and closure. An unordered
set cannot represent a vector, a union of intervals or an ODE family.
`ExpressionAnswer` and the derivative/antiderivative policies remain appropriate
for existing scalar expressions and primitives; adding an answer type must not
reinterpret their historical codes or syntax.

#234 implements reusable contracts below; #235-#242 own the mathematics,
parameter bounds and independent certificates of their generated families.
Where a contract requires family-specific canonicalization, #234 provides the
bounded representation/dispatcher and the delivery issue supplies its verifier.
Unsupported representations must remain unavailable until implemented and
tested. They must not be replaced with an easier scalar question and called
complete. Multiple component controls may collect a full structured result
without requiring one large ambiguous formula string.

| Contract | Required behavior | Representative source |
|---|---|---|
| `scalar`, `expression` | Exact value/function; declared variable domain; check every unevaluated denominator/log/root before simplification | AM1 15, 41, 50-68 |
| `primitive` | Derivative equality on every real component and required arbitrary constants; a point-value condition instead fixes the constant and requires exact function equality | AM1 50, 52-53, 64-68 |
| `category` | Finite named choices for the actual classification, including proposition/not-a-proposition and absolute/conditional/divergent cases | AM1 1-4; AM2A 3.3 |
| `logic` | Bounded propositional syntax; named atoms; full truth-table equivalence. Natural-language statements are generated from trusted atom models | AM1 2 |
| `limit_result` | Tagged finite value, signed infinity or does-not-exist. Finite branch uses exact checking, not a classification number in place of a finite value | AM1 26, 30, 31, 45; AM2A 5.4, 7.3 |
| `real_set` | Exact finite unions of intervals and isolated points, including empty/all-real sets; intersection with original exclusions | AM1 5, 10-17, 22; AM2A 3.4 |
| `ordered` | Fixed named slots with individual domains/types; preserve coordinate and Hessian order; every slot must pass | AM1 8, 13, 37, 42-49, 69-71; AM2A 6-9, 12.2 |
| `periodic_set` | Finite base-cell points/intervals and integer translates, normalized modulo a declared period; retain excluded poles | AM1 18, 23 |
| `region` | Exact declared inequality families in R2/R3, with intersections/unions and boundary exclusions; compare the whole region | AM2A 5.1 |
| `series` | Declared indexed coefficient expression, start, parity and convergence set; compare every coefficient symbolically within supported families | AM2A 4.1, 4.3 |
| `ode_family` | Explicit/implicit family, arbitrary constants, equilibrium/singular branches and maximal real intervals; preserve symbolic initial data | AM2A 13.2-13.6 |
| `iterated_bounds` | Ordered finite region pieces, variable order and exact bound functions; equivalent region decomposition with preserved generic integrand | AM2A 10.3 |
| `certificate` | Exact enclosure/error inequality with a stated error convention. A smaller bound is acceptable only when certified; first-order error estimates must be labelled as such | AM1 39(a), 44, 72-73; AM2A 7.1-7.2 |

General symbolic parameters are declared by trusted family metadata with finite
names and explicit real/positive/integer constraints. A learner cannot invent
new variables, change the answer kind or choose a more permissive domain. New
parameter names such as an integer period index or ODE constant are local to
new versions; the existing global variable allowlist must not silently widen
old versions. Time may be displayed as t and normalized consistently by the
new family rather than confusing it with the Laplace variable s.

Periodic solutions compare canonical sets over one declared common period,
including boundary equivalence; symbolic probing of a few angles is insufficient.
ODE checks require both a residual and completeness of the declared bounded
family, with all constants/branches and initial conditions. Residual zero alone
does not prove completeness. Implicit families use supported canonical relations
with declared branches and intervals; an arbitrary learner differential equation
or unbounded solve is outside this contract. Integration constants are distinct
from physical parameters. General ODE questions must not become IVPs.

Regions and reversed integrals use finite declared mathematical families and
exact inequality/boundary certificates, rather than a general theorem prover.
Proofs of domain equality or coefficient equality are deterministic exact
certificates; numerical samples may find a counterexample but cannot establish
equality. Unknown equivalence returns the existing inconclusive outcome.

Keep the aggregate input budgets: 256 bytes, 128 tokens, 96 nodes, nesting 12,
16 function calls, eight literal digits, six fractional digits and exponent
parts bounded by 12, as declared in `math_input/parser.py`. Aggregate component
limits apply across the whole submitted answer, not independently per slot.
The structured parser must count new container/separator nodes too. Preserve
the 2 s CPU limit, memory/wall caps and single worker slot. A contract exceeding
those budgets needs a bounded UI representation and generation constraints;
it does not authorize raising production limits. Trusted result metadata may
describe slot names/grammar but must not expose expected values or private
generator parameters.

## Source components and independent mathematical cases

Every computational family includes its own parameter-derived reference
derivation before catalogue publication. Learner proof/sketch components below
are separate #244 work; they never remove the reference solution requirement.

- AM1 7, 9, 12 and AM2A 5.2-5.3 are wholly learner proof/sketch/matching tasks.
  AM1 39(b-f), first-test B3 and main-exam D4 request uniqueness proofs without
  a numerical result. They are deferred, while 39(a)'s certified approximation
  and its starred root question retain computational components.
- Definition/theorem wording in parity, limit, derivative, convergence and
  identity tasks is explicitly deferred where the index marks `learner-proof`.
  Their computed classifications, expressions or domains remain first-stage
  where present. All ordinary worked solutions still explain their methods.
- Graph/domain drawings in AM1 5, 37(a), exam area questions and AM2A 5.1,
  10.2-10.3, 11.1 have separate learner-sketch components. First-stage solution
  graphics explain the same computation; they do not grade a learner drawing.
- AM2A 5.2's three surfaces share level-set panels A/B/C: it is a matching task,
  wholly deferred, rather than three numerical radius questions. AM2A 14.1's
  graph-f/g/h are given data for Laplace computation and stay first-stage:
  generated finite pulse, triangular pulse and ramp-to-plateau models must
  expose their piecewise definitions accessibly without exposing the transform.
- AM2A 13.1(c) retains three explicit Roman-numbered output references. AM1 8
  retains all four compositions and their domains; AM2A 8.1 retains every
  requested second partial rather than one mixed derivative.
- AM1 51 and the distinction polynomial question require every derivative-sign
  and inflection constraint; minimum-degree and exact-location requirements
  differ and must not be deduplicated into one unconstrained interpolation.
- The distinction decimal-prefix existence and arbitrary-positive-function
  ratio-limit questions are theoretical construction tasks in #244. Torus
  volume remains computational, with the general shell-formula proof deferred.

The source sometimes has no finite derivative/limit or no global attainment.
AM2A 7.3 requires an explicit one-sided versus two-sided directional convention;
the norm at the origin and cube-root singularity cannot be checked using a
smooth gradient formula. AM2A 9.1(f)'s noncompact domain requires boundary and
infinity checks. Integer production counts in 9.6 require discrete feasibility
after continuous optimization. General solution completeness and boundary
nonuniqueness in 13.3 must be addressed explicitly. These are required methods,
not optional coefficient variants.

## Visual and replay contract

#234 must reuse or extend trusted visual builders without changing frozen
`Task`, `Answer`, `TaskGenerator` or code protocols. Existing task metadata is
limited to string/integer display data; do not insert arbitrary private model
objects or serialize source figures there. If a new design requires a frozen
protocol change, record the required ADR-008 amendment before implementing it.

Each new template declares either a parameter-derived explanatory visual or a
mathematical reason why none is relevant. Region/polar/solid/centroid/inertia,
tangent/sign/convexity, geometric optimization and graph-defined Laplace tasks
require appropriate geometry. Sequences/series/ODE plots are used where they
explain the method. A decorative stock image is not evidence. Graph limits must
respect domains and asymptotes, unit directions, axes, orientation, endpoint
closure and physical units. Clipping must not create a false boundary.

Generate statement, answer, derivation and deterministic visual model from the
same immutable code and parameters. Render that model on reveal; never sample
again. Verify generation, history reopen, permanent code, shares/recipient
copies, mixed practice and worksheet replay. Task-visible figures use a public
projection of necessary data. Solution-only models, coordinates of hidden
extrema, answers and their accessibility text stay private until authorized
reveal. Reject unknown or learner-supplied visual schemas. Worksheet redesign
and native TeX restoration remain #181; compatibility checks remain required.

## Family gap matrix

`partial` means a related inspected generator is reusable but the complete
source family still has gaps. `missing` means no full matching implementation
was identified; it is not a claim that no supporting algebraic primitive exists.
No row certifies source-family completion. The JSON retains exact candidate
versions and source paths; the table below is a readable projection.

<!-- family-matrix -->
| Source group | Requested result | Contract | Existing | Owner issue |
|---|---|---|---|---|
| AM1/1 | proposition status and truth value | `category` | missing | #235 |
| AM1/2 | negation with conjunction/disjunction/implication/equivalence/exclusive-or | `logic` | missing | #235 |
| AM1/3 | truth of compound proposition | `category` | missing | #235 |
| AM1/4 | truth with quantified domains and quantifier order | `category` | missing | #235 |
| AM1/5 | complete natural real domain | `real_set` | partial | #235 |
| AM1/6 | even/odd/neither with symmetric-domain check | `category` | partial | #235 |
| AM1/7 | definition-based monotonicity proof | `deferred` | deferred | #244 |
| AM1/8 | four compositions, each expression paired with its natural domain | `ordered` | partial | #235 |
| AM1/9 | learner graph transformations from a generated piecewise graph | `deferred` | deferred | #244 |
| AM1/10 | all real roots with original denominator exclusions | `real_set` | missing | #235 |
| AM1/11 | all solution intervals with pole and endpoint handling | `real_set` | missing | #235 |
| AM1/12 | injectivity proof on the specified interval | `deferred` | deferred | #244 |
| AM1/13 | inverse formula, domain and range with specified branch | `ordered` | partial | #235 |
| AM1/14 | exponential equation/inequality solution set | `real_set` | missing | #235 |
| AM1/15 | exact logarithmic value | `scalar` | missing | #235 |
| AM1/16 | logarithmic solution set intersected with all argument domains | `real_set` | missing | #235 |
| AM1/17 | exponential solution set including substitutions and domain checks | `real_set` | missing | #235 |
| AM1/18 | angles on which each trigonometric identity is defined and valid | `periodic_set` | missing | #235 |
| AM1/19 | multiple-angle linearization of even trigonometric powers | `expression` | missing | #235 |
| AM1/20 | principal inverse-trigonometric values | `scalar` | missing | #235 |
| AM1/21 | nested trigonometric and principal inverse-trigonometric values | `scalar` | missing | #235 |
| AM1/22 | natural inverse-trigonometric function domain | `real_set` | missing | #235 |
| AM1/23 | all equation or inequality solutions with integer parameter | `periodic_set` | missing | #235 |
| AM1/24 | lower/upper boundedness and valid bounds | `ordered` | partial | #236 |
| AM1/25 | eventual monotonicity type and a certified starting index | `ordered` | partial | #236 |
| AM1/26 | finite or signed infinite sequence limit | `limit_result` | partial | #236 |
| AM1/27 | sequence limit using algebra, factorial cancellation or conjugation | `scalar` | partial | #236 |
| AM1/28 | sequence limit via squeeze, floor, nth roots or growing sums | `scalar` | missing | #236 |
| AM1/29 | exponential sequence limit including differences of powers | `scalar` | partial | #236 |
| AM1/30 | finite or signed infinite sequence limit | `limit_result` | missing | #236 |
| AM1/31 | finite or signed infinite function limit | `limit_result` | partial | #236 |
| AM1/32 | finite function limit using cancellation/conjugation/leading terms | `scalar` | partial | #236 |
| AM1/33 | both one-sided limits and existence classification | `ordered` | partial | #236 |
| AM1/34 | oscillatory function limit with exact squeeze bounds | `scalar` | missing | #236 |
| AM1/35 | standard infinitesimal, inverse-trig, logarithmic or power limit | `scalar` | partial | #236 |
| AM1/36 | all vertical/horizontal/oblique asymptotes by endpoint and direction | `ordered` | partial | #236 |
| AM1/37 | all continuity parameters at every join | `ordered` | partial | #236 |
| AM1/38 | all discontinuity locations with left/right limits and classification | `ordered` | missing | #236 |
| AM1/39 | root enclosure/approximation where requested; uniqueness proof separately deferred | `certificate` | partial | #236 |
| AM1/40 | derivative function from difference quotient, not just its value at a point | `expression` | partial | #237 |
| AM1/41 | full derivative expression and differentiability domain | `ordered` | partial | #237 |
| AM1/42 | tangent equation and point of contact | `ordered` | partial | #237 |
| AM1/43 | all tangent equations and contact points satisfying geometry | `ordered` | missing | #237 |
| AM1/44 | first-order propagated absolute error with stated units | `certificate` | partial | #237 |
| AM1/45 | finite, infinite or nonexistent lHopital limit with valid hypotheses | `limit_result` | partial | #237 |
| AM1/46 | all intervals of increase/decrease with domain breaks | `ordered` | partial | #237 |
| AM1/47 | all local extrema with locations, values and classifications | `ordered` | partial | #237 |
| AM1/48 | global extrema and all attaining points, or unattained bounds | `ordered` | partial | #237 |
| AM1/49 | optimal geometry and objective with feasibility/boundary comparison | `ordered` | partial | #237 |
| AM1/50 | antiderivative with arbitrary constant on each real domain component | `primitive` | partial | #238 |
| AM1/51 | minimum-degree polynomial meeting every stationary/inflection/value constraint | `expression` | missing | #237 |
| AM1/52 | parts antiderivative with constant and component domains | `primitive` | partial | #238 |
| AM1/53 | substitution antiderivative with constant and branch domains | `primitive` | partial | #238 |
| AM1/54 | definite integral with admissible bounds | `scalar` | partial | #238 |
| AM1/55 | Riemann-sum limit; learner derivation separately deferred | `scalar` | missing | #238 |
| AM1/56 | definite integration by parts | `scalar` | partial | #238 |
| AM1/57 | definite substitution with transformed bounds | `scalar` | partial | #238 |
| AM1/58 | total bounded region area with all pieces and intersections | `scalar` | missing | #238 |
| AM1/59 | arc length on complete specified interval | `scalar` | missing | #238 |
| AM1/60 | revolution volume around stated coordinate or shifted axis | `scalar` | missing | #238 |
| AM1/61 | revolution surface area, splitting nonsmooth points | `scalar` | missing | #238 |
| AM1/62 | physical work with declared positive physical parameters and units | `expression` | missing | #238 |
| AM1/63 | piecewise kinematic displacement or collision time | `scalar` | missing | #238 |
| AM1/64 | linear-denominator primitive with constants and excluded poles | `primitive` | partial | #238 |
| AM1/65 | irreducible quadratic primitive with completing-square decomposition | `primitive` | partial | #238 |
| AM1/66 | rational primitive with division/repeated and irreducible factors | `primitive` | partial | #238 |
| AM1/67 | trigonometric power primitive with reduction/angle identities | `primitive` | partial | #238 |
| AM1/68 | trigonometric rational primitive with substitutions and poles | `primitive` | missing | #238 |
| AM1/69 | all convexity/concavity intervals and inflection points | `ordered` | missing | #237 |
| AM1/70 | Taylor polynomial plus Lagrange remainder and intermediate-point constraints | `ordered` | missing | #237 |
| AM1/71 | Maclaurin polynomial plus nth Lagrange remainder | `ordered` | missing | #237 |
| AM1/72 | uniform exact absolute-error bound over the stated interval | `certificate` | missing | #237 |
| AM1/73 | computed approximation with certified requested accuracy | `certificate` | missing | #237 |
| AM2A/1.1 | convergence and value when finite; both tails independently | `ordered` | partial | #239 |
| AM2A/1.2 | convergence via explicit positive comparison | `category` | partial | #239 |
| AM2A/1.3 | convergence via positive finite limit comparison | `category` | partial | #239 |
| AM2A/1.4 | unbounded area, volume or surface convergence | `scalar` | partial | #239 |
| AM2A/2.1 | finite partial-sum expression and infinite convergence/sum | `ordered` | missing | #239 |
| AM2A/2.2 | convergence and integral-test hypotheses | `category` | partial | #239 |
| AM2A/2.3 | positive-series comparison classification | `category` | partial | #239 |
| AM2A/2.4 | limit-comparison classification | `category` | missing | #239 |
| AM2A/2.5 | ratio-test limit and convergence including factorial structures | `ordered` | partial | #239 |
| AM2A/2.6 | root-test limit and convergence | `ordered` | partial | #239 |
| AM2A/3.1 | sequence limit derived from series including factorial ratios | `limit_result` | missing | #239 |
| AM2A/3.2 | alternating convergence with hypotheses | `category` | partial | #239 |
| AM2A/3.3 | absolute/conditional/divergent classification | `category` | partial | #239 |
| AM2A/3.4 | entire convergence set with independent endpoint decisions | `real_set` | partial | #239 |
| AM2A/4.1 | full Maclaurin series and convergence set | `series` | partial | #239 |
| AM2A/4.2 | high derivative from coefficient and factorial | `scalar` | missing | #239 |
| AM2A/4.3 | differentiated/integrated power series and convergence set | `series` | partial | #239 |
| AM2A/4.4 | closed-form series sum on its correct domain; identity proof deferred | `expression` | missing | #239 |
| AM2A/4.5 | exact numerical series sum from generating functions | `scalar` | missing | #239 |
| AM2A/5.1 | full multivariable real domain with open/closed boundaries | `region` | partial | #240 |
| AM2A/5.2 | three-way surface/level-set matching; panels A/B/C shared | `deferred` | deferred | #244 |
| AM2A/5.3 | learner surface sketch | `deferred` | deferred | #244 |
| AM2A/5.4 | multivariable limit including nonexistent cases with path certificates | `limit_result` | missing | #240 |
| AM2A/6.1 | all requested first partials at the point, including nonsmooth cases | `ordered` | partial | #240 |
| AM2A/6.2 | full first partial vector with real domains | `ordered` | partial | #240 |
| AM2A/6.3 | computed Euler differential combination; identity proof deferred | `expression` | missing | #240 |
| AM2A/6.4 | tangent-plane coefficients and contact point | `ordered` | missing | #240 |
| AM2A/6.5 | all contact points or plane satisfying geometric condition | `ordered` | missing | #240 |
| AM2A/7.1 | linear approximation from full differential | `certificate` | partial | #240 |
| AM2A/7.2 | absolute/relative propagated measurement errors with units | `certificate` | partial | #240 |
| AM2A/7.3 | directional derivative value or nonexistence; one/two-sided convention explicit | `limit_result` | missing | #240 |
| AM2A/7.4 | complete gradient, not its norm | `ordered` | partial | #240 |
| AM2A/7.5 | normalized directional derivative | `scalar` | partial | #240 |
| AM2A/7.6 | derivative as angle function, maximum/zero directions and all unit vectors | `ordered` | missing | #240 |
| AM2A/8.1 | all ordered second partials/Hessian entries and their domains | `ordered` | partial | #240 |
| AM2A/8.2 | computed Laplacian; harmonic identity proof deferred | `expression` | missing | #240 |
| AM2A/8.3 | complete stationary points with classification and values | `ordered` | partial | #240 |
| AM2A/8.4 | constrained extrema with points, values and feasibility | `ordered` | partial | #240 |
| AM2A/9.1 | global extrema/attainment including boundary and noncompact cases | `ordered` | missing | #240 |
| AM2A/9.2 | least-squares minimizing point | `ordered` | missing | #240 |
| AM2A/9.3 | optimal open-container dimensions for prescribed volume | `ordered` | missing | #240 |
| AM2A/9.4 | skew-line distance via optimization | `scalar` | missing | #240 |
| AM2A/9.5 | cost-minimizing positive warehouse dimensions | `ordered` | missing | #240 |
| AM2A/9.6 | profit-maximizing nonnegative integer production counts | `ordered` | missing | #240 |
| AM2A/9.7 | all closest points and distance with global comparison | `ordered` | missing | #240 |
| AM2A/10.1 | rectangular double-integral exact value | `scalar` | partial | #241 |
| AM2A/10.2 | iterated integral value and generated region explanation | `scalar` | partial | #241 |
| AM2A/10.3 | equivalent order-reversed pieces for a generic integrand | `iterated_bounds` | partial | #241 |
| AM2A/10.4 | normal-region integral with intersections and splitting | `scalar` | partial | #241 |
| AM2A/11.1 | polar integral with Jacobian, sectors and shifted disks | `scalar` | partial | #241 |
| AM2A/11.2 | double-integral area including affine-coordinate and polar regions | `scalar` | missing | #241 |
| AM2A/11.3 | bounded-solid volume including clipped and shifted domains | `scalar` | missing | #241 |
| AM2A/12.1 | surface patch area with projection and graph/sphere Jacobian | `scalar` | missing | #241 |
| AM2A/12.2 | full centroid coordinates with additive/subtractive composite masses | `ordered` | missing | #241 |
| AM2A/12.3 | inertia about declared axis/point with positive symbolic dimensions/mass | `expression` | missing | #241 |
| AM2A/13.1 | decay mass/time/percent outputs and consistent physical units | `ordered` | missing | #242 |
| AM2A/13.2 | separable general solutions including equilibria/singular branches | `ode_family` | missing | #242 |
| AM2A/13.3 | separable IVP solution branches and maximal real intervals | `ode_family` | partial | #242 |
| AM2A/13.4 | nonhomogeneous first-order general solution and singular intervals | `ode_family` | missing | #242 |
| AM2A/13.5 | first-order IVP with symbolic initial parameters and maximal intervals | `ode_family` | partial | #242 |
| AM2A/13.6 | positive geometric curve family from trapezoid/tangent model | `ode_family` | missing | #242 |
| AM2A/14.1 | direct Laplace expression plus convergence half-plane, including graph-defined data | `ordered` | missing | #242 |
| AM2A/14.2 | direct Laplace using shifts/linearity plus convergence half-plane | `ordered` | missing | #242 |
| AM2A/14.3 | inverse transform on nonnegative time for all rational pole structures | `expression` | missing | #242 |
| AM2A/14.4 | Laplace IVP solution satisfying all initial data | `expression` | partial | #242 |
| AM1/exam-family/primitive-initial-value | primitive satisfying a point value | `expression` | missing | #238 |
| AM1/exam-family/differentiability-parameters | all join parameters making a piecewise function differentiable | `ordered` | missing | #237 |
| AM1/exam-family/monotonicity-convexity | intersection of full monotonicity and convexity intervals | `real_set` | missing | #237 |
| AM1/exam-family/substitution-then-parts | antiderivative requiring serial substitution then parts | `primitive` | missing | #238 |
| AM1/exam-family/constructive-decimal-existence | existence construction with a prescribed decimal prefix | `deferred` | deferred | #244 |
| AM1/exam-family/functional-limit-values | classify possible ratios for arbitrary continuous positive functions with constructions | `deferred` | deferred | #244 |
| AM1/exam-family/polynomial-sign-reconstruction | construct polynomial with exactly prescribed extrema and inflection points | `expression` | missing | #237 |
| AM1/exam-family/torus-shell-volume | torus volume for declared positive radii with major greater than minor | `expression` | missing | #238 |
