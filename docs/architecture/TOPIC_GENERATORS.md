# Integration topic generators

The rollout notes below describe the historical curriculum. After #199 the
legacy modules mentioned below are removed; current implementations are native
`app/engine/` forms and generators. See [final ADR-008](../decisions/0008-generator-engine.md)
for current module paths, extension instructions and verification commands.


Issue #9 was split before implementation into #77 (substitution), #78 (parts),
#79 (rational functions) and #80 (trigonometric integrals). These internal
libraries implement the remaining rows of
[ADR-003](../decisions/0003-mathematical-input-and-equivalence.md).

There are 18 templates and 108 distinct parameter records. Integration by parts
has three levels, 1–3 (ADR-003 amendment of 2026-10-20); it has no level 4 or 5. These templates
are indefinite; `definite-v1` (below) adds bounds to some of them. Coefficients are the six nonzero integers from -3 to 3. Difficulty
comes from the formula and transformations, never from increasing this range.

| Version / topic | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|---|---|---|---|---|---|
| `substitution-v2` | Visible derivative pair | Affine inner function and factor | Polynomial inner function | Factor a square before substitution | Double-angle identity and nested substitutions |
| `parts-v1` | Linear polynomial times exponential | Repeated parts with a quadratic | Cyclic exponential times sine | Not offered | Not offered |
| `rational-v1` | Constant over x | Denominator derivative | Distinct linear factors | Repeated linear factor | Polynomial division, then partial fractions |
| `trigonometric-v1` | Sine | Double argument | Odd sine power | Even sine power | Double-angle identity, then substitution |

## Use and persistence boundary

From `backend/`, with the project environment:

```python
from app.generators.families import generate_family, replay_family

problem = generate_family(topic="rational-functions", difficulty=5, seed=42)
record = problem.parameters.model_dump(mode="json")
assert replay_family(record) == problem
public = problem.public().model_dump()
```

The other topic slugs are `substitution`, `integration-by-parts` and
`trigonometric-integrals`. The local PRNG leaves global random state untouched.
A seed must be a strict unsigned 32-bit integer. Store the selected record,
not just the seed. Each complete private record has only these fields:

```json
{"generator_version":"rational-v1","template":"division_then_fractions","coefficient":2}
```

Replay rejects unknown versions, mismatched templates, extra or missing fields,
booleans, non-integer coefficients and out-of-range values before building
expressions. It never parses serialized expression strings or executable code.
`substitution-v2` is intentionally separate from the existing `substitution-v1`
preview format. Existing basic-v1 and substitution-v1 records keep their meaning.

`public()` contains only the topic and integral with its real domain. Answers,
parameters, template identifiers and solution steps remain private. New records
must not be written through the current saved-practice API until #36 connects
them to worker replay, domain-safe answer checking and explicit reveals.

## Mathematical and educational verification

Each template defines a clean exact antiderivative, its intended integrand and
method-preserving transformations. Replay proves that every solution stage
differentiates to the original integrand. Unevaluated SymPy integrals preserve
the method in intermediate stages: substitution, parts, division and identities
are visible rather than collapsed directly into a final answer. Substitution
stages display the new variable and its replacement below the integral.

The declared integrand domain must exactly match its real continuous domain;
the answer and explicit boundary terms in each solution must be real throughout
that domain. The rational templates use ln|x| and ln|x+1|, preserving negative
components. Their excluded poles are 0, or both -1 and 0. Positive symbolic
parameters cover each unbounded interval; a rational map covers the finite
interval (-1, 0). This proves derivative identities on every whole component,
without using numerical samples as proof. All other templates have domain R.
The final step must equal the exact answer plus an arbitrary constant C.

The exhaustive test corpus fixes each formula independently, exercises all 108
records, round-trips JSON, verifies domain restrictions and small exact numbers,
checks the existing input grammar can represent each answer, and rejects bad
records and corrupted solution steps. Seeded generation and public projections
have regression checks. Educational instructions use the shared typed English
catalogue and the existing deterministic `lint:content` check.

## Delivery boundary

#77–#80 delivered the internal library. #36 part 1 connects it to signed-in
practice: `core.catalogue(topic, level)` replays every record of a cell (six per
template), `GET /topics` offers all approved cells, and the worker's
`answer_check.replay_problem` accepts the four new versions. Saved substitution
levels 1–2 keep `substitution-v1`; levels 3–5 use `substitution-v2`. The checker
now reads each template's domain as a set of open intervals, including the
multi-pole rational domains; see [answer checking](ANSWER_CHECK.md).

No frontend, database schema or deployment change was needed: the website
already shows the levels `GET /topics` returns, and topic slugs were seeded with
the initial migration. #36 part 2 still owns definite integrals, weighted mixed
practice and template-declared mistake diagnosis.

Focused check: `.venv/bin/python -m pytest backend/tests/test_families.py`.
The full backend suite and hosted CI remain required for delivery.

## Definite integrals

`definite-v1` (#36, `backend/app/generators/definite.py`) adds clean bounds to
21 verified indefinite templates. A record has the same three fields as a
family record:

```json
{"generator_version":"definite-v1","template":"quadratic_exponential","coefficient":2}
```

The template fixes the base record (a `basic-v1` or family template) and the
closed interval; the record never carries bounds. The level is the base
template's level: evaluating at bounds is not a structural step. The base
replay proves the antiderivative on its whole domain. Replay then requires that
the closed interval lies inside that domain and inside the continuous domain of
the integrand and the antiderivative, so no bound touches or crosses a pole,
and that the value equals `F(b) - F(a)`. A value is clean only when it is a
nonzero real number with at most 8 operations, built from rationals with
numerator at most 30 and denominator at most 12, `π`, `e`, `ln` and `exp`.
The value is simplified per unit coefficient, so `3 ln(4/3)` is not merged
into `ln(64/27)`.

| Topic | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|---|---|---|---|---|---|
| Basic integrals | `x` on [0, 2]; `e^x` on [0, 1] | `x + e^x` on [0, 1] | `1/x` on [1, e]; `1/√x` on [1, 4] | `(x + 1)^2` on [0, 1] | — |
| Substitution | — | — | `3x^2 e^(x^3)` on [0, 1] | factor a square, [0, 1] | — |
| Integration by parts | `x e^x` on [0, 1] | `x^2 e^x` on [0, 1] | `e^x sin x` on [0, π] | — | — |
| Rational functions | `1/x` on [1, 2] | `2x/(x^2 + 1)` on [0, 1] | distinct factors on [1, 2] | repeated factor on [1, 2] | division, then fractions, on [1, 2] |
| Trigonometric integrals | `sin x` on [0, π] | `sin 2x` on [0, π/2] | `sin^3 x` on [0, π] | `sin^2 x` on [0, π] | identity, then substitution, on [0, π/2] |

`core.catalogue` appends the definite records of a cell after its indefinite
ones, so a cell offers both kinds and the guest demo's first exercise is
unchanged. The `definite-integrals` topic (#128) is every definite record of
the level from all five topics, and nothing else. The statement is `\int_{a}^{b} (...)\,dx`, the revealed answer is
the value, and the solution is the base method's steps without `+ C`, then the
evaluation `[F(x)]_a^b = F(b) - F(a)` and the value. The website shows
"Calculate the definite integral." for statements that start with bounds.

Focused check: `.venv/bin/python -m pytest backend/tests/test_definite.py`.

## Derivatives (`derivatives-v1`, #97)

`backend/app/generators/derivatives.py` implements the derivatives matrix of
[ADR-005](../decisions/0005-multiple-integrals-and-derivatives.md). A record is
`{generator_version, template, coefficient}` with a nonzero coefficient from
-3 to 3, validated before any SymPy construction. `core.catalogue("derivatives",
level)` offers every template of the level at every coefficient; the topic is
advertised by the practice API only once the topic-areas Issue (#98) adds it.

| Level | Templates (coefficient 1) |
|---|---|
| 1 | `x^4`, `e^x`, `sin x`, `cos x`, `ln x` on x > 0 |
| 2 | `2√x − 3/x` on x > 0 (rewrite as powers), `sin 3x`, `e^(2x)` (linear inner) |
| 3 | chain `e^(x²)`, `(x² + 1)³`; product `x sin x`; quotient `x/(x + 1)` |
| 4 | log laws `ln(x²(x + 1))`, `ln(x²/(x + 1))` on x > 0; `√(x² + 1)` as a power, then chain; `(x + 1)²/x` split, then power rule |
| 5 | product + chain `x² e^(3x)`, `x cos 2x`; quotient + chain `sin(x²)/x` |

Each step is a SymPy expression shown as `f(x) = …` (a rewrite) or `f'(x) = …`
(a rule applied, with unevaluated derivatives in prime notation). The verifier
evaluates every step and proves it equals the function or the derivative on each
component of the declared domain, and proves `d/dx f = f'`.

The checker compares the answer with `f'(x)` itself, not up to a constant:
`f'(x) + C` is `incorrect` with feedback `derivative_constant`, and `f'(x) + 1`
is `incorrect`. Declared mistakes (`derivative_power`, `derivative_trig_sign`,
`derivative_chain`, `derivative_factors`, `quotient_sign`) are matched exactly
and named only when one code matches.

Focused check: `.venv/bin/python -m pytest backend/tests/test_derivatives.py`.

## Partial derivatives (`partial-v1`, #101)

`backend/app/generators/partial.py` implements the partial-derivatives matrix of
[ADR-005](../decisions/0005-multiple-integrals-and-derivatives.md). A record is
`{generator_version, template, coefficient, variables}`. `variables` is the
template's `{name: domain}` declaration (#96), which the worker parses with;
replay rejects a record whose declaration, coefficient range or template is wrong
before any SymPy construction. `core.catalogue("partial-derivatives", level)`
offers every template of the level at every coefficient, with no definite
variants. The topic is in the Derivatives area, so that area has mixed practice.

| Level | Templates (coefficient 1) | Answer in |
|---|---|---|
| 1 | `∂/∂x (x³y + 2y²)`, `∂/∂y (x²y³ + 3x)` | `x, y` |
| 2 | `∂/∂y e^(xy)`, `∂/∂x x ln y` on y > 0, `∂/∂x sin(xy²)` | `x, y` |
| 3 | `∂²/∂x∂y x² e^(xy)`, `∂²/∂x² x³y²`, `∂²/∂z∂y xy²z³`, `∂/∂z xy²z³` | `x, y (, z)` |
| 4 | polar `f = xy`, `∂f/∂θ`; `f = x²y`, `∂f/∂r`; cylindrical `f = (x + y)z`, `∂f/∂θ`; `f = xyz`, `∂f/∂r` | `r, θ (, z)` |
| 5 | Jacobian `∂(x, y)/∂(r, θ)` of `x = a r cos θ, y = (a + 1) r sin θ`; `∂(x, y, z)/∂(r, θ, z)` of `x = a r cos θ, y = a r sin θ, z = z` (a = 1, 2, 3) | `r, θ (, z)` |

Domains: `x`, `y`, `z` and `θ` are real, `r > 0`, and `y > 0` where `ln y`
appears; the statement ends with them. The solution names the variables held
constant at each differentiation, shows both orders of a mixed partial (equal
because every template is smooth), and for a coordinate change shows the
substitution, each `∂f/∂u · ∂u/∂v` factor, the chain-rule sum and the simplified
result. Replay proves the answer from the definition: `sp.diff` for partials,
direct substitution for the chain rule, the determinant for a Jacobian.

`services/partial_check.py` checks an answer in the declared variables only, so
the same function written in `x, y` where `r, θ` is asked is `invalid`, as is an
added constant. A symbolic proof decides `correct`; exact rational sample points
of the domain can only certify `incorrect`. Declared mistakes are
`partial_held_constant` (a held-constant variable differentiated),
`derivative_chain` (an inner derivative dropped), `partial_chain_term` (one
chain-rule term dropped), `jacobian_missing_r` and `jacobian_sign`; one is named
only when exactly one code matches. Replay plus a check of each form takes well
under the 1 s CPU budget (`test_checks_fit_half_the_worker_cpu_limit`).

Focused check: `.venv/bin/python -m pytest backend/tests/test_partial.py`.

## Integral engine migration (#193)

New practice for basic integrals, substitution, integration by parts, rational
functions, trigonometric integrals and definite integrals comes from native
engine release pools. The existing structural levels, mixed weights and
worksheet writing space are unchanged. Indefinite/definite variants retain
their exact answer policy, real domains and solution graphs. See ADR-008's
integral amendment for versions, blocks and verification. Legacy saved records
of these topics are read-only archives; the old modules remain for the fixed
guest preview and archive fixtures until #199 removes the legacy system.

Double and triple integrals also use native engine pools after #194. Their
Cartesian, polar and cylindrical curriculum variants, levels and solution
visuals are retained. Native setup blocks verify the exact primary integral
with the correct Jacobian; old saved double-v1/triple-v1 records are archived.

After #195, derivatives and partial derivatives also issue native engine pools
at levels 1-5. The single/partial template matrices and domains described above
remain the curriculum; new records use `practice-derivative-v1` / SDV-1 and
`practice-partial-v1` / PDV-1. Existing saved legacy records are archives.
The engine derives partial-answer variable declarations from the code before
parsing, without symbolic construction in the API. Native incorrect-answer
feedback is general rather than the legacy mistake codes described above.

After #196, matrices, complex numbers, fundamental theorem of algebra and partial
fractions use native engine pools at their existing levels 1-5. Their current
scalar/expression curriculum is unchanged: determinant, modulus, sum of roots
and rational decomposition. ADR-008 lists versions and independent proofs;
legacy `symbolic-v1` records of these topics are read-only archives.

The algebraic expressions topic offers two versioned numeric exercises based on
algebra30: simplifying a radical with an extractable square factor, and
rationalizing a binomial denominator using its conjugate. Both accept equivalent
exact results, while requiring like radicals to be combined with square factors
extracted, and denominators to be rational, respectively. Other exercises in the
topic remain in development.

The polynomial division topic adds two independently versioned exercises:
the remainder on division by a linear factor at level 1 and the quotient at
level 2. Both use bounded integer coefficients and exact polynomial identities;
the quotient declares `x` as a real input variable. Previously issued codes
continue to use their original generator versions.

After #197, the six remaining analysis topics also use native engine pools:
functions/sequences, limits/continuity, improper integrals, series,
multivariable functions and differential equations. All existing levels, mixed
weights and worksheet spaces remain. The native series sums to a+1 for ratio
a/(a+1), and the x derivative of a*x^2*y+b*y is 2*a*x*y; both correct legacy
formula errors and have independent regression proofs. Old saved answers are
preserved in the read-only archive. All public topics now issue through the
engine; ADR-008 documents the versions, proofs and grammar metadata.
