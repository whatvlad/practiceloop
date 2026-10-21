# Bounded mathematical input

Issue #7 implements the input boundary in [ADR-003](../decisions/0003-mathematical-input-and-equivalence.md).
It is a backend library; no math endpoint or browser integration is enabled yet.

`app.services.math_parser.parse_math_input(text)` returns a frozen `MathNode`
tree. Normalization, tokenization, grammar and all tree/literal/power bounds run
without importing SymPy. It supports the ADR functions, exact fractions and
decimals, implicit multiplication, square roots, absolute-value bars and numeric
function powers. For example, `3π`, `2(x+1)`, `√3`, `ln|x|` and `sin^2(x)` work.
Numeric exponents are exact bounded rationals; `e^(2*x+1)` is also supported.
Only one additional single-letter real symbol is allowed; `i`, `I`, `j`, `J`
are reserved to prevent confusion with complex units. The checker from #8
([ANSWER_CHECK.md](ANSWER_CHECK.md)) enforces the arbitrary constant's affine form
and the problem's real domain.

Use `*` between a symbol and a following group, and before `e` after a number:
`x*(x+1)` and `2*e^x`. Unknown calls such as `f(x)`, scientific notation such as
`1e6`, and separated numbers such as `1 2` are rejected. Function arguments
require parentheses except for `ln|x|`/`log|x|`. Square-root shorthand consumes
one atom, so use `√(-3)` or `√(x+1)` when the argument contains operators.
Each `√` counts as the four ASCII bytes in `sqrt` for the normalized-size limit.
Numeric digit limits include leading zeros and both sides of the decimal point.

## Declared answer variables (ADR-005, Issue #96)

`parse_math_input(text, variables)` takes the template's declared variables, a
subset of `x`, `y`, `z`, `r` and `theta`. Without them the integration grammar
above applies unchanged. With them:

- Only the declared variables, `pi` and `e` are names. Any other letter, including
  an integration constant, is invalid: an answer in `r, θ` does not accept `x, y`.
- `θ` (and `ϑ`) read as `theta`, as `π` reads as `pi`; the size limit counts the
  five bytes of `theta`.
- Implicit multiplication follows one rule: a run of letters is read from the
  left, each time as the longest function, variable, `pi` or `e` that starts there.
  So `2xy` is `2*x*y`, `rtheta` and `r theta` are `r*theta`, `xsin(y)` is
  `x*sin(y)` and `ex` is `e*x`. A letter that starts no such name, such as `q` in
  `xq`, makes the answer invalid. Every split name is one token for the limits.
- A letter before a bracket is still a function call, so write `x*(y+1)`, and only
  `e` takes a variable exponent.

A template declares each variable's domain: `x`, `y`, `z` are `real` or
`positive`, `r` is `positive` and `theta` is `real`
(`math_parser.declared_variables`). The generator copies the declaration into the
private record as `variables`; the worker parses with it and refuses a record
whose declaration differs from its replayed template. `answer_check.ExpressionProblem`
compares an answer with the expected expression on that domain: a symbolic proof
decides `correct`, bounded sample points can only certify `incorrect`, and anything
else is `inconclusive`. The frontend mirror (`answerSyntax.ts`) takes the same
`variables`, and `AnswerInput`'s `variables` prop puts one key per declared
variable on the keypad and the phone keyboard, in place of `x` and `+C`.

`app.services.math_worker.validate_math_input(text)` validates syntax in the
parent, then starts a fresh interpreter using fixed argv and bounded stdin.
The child activates Linux resource ceilings before importing SymPy, reparses
the input and uses explicit allowlisted constructors with evaluation disabled.
It returns only a fixed success marker, never pickled expressions or input text.

The child has 2 CPU seconds, 256 MiB address space and 64 KiB combined stdout and
stderr. Both streams share an anonymous temporary file bounded by `RLIMIT_FSIZE`,
so a noisy child cannot fill an unbounded pipe or parent-memory buffer. The
parent enforces 3 wall-clock seconds and kills/reaps on timeout, communication
failure or interruption. Temporary output is closed on every exit. Windows and
other unsupported systems fail explicitly; there is no unbounded fallback.

Callers must distinguish `MathInputTooLong` (request validation, 422/no attempt)
from its base `MathInputError` (invalid syntax). The API must also reject empty
answers at request validation per its contract. `MathWorkerError` is a retryable
service failure, never `incorrect` or a persisted invalid attempt. Successful
construction does not establish equivalence, real-valuedness or domain coverage;
those are checked by `check_answer` (#8), which runs inside the same limited worker.

Verification, from `backend/` with the documented Python environment:

```sh
python -m pytest tests/test_math_parser.py tests/test_math_worker.py tests/test_answer_variables.py
```

Tests cover notation equivalence, hostile syntax, exact boundaries and actual
bounded pathological expressions. Fault-injected child computations separately
prove CPU, memory, combined-output and wall limits, reaping and parent isolation.
Worker tests explicitly skip off Linux; CI runs them on Linux/Python 3.12.
