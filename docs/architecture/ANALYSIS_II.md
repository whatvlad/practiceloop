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
