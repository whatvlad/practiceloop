# ADR-003: bounded real-valued integration answers

Date: 2026-10-19. Status: accepted by accountable human Feijhoaaaaa.

PracticeLoop accepts a deliberately small mathematical language, constructs
SymPy objects from a validated internal syntax tree, and checks answers over the
real domain declared by the generating template. This resolves OQ-01, OQ-02 and
OQ-03 without exposing Python or SymPy string parsers to learner input.

## Integration constants and domains

- An indefinite answer is correct only when it contains an explicit arbitrary
  constant and its derivative equals the integrand on every connected component
  of the template's declared real domain.
- Any one-letter symbol other than `x` or `e` may name the arbitrary constant;
  `C`, `c` and `k` are examples. Exactly one such symbol is allowed. After the
  known primitive is removed, its term must be `aK + b`, where `a` is a nonzero
  real numeric constant and `b` is numeric. This accepts `2K + 7`, whose range is
  all real numbers, but rejects restricted reparameterizations such as `K^2`.
- A valid primitive without that symbol returns `incorrect` with
  `feedbackCode: "missing_constant"`. It is tracked separately from other
  incorrect answers. Adding a fixed number such as `+ 7` does not satisfy the
  requirement.
- Definite answers contain no arbitrary constant and are compared on the
  template's closed interval. Bounds never cross an excluded point.
- Equivalent forms are accepted only when they are real and defined throughout
  the problem domain. For example, `log(x)` is not equivalent to `log(abs(x))`
  for a problem whose domain includes negative `x`, but it is valid when the
  declared domain is `x > 0`.
- Symbolic proof is authoritative. Bounded numerical samples may find a
  counterexample but never prove equivalence by themselves. If the bounded
  worker can neither prove equality nor find a certified difference, the API
  returns `503 math_check_inconclusive` and stores no attempt; it does not guess.

## Topic and difficulty matrix

Every template declares one primary topic, its exact domain, whether it is
definite, its generator version and its allowed auxiliary transformations.
Difficulty is global: a method is not relabeled as level 1 merely because it is
the easiest example in its topic. A cell is available to learners only after it
has at least one template that passes the derivative, domain, intended-method,
clean-value and deterministic-replay checks.

| Topic | 1 — direct | 2 — one preparation | 3 — one primary method | 4 — method plus preparation | 5 — two compatible techniques |
|---|---|---|---|---|---|
| Basic integrals | One constant, power, exponential, sine or cosine term | A clean sum or constant multiple of two direct terms | Negative/fractional powers or `1/x`, with an explicit real domain | Expand, cancel or split once, then integrate term by term | A clean mixed sum requiring two compatible algebraic rewrites |
| Substitution | A visible `f'(x)g(f(x))` pair | Recover one missing constant factor or use an affine inner function | One polynomial, exponential or trigonometric substitution | One algebraic/trigonometric rewrite before substitution, optionally with clean bounds | A nested substitution or substitution combined with one compatible identity |
| Integration by parts | One application with a linear polynomial and basic exponential/trigonometric factor | A degree-two polynomial, logarithmic family or clean definite problem requiring repeated parts | A cyclic exponential–trigonometric family or parts combined with one compatible preparation | Not offered | Not offered |
| Rational functions | A constant over one linear factor | Numerator proportional to a denominator derivative | Proper fractions with distinct linear factors | Repeated linear factors or one irreducible quadratic | Polynomial division followed by partial fractions |
| Trigonometric integrals | One standard sine, cosine or secant-squared primitive | A linear argument with one constant-factor adjustment | Odd sine/cosine powers with one factor split off | Even powers or products requiring one standard identity | One identity followed by a compatible substitution |

Amendment (2026-10-20, owner decision): integration by parts has three levels.
Its row keeps the original level 3–5 content, renumbered 1–3, because a learner
choosing parts has already chosen the method. Levels 4–5 are not offered for
parts, and the practice page hides levels a topic does not offer.

Across the matrix, levels increase by recognition, transformations and method
composition. Coefficients, exponents and bounds remain pedagogically clean.
Shipping may be staged, as in Issues #34 and #36. Intentionally unavailable or
not-yet-implemented cells must not be advertised by `GET /api/topics`; an older
task requiring all 25 combinations must follow this structural rule rather than
inventing misleading low-difficulty exercises.

Amendment (2026-10-21, ADR-005): the Derivatives area adds `derivatives` and
`partial-derivatives`, and the Integrals area adds `double-integrals` and
`triple-integrals`, each with its own matrix in ADR-005. The level meanings above
apply to them unchanged.

## Accepted input language

The parent process applies Unicode NFKC normalization, then maps `π` to `pi`,
Unicode minus to `-`, `×` to `*` and `÷` to `/`. At token level, `√` followed by
one number, allowed name or parenthesized expression is the `sqrt` function; this
supports `√3` without ambiguous textual rewriting. Any remaining non-ASCII
character is rejected. Whitespace is insignificant.

The grammar contains:

- decimal integers and finite decimals, with `/` for exact fractions;
- the real variable `x`, constants `pi` and `e`, and one additive arbitrary
  constant for indefinite answers;
- binary `+`, `-`, `*`, `/`, `^`; unary `+` and `-`; parentheses;
- `sin`, `cos`, `tan`, `sec`, `csc`, `cot`, `asin`, `acos`, `atan`, `exp`,
  `ln`, `log`, `sqrt` and `abs`, each with exactly one parenthesized argument;
- paired, non-nested `|expression|` as an `abs` shorthand, including
  `ln|x|`/`log|x|`, and numeric function powers such as `sin^2(x)`;
- implicit multiplication only between unambiguous adjacent atoms, including
  `3pi`, `2x`, `2(x+1)` and `(x+1)(x-1)`.

`ln` and `log` are synonyms for the natural logarithm. There is no factorial,
complex unit, comparison, assignment, comma, attribute access, subscript,
string, collection, keyword, scientific notation, or implicit function call.
The API never passes learner text to `eval`, `exec`, `sympify`, `parse_expr`,
`parse_latex` or `lambdify`.

Amendment (2026-10-21, ADR-005): a derivative template may declare the extra
variables `y`, `z`, `r` and `theta` (also typed `θ`) with their real domains.
Only declared variables are accepted; ADR-005 and Issue #96 define the rule.

## Fixed parser and worker limits

The 256-byte normalized-input limit is request validation: exceeding it returns
`422` and creates no attempt. The remaining limits apply after normalization and
before SymPy construction:

- at most 256 ASCII bytes, 128 tokens, 96 syntax-tree nodes, 12 nested groups,
  and 16 function calls;
- at most 8 digits in one numeric literal and at most 6 fractional digits;
- numeric powers have absolute numerator at most 12 and denominator at most 12;
  `e` may have a bounded expression as its exponent;
- no other variable exponent and no division by a literal zero.

The validated syntax tree is converted with explicit allowlisted SymPy
constructors in a fresh Linux child process for each check. Each child has a
2-second CPU limit, 256 MiB address-space limit and 64 KiB combined output
limit. The parent enforces a 3-second wall limit, kills and reaps the process on
expiry, and never uses a shell. A limit or worker failure is a retryable service
failure, never `incorrect`. Within the request-size limit, a grammar, token,
tree, nesting, literal or power-limit rejection is a persisted `invalid` attempt.

These are initial production ceilings, not configuration exposed to learners.
Raise one only with an adversarial regression corpus and measured evidence that
valid answers require it.

## Consequences

The parser must be purpose-built, but its small grammar is testable and avoids
the eval-based SymPy parsing APIs. Template domains become required trusted data,
and each template family needs positive, alternative-form, domain and resource
limit tests before it is advertised.

References: the [SymPy parsing documentation](https://docs.sympy.org/latest/modules/parsing.html#sympy.parsing.sympy_parser.parse_expr)
warns that `parse_expr` uses `eval` and is unsafe for unsanitized input; Python
documents [`setrlimit`](https://docs.python.org/3/library/resource.html#resource.setrlimit)
for child resource ceilings and requires explicitly
[killing and reaping a timed-out subprocess](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate).
