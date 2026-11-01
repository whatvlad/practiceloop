# Answer checking

All current practice uses typed engine answers. Pre-engine saved problems are
read-only archives: their stored statement, answer and steps remain available,
and checking returns `409 problem_archived` before any replay or worker.
The obsolete `services/answer_check.py` and generator-type dispatch are removed.
[ADR-008](../decisions/0008-generator-engine.md) is the architecture record.

`app.math_input` exposes the bounded parser/AST and safe SymPy builder.
`services/math_worker.py` starts a fresh child, applies 2 s CPU / 256 MiB memory /
64 KiB combined-output / 3 s wall limits, rebuilds the trusted code once, parses
the answer with its code-derived variable declaration and calls `Answer.check`.
One shared admission slot bounds checking and arbitrary-code reconstruction.
The API never sends raw learner text to SymPy parsing/eval.

The answer kinds own their policy:

- Exact numbers, including combinations, compare exact rational values.
- Expressions use only declared real/positive variables. Symbolic equality is
  proof; sampling may only certify a difference, never equality.
- Antiderivatives prove the derivative on every component of the stated real
  domain, require an explicit nonzero affine arbitrary constant and require one
  numeric offset across components. A valid primitive without C is
  `missing_constant`; a per-component offset such as |x|/x is incorrect.
- Derivatives compare the exact function on its domain, without arbitrary C.
  Definite/multiple integrals and initial-value solutions also reject C.

Unevaluated subexpressions are checked before cancellation. An all-real answer
containing a hole (including tan(x)'s poles or a cancelled denominator) is invalid.
On a restricted domain, a gap within the domain makes an answer incorrect; an
expression defined nowhere is invalid. If neither equality nor a difference can
be established, the outcome is inconclusive and the API returns a retryable 503.
Timeouts, failed children and malformed worker output are also service failures,
never incorrectly recorded learner answers. Every child is killed/reaped on a
wall timeout or interruption.

Native incorrect answers use general feedback; missing-constant feedback remains
explicit. Historical named feedback stays readable from saved attempts without
running the deleted mistake classifiers.

Verification: `python -m pytest tests/test_answer_check.py tests/test_answer_variables.py tests/test_engine_answers.py tests/test_math_worker.py` from backend.
Worker tests require Linux. The shared parser corpus is also checked in the
frontend; API/DB/E2E tests cover the persistence and reveal boundaries.
