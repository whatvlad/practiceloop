# Answer checking

Issue #8 implements the equivalence rules of [ADR-003](../decisions/0003-mathematical-input-and-equivalence.md)
as a backend library. No endpoint calls it yet; the practice API (#34, #10) does.

```python
from app.services.math_worker import check_answer

result = check_answer("2/3(x+2)^3 + 2x + 2ln|x| + C", private_record)
# AnswerCheck(result="correct", missing_constant=False)
```

`private_record` is the stored generator record (for example the `basic-v1` JSON
in [BASIC_GENERATOR.md](BASIC_GENERATOR.md)), never an expression string.

| Outcome | API meaning |
|---|---|
| `AnswerCheck("correct")` | `result: "correct"` |
| `AnswerCheck("incorrect", missing_constant=True)` | `result: "incorrect"`, `feedbackCode: "missing_constant"` |
| `AnswerCheck("incorrect")` | `result: "incorrect"` |
| `AnswerCheck("invalid")` | grammar rejection, or an expression that evaluates to an undefined value such as `1/(x-x)`; a persisted invalid attempt |
| `MathInputTooLong` | `422`, no attempt |
| `MathWorkerError` | retryable `503 math_worker_unavailable`, no attempt |
| `MathCheckInconclusive` | `503 math_check_inconclusive`, no attempt |
| `ValueError` | the stored record cannot be replayed: a server fault (`500`) |

## How it decides

The parent only parses the answer. A fresh worker with the ADR-003 limits
replays the record (integrand, primitive and declared domain), builds the
answer from the syntax tree, and runs `app.services.answer_check.classify`:

1. At most one symbol other than `x` is the arbitrary constant `K`. Its
   derivative `dF/dK` must be a nonzero real number, so the answer is `aK + b`.
   `K^2`, `K*x` and `e^K` are incorrect.
2. With `K = 0`, the rest must differentiate to the integrand and be real on
   every connected component of the domain. Each component is an open interval
   written in a positive symbol `t`: `a + t` or `b - t` when it is unbounded and
   `a + (b - a)t/(1 + t)` for a finite one such as the rational templates'
   `(-1, 0)`. So `ln|x|` passes on `x != 0` and `ln(x)` fails there. When SymPy
   cannot infer realness in `t` (for example `ln|x^2 + x|`), the answer's own
   `continuous_domain` must cover the whole domain instead.
3. With no constant, a valid primitive is `missing_constant`; adding a number
   such as `+ 7` does not count.
4. The primitive minus the template's own primitive must be one number on all
   components. `ln|x| + |x|/x + C` has derivative `1/x`, but the offset differs
   on each side of zero, so it is incorrect. Both primitives are already proven
   here, so when the offset does not simplify in `t`, its exact value at `t = 1`
   is that component's constant.

Before evaluation, every subexpression of the parsed answer is checked with
`continuous_domain`, so evaluation cannot cancel a hole. On all-real domains a
hole is `invalid`, as before. On other domains a part that is undefined somewhere
in the domain makes the answer `incorrect`, the same as `ln(x)` where `x < 0` is
allowed; a part defined nowhere, such as `1/(x-x)`, is `invalid`.

`sympy.simplify` returning zero is the only proof of equality. When it cannot
prove a difference is zero, the answer is evaluated at fixed sample points of
each component with 50-digit adaptive precision. A value above `1e-12`, or a
non-real or undefined value, certifies `incorrect`. If neither happens the
result is `inconclusive`, never a guess. For example `log(x^2)` on all reals is
undefined at 0, which no sample point hits, so it is inconclusive.

## Cost and limits

Measured locally, one check takes about 0.6–0.9 s of wall time; most of it is
importing SymPy and replaying the record (which re-verifies the generator's own
solution). That leaves about 1 s of the 2 s CPU limit for the answer itself.
Answers that need more, such as `((x+1)^12 + 1)^12 + C` or twelve nested `sin`,
end as a retryable `MathWorkerError`, never as `incorrect`. The corpus in
`backend/tests/test_answer_check.py` runs such answers through the real worker
and checks that each ends within the wall limit with its child reaped.

The #77–#80 records are replayed in the worker with `verify=False`: the
catalogue already proved each one when it was generated, and repeating that proof
cost most of the CPU budget for rational level 5 on CI runners. Their slowest
check, rational level 5, then uses about 0.5 s of child CPU locally. `replay_problem` accepts `basic-v1`,
`substitution-v1`, the four #77–#80 versions and `definite-v1`. A new generator
version adds its replay to `answer_check.replay_problem`.

## Definite integrals

A `definite-v1` answer (#36) must be one real number: an answer containing `x`
or any constant symbol is `incorrect`, so `e - 1 + C` is not accepted. Every
subexpression is evaluated first, and one without a value (such as
`ln(1 - 1)`) makes the answer `invalid`. Then `simplify(answer - value) == 0`
proves `correct`, so `2ln(2) - ln(3)`, `ln|4/3|` and `-ln(3/4)` all pass. A
difference above `1e-12` at 50 digits, or a non-real value such as `ln(-4/3)`,
is `incorrect`; a decimal such as `1.5708` for `π/2` is therefore incorrect.
Anything else is `inconclusive`. A definite check uses about 0.7–1.0 s of child
CPU locally, about the same as the slowest indefinite checks.

Verification, from `backend/`: `python -m pytest tests/test_answer_check.py`
(worker tests skip off Linux).
