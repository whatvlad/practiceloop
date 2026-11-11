"""Full second partials and Laplace identities from AM2A/8.1–8.2."""

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._multivariable_partials import XY, XYZ, X, Y, Z
from app.engine.generators._sequence_limits import finish
from app.math_input.contracts import Domain

HESSIAN_2D = ("xx", "xy", "yy")
HESSIAN_3D = ("xx", "xy", "xz", "yy", "yz", "zz")
HESSIAN_X = ("xx", "xy")
HESSIAN_Y = ("yy", "yz")
HESSIAN_Z = ("zz", "xz")
LAPLACE = ("xx", "yy", "Laplacian")


def second_partials(
    expression: sp.Expr,
    labels: tuple[str, ...],
    rule: str,
    *,
    three: bool = False,
    values: tuple[sp.Expr, ...] | None = None,
) -> Built:
    variables = {str(symbol): symbol for symbol in (X, Y, Z)}
    names = "x,y,z" if three else "x,y"
    symbols: tuple[tuple[str, Domain], ...] = XYZ if three else XY
    if values is None:
        values = tuple(
            sp.factor(sp.diff(expression, *(variables[char] for char in label))) for label in labels
        )
    components = tuple(
        FormulaAnswer(value, () if label == "Laplacian" else symbols)
        for value, label in zip(values, labels, strict=True)
    )
    requested = tuple(
        r"\Delta f=f_{xx}+f_{yy}" if label == "Laplacian" else rf"f_{{{label}}}" for label in labels
    )
    result = r",\quad ".join(
        rf"{derivative}={tex(value)}" for derivative, value in zip(requested, values, strict=True)
    )
    return finish(
        rf"f({names})={tex(expression)},\quad {names}>0."
        r"\quad\text{Compute the following in order }" + r",\ ".join(requested) + ".",
        OrderedAnswer(components, labels),
        rule,
        result
        + r".\quad\text{The function is smooth on the stated domain, so mixed orders agree.}",
    )


def radial_cosine_hessian(a: int, b: int, c: int) -> Built:
    return second_partials(
        c * sp.cos(a * X**2 + b * Y**2),
        HESSIAN_2D,
        r"\text{The first partials use the chain rule. Differentiate their products once more.}",
    )


def exponential_hessian(a: int, b: int, c: int) -> Built:
    return second_partials(
        a * Y * sp.exp(b * X * Y + c),
        HESSIAN_2D,
        r"\text{Use the product and chain rules for }y\text{ and hold }y\text{ fixed for }x.",
    )


def rational_hessian(a: int, b: int, c: int) -> Built:
    return second_partials(
        a * X**2 + b * Y**3 / (c * X),
        HESSIAN_2D,
        r"\text{Write the rational term as a constant times }x^{-1}y^3.",
    )


def logarithmic_hessian(a: int, b: int, c: int) -> Built:
    return second_partials(
        a * Y * sp.log(b * X / (c * Y)),
        HESSIAN_2D,
        r"\text{Expand the logarithm as a difference "
        r"on the positive quadrant, then differentiate.}",
    )


def polynomial_hessian(a: int, b: int, c: int) -> Built:
    return second_partials(
        Y * (a + b * X**2 + c * Z**2),
        HESSIAN_3D,
        r"\text{Differentiate each monomial twice and note which variables are independent.}",
        three=True,
    )


def nested_log_hessian(a: int, b: int, c: int, labels: tuple[str, ...]) -> Built:
    return second_partials(
        sp.log(a * X + b * Y**2 + c * Z**3 + 1),
        labels,
        r"\text{For the logarithm of }u\text{ use }f_{ij}=u_{ij}/u-u_i u_j/u^2.",
        three=True,
    )


def nested_log_hessian_x(a: int, b: int, c: int) -> Built:
    return nested_log_hessian(a, b, c, HESSIAN_X)


def nested_log_hessian_y(a: int, b: int, c: int) -> Built:
    return nested_log_hessian(a, b, c, HESSIAN_Y)


def nested_log_hessian_z(a: int, b: int, c: int) -> Built:
    return nested_log_hessian(a, b, c, HESSIAN_Z)


def arctangent_laplacian(a: int, b: int, c: int) -> Built:
    u, v = X + b, Y + c
    part = 2 * a * u * v / (u**2 + v**2) ** 2
    return second_partials(
        a * sp.atan(u / v),
        LAPLACE,
        r"\text{The first partials have a common denominator }u^2+v^2"
        r"\text{. The two pure second partials are opposites.}",
        values=(-part, part, sp.S.Zero),
    )


def radial_log_laplacian(a: int, b: int, c: int) -> Built:
    u, v = X + b, Y + c
    part = 2 * a * (v**2 - u**2) / (u**2 + v**2) ** 2
    return second_partials(
        a * sp.log(u**2 + v**2),
        LAPLACE,
        r"\text{The two pure second partials have opposite numerators over the same denominator.}",
        values=(part, -part, sp.S.Zero),
    )


def trigonometric_laplacian(a: int, b: int, c: int) -> Built:
    expression = sp.Rational(a, 2) * sp.cos(b * X) * (sp.exp(b * Y + c) + sp.exp(-b * Y - c))
    part = b**2 * expression
    return second_partials(
        expression,
        LAPLACE,
        r"\text{Each }x\text{ pair multiplies by }-b^2"
        r"\text{ and each }y\text{ pair by }b^2\text{, with }b\text{ the shared frequency.}",
        values=(-part, part, sp.S.Zero),
    )
