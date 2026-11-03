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
