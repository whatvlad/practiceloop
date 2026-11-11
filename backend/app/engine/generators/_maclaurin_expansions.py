"""Full Maclaurin coefficient templates, high derivatives and termwise calculus (#275)."""

from dataclasses import replace

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer, RealSetAnswer
from app.engine.generators._alternating_power_series import convergence_visual
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._sequence_limits import finish

X = sp.Symbol("x", real=True)
N = sp.Symbol("n", integer=True, nonnegative=True)
A, B = sp.symbols("A B", positive=True)
COEFFICIENT_LABELS = ("A", "B", "Convergence set")


def expansion(
    function: sp.Expr,
    template: sp.Expr,
    start: int,
    amplitude: sp.Expr,
    scale: sp.Expr,
    domain: sp.Set,
    method: str,
    proof: str,
) -> Built:
    term = template.subs({A: amplitude, B: scale})
    answer = OrderedAnswer(
        (FormulaAnswer(amplitude), FormulaAnswer(scale), RealSetAnswer(domain)), COEFFICIENT_LABELS
    )
    built = finish(
        rf"\text{{Find the full Maclaurin expansion of }}f(x)={tex(function)}"
        rf"\text{{ in the form }}\sum_{{n={start}}}^\infty {tex(template)},\quad A>0,\ B>0."
        r"\text{ Give (A; B; complete real convergence set), including endpoints.}",
        answer,
        method,
        proof + rf"\quad f(x)=\sum_{{n={start}}}^\infty {tex(term)},\quad D={tex(domain)}.",
    )
    return replace(built, visual=convergence_visual(domain))


def geometric_maclaurin(a: int, b: int, c: int) -> Built:
    return expansion(
        a / (1 - b * X),
        A * B**N * X**N,
        0,
        sp.Integer(a),
        sp.Integer(b),
        sp.Interval.open(-sp.Rational(1, b), sp.Rational(1, b)),
        r"\frac1{1-t}=\sum_{n=0}^\infty t^n\quad(|t|<1).",
        rf"t={b}x.\quad\text{{At }}x=\pm1/{b}\text{{ the terms do not tend to zero.}}",
    )


def sine_maclaurin(a: int, b: int, c: int) -> Built:
    return expansion(
        a * sp.sin(b * X),
        (-1) ** N * A * B ** (2 * N + 1) * X ** (2 * N + 1) / sp.factorial(2 * N + 1),
        0,
        sp.Integer(a),
        sp.Integer(b),
        sp.S.Reals,
        r"\sin t=\sum_{n=0}^\infty\frac{(-1)^nt^{2n+1}}{(2n+1)!}.",
        rf"t={b}x.\quad\text{{The factorial denominator gives convergence for every real }}x.",
    )


def polynomial_exponential_maclaurin(a: int, b: int, c: int) -> Built:
    shift = c + 1
    return expansion(
        a * X**shift * sp.exp(-b * X),
        A * (-B) ** N * X ** (N + shift) / sp.factorial(N),
        0,
        sp.Integer(a),
        sp.Integer(b),
        sp.S.Reals,
        r"e^t=\sum_{n=0}^\infty t^n/n!.\quad\text{Substitute, "
        r"then multiply by the stated monomial.}",
        rf"t=-{b}x,\quad f(x)={a}x^{{{shift}}}\sum_{{n=0}}^\infty\frac{{(-{b}x)^n}}{{n!}}."
        r"\quad\text{Multiplication by a fixed polynomial keeps the convergence set real.}",
    )


def odd_rational_maclaurin(a: int, b: int, c: int) -> Built:
    return expansion(
        a * X**3 / (b * b + X**2),
        A * (-B) ** N * X ** (2 * N + 3),
        0,
        sp.Rational(a, b * b),
        sp.Rational(1, b * b),
        sp.Interval.open(-b, b),
        rf"f(x)=\frac{{{a}x^3}}{{{b * b}}}\frac1{{1+x^2/{b * b}}}."
        rf"\quad\text{{Use the geometric series.}}",
        rf"|x^2/{b * b}|<1\Longleftrightarrow|x|<{b}.\quad"
        r"\text{At either endpoint the individual series terms fail to tend to zero.}",
    )


def hyperbolic_cosine_maclaurin(a: int, b: int, c: int) -> Built:
    return expansion(
        a * sp.cosh(b * X),
        A * B ** (2 * N) * X ** (2 * N) / sp.factorial(2 * N),
        0,
        sp.Integer(a),
        sp.Integer(b),
        sp.S.Reals,
        r"\cosh t=(e^t+e^{-t})/2.\quad\text{Odd powers "
        r"cancel when the exponential series are added.}",
        rf"t={b}x.\quad\text{{The remaining even factorial series converges for every real }}x.",
    )


def sine_square_maclaurin(a: int, b: int, c: int) -> Built:
    return expansion(
        a * sp.sin(b * X) ** 2,
        (-1) ** (N + 1) * A * B ** (2 * N) * X ** (2 * N) / sp.factorial(2 * N),
        1,
        sp.Rational(a, 2),
        sp.Integer(2 * b),
        sp.S.Reals,
        rf"f(x)=\frac{{{a}}}2(1-\cos({2 * b}x)).\quad"
        rf"\text{{Expand the cosine and cancel the constant term.}}",
        r"\text{The resulting series starts at }n=1\text{ and converges on all of the real line.}",
    )


def high_derivative(
    function: sp.Expr, order: int, value: sp.Expr, coefficient: str, method: str
) -> Built:
    return finish(
        rf"\text{{Use a Maclaurin coefficient to evaluate "
        rf"}}f^{{({order})}}(0),\quad f(x)={tex(function)}.",
        FormulaAnswer(value),
        method,
        rf"[x^{{{order}}}]f(x)={coefficient},\quad "
        rf"f^{{({order})}}(0)={order}!\,[x^{{{order}}}]f(x)={tex(value)}.",
    )


def cosine_high_derivative(a: int, b: int, c: int) -> Built:
    index = 20 + (b + c) % 9
    order = 2 * index + 2
    value = a * (-1) ** index * order * (order - 1)
    return high_derivative(
        a * X**2 * sp.cos(X),
        order,
        sp.Integer(value),
        rf"\frac{{{a}(-1)^{{{index}}}}}{{{order - 2}!}}",
        r"x^2\cos x=\sum_{n=0}^\infty\frac{(-1)^nx^{2n+2}}{(2n)!}."
        r"\quad\text{Match the requested exponent.}",
    )


def exponential_high_derivative(a: int, b: int, c: int) -> Built:
    order = 15 + b + c
    value = a * (-1) ** (order - 1) * order
    return high_derivative(
        a * X * sp.exp(-X),
        order,
        sp.Integer(value),
        rf"\frac{{{a}(-1)^{{{order - 1}}}}}{{{order - 1}!}}",
        r"xe^{-x}=\sum_{n=0}^\infty(-1)^nx^{n+1}/n!.\quad"
        r"\text{Match }n+1\text{ to the derivative order.}",
    )


def rational_high_derivative(a: int, b: int, c: int) -> Built:
    amplitude = 1 + a % 2
    index = 1 + (b + c) % 4
    order = 3 + 2 * index
    value = amplitude * (-1) ** index * sp.factorial(order)
    return high_derivative(
        amplitude * X**3 / (1 + X**2),
        order,
        value,
        tex(sp.Integer(amplitude * (-1) ** index)),
        r"\frac{x^3}{1+x^2}=\sum_{n=0}^\infty(-1)^nx^{2n+3}.\quad"
        r"\text{Read the coefficient at the requested odd exponent.}",
    )


def sine_square_high_derivative(a: int, b: int, c: int) -> Built:
    order = 6 + c
    index = (order - 1) // 2
    value = sp.S.Zero if order % 2 == 0 else -sp.Rational(a * (-1) ** index * order, 2)
    coefficient = "0" if order % 2 == 0 else rf"-\frac{{{a}(-1)^{{{index}}}}}{{2\cdot{order - 1}!}}"
    return high_derivative(
        a * X * sp.sin(X / 2) ** 2,
        order,
        value,
        coefficient,
        rf"f(x)=\frac{{{a}x}}2(1-\cos x).\quad\text{{Only "
        rf"odd powers occur, and the linear term cancels.}}",
    )


def differentiated_geometric_maclaurin(a: int, b: int, c: int) -> Built:
    return expansion(
        a / (1 + b * X) ** 2,
        A * (N + 1) * (-B) ** N * X**N,
        0,
        sp.Integer(a),
        sp.Integer(b),
        sp.Interval.open(-sp.Rational(1, b), sp.Rational(1, b)),
        rf"\frac1{{1+{b}x}}=\sum_{{n=0}}^\infty(-{b})^n x^n."
        rf"\quad\text{{Differentiate inside its radius.}}",
        rf"\frac{{{a}}}{{(1+{b}x)^2}}=-\frac{{{a}}}{{{b}}}\frac d{{dx}}\frac1{{1+{b}x}}."
        r"\quad\text{Reindex after differentiation. At "
        r"both endpoints the magnitudes grow like }n+1.",
    )


def differentiated_exponential_maclaurin(a: int, b: int, c: int) -> Built:
    return expansion(
        a * X * sp.exp(-b * X),
        A * (-B) ** N * X ** (N + 1) / sp.factorial(N),
        0,
        sp.Integer(a),
        sp.Integer(b),
        sp.S.Reals,
        rf"f(x)=-\frac{{{a}}}{{{b}}}x\frac d{{dx}}e^{{-{b}x}}.\quad"
        rf"\text{{Differentiate the exponential series termwise.}}",
        rf"-\frac{{{a}}}{{{b}}}\sum_{{n=1}}^\infty\frac{{n(-{b})^nx^n}}{{n!}}"
        rf"={a}\sum_{{m=0}}^\infty\frac{{(-{b})^mx^{{m+1}}}}{{m!}}.\quad D=\mathbb R.",
    )


def integrated_logarithm_maclaurin(a: int, b: int, c: int) -> Built:
    radius = 1 / sp.sqrt(b)
    return expansion(
        a * sp.log(1 + b * X**2),
        (-1) ** (N + 1) * A * B**N * X ** (2 * N) / N,
        1,
        sp.Integer(a),
        sp.Integer(b),
        sp.Interval(-radius, radius),
        rf"\ln(1+{b}x^2)=\int_0^{{{b}x^2}}\frac{{dt}}{{1+t}}."
        rf"\quad\text{{Integrate the geometric series termwise.}}",
        r"\text{Inside the radius the integrated series is valid. At each "
        r"endpoint it becomes the convergent alternating harmonic series.}",
    )


def integrated_arctangent_maclaurin(a: int, b: int, c: int) -> Built:
    return expansion(
        a * sp.atan(b * X),
        (-1) ** N * A * B ** (2 * N + 1) * X ** (2 * N + 1) / (2 * N + 1),
        0,
        sp.Integer(a),
        sp.Integer(b),
        sp.Interval(-sp.Rational(1, b), sp.Rational(1, b)),
        rf"f(x)=\int_0^x\frac{{{a * b}}}{{1+{b * b}t^2}}\,dt."
        rf"\quad\text{{Integrate the geometric series termwise.}}",
        r"\text{At both endpoints, Leibniz decides "
        r"convergence of the alternating odd-harmonic series.}",
    )
