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
are reserved to prevent confusion with complex units. The checker in #8 must
still enforce the arbitrary constant's affine form and the problem's real domain.

Use `*` between a symbol and a following group, and before `e` after a number:
`x*(x+1)` and `2*e^x`. Unknown calls such as `f(x)`, scientific notation such as
`1e6`, and separated numbers such as `1 2` are rejected. Function arguments
require parentheses except for `ln|x|`/`log|x|`. Square-root shorthand consumes
one atom, so use `√(-3)` or `√(x+1)` when the argument contains operators.
Each `√` counts as the four ASCII bytes in `sqrt` for the normalized-size limit.
Numeric digit limits include leading zeros and both sides of the decimal point.

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
those belong to #8 and must also execute inside the limited worker.

Verification, from `backend/` with the documented Python environment:

```sh
python -m pytest tests/test_math_parser.py tests/test_math_worker.py
```

Tests cover notation equivalence, hostile syntax, exact boundaries and actual
bounded pathological expressions. Fault-injected child computations separately
prove CPU, memory, combined-output and wall limits, reaping and parent isolation.
Worker tests explicitly skip off Linux; CI runs them on Linux/Python 3.12.
