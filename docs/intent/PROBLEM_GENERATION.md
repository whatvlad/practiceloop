# Problem generation intent

Status: confirmed by the product owner on 2026-10-18.

This document records the intended learning behavior of the MathLoop problem
generator. It is not an implementation plan and does not define the final
template matrix.

## Outcome

Generate mathematically correct integration exercises backwards from a known
antiderivative. Each exercise should deliberately train a selected integration
method instead of becoming difficult through large or arbitrary numbers.

## Generation model

1. Select whether the exercise is definite or indefinite.
2. Select the primary integration method and a compatible answer family.
3. Generate a pedagogically clean antiderivative `F(x)`.
4. Differentiate `F(x)` symbolically.
5. Apply equality-preserving transformations that produce the target integrand
   and make the selected method the genuine intended route.
6. Reject a candidate if it simplifies into an easier problem, has an unclear
   real domain, crosses a singularity, exposes ugly values, or fails symbolic
   verification.
7. Attach the canonical solution steps and the known mistake patterns supported
   by that template.

Alternative mathematically valid solution methods and equivalent answers remain
acceptable even when they differ from the canonical solution.

## Pedagogically clean values

Every value visible in the problem, final answer, or solution steps should be
simple enough to support learning rather than arithmetic busywork. Suitable
examples include:

- small integers and simple rational numbers;
- `4π`;
- `(3/4)e³`;
- `√3/2`;
- standard trigonometric angles and values.

Candidates containing accidental large coefficients or exponents, awkward
fractions, unusual angles, or unnecessary nested radicals should be rejected.
Internal candidate generation may produce such values, but they must never reach
the learner.

## Difficulty

Difficulty should increase through mathematical structure, recognition, and the
number of meaningful transformations—not through larger numbers.

- Level 1: direct recognition of a standard antiderivative.
- Level 2: one simple preparatory transformation.
- Level 3: one primary method, such as substitution.
- Level 4: a primary method plus an identity or non-trivial preparation.
- Level 5: a deliberate combination of two compatible techniques.

Level 5 must not become an arbitrary mixture of unrelated operations. Each
exercise has one primary method and may have explicitly identified auxiliary
transformations.

## Typical mistakes and feedback

Templates should declare the common mistakes they are designed to expose, such
as:

- omitting the integration constant;
- omitting a chain-rule factor;
- increasing a power incorrectly;
- losing a trigonometric sign;
- using `ln(x)` where `ln|x|` is required;
- splitting a product incorrectly;
- choosing an unproductive `u` and `dv` for integration by parts.

After an incorrect attempt, the system may provide targeted feedback only when
the submitted expression unambiguously matches a declared mistake. Otherwise it
should give a general hint and avoid inventing a diagnosis.

A correct antiderivative without an arbitrary constant is incomplete rather than
fully wrong. The learner receives a dedicated reminder and the exercise is
completed after the constant is added. Any symbol representing a constant
independent of `x` may be accepted; a particular letter is not required.

Omission of the integration constant is tracked separately from an ordinary
incorrect answer. User statistics should show its count, rate, topic/difficulty
breakdown, and trend over time.

## Definite and indefinite integrals

Definite and indefinite integrals are separate exercise types.

- Indefinite integrals require an arbitrary integration constant.
- For definite integrals, the generator chooses clean bounds and accepts the
  candidate only when `F(b) - F(a)` is pedagogically clean.
- Definite-integral bounds must not cross singularities, and `+C` is not part of
  the answer.

## Practice modes

- **Practice by topic:** the learner chooses a method or topic; the generator
  selects a compatible family within it.
- **Mixed practice:** the learner chooses a difficulty and the generator selects
  the method using explicit weights.

Adaptive weighting based on the learner's mistake history is a later feature.
The first mixed-practice implementation may use simple transparent weights.

## Mathematical boundaries

The initial generator works over the real numbers. It records and validates
domain conditions, uses forms such as `ln|x|` when required, and rejects definite
integrals whose interval contains a point where the integrand is undefined.
Complex analysis is a separate future module.

## Success criteria

An accepted generated exercise must:

- differentiate back to the displayed integrand;
- have valid real-domain assumptions;
- genuinely exercise the selected primary method;
- avoid a simpler unintended solution caused by accidental simplification;
- contain clean visible values throughout the canonical solution;
- have reproducible solution steps and declared mistake patterns;
- accept mathematically equivalent user answers.

## Out of scope for this decision

- the exact answer families and integration templates;
- the complete catalogue of mistake patterns;
- the exact topic/method matrix for all five levels;
- adaptive method weighting;
- complex-valued exercises;
- implementation, API, database, and UI design.

Those items require a separate specification before implementation.
