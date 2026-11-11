"""Linear and quadratic partial fractions and rational primitives (#266)."""

import sympy as sp

from app.engine.blocks.analysis_one import X
from app.engine.generators._antiderivatives import REALS, antiderivative
from app.engine.generators._elementary_common import Built, tex


def right_of(pole: sp.Expr | int) -> sp.Interval:
    return sp.Interval.open(pole, sp.oo)


def rational(
    numerator: sp.Expr | int,
    denominator: sp.Expr,
    domain: sp.Set,
    primitive: sp.Expr,
    method: str,
    work: str,
) -> Built:
    shown = rf"\frac{{{tex(numerator)}}}{{{tex(sp.expand(denominator))}}}"
    return antiderivative(
        numerator / denominator,
        domain,
        method,
        shown=shown,
        primitive=primitive,
        derivation=work + r",\quad ",
    )


def linear_high_power(a: int, b: int, c: int) -> Built:
    t, n = X - b, c + 4
    return antiderivative(
        a / t**n,
        right_of(b),
        r"t=x-" + str(b) + r",\quad dt=dx.",
        primitive=-a / ((n - 1) * t ** (n - 1)),
    )


def shifted_log(a: int, b: int, c: int) -> Built:
    t = X + b
    return antiderivative(
        a / t,
        right_of(-b),
        rf"t=x+{b}>0,\quad dt=dx.",
        primitive=a * sp.log(t),
    )


def decreasing_linear_power(a: int, b: int, c: int) -> Built:
    k = a + 1
    t = b - k * X
    return antiderivative(
        c / t**3,
        sp.Interval.open(-sp.oo, sp.Rational(b, k)),
        rf"t={tex(t)}>0,\quad dt=-{k}\,dx.",
        primitive=c / (2 * k * t**2),
    )


def scaled_linear_log(a: int, b: int, c: int) -> Built:
    k = a + 1
    t = k * X + b
    return antiderivative(
        c / t,
        right_of(-sp.Rational(b, k)),
        rf"t={tex(t)}>0,\quad dt={k}\,dx.",
        primitive=sp.Rational(c, k) * sp.log(t),
    )


def quadratic(center: int, width: int, slope: int, residual: int, scale: int = 1) -> Built:
    t = X - center
    q = t**2 + width**2
    numerator = sp.expand(slope * t + residual)
    result = sp.Rational(slope, 2 * scale) * sp.log(q) + sp.Rational(
        residual, width * scale
    ) * sp.atan(t / width)
    u = sp.Symbol("u", real=True)
    integrand = (slope * u + residual) / (scale * (u**2 + width**2))
    work = rf"\int {tex(integrand)}\,du"
    if slope and residual:
        first = sp.Rational(slope, scale) * u / (u**2 + width**2)
        second = sp.Rational(residual, scale) / (u**2 + width**2)
        work += rf"=\int {tex(first)}\,du+\int {tex(second)}\,du"
    return rational(
        numerator,
        scale * q,
        REALS,
        result,
        rf"{tex(sp.expand(scale * q))}={tex(scale * q)},\quad u={tex(t)},\quad du=dx.",
        work,
    )


def quadratic_arctangent(a: int, b: int, c: int) -> Built:
    return quadratic(-a, b + 1, 0, c)


def quadratic_logarithm(a: int, b: int, c: int) -> Built:
    return quadratic(-a, b + 1, 2 * c, 0)


def quadratic_log_and_arctangent(a: int, b: int, c: int) -> Built:
    return quadratic(a, b + 1, 2 * c, b)


def nonmonic_quadratic(a: int, b: int, c: int) -> Built:
    return quadratic(-b, c + 1, a, -c, scale=a + 1)


def decomposed(
    numerator: sp.Expr | int,
    denominator: sp.Expr,
    domain: sp.Set,
    pieces: sp.Expr,
    primitive: sp.Expr,
    method: str,
) -> Built:
    return rational(
        numerator,
        denominator,
        domain,
        primitive,
        method,
        rf"\frac{{{tex(numerator)}}}{{{tex(sp.expand(denominator))}}}={tex(pieces)}",
    )


def distinct_linear_factors(a: int, b: int, c: int) -> Built:
    first = -sp.Rational(b, a)
    second = c - first
    return decomposed(
        c * X + b,
        X * (X - a),
        right_of(a),
        first / X + second / (X - a),
        first * sp.log(X) + second * sp.log(X - a),
        r"\text{Match the numerator coefficients over the two linear factors.}",
    )


def divide_by_linear(a: int, b: int, c: int) -> Built:
    t = X + b
    return decomposed(
        c * X**2,
        t,
        right_of(-b),
        c * (X - b + b**2 / t),
        c * (X**2 / 2 - b * X + b**2 * sp.log(t)),
        r"\text{Divide the numerator by the linear denominator.}",
    )


def repeated_linear_factor(a: int, b: int, c: int) -> Built:
    first = sp.Rational(c, a**2)
    second = sp.Rational(c, a)
    return decomposed(
        c,
        X**2 * (X - a),
        right_of(a),
        first / (X - a) - first / X - second / X**2,
        first * (sp.log(X - a) - sp.log(X)) + second / X,
        r"\text{Include both inverse powers of the repeated factor }x.",
    )


def divide_by_difference_of_squares(a: int, b: int, c: int) -> Built:
    q = X**2 - a**2
    residue = sp.Rational(c * a**3, 2)
    return decomposed(
        c * X**4,
        q,
        right_of(a),
        c * (X**2 + a**2) + residue / (X - a) - residue / (X + a),
        c * (X**3 / 3 + a**2 * X) + residue * (sp.log(X - a) - sp.log(X + a)),
        rf"\text{{Divide first, then use }}{tex(q)}=(x-{a})(x+{a}).",
    )


def distinct_quadratic_factors(a: int, b: int, c: int) -> Built:
    width = a + b
    first, second = X**2 + a**2, X**2 + width**2
    scale = sp.Rational(c, width**2 - a**2)
    return decomposed(
        c,
        first * second,
        REALS,
        scale / first - scale / second,
        scale * (sp.atan(X / a) / a - sp.atan(X / width) / width),
        rf"{tex(second)}-({tex(first)})={width**2 - a**2}\text{{, so split the reciprocals.}}",
    )


def nonmonic_logarithm(a: int, b: int, c: int) -> Built:
    k = a + 1
    q = k * ((X + b) ** 2 + (c + 1) ** 2)
    return rational(
        sp.expand(c * sp.diff(q, X)),
        q,
        REALS,
        c * sp.log(q),
        rf"u={tex(sp.expand(q))}>0,\quad du=({tex(sp.diff(q, X))})\,dx.",
        rf"\int \frac{{{c}}}{{u}}\,du={c}\ln u+C",
    )


def positive_quadratic_reciprocal(a: int, b: int, c: int) -> Built:
    return quadratic(-a, b + c, 0, b + 1)


def three_linear_factors(a: int, b: int, c: int) -> Built:
    scale = sp.Rational(c, 2 * a**2)
    return decomposed(
        c,
        X * (X**2 - a**2),
        right_of(a),
        scale * (-2 / X + 1 / (X - a) + 1 / (X + a)),
        scale * (-2 * sp.log(X) + sp.log(X - a) + sp.log(X + a)),
        r"\text{Factor the cubic and match the three simple fractions.}",
    )


def decreasing_quadratic_numerator(a: int, b: int, c: int) -> Built:
    return quadratic(b, a + c, -a, c)


def divide_by_irreducible_quadratic(a: int, b: int, c: int) -> Built:
    t, width = X - a, a + b
    q = t**2 + width**2
    residue = a**2 - width**2
    return decomposed(
        c * X**2,
        q,
        REALS,
        c * (1 + (2 * a * t + residue) / q),
        c * (X + a * sp.log(q) + sp.Rational(residue, width) * sp.atan(t / width)),
        rf"u={tex(t)},\quad {tex(X**2)}=(u^2+{width**2})+{2 * a}u+({residue}).",
    )


def linear_times_irreducible_quadratic(a: int, b: int, c: int) -> Built:
    q = X**2 + a**2
    scale = sp.Rational(c, a**2)
    return decomposed(
        c,
        X * q,
        right_of(0),
        scale * (1 / X - X / q),
        scale * (sp.log(X) - sp.log(q) / 2),
        r"\text{Split into a linear factor and the derivative of the positive quadratic.}",
    )


def quartic_via_square(a: int, b: int, c: int) -> Built:
    u = sp.Symbol("u", positive=True)
    scale = sp.Rational(c, 4 * a**2)
    return rational(
        c * X,
        X**4 - a**4,
        right_of(a),
        scale * (sp.log(X**2 - a**2) - sp.log(X**2 + a**2)),
        rf"u=x^2,\quad du=2x\,dx,\quad u>{a**2}.",
        rf"\int {tex(sp.Rational(c, 2) / (u**2 - a**4))}\,du"
        rf"=\int\left({tex(scale / (u - a**2) - scale / (u + a**2))}\right)du",
    )


def mixed_cubic_exam(a: int, b: int, c: int) -> Built:
    q = X**2 + a**2
    return decomposed(
        (b + 1) * X**2 + c * X + a**2,
        X * q,
        right_of(0),
        1 / X + (b * X + c) / q,
        sp.log(X) + sp.Rational(b, 2) * sp.log(q) + sp.Rational(c, a) * sp.atan(X / a),
        r"\text{Use a constant numerator over }x\text{ and a linear numerator over the quadratic.}",
    )


def difference_of_squares_log_exam(a: int, b: int, c: int) -> Built:
    q = b**2 - a**2 * X**2
    scale = -sp.Rational(c, 2 * a**2)
    return rational(
        c * X,
        q,
        sp.Interval.open(-sp.Rational(b, a), sp.Rational(b, a)),
        scale * sp.log(q),
        rf"u={tex(q)}>0,\quad du=-{2 * a * a}x\,dx.",
        rf"\int {tex(scale / sp.Symbol('u', positive=True))}\,du={tex(scale)}\ln u+C",
    )
