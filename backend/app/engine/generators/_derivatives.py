"""Derivative definitions, rules with differentiability domains and tangents (#260)."""

import sympy as sp

from app.engine.answers.computational import (
    ComputationalAnswer,
    FormulaAnswer,
    OrderedAnswer,
    PeriodicSetAnswer,
    RealSetAnswer,
)
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.blocks.analysis_one import X
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._sequence_limits import finish
from app.math_input.contracts import Domain

REAL_X: tuple[tuple[str, Domain], ...] = (("x", "real"),)
DERIVATIVE_DOMAIN = ("Derivative", "Differentiability domain")
DERIVATIVE_EXCLUDED = ("Derivative", "Excluded points")
TANGENT_AT = ("Ordinate of the point", "Tangent line")
TANGENT_FIND = ("Abscissa of the point", "Tangent line")
TANGENT_FULL = ("Abscissa", "Ordinate", "Tangent line")
TWO_TANGENTS = ("Left tangent", "Right tangent")


def scaled(k: int) -> str:
    return "" if k == 1 else str(k)


def derivative(f: sp.Expr) -> sp.Expr:
    """The rule-by-rule derivative, left in the form the rules produce."""
    return sp.diff(f, X)


def by_definition(shown: str, f: sp.Expr, domain: sp.Set, quotient: str) -> Built:
    value = derivative(f)
    return finish(
        r"\text{Using the definition (limit of the difference quotient), find }f'(x)"
        rf"\text{{ on the domain:}}\quad f(x)={shown}.",
        DomainFormulaAnswer(value, domain),
        r"\text{Simplify }\frac{f(x+h)-f(x)}{h}\text{ before letting }h\to0.",
        quotient + rf"\ \xrightarrow[h\to0]{{}}\ {tex(value)}.",
    )


def with_domain(shown: str, f: sp.Expr, domain: sp.Set, method: str) -> Built:
    value = derivative(f)
    return finish(
        r"\text{Find }f'(x)\text{ and the largest set on which }f\text{ is differentiable:}"
        rf"\quad f(x)={shown}.",
        OrderedAnswer(
            (DomainFormulaAnswer(value, domain), RealSetAnswer(domain)), DERIVATIVE_DOMAIN
        ),
        method,
        rf"f'(x)={tex(value)},\qquad x\in{tex(domain)}.",
    )


# AM1/40: derivative functions from the difference quotient.


def definition_power(a: int, b: int, c: int) -> Built:
    power = b + 1
    f = a * X**power + c * X
    return by_definition(
        tex(f),
        f,
        sp.S.Reals,
        rf"\frac{{{scaled(a)}((x+h)^{{{power}}}-x^{{{power}}})+{c}h}}{{h}}"
        rf"={scaled(a)}\sum_{{k=1}}^{{{power}}}\binom{{{power}}}{{k}}x^{{{power}-k}}h^{{k-1}}+{c}",
    )


def definition_reciprocal(a: int, b: int, c: int) -> Built:
    f = a / (X - b)
    return by_definition(
        rf"\frac{{{a}}}{{x-{b}}}\ (x\ne{b})",
        f,
        sp.S.Reals - sp.FiniteSet(b),
        rf"\frac{{1}}{{h}}\left(\frac{{{a}}}{{x+h-{b}}}-\frac{{{a}}}{{x-{b}}}\right)"
        rf"=\frac{{-{a}}}{{(x+h-{b})(x-{b})}}",
    )


def definition_root(a: int, b: int, c: int) -> Built:
    f = a * sp.sqrt(X + c)
    return by_definition(
        rf"{scaled(a)}\sqrt{{x+{c}}}\ (x>-{c})",
        f,
        sp.Interval.open(-c, sp.oo),
        rf"\frac{{{scaled(a)}(\sqrt{{x+h+{c}}}-\sqrt{{x+{c}}})}}{{h}}"
        rf"=\frac{{{a}}}{{\sqrt{{x+h+{c}}}+\sqrt{{x+{c}}}}}",
    )


def definition_sine(a: int, b: int, c: int) -> Built:
    f = a * sp.sin(b * X)
    return by_definition(
        tex(f),
        f,
        sp.S.Reals,
        rf"\frac{{{scaled(a)}(\sin({b}x+{b}h)-\sin {scaled(b)}x)}}{{h}}"
        rf"={scaled(a)}\cos\left({scaled(b)}x+\tfrac{{{b}h}}{{2}}\right)"
        rf"\frac{{2\sin({b}h/2)}}{{h}}",
    )


# AM1/41: rules of differentiation with the differentiability domain.


def trig_sum(a: int, b: int, c: int) -> Built:
    f = a * sp.sin(X) + b * sp.cot(X)
    value = derivative(f)
    return finish(
        r"\text{Find }f'(x)\text{ and the excluded points of the domain, as a period and a base}"
        rf"\text{{ set in }}[0,\pi):\quad f(x)={tex(f)}.",
        OrderedAnswer(
            (
                DomainFormulaAnswer(value, sp.Interval.open(0, sp.pi)),
                PeriodicSetAnswer(sp.pi, sp.FiniteSet(0)),
            ),
            DERIVATIVE_EXCLUDED,
        ),
        r"\text{Differentiate term by term: }(\sin x)'=\cos x,\ (\cot x)'=-1/\sin^2x.",
        rf"f'(x)={tex(value)},\qquad \sin x\ne0\iff x\ne k\pi.",
    )


def exponential_quadratic(a: int, b: int, c: int) -> Built:
    f = sp.exp(a * X) * (X**2 + b * X + c)
    return with_domain(
        tex(f),
        f,
        sp.S.Reals,
        r"\text{Product rule with }(e^{ax})'=ae^{ax}.",
    )


def rational_quotient(a: int, b: int, c: int) -> Built:
    f = (X**2 + a) / (X - b)
    return with_domain(
        tex(f),
        f,
        sp.S.Reals - sp.FiniteSet(b),
        r"\text{Quotient rule; the denominator vanishes only at }x=" + str(b) + ".",
    )


def exponential_square(a: int, b: int, c: int) -> Built:
    f = sp.exp(-a * X) * (b * X + c) ** 2
    return with_domain(
        tex(f), f, sp.S.Reals, r"\text{Product rule and the chain rule for the square.}"
    )


def log_arctan_root(a: int, b: int, c: int) -> Built:
    f = sp.log(X**2 + a + 1) * sp.atan(b * sp.sqrt(X))
    return with_domain(
        tex(f),
        f,
        sp.Interval.open(0, sp.oo),
        r"\text{The root is defined for }x\ge0\text{ but differentiable only for }x>0"
        r"\text{; at }0\text{ the difference quotient is unbounded because }\ln(a+1)>0.",
    )


def exponential_arctan(a: int, b: int, c: int) -> Built:
    f = sp.exp(a / X) * sp.atan(b - X)
    return with_domain(
        tex(f),
        f,
        sp.S.Reals - sp.FiniteSet(0),
        r"\text{Product rule; }e^{a/x}\text{ is defined and differentiable for }x\ne0.",
    )


def log_cosine(a: int, b: int, c: int) -> Built:
    f = sp.log(a * sp.cos(X) ** 2 + b)
    return with_domain(
        tex(f),
        f,
        sp.S.Reals,
        rf"\text{{The argument is at least }}{b}>0"
        r"\text{, so the chain rule applies on }\mathbb R.",
    )


def root_arccos(a: int, b: int, c: int) -> Built:
    f = a * sp.sqrt(sp.acos(X**2 / c**2))
    return with_domain(
        tex(f),
        f,
        sp.Interval.open(-c, c),
        rf"\text{{The arccosine is differentiable for }}x^2<{c * c}"
        r"\text{, where it is positive.}",
    )


def constant_over_power(a: int, b: int, c: int) -> Built:
    f = sp.sqrt(a) / (X**2 + b) ** c
    return with_domain(
        tex(f), f, sp.S.Reals, r"\text{The numerator is a constant: use the chain rule.}"
    )


def exponential_trig_powers(a: int, b: int, c: int) -> Built:
    f = (a + 1) ** (sp.sin(X) ** 2) / (b + 1) ** (sp.cos(X) ** 2)
    return with_domain(
        tex(f),
        f,
        sp.S.Reals,
        r"\text{Use }(q^{u})'=q^{u}\ln q\cdot u'\text{ for each power.}",
    )


def power_of_exponential(a: int, b: int, c: int) -> Built:
    f = (sp.exp(-a * X) + b) ** (c + 1)
    return with_domain(tex(f), f, sp.S.Reals, r"\text{Chain rule.}")


def variable_power(a: int, b: int, c: int) -> Built:
    # Written through exp so the answer uses the only variable power learners can type.
    f = sp.exp(b * X * sp.log(sp.sin(a * X)))
    domain = sp.Interval.open(0, sp.pi / a)
    value = derivative(f)
    return finish(
        rf"\text{{For }}0<x<{tex(sp.pi / a)}\text{{ find }}f'(x):\quad f(x)="
        + tex(sp.sin(a * X) ** (b * X))
        + ".",
        DomainFormulaAnswer(value, domain),
        r"\text{Logarithmic differentiation: }\ln f=bx\ln\sin ax.",
        rf"\frac{{f'}}{{f}}={scaled(b)}\ln\sin {scaled(a)}x+{a * b}x\cot {scaled(a)}x,"
        rf"\qquad f'(x)={tex(value)}.",
    )


def inverse_trig_constant(a: int, b: int, c: int) -> Built:
    domain = sp.Interval.open(-c, c)
    return finish(
        r"\text{Find }f'(x)\text{ and the largest set on which }f\text{ is differentiable:}"
        rf"\quad f(x)=\left({scaled(a)}\left(\arcsin\frac{{x}}{{{c}}}+\arccos\frac{{x}}{{{c}}}"
        rf"\right)+{b}\right)^2.",
        OrderedAnswer(
            (DomainFormulaAnswer(sp.Integer(0), domain), RealSetAnswer(domain)),
            DERIVATIVE_DOMAIN,
        ),
        r"\text{Differentiate inside: }(\arcsin u+\arccos u)'=0\text{ for }|u|<1.",
        rf"\arcsin u+\arccos u=\tfrac{{\pi}}{{2}}\ \Rightarrow\ f\equiv"
        rf"\left(\tfrac{{{a}\pi}}{{2}}+{b}\right)^2,\quad f'=0\text{{ on }}(-{c},{c}).",
    )


def logarithm_constant(a: int, b: int, c: int) -> Built:
    domain = sp.Interval.open(0, sp.oo)
    return finish(
        r"\text{Find }f'(x)\text{ and the largest set on which }f\text{ is differentiable:}"
        rf"\quad f(x)=\ln({scaled(a)}x)+\ln\frac{{{b}}}{{x}}+{scaled(c)}x.",
        OrderedAnswer(
            (DomainFormulaAnswer(sp.Integer(c), domain), RealSetAnswer(domain)),
            DERIVATIVE_DOMAIN,
        ),
        r"\text{Both logarithms need }x>0.\text{ Their sum is a constant.}",
        rf"\ln({scaled(a)}x)+\ln\frac{{{b}}}{{x}}=\ln{a * b},\qquad f'(x)={c}.",
    )


def log_constant_quotient(a: int, b: int, c: int) -> Built:
    year = 2000 + 5 * a + b
    f = sp.log(year) / (X**2 + c)
    return with_domain(
        rf"\frac{{\ln {year}}}{{x^2+{c}}}",
        f,
        sp.S.Reals,
        rf"\ln {year}\text{{ is a constant factor.}}",
    )


def constant_coefficients(a: int, b: int, c: int) -> Built:
    f = sp.exp(a) * sp.sin(b * X) + sp.sqrt(sp.pi) * sp.cos(c * X)
    return with_domain(
        tex(f), f, sp.S.Reals, r"e^{a}\text{ and }\sqrt\pi\text{ are constant factors.}"
    )


def root_exponential_domain(a: int, b: int, c: int) -> Built:
    f = sp.exp(a * sp.sqrt(2 * b * X - X**2))
    return with_domain(
        tex(f),
        f,
        sp.Interval.open(0, 2 * b),
        rf"\text{{The radicand is nonnegative on }}[0,{2 * b}]\text{{ and the root is}}"
        r"\text{ differentiable only where it is positive.}",
    )


def arcsine_shifted_square(a: int, b: int, c: int) -> Built:
    shift = b + 1
    f = a * sp.asin(X**2 - shift)
    low, high = sp.sqrt(shift - 1), sp.sqrt(shift + 1)
    domain = sp.Union(sp.Interval.open(-high, -low), sp.Interval.open(low, high))
    return with_domain(
        tex(f),
        f,
        domain,
        rf"\text{{The arcsine is differentiable for }}|x^2-{shift}|<1.",
    )


# AM1/42 and the exam tangents at a given point.


def tangent_given(shown: str, f: sp.Expr, x0: sp.Expr, method: str) -> Built:
    y0 = sp.simplify(f.subs(X, x0))
    slope = sp.simplify(sp.diff(f, X).subs(X, x0))
    line = sp.expand(slope * (X - x0) + y0)
    return finish(
        rf"\text{{Find the ordinate of the point and the tangent line at }}x_0={tex(x0)}:"
        rf"\quad f(x)={shown}.",
        OrderedAnswer((FormulaAnswer(y0), FormulaAnswer(line, REAL_X)), TANGENT_AT),
        method,
        rf"f({tex(x0)})={tex(y0)},\quad f'({tex(x0)})={tex(slope)},\qquad y={tex(line)}.",
    )


def tangent_arctan(a: int, b: int, c: int) -> Built:
    f = a * sp.atan(X / b)
    return tangent_given(tex(f), f, sp.Integer(b), r"\text{Tangent: }y=f(x_0)+f'(x_0)(x-x_0).")


def tangent_logarithm(a: int, b: int, c: int) -> Built:
    f = sp.log(X**2 + b)
    return tangent_given(tex(f), f, sp.Integer(c - 3), r"(\ln u)'=u'/u.")


def tangent_tangent_square(a: int, b: int, c: int) -> Built:
    f = a * sp.tan(b * X) ** 2
    return tangent_given(tex(f), f, sp.pi / (4 * b), r"(\tan^2u)'=2\tan u\,(1+\tan^2u)\,u'.")


def tangent_root_exponential(a: int, b: int, c: int) -> Built:
    f = sp.sqrt((a + 1) ** X + c)
    return tangent_given(tex(f), f, sp.Integer(b), r"(\sqrt u)'=u'/(2\sqrt u),\ (q^x)'=q^x\ln q.")


def tangent_rational(a: int, b: int, c: int) -> Built:
    f = a * X / (b + X**2)
    return tangent_given(tex(f), f, sp.sqrt(c), r"\text{Quotient rule.}")


def tangent_exponential_level(a: int, b: int, c: int) -> Built:
    f = sp.exp(a + b / X)
    x0 = sp.Rational(-b, a)
    slope = sp.simplify(sp.diff(f, X).subs(X, x0))
    line = sp.expand(slope * (X - x0) + 1)
    return finish(
        rf"\text{{Find }}x_0\text{{ with }}f(x_0)=1\text{{ and the tangent at }}(x_0,1):"
        rf"\quad f(x)={tex(f)}.",
        OrderedAnswer((FormulaAnswer(x0), FormulaAnswer(line, REAL_X)), TANGENT_FIND),
        r"e^{u}=1\iff u=0.",
        rf"{a}+\frac{{{b}}}{{x_0}}=0\Rightarrow x_0={tex(x0)},\quad f'(x_0)={tex(slope)},"
        rf"\qquad y={tex(line)}.",
    )


def tangent_arctan_quotient(a: int, b: int, c: int) -> Built:
    x0 = (sp.sqrt(3), sp.Integer(1), 1 / sp.sqrt(3))[c % 3]
    f = a * sp.atan(X) / X
    return tangent_given(tex(f), f, x0, r"\text{Quotient rule with }(\arctan x)'=1/(1+x^2).")


def tangent_exponential_cubic(a: int, b: int, c: int) -> Built:
    x0 = 1 + b % 3
    level = x0**3 - a
    f = sp.exp(X**3 - a)
    slope = sp.diff(f, X).subs(X, x0)
    line = sp.expand(slope * (X - x0) + sp.exp(level))
    return finish(
        rf"\text{{Find }}x_0\text{{ and the tangent line at the point }}(x_0,{tex(sp.exp(level))}):"
        rf"\quad f(x)={tex(f)}.",
        OrderedAnswer((FormulaAnswer(x0), FormulaAnswer(line, REAL_X)), TANGENT_FIND),
        r"\text{The exponential is injective: compare exponents.}",
        rf"x_0^3-{a}={level}\Rightarrow x_0={x0},\quad f'(x_0)={tex(slope)},\qquad y={tex(line)}.",
    )


# AM1/43 and the exam tangents fixed by a geometric condition.


def tangent_full(
    shown: str, condition: str, f: sp.Expr, x0: sp.Expr, method: str, solve: str
) -> Built:
    y0 = sp.simplify(f.subs(X, x0))
    slope = sp.simplify(sp.diff(f, X).subs(X, x0))
    line = sp.expand(slope * (X - x0) + y0)
    return finish(
        rf"\text{{Find the point of contact and the tangent line {condition}:}}"
        rf"\quad f(x)={shown}.",
        OrderedAnswer(
            (FormulaAnswer(x0), FormulaAnswer(y0), FormulaAnswer(line, REAL_X)), TANGENT_FULL
        ),
        method,
        solve + rf",\quad y_0={tex(y0)},\qquad y={tex(line)}.",
    )


def tangent_parallel_quartic(a: int, b: int, c: int) -> Built:
    x0 = 1 + c % 2
    slope = 4 * x0**3 - a
    f = X**4 - a * X + b
    return tangent_full(
        tex(f),
        rf"\text{{ parallel to }}y={tex(slope * X + c)}",
        f,
        sp.Integer(x0),
        r"\text{Parallel lines have equal slopes; }4x^3\text{ is strictly increasing.}",
        rf"4x_0^3-{a}={slope}\Rightarrow x_0={x0}",
    )


def tangent_angle_root(a: int, b: int, c: int) -> Built:
    slope = sp.Integer(1) if c % 2 else sp.sqrt(3)
    angle = r"\pi/4" if c % 2 else r"\pi/3"
    f = a * sp.sqrt(X)
    x0 = sp.Rational(a * a, 4) / slope**2
    return tangent_full(
        tex(f),
        rf"\text{{ making the angle }}{angle}\text{{ with the }}x\text{{-axis}}",
        f,
        x0,
        rf"\text{{The slope is }}\tan({angle})={tex(slope)}.",
        rf"\frac{{{a}}}{{2\sqrt{{x_0}}}}={tex(slope)}\Rightarrow x_0={tex(x0)}",
    )


def tangent_perpendicular_xlogx(a: int, b: int, c: int) -> Built:
    slope = a + 1
    f = X * sp.log(X)
    x0 = sp.exp(slope - 1)
    return tangent_full(
        tex(f),
        rf"\text{{ perpendicular to }}x+{slope}y-{c}=0",
        f,
        x0,
        rf"\text{{The given line has slope }}-1/{slope}"
        rf"\text{{, so the tangent has slope }}{slope}.",
        rf"\ln x_0+1={slope}\Rightarrow x_0={tex(x0)}",
    )


def tangent_line_intersection(a: int, b: int, c: int) -> Built:
    f = a * X * sp.atan(b / X)
    return tangent_full(
        rf"{scaled(a)}x\arctan\frac{{{b}}}{{x}}",
        rf"\text{{ at its intersection with }}4y={scaled(a)}\pi x",
        f,
        sp.Integer(b),
        r"\text{For }x\ne0\text{ the equation reduces to }\arctan(b/x)=\pi/4.",
        rf"\arctan\frac{{{b}}}{{x_0}}=\frac{{\pi}}{{4}}\Rightarrow x_0={b}",
    )


def tangent_axis_intersection(a: int, b: int, c: int) -> Built:
    f = sp.sin(a * X) - sp.cos(b * X) + c
    return tangent_full(
        tex(f),
        r"\text{ at its intersection with the }y\text{-axis}",
        f,
        sp.Integer(0),
        r"\text{The }y\text{-axis is }x=0.",
        r"x_0=0",
    )


def tangent_horizontal(a: int, b: int, c: int) -> Built:
    f = (X - b) * sp.exp(-a * X)
    x0 = b + sp.Rational(1, a)
    return tangent_full(
        tex(f),
        rf"\text{{ parallel to the line }}y=e^{{{c}}}",
        f,
        x0,
        r"\text{A horizontal tangent needs }f'(x_0)=0.",
        rf"f'(x)=e^{{-{a}x}}(1-{a}(x-{b}))=0\Rightarrow x_0={tex(x0)}",
    )


def tangent_pair_perpendicular(a: int, b: int, c: int) -> Built:
    f = a * X / (1 + X**2)
    x0 = 1 / sp.sqrt(b + 1)
    slope = sp.Rational(a * b * (b + 1), (b + 2) ** 2)
    tangents = []
    for point in (-x0, x0):
        y0 = sp.simplify(f.subs(X, point))
        line = sp.expand(slope * (X - point) + y0)
        tangents.append(
            OrderedAnswer(
                (FormulaAnswer(point), FormulaAnswer(y0), FormulaAnswer(line, REAL_X)),
                TANGENT_FULL,
            )
        )
    answers: tuple[ComputationalAnswer, ...] = tuple(tangents)
    p, q = (b + 2) ** 2, a * b * (b + 1)
    return finish(
        r"\text{Find every tangent line perpendicular to the given line, ordered by the}"
        rf"\text{{ abscissa of contact:}}\quad {p}x+{q}y-{c}=0,\quad f(x)={tex(f)}.",
        OrderedAnswer(answers, TWO_TANGENTS),
        rf"\text{{The given line has slope }}-{tex(sp.Rational(p, q))}"
        rf"\text{{, so the tangents have slope }}{tex(slope)}.",
        rf"\frac{{{a}(1-x^2)}}{{(1+x^2)^2}}={tex(slope)}\iff x^2={tex(x0**2)}"
        r"\ (\text{the other root in }x^2\text{ is negative}),\qquad x_0=\pm" + tex(x0) + ".",
    )
