# Analysis II curriculum (#146)

Analysis II extends the existing Mathematical Analysis topics with 47 new
independently versioned templates and 141 additional golden samples. It reuses
the proven partial-derivative, double-integral and triple-integral generators.
All 118 generator versions shipped before this issue retain their exact codes,
statements, answers, steps, metadata and replay behavior.

## Issuing matrix

Every level denotes a method or structure, rather than a randomly assigned
difficulty label. Existing topic names, slugs, levels, mixed weights and worksheet
spaces remain unchanged. No database migration or new public topic is needed.

| Topic | Level | Templates |
|---|---|---|
| Improper integrals | 1 | existing convergent power integral; p-test including divergence |
| | 2 | power tail with a finite lower bound; exponential tail |
| | 3 | limit comparison; arctangent tail value |
| | 4 | logarithmic convergence threshold; comparison with the divergent harmonic integral |
| | 5 | mass of an unbounded rod with exponential density; volume of an unbounded solid of revolution |
| Series | 1 | existing geometric sum; p-series; necessary term test |
| | 2 | Leibniz plus absolute/conditional convergence; positive comparison; root test |
| | 3 | factorial ratio test; logarithmic integral test; Cauchy-Hadamard radius |
| | 4 | centered power-series endpoints and full convergence interval; infinite radius |
| | 5 | Taylor polynomial and full exponential expansion; sine/cosine Maclaurin polynomials and full expansions; logarithmic Maclaurin coefficient |
| Multivariable functions | 1 | closed disk and open ball domains in R²/R³; evaluation of two- and three-variable functions |
| | 2 | full gradient norm in R²; normalized directional derivative; third mixed partial |
| | 3 | total differential in R²/R³; full gradient norm in R³ |
| | 4 | local minimum with a positive definite Hessian; minimum/maximum/saddle classification |
| | 5 | Lagrange-constrained quadratic minimum; maximum box volume under a positive linear constraint |
| Differential equations | 1 | existing elementary exponential IVP; two separable IVPs |
| | 2 | affine-forcing first-order linear IVP; variable-coefficient integrating factor |
| | 3 | harmonic second-order IVP; distinct real characteristic roots |
| | 4 | repeated characteristic root; resonant forcing |
| | 5 | first-order exponential-forcing Laplace IVP; second-order forced-oscillator Laplace IVP |

All first-kind improper endpoints are at infinity; no second-kind singular endpoint
integrals are introduced. Series cover convergent and divergent positive series,
absolute and conditional alternating series, and both endpoint decisions. Taylor
tasks display the full analytic series and its convergence domain before the
requested finite polynomial or coefficient.

## Retained multivariable and integral matrix

These are existing generators, not reimplementations or replacements:

| Topic | Level | Retained structures |
|---|---|---|
| Partial derivatives | 1 | polynomial x/y derivatives |
| | 2 | exponential product, logarithmic factor, sine inner function |
| | 3 | mixed/second derivatives, three-variable derivatives |
| | 4 | polar and cylindrical chain rules |
| | 5 | scaled polar and cylindrical Jacobians |
| Double integrals | 1 | separable rectangular Cartesian regions |
| | 2 | rectangular regions with dependent intermediate results |
| | 3 | type-I/type-II Cartesian bounds; stated polar disk, annulus and sector |
| | 4 | reverse order; choose bounds from a region description |
| | 5 | Cartesian-to-polar conversion when the Cartesian inner integral is unsuitable |
| Triple integrals | 1–5 | existing Cartesian and cylindrical solids, iterated bounds and Jacobians |

The existing typed setups keep the region, iterated bounds, coordinate change,
Jacobian factor r and checked integration steps. Their solution-only visuals and
all historical saved fields remain intact. The frozen 84 partial-derivative and
44 multiple-integral form corpus still runs, along with all shipped goldens and
independent integration orders. Extra regression cases explicitly inspect polar
disk/annulus/sector/conversion bounds and Jacobians.

## Records, domains and exact checking

Drawn primitive parameters a, b and c are strict integers 1–5; a seed is in the
frozen 16-digit range. Derived exponents, Taylor degrees and unit directions come
from finite declared rules. Directions use the fixed triples (3,4,5), (5,12,13)
and (8,15,17), always normalized exactly. Generator prefixes are allocated
explicitly, independently of the product topic order.

The generator provider composes strict mathematical forms, exact proof results,
the existing typed expression answer and permanent codes. English prompts and
worked explanations belong to generator modules; the product matrix belongs to
`topics/analysis_two.py`. The private helper modules are trusted application code,
not plugins selected by a request. Registry discovery and all frozen protocols
are unchanged.

Numerical questions use the existing scalar expression kind and its strict
constant policy. Classification prompts state their numeric choices. A power
interval question requests its endpoint-inclusion mask and displays the complete
interval in the solution. Domain questions request the radius and display the
full open/closed disk or ball. Gradient/differential questions show all components
and request an exact scalar norm, direction value or differential. This keeps
the questions fully specified within the existing formula editor.

Taylor polynomials and every new ODE solution declare real x and use the all-real
answer policy added in #145. Domain holes are checked before cancellation; scalar
answers reject undeclared variables before cancellation. All new IVPs have global
real solutions. The separable square-root IVP explicitly takes its positive branch,
whose radicand is strictly positive for every real x.

Exact residuals and all initial values verify each ODE, including the second initial
condition for order two. Laplace solutions additionally verify their rational
transforms with real exponential/sine/cosine tables and state the convergence
half-plane. Independent tests use SymPy dsolve and Laplace transforms, not the
generator's construction. No numerical solver or learner-entered equation/setup
is exposed in requests.

Equivalent arctangent tail forms are compared through the exact real identity
atan(q)=pi/2−atan(1/q) for rational q>1. Its derivative and value at 1 are independently
proved in tests. Numerical samples never establish equality. Other unsupported
identities retain the existing safe inconclusive outcome rather than a guessed
acceptance.

## Integration and verification

Public topics and mixed weights stay fixed. Existing geometric-series, power-tail
and exponential-IVP generators remain in introductory issuing cells. All four
replaced placeholder versions retain historical level views for permanent codes;
saved history and old reveals are not rewritten.

Practice and worksheets continue to read the private verified 64-code catalogue;
requests do not fall back to generation. Records remain exactly generator_version
and code. Only statement/topic/level cross anonymous code/share boundaries; answers
and steps remain behind authorized reveals. History/statistics use the unchanged
owner-scoped APIs and RLS rules.

Tests cover every new template's JSON replay, equivalent and wrong answers,
undeclared variables and hidden holes, independent convergence/integration/ODE
proofs, all prior goldens, all 1,000-seed topic sweeps and every stored catalogue
row. The HTTP E2E matrix now has 74 scenarios: all 36 public topics, both area
mixes, every Analysis I/II level and the retained partial/double-integral levels,
including attempts, reveals, pagination, statistics and anonymous sharing.
Ready CI, deploys and live code checks are recorded in the PR and HANDOFF.

Spherical coordinates, line/surface integrals, complex analysis, PDEs, numerical
solvers, learner-entered setup, adaptive learning, localization and Probability
and Statistics (#200) remain excluded. TeX verification is still disabled under
#181. No MVP, database, dependency, lockfile or frozen engine interface changes.

## Improper integral source expansion (#271)

Versions `IPAA`–`IPAT` cover AM2A/1.1 through AM2A/1.4 in the existing
Improper integrals topic. Definition problems return convergence and the improper
value, including infinity or a nonexistent oscillatory limit. The two-sided
families separately return both tails and the full value. Their reference
solutions require each tail to converge independently.

Direct-comparison solutions give explicit inequalities and the range where
they hold. Limit-comparison solutions calculate a positive finite limit and
identify the corresponding power criterion. Positive integer parameters from
1 through 5 keep poles and square-root zeros outside each stated tail. The
surface family varies its decay exponent from 1 through 3, with a two-sided
comparison that decides finite or infinite lateral area.

The oscillatory truncated integral and the three unbounded geometric
applications have parameter-derived solution diagrams. Their descriptions
identify the truncated plotting window. Other classifications and symbolic
tail limits require no geometric diagram. Independent tests check finite tails
by quadrature, oscillatory endpoint sequences, asymptotic ratios and the surface
bounds. Golden replay, Linux worker checks and saved-practice integration cover
the versions. The source index retains the deferred learner-proof components.

## Partial sums and comparison tests (#272)

Versions `SRAA`–`SRAT` cover AM2A/2.1 through AM2A/2.4 in the Series topic.
The partial-sum families give a structural formula for `S_N` and ask for its
exact coefficients, convergence and infinite sum. This determines the complete
formula, including the factorial telescoping form. Worked solutions derive the
telescoping or geometric identity. Their diagrams show the actual partial sums
at integer endpoints and the limiting sum when finite.

Integral-test variants state positivity and eventual decrease, then exhibit a
primitive or convergent tail integral. Direct comparisons give explicit positive
bounds. Limit comparisons calculate the coefficient and identify the harmonic,
power or geometric series used. Factorial quotients are cancelled before taking
their asymptotic limit. Sampled integer coefficients and shifts range from 1
through 5. Logarithmic powers are 2 or 3, and factorial shifts are 2 or 3.

Independent tests sum the original finite terms, reconstruct the entire
partial-sum formula from the submitted coefficients, check interpolation
monotonicity and verify comparison orders and bounds. Three golden seeds,
limited-worker checks and saved-practice integration cover the versions.

## Ratio and root tests, sequence limits (#273)

Versions `SRAU`–`SRBG` cover AM2A/2.5, AM2A/2.6 and AM2A/3.1. Ratio and
root problems return the exact test limit together with the convergence
classification. Sampled coefficients vary across both sides of the threshold.
When the limit is one, the central-binomial and quadratic-self-power families
also check the necessary term condition. A unit test limit alone never decides
their convergence.

The sequence families prove convergence of a suitable positive series before
using its vanishing term, or use the reciprocal of that term for an infinite
limit. Balanced factorial quotients retain equal total factorial degree and use
strict convexity of `t log t` to prove their ratio limit is below one. Integer
coefficients range from 1 through 5. Multiple-factorial steps are 2 or 3, and
the polynomial-exponential sequence has degree at most 36.

Independent tests evaluate the ratios or nth roots of the original terms and
the sequence values at large integer indices, including both unit-limit cases.
These algebraic convergence and limit problems require no geometric diagram.
Three golden seeds, worker checks and saved-practice integration cover replay
and the answer contracts.

## Alternating and power series (#274)

Versions `SRBH`–`SRBU` cover AM2A/3.2 through AM2A/3.4. Leibniz solutions
identify positive magnitudes, prove eventual decrease and take their limit.
Absolute-convergence classifications distinguish geometric domination,
conditional harmonic-size terms and failure of the necessary term condition.
The negative rational-power family includes the unit-root-limit case, whose
terms have a nonzero limiting magnitude.

Power-series versions return the full real convergence set. Every finite
boundary is tested separately in the solution. The logarithmic-power family
includes its left endpoint and varies right-endpoint inclusion with exponent
1 or 2. Geometric, exponential-difference and even-power families exclude both
endpoints when their terms fail to vanish. The factorial family converges on
the whole real line. Parameter-derived number-line diagrams show endpoint
inclusion or arrows in both directions for the entire real line.

Independent tests evaluate the original alternating magnitudes, root limits,
interior and exterior terms and the boundary terms. They also verify diagram
markers and worksheet rendering. Golden seeds, worker checks and saved-practice
tests cover all fourteen versions.

## Maclaurin coefficients and high derivatives (#275)

Versions `SRBV`–`SRCI` cover AM2A/4.1 through AM2A/4.3. Full expansions use
a stated coefficient template with positive unknown constants `A` and `B`.
The answer supplies both constants and the complete convergence set, so it
determines the whole infinite expansion. The families include geometric, sine,
polynomial-exponential, odd rational, hyperbolic cosine and sine-square forms.
Termwise differentiation and integration produce the four AM2A/4.3 families.
Their reference solutions explain the transformation and decide both endpoints.

High-derivative tasks extract the requested Maclaurin coefficient before
multiplying by the factorial. The cosine-product orders range from 42 through
58, and the exponential-product orders from 17 through 25. Odd rational orders
are 5, 7, 9 or 11. The sine-square product includes both odd and even orders,
with the even derivatives vanishing. Parameter bounds keep the exact scalar
answers within the existing numeric-literal budget.

Expansion solutions include convergence number lines. Algebraic high-derivative
calculations require no geometric diagram. Independent symbolic Taylor
expansions verify all coefficient formulas, and direct differentiation checks
the high derivatives. Seed sweeps, goldens, worker checks and saved-practice
integration cover the versions.

## Identities and exact numerical sums (#276)

Versions `SRCJ`–`SRCP` cover AM2A/4.4 and AM2A/4.5. The two weighted
geometric identities follow from termwise differentiation inside the radius.
The factorial identity in AM2A/4.4/c is corrected to the exponential sum
`a (exp(bx) - 1)` on the real line. The printed logarithmic identity belongs
to a different series with denominator `n`. The source index records the
correction, and tests reject that logarithmic expression for the factorial
problem.

The four numerical-sum families rescale geometric identities or integrate a
geometric series to obtain the legitimate logarithmic sum. Reference solutions
show index changes and subtraction of omitted initial terms. Formula identities
have convergence number lines. Scalar numerical sums require no geometric
diagram. Independent Taylor coefficients and direct 200-term sums verify the
results, with full seed sweeps, goldens, worker checks and practice integration.

The local computational scope of #239 now maps 88 source references and 88
result components. Learner proofs retain their recorded #244 deferrals.

## Natural domains and multivariable limits (#277)

Versions `MVAA`–`MVAJ` cover AM2A/5.1 and AM2A/5.4. Domain exercises give
named inequality predicates and ask for the full region as a Boolean formula.
The grader compares truth values on every geometrically realizable assignment
of those predicates. This accepts equivalent descriptions and distinguishes
strict boundaries, included boundaries and denominator poles.

Parameter-specific diagrams show planar regions, the xz projection of the
independent square-root region and a meridian section of the spherical shell.
Limit solutions use uniform radial bounds or compare coordinate-axis limits.
The quadratic cosine family varies whether the axis limits coincide and proves
the joint limit by radial substitution in the equal-coefficient case.
Independent domain witnesses and high-precision radial evaluations cover the
generated cases. Golden seeds, worker checks and saved-practice integration
cover the answer contracts.

## First partial derivatives and Euler identities (#278)

Versions `MVAK`–`MVBA` cover all thirteen computational references in
AM2A/6.1 through AM2A/6.3. The pointwise exercises use coordinate difference
quotients, including the radical at the origin. Formula exercises explicitly
specify the positive orthant, where the exact formula contract can check
well-definedness. For the nested trigonometric and radical families, each
coordinate derivative has a separate version so full symbolic answers fit
the shared input budget. Euler families return the two partials and the
constant in the stated identity. Worked solutions explain the differentiation
rules, the coordinate restrictions and the Euler cancellation.

Independent high-precision differentiation checks every coordinate and the
Euler identities across the parameter sweep. Golden seeds and practice
integration cover the pointwise, tuple and single-formula answers.

## Tangent planes and total differentials (#279)

Versions `MVBB`–`MVBO` cover AM2A/6.4 through AM2A/7.2. Tangent-plane
problems return the exact two slopes and offset, or the exact contact point
for a specified parallel plane. Axis-intersection and normal-vector conditions
determine the base point before constructing the plane. Plots show both
coordinate sections of the surface with their tangents at the same height.

Linear approximation exercises return the exact first-order change and the
linear estimate. Measurement problems give the first-order absolute volume
error, diagonal increase, or relative volume error as requested. Their plots
compare the first-order model to the original function along the perturbation.
Independent numerical differentiation checks both plane slopes, the contact
height, and the directional changes. Plot checks also verify the worksheet
rendering and the displayed estimates.

## Gradients and directional derivatives (#280)

Versions `MVBP`–`MVCB` cover AM2A/7.3 through AM2A/7.6. The nonsmooth
exercises ask for both one-sided difference-quotient limits and their
two-sided limit. The norm has two distinct finite slopes, while the real
cube root has two positive infinite limits. Smooth exercises compute full
gradients or the dot product with a given unit direction. For AM2A/7.5/a,
the printed equality `f(x,y)=x²=y²` leaves the function unspecified. The
replacement exercise independently specifies a parameterized difference of squares.

Extremal-direction tasks encode angles by unit vectors. The positive-x
zero-rate vector determines its opposite, and the maximizing vector is
the normalized gradient. Parameter-specific plots show directional sections
or the rate as a function of angle. Independent numerical tests check both
one-sided quotients, every gradient coordinate, and the unit-vector,
orthogonality and maximal-rate conditions.

## Second partials and local extrema (#281)

Versions `MVCC`–`MVCZ` cover AM2A/8.1 through AM2A/8.4. Hessian tasks
request the distinct entries and explain equality of mixed orders. The
nested logarithm distributes its six entries across three versions to fit
the exact formula parser. Laplace exercises return both pure partials and
their sum. These formula exercises state their positive-coordinate domains.

Local-extremum solutions solve the stationary equations and classify all
candidates with the Hessian. The square-root problem also examines its
boundary. The constrained families reduce the problem to a line, parabola,
positive logarithmic profile or circle. The parabolic profile distinguishes
its two global minima and its local maximum. Local sections and restricted
profiles illustrate the classified points. Independent numerical tests
check the Hessian entries, critical points, signs, values and constraints.

## Global extrema and distances (#282)

Versions `MVDA`–`MVDH` cover AM2A/9.1, AM2A/9.2 and AM2A/9.4.
The global-extremum families solve in scaled coordinates and report points
in the exercise coordinates. Solutions account for all equality cases
and show every extremizer in the feasible-region diagram. Where symmetry
gives four equivalent points, the input requests a specified representative.
The least-squares task uses the centroid identity. The skew-line task uses
the lower bound from vertical separation and constructs a connector attaining
it. Independent tests evaluate feasible samples, extremal values and points,
the least-squares increase and the skew-line cross product.

## Applied optimization (#283)

Versions `MVDI`–`MVDL` cover AM2A/9.3 and AM2A/9.5 through AM2A/9.7.
The tank and warehouse use fixed-volume reduction to a square base and a
one-variable minimum. The profit exercise constructs a unique nonnegative
integer optimum and proves it by completing the quadratic. The parabola
exercise uses strict convexity of the squared distance and shows the
perpendicular connector. Independent tests check volume, objective values,
discrete alternatives and the connector.

The local computational scope of #240 covers all 84 source references and
84 result components in 90 versions. Learner proofs and sketches retain
their #244 deferrals.

## Cartesian double integrals and order reversal (#284)

Versions `DIAA`–`DIAX` cover AM2A/10.1 through AM2A/10.4. Definite
integrals show the iterated bounds, the inner antiderivative and the
remaining one-variable calculation. Normal-region exercises start with
the boundary equations. Every exercise has a region diagram.

Order reversal answers supply one to three pieces with exact outer
endpoints and exact inner functions, in the order stated in each exercise.
Inner functions are checked on the corresponding closed outer interval in
the correct coordinate. This supports square-root and inverse trigonometric
boundaries. Independent tests compare numerical double quadrature and verify
reversed-region membership against the original inequalities across the seed
sweep. Drawing the region as a learner interaction stays with #244.

## Polar integrals, areas and volumes (#285)

Versions `DIAY`–`DIBP` cover AM2A/11.1 through AM2A/11.3. Polar
solutions show the coordinate substitution, Jacobian, radial bounds,
radial primitive and angular calculation. The parallelogram uses an
affine Jacobian. Volume families integrate the height difference over
the projected region or the disk area at each height. Diagrams show
the integration boundaries and both limiting sections for the
paraboloid slab. Independent quadrature checks the original Cartesian
integrands, planar areas and volume heights.

## Surface patches, centroids and inertia (#286)

Versions `DIBQ`–`DICF` cover AM2A/12.1 through AM2A/12.3. Surface
solutions use the graph area element over the projected domain. The
sphere over a tangent disk handles its integrable equatorial endpoint.
Centroids use first moments, including adding a semicircle to a triangle
and subtracting one from a square. The exponential bound printed in
AM2A/12.2/c is constant, so that family uses a rectangle.

Inertia solutions use squared distance to the named axis or center with
density `m/A`. Answers are exact expressions in the declared positive
mass `m`. The ellipse asks for both axis moments. Independent tests
integrate the original surface and moment expressions and check the
projected boundaries, centroid markers and worksheet rendering.

The local computational scope of #241 covers 58 source references and
58 result components in 58 versions. Learner sketches retain the #244
deferral recorded in the source index.

## Decay and separable equations (#287)

Versions `ODAA`–`ODAO` cover AM2A/13.1 through AM2A/13.3. Decay
exercises use exact observation ratios and half-lives. General separable
solutions use a normalized family template with a free real constant,
graded admissible constant sets and equilibrium values. The worked
solution gives the maximal branch intervals and all differentiable
continuations. The vanishing-factor and arcsine families include
stationary plateaus and their joins.

Initial-value problems grade the maximal open interval together with
the solution. Two positive branches use normalized implicit functions
to express solutions without requiring Lambert W or a numerical answer.
The square-root IVP at an equilibrium is nonunique. It grades the two
functions defining the branch, the range of independent departure
constants, and the common maximal interval. The logarithm-sine IVP
explicitly excludes zeros of the leading sine coefficient. Independent
tests evaluate decay observations, ODE residuals, initial conditions,
branch joins and interval endpoints.

## Linear first-order equations and tangent curves (#288)

Versions `ODAP`–`ODAZ` cover AM2A/13.4 through AM2A/13.6. Linear
families grade a normalized particular solution, homogeneous factor,
arbitrary constant set and time domain. The Euler families distinguish
differentiable joins at zero from logarithmically singular cases.
Initial-value problems include an equilibrium case and two intervals
cut by singular coefficients or poles.

The tangent problem uses the trapezoid area to derive a linear equation.
It grades the full arbitrary-constant family and both strict intercept
bounds. The diagram shows a representative curve, its tangent and the
trapezoid with the generated area. Independent residual and initial
value tests verify the formulas, singular behavior and the diagram area.

## Direct and table-based Laplace transforms (#289)

Versions `LTAA`–`LTAO` cover AM2A/14.1 and AM2A/14.2. Exact answers
include the real convergence set. Compact-support graphs have a
formula away from zero and a separate value at the removable point
(s=0). Worked solutions show the definition, integration by parts,
linearity or the exponential shift as appropriate.

Three tasks derive the transform from a generated rectangle, triangle
or ramp with a constant tail. The plot and its exact text description
are part of the public condition and are projected from the frozen
code without building the symbolic answer. Practice, history, share,
code lookup and exercise PDFs preserve the same prompt. The answer and
derivation use the existing reveal workflow. Independent numerical
quadrature checks all transforms and tests the graph projection.

## Inverse Laplace transforms and forced IVPs (#290)

Versions `LTAP`–`LTBC` cover AM2A/14.3 and AM2A/14.4. Inversion
uses simple and repeated poles, completed squares and exponential
shifts. The IVPs derive the rational transform with the initial data
and invert it on the stated real convergence half-line. The resonant
decay family detects cancellation of its zero pole and adjusts that
half-line. Time diagrams show the same computed functions.

Independent tests integrate the time functions against the Laplace
kernel and compare with the original transforms. They also check
forcing residuals, initial values and initial derivatives. The local
computational scope of #242 covers 55 source references and 57 result
components in 55 versions.
