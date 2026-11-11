# Analysis I curriculum (#145)

The new `analysis1-…-v1` generators extend Mathematical Analysis using ADR-008.
Each row below is an issuing level with distinct methods, not larger random
coefficients. Parameters a, b and c are strict integers 1–5; seed is bounded by
the frozen code format. Every template has its own immutable version and prefix.

| Topic | Level | Declared templates |
|---|---|---|
| Functions and sequences | 1 | parity; square-root domain endpoint |
| | 2 | composition; affine inverse on R |
| | 3 | consecutive differences and monotonicity; least upper bound |
| | 4 | rational convergence; oscillation via subsequences; unbounded divergence |
| | 5 | exponential 1-to-infinity form; radical infinity-minus-infinity form |
| Limits and continuity | 1 | polynomial continuity and limit laws; removable 0/0 |
| | 2 | sine and exponential standard limits |
| | 3 | left and right limits of an absolute-value quotient; positive infinite limit |
| | 4 | rational infinity/infinity; oblique asymptote; piecewise continuity |
| | 5 | two applications of lHopital; certified bisection of exp(x)+x²=a+1 |
| Differential calculus | 1 | derivative by difference quotient; tangent slope |
| | 2 | numerical differential; exponential chain rule |
| | 3 | Lagrange mean value theorem; full derivative sign chart |
| | 4 | local maximum; global minimum on a compact interval |
| | 5 | rectangle area optimization; open-box volume optimization |

The existing **Derivatives** topic continues to provide elementary derivatives,
product/quotient/chain rules and higher structural levels. The six existing
single-variable integral topics are the Integral calculus part of Analysis I.
Their versions, statements, answers, public slugs and levels are unchanged.
No integral generator is duplicated. Partial derivatives and multiple integrals
remain separate existing topics for Analysis II (#146).

The existing combined-log rational-integral worker regression exceeded its CPU
cap during this expansion. A shared exact rational/log-absolute derivative
certificate now avoids repeated substituted symbolic proofs during replay and
checking, including every displayed rational transformation. Its domain check
is exact. Component constants are evaluated at exact interior points only after
equal derivatives are proved. All other proof paths and worker limits remain;
the frozen integral output corpus is unchanged.

## Answers, domains and steps

Exact scalar or real-expression answers use `ExpressionAnswer`, with declared x
only for composition, inverse, asymptote and chain-rule tasks. These four use the
existing expression kind with `FullRealExpressionAnswer`: the established
unevaluated-subexpression domain check runs before simplification, so added
terms such as 0/(x-2) cannot hide a hole in an all-real answer. Scalar tasks also
reject undeclared variables before cancellation, while accepting exact constants
such as pi and e. No input grammar, answer dispatcher, frontend answer bank or
frozen protocol is added.
Classification prompts explicitly define their numeric choices (parity,
convergence, boundedness and the sign of an infinite limit). Interval exercises
ask for an endpoint while their worked solutions display the complete domain
or monotonicity intervals. This avoids accepting ambiguous free-text intervals.

All identities/limits/derivatives/extrema are proved in the private mathematical
block. The box optimization compares all feasible stationary points and boundary
limits; global extrema include endpoints. The mean value task states the compact
interval and verifies the theorem's hypotheses. Cancellation excludes its pole.

Bisection uses [0,a], six iterations and a requested final midpoint. The unique
root exists by continuity and strict increase. Taylor sums with an exact rational
geometric bound on the tail certify every sign; floating-point rounding does not
choose a half-interval. The returned rational midpoint has error at most a/128.
The question requests that specific approximation, not an unspecified tolerance.
No symbolic closed-form solver is exposed to the learner or request process.

## Persistence and verification

The public API issues only verified rendered catalogue rows. Answers, parameter
records, proofs and solutions remain backend-private until an authorized reveal.
The only new database data is the additive `differential-calculus` topic row.
All three topics join area mixed practice with weight 1 at levels 1–5.
Saved practice, history, statistics, sharing and worksheets use the existing
owner-scoped paths. Historical `practice-sequence-v1` and `practice-limits-v1`
codes retain explicit opening views; all old golden entries remain unchanged.

New tests check every version's replay and equivalent/wrong answers, certified
bisection signs and error bounds, domains/optimization and limited-worker checks.
The shared 1,000-seed sweep, private pool replay and all-golden opening tests also
discover these versions. HTTP E2E covers all 15 Analysis I topic/level cells,
attempts, reveals, saved history, statistics and learner-safe anonymous sharing.
Hosted CI and deployed checks are recorded in the linked PR and HANDOFF.

The separate [sequence and continuity expansion](ANALYSIS_LIMITS.md) records
the #236 methods, answer contracts and source coverage.

## Elementary antiderivative expansion (#265)

Versions `INAA`–`INBM` cover AM1/50, AM1/52, AM1/53 and six exam references.
The source index maps each reference to its immutable version, including the
two exam forms that substitute and then integrate by parts. Practice uses the
existing Basic integrals, Integration by parts and Substitution topics.

Each seed draws three integers from 1 through 5. The forms use these as
coefficients, frequencies, shifts and exponents. Coincident frequencies in
product-to-sum forms are separated by increasing the second frequency by one.
Statements give the interval for the primitive so that roots, logarithms and
trigonometric denominators have the intended real branches. Difficulty rises
from termwise integration and single applications of parts to rationalized
substitutions and combined methods. These exercises ask for symbolic
antiderivatives on stated intervals, so they require no geometric diagram.

General primitives use the existing exact derivative check and require an
arbitrary constant. The exam problem with a prescribed value instead checks
the identity of the unique primitive on the positive interval. Solution steps
show how the stated substitution, identity or integration-by-parts formula
leads to the result. The golden fixture pins three seeds per version. The
independent numerical sweep differentiates each generated primitive against
the original integrand at interior points and checks the prescribed value when
present. The Linux worker tests verify accepted and rejected inputs under the
production resource limits. The saved-practice integration tests cover replay,
history, owner isolation, sharing and worksheet preparation.

## Rational antiderivative expansion (#266)

Versions `INBN`–`INCI` add 22 generators to Rational functions. The source
index maps AM1/64, AM1/65, AM1/66 and five exam references, reusing three
versions where an exam repeats the same computational method.

The bounded draws use three integers from 1 through 5. They give distinct real
poles, repeated linear factors, and strictly positive quadratics with rational
centres and widths. Each statement with real poles specifies a connected
interval between or beside them. This fixes the signs of logarithm arguments
and gives one arbitrary integration constant on the stated interval. The
worked steps show substitution, completing the square, polynomial division or
partial fraction decomposition as needed. There is no geometric diagram for
these symbolic problems.

The seed sweep compares the exact derivative with an independently specified
original fraction and checks the interval against its real poles. Three golden
seeds per version pin replay. Worker checks exercise accepted and rejected
answers, and representative saved-practice tests cover history, sharing and
worksheet preparation.

## Trigonometric antiderivative expansion (#267)

Versions `INCJ`–`INCY` cover AM1/67, AM1/68 and the exam sine-fourth primitive.
The prescribed-value primitive is already covered by `INBM`. The new versions
use odd-power substitutions, power reduction, partial fractions after cosine
substitution and tangent half-angle substitutions. Frequencies and amplitudes
range from 1 through 5. The shifted cosine-fourth family also varies its phase.
For the half-angle denominator family, an integer parameter gives Pythagorean
coefficients so that the transformed rational denominator is a perfect square.

Each rational trigonometric statement specifies a connected interval on which
its denominators and logarithm arguments have the required signs. Worked steps
show the substitution and the polynomial or rational integral that results.
These symbolic problems require no geometric diagram. Equivalent forms of the
integrand used for exact checking are tested independently against the original
trigonometric expression at 40-digit precision, along with the derivative of
the reference primitive. Three golden seeds, Linux worker checks and the
saved-practice integration tests cover replay and the private solution boundary.

## Definite integral expansion (#268)

Versions `INCZ`–`INDV` cover AM1/54 through AM1/57 and the exam linear-cosine
integral. They are available in the existing Definite integrals topic, with
levels separating direct endpoint evaluation, Riemann sums, integration by
parts, substitutions and an integrable singular endpoint.

Each reference solution evaluates a parameter-derived primitive at the stated
bounds. Substitution solutions give the transformed bounds. The endpoint-root
problem explicitly takes the right-hand limit at zero. The three Riemann-sum
families identify the continuous function, uniform partition and right-endpoint
sum before evaluating the limiting integral. Their diagrams use five sample
rectangles from the same function. The quarter-circle substitution also has a
parameter-derived solution diagram. The other symbolic endpoint calculations
require no separate geometric diagram.

Independent numerical quadrature verifies the original integrands and bounds.
Direct finite sums check the Riemann-sum normalization and its monotone error
bound. Diagram tests check coordinates and worksheet rendering. Seed sweeps,
golden replay, limited-worker checks and saved-practice integration tests cover
the new versions. The learner-proof components of AM1/55 stay deferred to #244.

## Integral applications (#269)

Versions `INDW`–`INFA` cover the 34 references in AM1/58, AM1/59, AM1/62,
AM1/63 and their exam families. They use the existing Definite integrals topic.
Every version supplies a parameter-derived profile, region or physical diagram.
Region solutions calculate intersections, specify the selected component and
split strips where the active boundary changes. Horizontal strips handle
inverse curves and circle slices. Exam prompts identify the relevant side of
an axis when several bounded components are possible.

Arc-length solutions derive the speed from the graph and state the interval
on which each simplification has the required sign. Work problems state the
units, spring extension, water density, gravity and lift height. The motion
problems carry velocity across the phase change and prove positivity or unique
collision time. All draw parameters are integers from 1 through 5. The reciprocal
power arc uses powers 2 through 4 and endpoints from 1 through 4. The exponential
region uses heights with exponent 2 or 4. These bounds keep exact rational and
logarithmic answers within the existing input grammar.

AM1/58/o needs a source correction. Tangent and cotangent intersect once on
the printed interval and enclose no bounded region. Vlad selected generated
total-area problems on that open interval, with answer infinity and a worked
divergence explanation. The source index records this decision.

Independent quadrature checks original boundaries, arc lengths, work and motion.
The diagram tests compare polygon areas and curve profiles with the
results and verify worksheet rendering. Formula answers reject numerically
distinct constants before symbolic logarithm simplification can create huge
integer powers. Numerical agreement still requires the existing exact equality
proof. Regression tests cover equivalent logarithms and small nonzero offsets.

## Solids of revolution (#270)

Versions `INFB`–`INFV` cover AM1/60, AM1/61, two exam applications and the
torus application. The generating profiles and rotation axes are drawn from
the same parameters as the volume or lateral-surface calculation. The diagrams
include the shifted horizontal or vertical axis where applicable. Worked
solutions state shell radii or washer radii and their signs, derive the
arc-length factor for surfaces, and retain all factors of pi. Lateral surfaces
include the surface swept by the generating curve.

The main exam sine problem asks for both volume and surface area. Its generator
returns an ordered pair and the source index restores the previously omitted
surface-area component. The torus family has positive minor radius and a
strictly larger major radius. Its reference solution derives the shell integral
and cancels the odd term after translation to the disc centre.

Original shell, washer and surface integrals are verified by numerical
quadrature. Surface tests also differentiate the original generating curves
independently. Diagrams and their rotation axes are checked for worksheet
compatibility. The versions have three golden seeds, production-worker checks
and saved-practice integration coverage. The mathematical computational scope
of #238 now maps 159 source references and 161 result components. The staged
learner proofs and sketch interactions retain their #244 deferrals.
