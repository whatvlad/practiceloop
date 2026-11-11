"""First-order linear equations and tangent-defined curves from AM2A/13.4–13.6."""

import math
from dataclasses import replace

import sympy as sp

from app.engine.answers.computational import OrderedAnswer, RealSetAnswer
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot, point
from app.engine.generators._separable_odes import NONZERO, POSITIVE, R, T, explicit_ivp, visual
from app.engine.generators._sequence_limits import finish

LINEAR_FAMILY = ("Particular solution", "Homogeneous factor", "Constants", "Time set")
TANGENT_FAMILY = (
    "Particular solution",
    "Homogeneous factor",
    "Constants",
    "Lower bound for constant",
    "Upper bound for constant",
)


def linear_family(
    equation: str,
    particular: sp.Expr,
    homogeneous: sp.Expr,
    domain: sp.Set,
    normalization: str,
    derivation: str,
    domain_detail: str,
    windows: tuple[tuple[float, float], ...],
) -> Built:
    answer = OrderedAnswer(
        (
            DomainFormulaAnswer(particular, domain, "t"),
            DomainFormulaAnswer(homogeneous, domain, "t"),
            RealSetAnswer(R),
            RealSetAnswer(domain),
        ),
        LINEAR_FAMILY,
    )
    built = finish(
        rf"\text{{Find the general real solution of }}{equation}."
        r"\quad\text{Use }y=P(t)+C H(t).\quad"
        + normalization
        + r"\quad\text{Give }P(t),H(t),\text{ the set of constants and the full allowed time set.}",
        answer,
        derivation,
        rf"y={tex(particular)}+C\left({tex(homogeneous)}\right),\quad C\in\mathbb R."
        rf"\quad t\in{tex(domain)}.\quad" + domain_detail,
    )
    names = (
        ("First solution", "Second solution")
        if len(windows) == 1
        else ("Left branch", "Right branch")
    )
    params = (-1, 1)
    curves = [
        (name, *window, sp.lambdify(T, particular + constant * homogeneous, "math"))
        for name, window, constant in zip(
            names, windows * 2 if len(windows) == 1 else windows, params, strict=True
        )
    ]
    return replace(built, visual=visual(curves, []))


def sinusoidal_forcing_family(a: int, b: int, c: int) -> Built:
    particular = b * (a * sp.sin(c * T) - c * sp.cos(c * T)) / (a * a + c * c)
    homogeneous = sp.exp(-a * T)
    return linear_family(
        rf"y'+{a}y={b}\sin({c}t)",
        particular,
        homogeneous,
        R,
        r"\text{Choose the periodic particular solution and normalize }H(0)=1.",
        r"\text{Set }P=A\sin(ct)+B\cos(ct)\text{ and match the sine and cosine coefficients.}"
        rf"\quad A={tex(sp.Rational(a * b, a * a + c * c))},"
        rf"\quad B={tex(-sp.Rational(b * c, a * a + c * c))}."
        rf"\quad H'+{a}H=0.",
        r"\text{Both functions are defined for all real time.}",
        ((-1, 2),),
    )


def gaussian_forcing_family(a: int, b: int, c: int) -> Built:
    u = T - c
    h = sp.exp(-a * u * u)
    return linear_family(
        rf"y'+{2 * a}(t-{c})y={b}e^{{-{a}(t-{c})^2}}",
        b * u * h,
        h,
        R,
        rf"P({c})=0,\quad H({c})=1.",
        rf"\left(e^{{{a}(t-{c})^2}}y\right)'={b}."
        r"\quad\text{Integrate and apply the two normalizations.}",
        r"\text{The integrating factor never vanishes.}",
        ((c - 2, c + 2),),
    )


def cosine_euler_family(a: int, b: int, c: int) -> Built:
    factor = sp.Rational(b + c, a)
    p = factor * T**2 * sp.sin(a * T)
    return linear_family(
        rf"t y'-2y={b + c}t^3\cos({a}t)",
        p,
        T**2,
        R,
        r"\text{Use the particular solution with no constant term in }P(t)/t^2"
        r"\text{ and normalize }H(t)=t^2.",
        rf"(y/t^2)'={b + c}\cos({a}t)\quad(t\ne0).",
        r"\text{At zero the equation forces }y(0)=0."
        r"\quad\text{The two one-sided derivatives vanish, so the constants may be independent.}",
        ((-2, 2),),
    )


def power_euler_family(a: int, b: int, c: int) -> Built:
    degree = c + 3
    factor = sp.Rational(a + b, degree - 2)
    return linear_family(
        rf"t y'-2y={a + b}t^{{{degree}}}",
        factor * T**degree,
        T**2,
        R,
        r"\text{Use a monomial particular solution and }H(t)=t^2.",
        rf"(y/t^2)'={a + b}t^{{{degree - 3}}}\quad(t\ne0).",
        r"\text{The zero value and zero derivative at the "
        r"origin allow independent constants on the two sides.}",
        ((-2, 2),),
    )


def exponential_singular_family(a: int, b: int, c: int) -> Built:
    h = sp.exp(a * T)
    k = b + c
    return linear_family(
        rf"t y'-{a}t y={k}e^{{{a}t}}",
        k * h * sp.log(sp.Abs(T)),
        h,
        NONZERO,
        r"\text{Use zero additive constant after multiplying by the integrating factor, and }H(0)=1"
        r"\text{ for its continuous extension.}",
        rf"\left(e^{{-{a}t}}y\right)'={k}/t\quad(t\ne0).",
        r"\text{At }t=0\text{ the original equation is inconsistent."
        r" Each open half-line has its own arbitrary constant.}",
        ((-2, -0.1), (0.1, 2)),
    )


def shifted_singular_family(a: int, b: int, c: int) -> Built:
    u = T + a
    k = b + c
    p = k * (u * sp.log(sp.Abs(u)) + a)
    domain = R - sp.FiniteSet(-a)
    return linear_family(
        rf"(t+{a})y'-y={k}t",
        p,
        u,
        domain,
        r"\text{Normalize the homogeneous factor to slope one and give a particular solution"
        r" with zero homogeneous integration constant.}",
        rf"\left(\frac{{y}}{{t+{a}}}\right)'"
        rf"=\frac{{{k}}}{{t+{a}}}-\frac{{{k * a}}}{{(t+{a})^2}}.",
        rf"\text{{At }}t=-{a}\text{{ the derivative diverges logarithmically on either side.}}"
        r"\quad\text{There is no differentiable crossing of the singular time.}",
        ((-a - 2, -a - 0.1), (-a + 0.1, -a + 2)),
    )


def constant_forcing_ivp(a: int, b: int, c: int) -> Built:
    y0 = b + c
    offset = sp.Rational(b, a)
    y = (y0 + offset) * sp.exp(a * (T - c)) - offset
    return explicit_ivp(
        rf"y'-{a}y={b}",
        rf"y({c})={y0}",
        y,
        R,
        rf"(y+{tex(offset)})'={a}(y+{tex(offset)})."
        rf"\quad y({c})+{tex(offset)}={tex(y0 + offset)}.",
        r"\text{The coefficients are continuous on the whole real line.}",
        (c - 1, c + 1),
        (c, y0),
    )


def sinusoidal_coefficient_ivp(a: int, b: int, c: int) -> Built:
    t0 = sp.pi / (c + 2)
    y0 = -b if c % 2 == 0 else b + c
    y = -b + (y0 + b) * sp.exp(a * (sp.cos(t0) - sp.cos(T)))
    return explicit_ivp(
        rf"y'={a}(y+{b})\sin t",
        rf"y({tex(t0)})={y0}",
        y,
        R,
        rf"w=y+{b}\Longrightarrow w'={a}w\sin t."
        rf"\quad w(t)=w(t_0)e^{{{a}(\cos t_0-\cos t)}}.",
        r"\text{The formula also covers }w(t_0)=0\text{, the equilibrium solution.}",
        (-math.pi, math.pi),
        (float(t0), y0),
    )


def rational_forcing_ivp(a: int, b: int, c: int) -> Built:
    constant = -c * (sp.Rational(a * c, 2) + b)
    y = a * T / 2 + b + constant / T
    return explicit_ivp(
        rf"t y'+y={a}t+{b}",
        rf"y({c})=0",
        y,
        POSITIVE,
        rf"(ty)'={a}t+{b}\quad\Longrightarrow\quad ty={a}t^2/2+{b}t+K."
        rf"\quad K={tex(constant)}.",
        r"\text{The nonzero reciprocal coefficient gives a pole at }t=0.",
        (0.2, c + 2),
        (c, 0),
    )


def trigonometric_singular_ivp(a: int, b: int, c: int) -> Built:
    t0 = sp.pi / (c + 3)
    k = a + b
    y = k * (sp.cos(t0) * sp.tan(T) - sp.sin(T))
    return explicit_ivp(
        rf"\sin t\cos t\,y'=y+{k}\sin^3 t,\quad \sin t\cos t\ne0",
        rf"y({tex(t0)})=0",
        y,
        sp.Interval.open(0, sp.pi / 2),
        rf"(y\cot t)'={k}\sin t\quad\Longrightarrow\quad y\cot t=K-{k}\cos t."
        rf"\quad K={tex(k * sp.cos(t0))}.",
        r"\text{The interval containing the initial point "
        r"is between the excluded coefficient zeros.}",
        (0.05, 1.45),
        (float(t0), 0),
    )


def tangent_area_family(a: int, b: int, c: int) -> Built:
    area = a + b + c
    particular = sp.Rational(2 * area, 3) / T
    homogeneous = T**2
    lower = -sp.Rational(2 * area, 3) / T**3
    upper = sp.Rational(4 * area, 3) / T**3
    answer = OrderedAnswer(
        (
            DomainFormulaAnswer(particular, POSITIVE, "t"),
            DomainFormulaAnswer(homogeneous, POSITIVE, "t"),
            RealSetAnswer(R),
            DomainFormulaAnswer(lower, POSITIVE, "t"),
            DomainFormulaAnswer(upper, POSITIVE, "t"),
        ),
        TANGENT_FAMILY,
    )
    built = finish(
        rf"\text{{A tangent at }}(t,y),\ t>0,\ y>0,\text{{ has a positive vertical intercept.}}"
        rf"\quad\text{{The trapezoid between the axes, tangent and vertical at }}t"
        rf"\text{{ has area }}{area}\text{{. Find the family }}y=P(t)+Ct^2."
        r"\quad\text{Give }P(t),H(t)=t^2,\text{ the admissible set of }C"
        r"\text{ and its strict lower and upper bounds at a given }t.",
        answer,
        rf"Y=y-t y',\quad A=t(y+Y)/2=t y-t^2 y'/2={area}."
        rf"\quad (y/t^2)'=-{2 * area}/t^4.",
        rf"y={tex(particular)}+Ct^2,\quad Y={tex(2 * particular)}-Ct^2."
        rf"\quad y,Y>0\Longleftrightarrow {tex(lower)}<C<{tex(upper)}."
        r"\quad\text{Each }C\in\mathbb R\text{ is possible near zero and the inequalities give"
        r" its maximal interval in the first quadrant.}",
    )
    y = 5 * area / 6
    intercept = 7 * area / 6
    diagram = plot(
        "Tangent and fixed-area trapezoid",
        "A representative member touches the tangent at "
        "the marked point. The closed path is the trapezoid.",
        [
            path("Solution curve", 0.25, 1.6, lambda t: 2 * area / (3 * t) + area * t * t / 6),
            path("Tangent", 0, 1.4, lambda t: intercept - area * t / 3),
            {
                "label": "Area trapezoid",
                "closed": True,
                "points": [[0, 0], [1, 0], [1, y], [0, intercept], [0, 0]],
            },
        ],
        [point("Contact", 1, y, included=True)],
    )
    diagram.update(xLabel="t", yLabel="y")
    return replace(built, visual=diagram)
