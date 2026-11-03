# Probability and Statistics curriculum (#200)

Status: **approved by Vlad; implementation in progress**. Vlad accepted the
complete nine-topic/five-level matrix, design and exclusions linked at planning
commit `ce4b1c4dd6c5f65e16bd178e82fe00b32c43f6cf`; the decision is recorded in
issue comment 6604843016. Base: `b8130b8bf499e9d56a8c9a2e676fffa56eef562b`.

## Approved release

Add the public area `probability-statistics`, titled **Probability and
Statistics**, with nine topics and five structural levels per topic (45 cells).
Every named structure in a cell receives a versioned template; levels describe
methods, not wider random coefficient ranges. There are 74 new frozen versions
with explicit PSAA through PSCV prefixes and 222 appended golden samples.
All existing 36 topics,
165 generator versions, historical codes and product metadata remain intact.

| Public topic / slug | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|---|---|---|---|---|---|
| Events and counting / `probability-events` | Equally likely finite outcomes | Complements and at-least-one events | Union, intersection and inclusion-exclusion | Counting selections without replacement; finite event-set operations | Independence from a consistent event table |
| Conditional probability and Bayes / `conditional-probability` | Conditional probability from a table | Two draws with/without replacement | Total probability over two groups | Bayes with two possible sources | Three-source Bayes and a two-stage probability tree |
| Discrete random variables / `discrete-random-variables` | Normalize a finite probability table | Point and cumulative probabilities | Tails and the finite support set | Recover masses from CDF jumps | Distribution of a transformed finite variable, including collisions |
| Standard discrete distributions / `discrete-distributions` | Bernoulli | Binomial | Geometric, counting trials through the first success | Hypergeometric | Poisson |
| Continuous distributions / `continuous-distributions` | Uniform probabilities | Normalize a bounded polynomial density; identify its support interval | Piecewise polynomial CDF and interval probabilities | Exponential tails, memorylessness and quantiles | Normal standardization, probabilities and quantiles using supplied tables |
| Moments and joint distributions / `moments-joint-distributions` | Expectation | Variance and standard deviation | Affine transformations and linearity | Joint tables, marginals and conditional probabilities | Covariance, correlation and independence of two variables |
| Descriptive statistics / `descriptive-statistics` | Arithmetic and weighted means | Median and all modes | Quartiles and IQR with the convention stated | Population/sample variance and standard deviation | Pearson correlation and least-squares slope/intercept |
| Confidence intervals / `confidence-intervals` | Normal mean with known population sigma, two-sided z | Normal mean with unknown sigma, t | One-sided mean bounds | Large-sample proportion interval with stated conditions | Paired-mean t and independent-mean difference with known sigmas |
| Hypothesis tests / `hypothesis-tests` | Calculate a mean z statistic | One-/two-sided z decisions | One-sample t statistic and decision | Large-sample proportion test | Paired t and independent-mean z decisions |

Each topic offers levels 1-5, mixed weight 1 and appropriate worksheet space.
Mixed practice and worksheet capacity come from the existing verified-catalogue
path. Existing combinations stay in Algebra; probability tasks reuse exact
integer binomial coefficients rather than change `combinations-v1`.

This is an introductory probability and statistics release. It does not include
ANOVA, chi-square/F tests, multiple regression, nonparametric methods, stochastic
processes, proofs of limit theorems, simulation, uploaded datasets or arbitrary
learner-entered distributions. These exclusions were included in the accepted request.

## Mathematical conventions and bounded records

- Finite samples/supports have at most eight distinct values; joint tables have
  at most 4 x 4 entries. Exact rational masses are nonnegative and sum to one.
  A conditional event always has strictly positive probability.
- Distribution primitives use strict integer/rational parameters. Declared
  bounds: support/data values -12..12; binomial n <= 12; geometric query <= 12;
  hypergeometric population <= 20; Poisson rate 1..5. Structured records reject
  bool-as-int, invalid supports and invalid parameter combinations.
- Datasets have 3..12 observations; paired datasets have equal lengths.
  Median, all modes and quartiles are explicitly defined. Quartiles use medians
  of the lower/upper halves, excluding the overall median for odd n. Population
  variance divides by n; unbiased sample variance divides by n-1. Correlation
  and regression require nonzero relevant variances.
- Uniform/exponential scales are positive. Polynomial densities have degree at
  most three and are constructed with exact nonnegativity and normalization
  certificates. Continuous CDF endpoints, support and moments are checked.
- Every geometric statement names its support {1,2,...}; normal parameters
  distinguish sigma from sigma squared. Every inference task states sampling,
  normality/large-sample assumptions, alpha, tail and the target parameter.
- Normal/t critical values and normal CDF entries come from a finite verified
  table and are supplied in the statement with their precision. A question says
  to use those displayed values. Checking proves equality to the calculation
  from those supplied constants; it does not claim a rounded table is an exact
  distribution identity. Learners need no erf or inverse-CDF grammar.
- Mean inference uses bounded sample sizes 4..100 and positive variances.
  Proportion examples use n <= 200, with both success/failure counts at least
  10 (under the null for tests, using the estimate for the proposed Wald CI).
  Generated proportion intervals stay within [0,1]. Approximate procedures are
  labeled. The confidence interpretation describes repeated-sampling coverage.
- Decisions use the stated strict critical region; fixtures cover equality at
  a boundary. "Do not reject" does not assert that the null is true. No p-value
  requires an unsupported numerical distribution computation.

Published seeds keep the existing PRNG and code format. Parameters are drawn
once, validated, and deterministically built; no rejection/redraw loop or
learner-selected mathematical program is introduced. New frozen prefixes are
allocated explicitly after the curriculum is accepted.

## Distribution block design

`blocks/distribution.py` supplies strict immutable mathematical data/results:

1. `FiniteDistribution`: distinct rational support, rational masses, exact
   normalization, event probabilities, CDF values, expectation/variance and
   pushforward aggregation. `JointDistribution` additionally supplies marginals,
   conditionals, covariance and an exact independence certificate.
2. Trusted bounded standard forms: Bernoulli, binomial, geometric,
   hypergeometric and Poisson. Each has an explicit support convention, pmf,
   queried finite sums/tails and exact moment identities. Infinite-family
   normalization is justified by its mathematical identity rather than by
   truncating a simulated sample.
3. Continuous forms: uniform, exponential and certified bounded polynomial
   density segments. Results expose exact bounds, CDF/primitive certificates and
   moments. Normal tasks compose a typed normal parameter form with the finite
   supplied-reference-table data; no general numerical CDF solver is exposed.

Blocks contain mathematical data and proofs. Generators own English prompts and
step text. Topic entries own the product matrix. Composition uses typed results,
never another task's metadata. Trusted formulas are verified independently in
tests; no sample comparison establishes learner-answer equivalence.

## New answer kinds and input UI

Retain `Answer.check(MathNode) -> Outcome`, Task/TaskGenerator/Topic and all
existing signatures. Add three answer classes and corresponding bounded AST
root variants. A small `parse_answer_input` entry point chooses grammar using
the trusted generator answer kind; scalar cases delegate to the unchanged
`parse_math_input`. It is used consistently before worker admission and inside
the limited child. The learner cannot select an alternate checker.

| Kind / actual consumers | Learner input and wire text | Comparison |
|---|---|---|
| `boolean`: independence and hypothesis decisions | Accessible Yes/No radio group, initially unselected; canonical `true` / `false`. The question explicitly asks the yes/no proposition. | Exact boolean equality; numeric 0/1 is not silently substituted. |
| `finite_set`: events, finite supports, all modes | Up to eight formula fields, add/remove controls and an explicit empty-set action; `{1,2/3}` or `{}`. Plain-text fallback uses the same syntax. | Order-independent exact real scalar equality, with mathematically equal duplicates normalized. |
| `interval`: supports and confidence bounds | Two formula fields, open/closed endpoint controls and unbounded-end choices; e.g. `[1/3,2/3]`, `(-inf,2]`. Plain-text fallback uses the same syntax. | Endpoint equivalence and closure/unboundedness; reversed or undefined endpoints are invalid. One nonempty interval only, no union grammar. |

New scalar answers continue to use the constant expression policy and the
existing formula editor. No convergence/classification number masks stand in
for the three new kinds.

The global 256-byte, AST/token/nesting and worker limits still apply to an entire
structured answer, not independently to each component. Finite-set entries and
finite interval endpoints use the existing bounded constant expression grammar
with no free variables; infinity is a dedicated endpoint sentinel, never an
arbitrary SymPy expression. Undefined/complex values and cancelled domain holes
are rejected before equivalence. Undecided proofs retain `inconclusive`, not a
guessed result. No eval, sympify of learner strings, distribution parsing or
network computation is introduced.

Keep the attempt request's answer string and the private two-key generator
record. Public problem/open-code/share/history projections may add an optional
`answerInput` descriptor only for new structured tasks. It contains a validated
kind and fixed input limits, no expected values or private parameters. It is
derived from trusted registry metadata without building a symbolic task in the
API. Existing task output and old public projections stay unchanged. History
reopens the proper input and preserves the original last-answer string;
authorized reveals render the answer class's safe LaTeX. Worksheet printing and
anonymous shares continue to obey their existing privacy boundaries.

This additive grammar design is recorded as an ADR-003 input amendment during
implementation; it does not change the frozen engine protocols in ADR-008.
Scalar parsing, old goldens and the frontend/backend syntax corpus must remain
compatible. New input controls require keyboard, mobile/fallback, accessibility,
invalid/unfinished and reopen/history tests.

## Delivery and verification after approval

1. Record Vlad's approval (or revise this matrix first), then implement the
   Distribution block and answer classes/grammar/UI with independent tests.
2. Add bounded generator providers and nine declarative topic entries; add one
   additive topic-row migration, preserving existing IDs and rows. Update the
   shared area types, catalogue/dashboard/curriculum, statistics and worksheets.
3. Append at least three goldens per new version. Cover each named structure,
   correct/equivalent/wrong/invalid answers, all 45 topic cells with 1,000-seed
   sweeps, and every release-pool record. Verify all 165 prior versions unchanged.
4. Independently prove finite sums/moments, pmf and density normalization,
   transforms, inference formulas and boundary decisions. Every new canonical
   and declared alternative answer must meet the existing 1 s CPU target inside
   the unchanged 2 s CPU/256 MiB/3 s wall worker boundary.
5. Extend HTTP E2E for every new topic/level plus area mixed practice, all answer
   kinds, history/reveals/sharing and owner isolation. Run normal backend,
   PostgreSQL, frontend and security checks; strict KaTeX covers all formulas.
6. Use a draft PR while fixing, request advisory mathematical/database review,
   mark ready, wait for full green hosted CI, merge, update/read back the project,
   check migrations/frontend/backend deploys and verify live public codes and UI.

TeX remains disabled under #181. No other queue issue is included. Graphify is
optional agent tooling, never a runtime or production dependency.

## Reference conventions

The proposed sequence and bounded templates are product choices for owner
review. Mathematical reference points include [Penn State STAT 414](https://online.stat.psu.edu/stat414/index)
for probability/distributions, [NIST confidence intervals](https://www.itl.nist.gov/div898/handbook/prc/section1/prc14.htm)
for known-sigma bounds and coverage, and [NIST confidence limits for the mean](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm)
for t intervals and sided critical regions. Exact finite lookup values and
fixtures must be checked against their primary tables during implementation.
