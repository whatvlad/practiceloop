# Basic-integral generator

Issue #6 implements the basic-integrals row of [ADR-003](../decisions/0003-mathematical-input-and-equivalence.md).
All templates are indefinite and use an explicit arbitrary constant in the final
answer. Other topics, definite integrals, answer checking (#8), persistence (#10)
and the connected practice flow (#34) are separate work.

| Level | Templates | Intended work | Real domain |
|---|---|---|---|
| 1 | `constant`, `power`, `exponential`, `sine`, `cosine` | Recognize one standard primitive | All real x |
| 2 | `sum` | Split a polynomial-plus-exponential sum and integrate each term | All real x |
| 3 | `negative_power`, `fractional_power`, `reciprocal` | Rewrite a negative/fractional power, or use ln\|x\| | x != 0; x > 0 for the reciprocal square root |
| 4 | `expand_square` | Expand a squared linear factor, then integrate term by term | All real x |
| 5 | `expand_and_split` | Expand a square and split a fraction, then integrate term by term | x != 0 |

Generation starts from a small exact antiderivative, differentiates it and
applies the template's equality-preserving display transformations. Each
candidate is symbolically checked before return. Positive and negative symbolic
variables cover both connected components when x != 0, so ln\|x\| is verified
on both sides of zero. Numerical sampling is not used as proof.

Level 4 displays `a(x+b)^2`. Level 5 displays `a(x+b)^2 + b(x+1)/x`, requiring
both expansion and fraction splitting. Its positive coefficients prevent terms
from canceling into an easier exercise. Coefficients are nonzero integers from
-3 to 3 (positive only for level 5), `secondary` is 1 or 2, and `power` is 2, 3
or 4. Unused parameters must retain their canonical defaults: secondary 1 and
power 2. All 126 allowed records are covered by exhaustive tests, including
continuous domains, every step, explicit +C and clean coefficients.

From the installed backend or from `backend/`:

```python
from app.generators.basic import generate_basic, replay_basic

problem = generate_basic(difficulty=5, seed=42)
private_record = problem.parameters.model_dump(mode="json")
replayed = replay_basic(private_record)
assert replayed == problem
public_statement = problem.public().model_dump()
```

The local seeded PRNG does not change global random state. Difficulty must be
an integer 1–5, and the seed an unsigned 32-bit integer; booleans are rejected.
Persist the selected record, not the seed alone. Its complete JSON shape is:

```json
{"generator_version":"basic-v1","template":"expand_and_split","coefficient":2,"secondary":1,"power":2}
```

Replay validates the version, template, strict integer types, bounds and unknown
fields before symbolic construction. No expression strings, pickles or executable
serialization are accepted. Future versions must keep the v1 reconstruction
rules if stored v1 problems need replay; they must not reinterpret old records.

`InternalProblem` holds the private record, integrand, antiderivative, declared
domain and structured steps. Each step has a typed kind, symbolic expression,
short English `say` text and generated `latex`. The small text catalogue lives
in the generator; the shared catalogue and content checker belong to #34.
`public()` exposes only `topic` and a LaTeX integral with its domain restriction.
Parameters, primitives, answers and solution steps stay private until an
authorized reveal path is implemented.

The old positional `generate_basic(coefficient, power)` development fixture had
no production callers and is replaced by keyword-only `difficulty` and `seed`.
The two-field public projection stays compatible. No endpoint or browser behavior
changes in this issue. Focused verification: `python -m pytest tests/test_basic.py`.
