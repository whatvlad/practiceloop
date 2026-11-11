"""Taylor and Maclaurin formulas with Lagrange remainders, error bounds, approximations (#264)."""

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.blocks.analysis_one import X
from app.engine.generators._derivatives import REAL_X
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._sequence_limits import finish

TAYLOR = ("Taylor polynomial", "n-th derivative")
APPROXIMATION = ("Remainder order n", "Approximation")


def scaled(k: int) -> str:
    return "" if k == 1 else str(k)


def taylor_polynomial(f: sp.Expr, x0: sp.Expr, degree: int) -> sp.Expr:
    return sp.expand(
        sum(
            sp.diff(f, X, k).subs(X, x0) / sp.factorial(k) * (X - x0) ** k
            for k in range(degree + 1)
        )
    )


def lagrange(
    shown: str, f: sp.Expr, x0: sp.Expr, n: int, label: str, domain: sp.Set = sp.S.Reals
) -> Built:
    polynomial = taylor_polynomial(f, x0, n - 1)
    nth = sp.diff(f, X, n)
    # Hyperbolic functions are entered through exp.
    nth = sp.expand(nth.rewrite(sp.exp)) if f.has(sp.cosh) else sp.simplify(nth)
    point = "0" if x0 == 0 else tex(x0)
    return finish(
        rf"\text{{Write the {label} formula of order }}n={n}\text{{ at }}x_0={point}"
        r"\text{ with the Lagrange remainder }R_n=\frac{f^{(n)}(\xi)}{n!}(x-x_0)^n"
        r"\text{, }\xi\text{ between }x_0\text{ and }x.\text{ Give }T_{n-1}(x)\text{ and }"
        rf"f^{{(n)}}(x):\quad f(x)={shown}.",
        OrderedAnswer(
            (FormulaAnswer(polynomial, REAL_X), DomainFormulaAnswer(nth, domain)), TAYLOR
        ),
        r"\text{Evaluate }f^{(k)}(x_0)\text{ for }k<n\text{ and differentiate }n\text{ times.}",
        rf"T_{{{n - 1}}}(x)={tex(polynomial)},\qquad f^{{({n})}}(x)={tex(nth)},\qquad "
        rf"R_{{{n}}}(x)=\frac{{f^{{({n})}}(\xi)}}{{{n}!}}{tex((X - x0) ** n)}.",
    )


# AM1/70: Taylor formulas at a point.


def taylor_cubic(a: int, b: int, c: int) -> Built:
    f = a * X**3 + b * X
    return lagrange(tex(f), f, sp.Integer(-c), 4, "Taylor")


def taylor_reciprocal_power(a: int, b: int, c: int) -> Built:
    power = 1 + a % 3
    f = X ** (-power)
    return lagrange(
        rf"\frac{{1}}{{x^{{{power}}}}}", f, sp.Integer(b), 2, "Taylor", sp.Interval.open(0, sp.oo)
    )


def taylor_sine_at_pi(a: int, b: int, c: int) -> Built:
    f = sp.sin(b * X)
    return lagrange(tex(f), f, sp.pi, 3, "Taylor")


def taylor_exponential(a: int, b: int, c: int) -> Built:
    f = sp.exp(-a * X)
    return lagrange(tex(f), f, sp.Integer(0), 3 + c % 3, "Taylor")


# AM1/71: Maclaurin formulas of a stated order.


def maclaurin_sine(a: int, b: int, c: int) -> Built:
    f = sp.sin(X / (b + 1))
    return lagrange(tex(f), f, sp.Integer(0), 3 + c % 3, "Maclaurin")


def maclaurin_cosh(a: int, b: int, c: int) -> Built:
    f = sp.cosh(a * X)
    return lagrange(tex(f), f, sp.Integer(0), 3 + c % 3, "Maclaurin")


def maclaurin_cosine(a: int, b: int, c: int) -> Built:
    f = sp.cos(a * X)
    return lagrange(tex(f), f, sp.Integer(0), 3 + c % 3, "Maclaurin")


def maclaurin_exponential_product(a: int, b: int, c: int) -> Built:
    f = X * sp.exp(-a * X)
    return lagrange(rf"\frac{{x}}{{e^{{{scaled(a)}x}}}}", f, sp.Integer(0), 3 + c % 3, "Maclaurin")


# AM1/72 and exam: uniform error bound from a stated Lagrange remainder.


def error_bound(
    approximation: str, radius: sp.Expr, n: int, bound: sp.Expr, nth: str, where: str
) -> Built:
    return finish(
        rf"\text{{Bound the error of }}{approximation}\text{{ for }}|x|\le{tex(radius)}"
        rf"\text{{ by }}\max|f^{{({n})}}|\cdot\frac{{|x|^{n}}}{{{n}!}}"
        r"\text{, the maximum taken over}"
        r"\text{ the interval. Give this bound exactly.}",
        FormulaAnswer(bound),
        rf"\text{{The approximation is the Taylor polynomial }}T_{{{n - 1}}}\text{{ at }}0.",
        rf"f^{{({n})}}(x)={nth},\ \text{{largest at }}{where};\qquad"
        rf"\text{{bound}}={tex(bound)}.",
    )


def error_tangent(a: int, b: int, c: int) -> Built:
    radius = sp.pi / (6 * (b + 1))
    third = sp.diff(sp.tan(X), X, 3)
    bound = sp.simplify(third.subs(X, radius) * radius**3 / 6)
    return error_bound(
        r"\tan x\approx x", radius, 3, bound, tex(sp.simplify(third)), r"x=\pm" + tex(radius)
    )


def error_cosine_square(a: int, b: int, c: int) -> Built:
    radius = sp.Rational(b, 10)
    bound = sp.Rational(8, 24) * radius**4
    return error_bound(r"\cos^2x\approx1-x^2", radius, 4, bound, r"8\cos 2x", "x=0")


def error_square_root(a: int, b: int, c: int) -> Built:
    radius = sp.Rational(b, 20)
    bound = sp.Rational(3, 8) * (1 - radius) ** sp.Rational(-5, 2) * radius**3 / 6
    return error_bound(
        r"\sqrt{1+x}\approx1+\frac x2-\frac{x^2}8",
        radius,
        3,
        sp.nsimplify(bound),
        r"\tfrac38(1+x)^{-5/2}",
        rf"x=-{tex(radius)}",
    )


def error_logarithm(a: int, b: int, c: int) -> Built:
    radius = sp.Rational(b, 20)
    bound = 6 / (1 - radius) ** 4 * radius**4 / 24
    return error_bound(
        r"\ln(1-x)\approx-x-\frac{x^2}2-\frac{x^3}3",
        radius,
        4,
        bound,
        r"-\frac{6}{(1-x)^4}",
        rf"x={tex(radius)}",
    )


def error_inverse_root(a: int, b: int, c: int) -> Built:
    radius = sp.Rational(b, 20)
    bound = sp.Rational(15, 8) * (1 - radius) ** sp.Rational(-7, 2) * radius**3 / 6
    return error_bound(
        r"\frac1{\sqrt{x+1}}\approx1-\frac x2+\frac{3x^2}8",
        radius,
        3,
        sp.nsimplify(bound),
        r"-\tfrac{15}8(1+x)^{-7/2}",
        rf"x=-{tex(radius)}",
    )


# AM1/73: least order meeting an accuracy, and the approximation it gives.


def least_order(f: sp.Expr, point: sp.Expr, accuracy: sp.Expr) -> tuple[int, sp.Expr]:
    for n in range(1, 40):
        nth = sp.diff(f, X, n)
        top = max(abs(sp.N(nth.subs(X, 0), 50)), abs(sp.N(nth.subs(X, point), 50)))
        if top * abs(sp.N(point, 50)) ** n / sp.factorial(n) <= sp.N(accuracy, 50):
            return n, sp.nsimplify(taylor_polynomial(f, 0, n - 1).subs(X, point))
    raise ValueError("No order found")


def approximation(shown: str, f: sp.Expr, point: sp.Expr, accuracy: sp.Expr) -> Built:
    n, value = least_order(f, point, accuracy)
    return finish(
        rf"\text{{Approximate }}{shown}\text{{ with }}T_{{n-1}}\text{{ of }}f(x)={tex(f)}"
        rf"\text{{ at }}0\text{{, evaluated at }}x={tex(point)}."
        r"\text{ Take the least }n\text{ for which }\max|f^{(n)}|\,\frac{|x|^n}{n!}\le"
        + tex(accuracy)
        + r"\text{ (maximum over the interval between }0\text{ and }x\text{). Give }n"
        r"\text{ and the exact value of }T_{n-1}(x).",
        OrderedAnswer((FormulaAnswer(n), FormulaAnswer(value)), APPROXIMATION),
        r"\text{Increase }n\text{ until the Lagrange bound meets the accuracy.}",
        rf"n={n},\qquad T_{{{n - 1}}}({tex(point)})={tex(value)}.",
    )


def approximate_reciprocal_e(a: int, b: int, c: int) -> Built:
    point = sp.Rational(-1, a)
    accuracy = sp.Rational(1, 10 ** (3 + b % 3))
    return approximation(tex(sp.exp(point)), sp.exp(X), point, accuracy)


def approximate_cube_root(a: int, b: int, c: int) -> Built:
    point = sp.Rational(-a, 1000)
    accuracy = sp.Rational(1, 10 ** (3 + b % 3))
    return approximation(
        rf"\sqrt[3]{{{tex(1 + point)}}}", (1 + X) ** sp.Rational(1, 3), point, accuracy
    )


def approximate_logarithm(a: int, b: int, c: int) -> Built:
    point = sp.Rational(a, 20)
    accuracy = sp.Rational(1, 10 ** (3 + b % 3))
    return approximation(rf"\ln {tex(1 + point)}", sp.log(1 + X), point, accuracy)


def approximate_sine(a: int, b: int, c: int) -> Built:
    point = sp.Rational(a, 10)
    accuracy = sp.Rational(1, 10 ** (4 + b % 3))
    return approximation(rf"\sin {tex(point)}", sp.sin(X), point, accuracy)
