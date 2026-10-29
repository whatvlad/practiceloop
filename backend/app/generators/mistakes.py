"""#36: the common mistakes each template declares, as the wrong answer they produce.

A declared mistake is the antiderivative a learner writes after making it, for
example `ln(x)` where `ln|x|` is needed. The checker names a mistake only when
an incorrect answer matches exactly one declared code; otherwise the learner gets
a general hint. Definite templates reuse their base template's mistakes,
evaluated at the bounds, and add three of their own.
"""

from collections.abc import Callable
from typing import Any, cast

import sympy as sp

from app.generators.basic import X
from app.schemas.feedback import MistakeCode

type Mistakes = tuple[tuple[MistakeCode, Any], ...]

_SIN, _COS, _EXP = sp.sin(X), sp.cos(X), sp.exp(X)
_LOG_X, _LOG_NEXT = sp.log(sp.Abs(X)), sp.log(sp.Abs(X + 1))


def _without_absolute(expression: Any) -> Any:
    return expression.replace(sp.Abs, lambda argument: argument)


def _basic(name: str, a: Any, b: Any, n: int, primitive: Any) -> Mistakes:
    if name == "power":  # the power is raised but never divided by
        return (("power_rule", a * X**n),)
    if name == "sum":
        return (("power_rule", a * X**n + b * _EXP),)
    if name == "negative_power":  # the power is lowered instead of raised
        return (("power_rule", a * X ** (-n - 1) / (-n - 1)),)
    if name == "fractional_power":
        return (("power_rule", -2 * a * X ** sp.Rational(-3, 2) / 3),)
    if name in {"sine", "cosine"}:
        return (("trig_sign", -primitive),)
    if name in {"reciprocal", "expand_and_split"}:
        return (("log_absolute", _without_absolute(primitive)),)
    return ()


# Family templates: (version, template) -> wrong answers at coefficient `a`.
_FAMILY: dict[tuple[str, str], Callable[[Any, Any], Mistakes]] = {
    ("substitution-v2", "visible_pair"): lambda a, f: (
        ("trig_sign", -f),
        ("split_product", a * X**2 * sp.sin(X**2)),
    ),
    ("substitution-v2", "affine_factor"): lambda a, f: (
        ("chain_factor", 2 * f),
        ("trig_sign", -f),
    ),
    ("substitution-v2", "polynomial_inner"): lambda a, f: (("chain_factor", 3 * f),),
    ("substitution-v2", "factor_square"): lambda a, f: (("chain_factor", 2 * f),),
    ("substitution-v2", "identity_nested"): lambda a, f: (("chain_factor", 2 * f),),
    ("parts-v1", "linear_exponential"): lambda a, f: (
        ("parts_sign", a * _EXP * (X + 1)),
        ("split_product", a * X**2 * _EXP / 2),
    ),
    ("parts-v1", "quadratic_exponential"): lambda a, f: (
        ("parts_sign", a * _EXP * (X**2 + 2 * X + 2)),
        ("parts_sign", a * _EXP * (X**2 - 2 * X - 2)),
        ("split_product", a * X**3 * _EXP / 3),
    ),
    ("parts-v1", "cyclic_sine"): lambda a, f: (
        ("parts_sign", a * _EXP * (_SIN + _COS) / 2),
        ("cycle_factor", 2 * f),
    ),
    ("rational-v1", "linear_denominator"): lambda a, f: (("log_absolute", _without_absolute(f)),),
    ("rational-v1", "denominator_derivative"): lambda a, f: (("chain_factor", 2 * f),),
    ("rational-v1", "distinct_factors"): lambda a, f: (
        ("log_absolute", _without_absolute(f)),
        ("partial_fraction_sign", a * (_LOG_X + _LOG_NEXT)),
    ),
    ("rational-v1", "repeated_factor"): lambda a, f: (
        ("log_absolute", _without_absolute(f)),
        ("partial_fraction_sign", a * (_LOG_X - _LOG_NEXT - 1 / (X + 1))),
    ),
    ("rational-v1", "division_then_fractions"): lambda a, f: (
        ("log_absolute", _without_absolute(f)),
    ),
    ("trigonometric-v1", "sine"): lambda a, f: (("trig_sign", -f),),
    ("trigonometric-v1", "double_argument"): lambda a, f: (
        ("chain_factor", 2 * f),
        ("trig_sign", -f),
    ),
    ("trigonometric-v1", "odd_power"): lambda a, f: (
        ("power_rule", a * _SIN**4 / 4),
        ("trig_sign", -f),
    ),
    ("trigonometric-v1", "even_power"): lambda a, f: (
        ("power_rule", a * _SIN**3 / 3),
        ("trig_sign", a * (X / 2 + sp.sin(2 * X) / 4)),
    ),
    ("trigonometric-v1", "identity_substitution"): lambda a, f: (("trig_sign", -f),),
}


def declared(record: dict[str, object], primitive: Any) -> Mistakes:
    """Wrong antiderivatives for an indefinite record; `primitive` is its answer."""
    version = record.get("generator_version")
    if version == "symbolic-v1":
        return ()
    # Records are validated by their replay before this runs; every value is an int.
    number = cast(dict[str, int], record)
    a = sp.Integer(number["a"] if version == "substitution-v1" else number["coefficient"])
    if version == "basic-v1":
        # basic-v1 records may omit `secondary` and `power`, which default to 1 and 2.
        secondary, power = number.get("secondary", 1), number.get("power", 2)
        return _basic(str(record["template"]), a, sp.Integer(secondary), power, primitive)
    if version == "substitution-v1":
        family, scale = record["family"], record["scale"]
        mistakes: Mistakes = (("trig_sign", -primitive),) if family != "exp" else ()
        if scale != 1:  # the inner derivative's constant factor is dropped
            mistakes += (("chain_factor", scale * primitive),)
        return mistakes
    builder = _FAMILY.get((str(version), str(record.get("template"))))
    return builder(a, primitive) if builder else ()
