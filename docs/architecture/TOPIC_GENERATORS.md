# Integration topic generators

Issue #9 was split before implementation into #77 (substitution), #78 (parts),
#79 (rational functions) and #80 (trigonometric integrals). These internal
libraries implement the remaining rows of
[ADR-003](../decisions/0003-mathematical-input-and-equivalence.md).

There are 18 templates and 108 distinct parameter records. Integration by parts
starts at level 3; its levels 1–2 are deliberately unavailable. These templates
are indefinite; `definite-v1` (below) adds bounds to some of them. Coefficients are the six nonzero integers from -3 to 3. Difficulty
comes from the formula and transformations, never from increasing this range.

| Version / topic | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|---|---|---|---|---|---|
| `substitution-v2` | Visible derivative pair | Affine inner function and factor | Polynomial inner function | Factor a square before substitution | Double-angle identity and nested substitutions |
| `parts-v1` | Unavailable | Unavailable | Linear polynomial times exponential | Repeated parts with a quadratic | Cyclic exponential times sine |
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
| Integration by parts | — | — | `x e^x` on [0, 1] | `x^2 e^x` on [0, 1] | `e^x sin x` on [0, π] |
| Rational functions | `1/x` on [1, 2] | `2x/(x^2 + 1)` on [0, 1] | distinct factors on [1, 2] | repeated factor on [1, 2] | division, then fractions, on [1, 2] |
| Trigonometric integrals | `sin x` on [0, π] | `sin 2x` on [0, π/2] | `sin^3 x` on [0, π] | `sin^2 x` on [0, π] | identity, then substitution, on [0, π/2] |

`core.catalogue` appends the definite records of a cell after its indefinite
ones, so a cell offers both kinds and the guest demo's first exercise is
unchanged. The statement is `\int_{a}^{b} (...)\,dx`, the revealed answer is
the value, and the solution is the base method's steps without `+ C`, then the
evaluation `[F(x)]_a^b = F(b) - F(a)` and the value. The website shows
"Calculate the definite integral." for statements that start with bounds.

Focused check: `.venv/bin/python -m pytest backend/tests/test_definite.py`.
