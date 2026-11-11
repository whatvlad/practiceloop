"""Bounded function limits, joins, asymptotes and root certificates."""

from fractions import Fraction

import sympy as sp

from app.engine.answers.computational import (
    CategoryAnswer,
    ComputationalAnswer,
    FormulaAnswer,
    LimitAnswer,
    OrderedAnswer,
    PeriodicSetAnswer,
    RealSetAnswer,
)
from app.engine.blocks.analysis_one import X, bisect_exp
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._sequence_limits import finish
from app.math_input.contracts import Domain

SIDES = ("Left limit", "Right limit", "Two-sided limit")
JOINS = ("First parameter", "Second parameter")
ASYMPTOTES = ("Vertical locations", "Left line", "Right line")
DISCONTINUITY = ("removable", "jump", "infinite", "oscillatory")
DISCONTINUITY_LABELS = ("Location", "Left limit", "Right limit", "Classification")
ROOT = ("Approximation", "Error bound")
REAL_X: tuple[tuple[str, Domain], ...] = (("x", "real"),)
DNE = "does_not_exist"


def definition_pole(a: int, b: int, c: int) -> Built:
    expr = (a + b) / (X - c)
    return function_limit(
        expr,
        c,
        sp.oo,
        r"\text{Approach the pole from the right.}",
        rf"\text{{For }}M>0,\quad 0<x-{c}<\frac{{{a + b}}}{{M}}"
        rf"\implies \frac{{{a + b}}}{{x-{c}}}>M.",
        direction="+",
    )


def rational_cancellation(a: int, b: int, c: int) -> Built:
    expr = (a * X**2 - a * c**2) / ((X - c) * (X + b))
    simplified = a * (X + c) / (X + b)
    return function_limit(
        expr,
        c,
        sp.Rational(2 * a * c, b + c),
        r"\text{Factor the difference of squares and cancel away from the limit point.}",
        rf"f(x)={tex(simplified)}\quad(x\ne {c},-{b}),"
        rf"\qquad {tex(simplified)}\bigg|_{{x={c}}}=\frac{{{2 * a * c}}}{{{b + c}}}.",
    )


def radical_cancellation(a: int, b: int, c: int) -> Built:
    expr = (sp.sqrt(a * (X - c) + b**2) - b) / (X - c)
    return function_limit(
        expr,
        c,
        sp.Rational(a, 2 * b),
        r"\text{Multiply numerator and denominator by the conjugate.}",
        rf"f(x)=\frac{{{a}}}{{\sqrt{{{a}(x-{c})+{b * b}}}+{b}}}"
        rf"\quad(x\ne {c}),\qquad f(x)\to\frac{{{a}}}{{{2 * b}}}.",
    )


def exponential_dominance(a: int, b: int, c: int) -> Built:
    small, large = a + 1, a + b + 2
    expr = (small**X + c) / (large**X + b)
    return function_limit(
        expr,
        sp.oo,
        0,
        r"\text{Divide both numerator and denominator by the larger exponential.}",
        rf"f(x)=\frac{{({small}/{large})^x+{c}/{large}^x}}{{1+{b}/{large}^x}}\to0.",
    )


def absolute_jump(a: int, b: int, c: int) -> Built:
    expr = a * (X - c) / sp.Abs(X - c) + b
    return finish(
        rf"\text{{Give both one-sided limits and the two-sided limit at }}x={c}:\quad "
        rf"f(x)={tex(expr)}.",
        OrderedAnswer((LimitAnswer(b - a), LimitAnswer(b + a), LimitAnswer(DNE)), SIDES),
        r"\text{The ratio of a nonzero number to its absolute value is its sign.}",
        rf"f(x)={b}-{a}\quad(x<{c}),\qquad f(x)={b}+{a}\quad(x>{c})."
        r"\quad\text{The one-sided limits differ.}",
    )


def essential_exponential(a: int, b: int, c: int) -> Built:
    expr = b + sp.exp(a / (X - c))
    return finish(
        rf"\text{{Give both one-sided limits and the two-sided limit at }}x={c}:\quad "
        rf"f(x)={tex(expr)}.",
        OrderedAnswer((LimitAnswer(b), LimitAnswer(sp.oo), LimitAnswer(DNE)), SIDES),
        r"\text{The exponent has opposite infinite limits on the two sides.}",
        rf"\frac{{{a}}}{{x-{c}}}\to-\infty\text{{ from the left, and }}+\infty"
        rf"\text{{ from the right. Thus the exponential tends to }}0\text{{ and }}+\infty.",
    )


def squeeze_function(a: int, b: int, c: int) -> Built:
    t = X - c
    expr = sp.sqrt(t) * sp.sin(a / t**2) + b
    return function_limit(
        expr,
        c,
        b,
        r"\text{On the right, bound the sine by }-1\text{ and }1.",
        rf"{b}-\sqrt{{x-{c}}}\le f(x)\le{b}+\sqrt{{x-{c}}},"
        rf"\qquad\text{{both bounds tend to }}{b}.",
        direction="+",
    )


def infinitesimal_exp_sin(a: int, b: int, c: int) -> Built:
    t = X - c
    expr = (sp.exp(a * t) - 1) / sp.sin(b * t)
    return function_limit(
        expr,
        c,
        sp.Rational(a, b),
        r"\text{Use the standard equivalents }e^u-1\sim u\text{ and }\sin u\sim u.",
        rf"e^{{{a}(x-{c})}}-1\sim {a}(x-{c}),"
        rf"\qquad\sin({b}(x-{c}))\sim {b}(x-{c}).",
    )


def infinitesimal_log(a: int, b: int, c: int) -> Built:
    expr = sp.log(1 + a * (X - c)) / sp.atan(b * (X - c))
    return function_limit(
        expr,
        c,
        sp.Rational(a, b),
        r"\text{Both functions are defined in a neighborhood of the limit point.}",
        rf"\log(1+{a}(x-{c}))\sim {a}(x-{c}),"
        rf"\qquad\arctan({b}(x-{c}))\sim {b}(x-{c}).",
    )


def infinitesimal_power(a: int, b: int, c: int) -> Built:
    expr = (1 + a * (X - c)) ** (b / (X - c))
    return function_limit(
        expr,
        c,
        sp.exp(a * b),
        r"\text{The base is positive sufficiently close to the limit point. Take logs.}",
        rf"\log f(x)=\frac{{{b}\log(1+{a}(x-{c}))}}{{x-{c}}}\to {a * b}.",
    )


def asymptote_rational(a: int, b: int, c: int) -> Built:
    line = a * X + b
    expr = line + c / (X**2 - b**2)
    return finish(
        r"\text{Give all vertical asymptote locations as a set and both asymptotic line}"
        r"\text{ expressions at }-\infty\text{ and }+\infty:\quad f(x)=" + tex(expr),
        OrderedAnswer(
            (
                RealSetAnswer(sp.FiniteSet(-b, b)),
                FormulaAnswer(line, REAL_X),
                FormulaAnswer(line, REAL_X),
            ),
            ASYMPTOTES,
        ),
        r"\text{The remainder has two simple poles and tends to zero at both ends.}",
        rf"f(x)-({tex(line)})=\frac{{{c}}}{{(x+{b})(x-{b})}}\to0"
        rf"\quad(x\to\pm\infty),\qquad x=\pm {b}\text{{ are simple poles}}.",
    )


def asymptote_inverse_trig(a: int, b: int, c: int) -> Built:
    expr = a * X + b * sp.atan(X - c)
    return finish(
        r"\text{Give all vertical asymptote locations as a set and both asymptotic line}"
        r"\text{ expressions at }-\infty\text{ and }+\infty:\quad f(x)=" + tex(expr),
        OrderedAnswer(
            (
                RealSetAnswer(sp.S.EmptySet),
                FormulaAnswer(a * X - b * sp.pi / 2, REAL_X),
                FormulaAnswer(a * X + b * sp.pi / 2, REAL_X),
            ),
            ASYMPTOTES,
        ),
        r"\text{There are no finite poles because the function is continuous everywhere.}",
        rf"f(x)-{a}x={b}\arctan(x-{c})\to\pm\frac{{{b}\pi}}{{2}}"
        r"\quad(x\to\pm\infty\text{ respectively}).",
    )


def continuity_sine(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Find the parameters }p,q\text{ for continuity on }\mathbb R:\quad "
        rf"f(x)=\begin{{cases}}{a},&x<0\\p+q\sin({b}x),&0\le x\le \pi/{2 * b}\\"
        rf"{a + c},&x>\pi/{2 * b}\end{{cases}}.",
        OrderedAnswer((FormulaAnswer(a), FormulaAnswer(c)), JOINS),
        r"\text{Each branch is continuous on its interval. Match values at both joins.}",
        rf"p+q\sin 0={a},\qquad p+q\sin(\pi/2)={a + c}"
        rf"\quad\Longrightarrow\quad p={a},\ q={c}.",
    )


def continuity_reciprocal(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Find the parameter }p\text{ for continuity on }\mathbb R:\quad "
        rf"f(x)=\begin{{cases}}{a}+p/x,&x<-{b}\\{c}-x,&x\ge-{b}\end{{cases}}.",
        FormulaAnswer(b * (a - c - b)),
        r"\text{The pole at zero is outside the reciprocal branch. Match at the join.}",
        rf"{a}-\frac{{p}}{{{b}}}={c + b}\quad\Longrightarrow\quad p={b * (a - c - b)}.",
    )


def discontinuity_arctan(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Give the discontinuity location, both one-sided limits and its type:}\quad "
        rf"f(x)=\begin{{cases}}{b}+{a}\arctan\!\left(\frac1{{x-{c}}}\right),&x\ne {c}\\"
        rf"{b},&x={c}\end{{cases}}.",
        OrderedAnswer(
            (
                FormulaAnswer(c),
                LimitAnswer(b - a * sp.pi / 2),
                LimitAnswer(b + a * sp.pi / 2),
                CategoryAnswer("jump", DISCONTINUITY),
            ),
            DISCONTINUITY_LABELS,
        ),
        r"\text{The formula is continuous away from the join. At the join, use the arctan limits.}",
        rf"\frac1{{x-{c}}}\to\pm\infty\quad\Longrightarrow\quad "
        rf"f(x)\to {b}\pm\frac{{{a}\pi}}{{2}}"
        r"\quad\text{from the right and left respectively}.",
    )


def discontinuity_oscillatory(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Give the discontinuity location, both one-sided limits and its type:}\quad "
        rf"f(x)=\begin{{cases}}{b}+{a}\cos\!\left(\frac{{{c}}}{{x-{b}}}\right),&x\ne {b}\\"
        rf"{b},&x={b}\end{{cases}}.",
        OrderedAnswer(
            (
                FormulaAnswer(b),
                LimitAnswer(DNE),
                LimitAnswer(DNE),
                CategoryAnswer("oscillatory", DISCONTINUITY),
            ),
            DISCONTINUITY_LABELS,
        ),
        r"\text{The function is continuous off the join. Approach along two sequences per side.}",
        rf"x_k={b}\pm\frac{{{c}}}{{2k\pi}},\quad y_k={b}\pm\frac{{{c}}}{{(2k+1)\pi}},"
        rf"\qquad f(x_k)={b + a},\ f(y_k)={b - a}.",
    )


def certified_root(a: int, b: int, c: int) -> Built:
    midpoint, intervals = bisect_exp(a)
    lo, hi = intervals[-1]
    bound = (hi - lo) / 2
    shifted = b * midpoint + c
    error = b * bound
    return finish(
        r"\text{Bisect the unique root bracket six times. Give the final midpoint}"
        r"\text{ and half-width as exact fractions:}\quad "
        rf"\exp((x-{c})/{b})+((x-{c})/{b})^2={a + 1},"
        rf"\quad x\in[{c},{c + a * b}].",
        OrderedAnswer(
            (FormulaAnswer(sp.Rational(shifted)), FormulaAnswer(sp.Rational(error))), ROOT
        ),
        rf"\text{{Set }}t=(x-{c})/{b}."
        r"\quad e^t+t^2\text{ is strictly increasing on the bracket and crosses the target.}",
        r"\text{Taylor enclosures certify the sign at each midpoint:}\quad "
        + r"\ \to\ ".join(bracket(left, right) for left, right in intervals)
        + rf"\quad\text{{in }}t,\qquad x={c}+{b}t.",
    )


def bracket(left: Fraction, right: Fraction) -> str:
    return r"\left[" + tex(sp.Rational(left)) + "," + tex(sp.Rational(right)) + r"\right]"


def function_limit(
    expr: sp.Expr | str,
    at: object,
    expected: object,
    method: str,
    derivation: str,
    *,
    direction: str = "",
) -> Built:
    """Ask for a limit; a string is a ready display, already grouped where needed."""
    side = "^" + direction if direction else ""
    shown = expr if isinstance(expr, str) else tex(expr)
    return finish(
        r"\text{Evaluate:}\quad \lim_{x\to " + tex(at) + side + "}" + shown,
        LimitAnswer(expected),
        method,
        derivation,
    )


def two_sided_absolute(a: int, b: int, c: int) -> Built:
    t = X - c
    expr = a * t**2 / sp.Abs(t) + b
    return finish(
        rf"\text{{Give both one-sided limits and the two-sided limit at }}x={c}:\quad "
        rf"f(x)={tex(expr)}.",
        OrderedAnswer((LimitAnswer(b), LimitAnswer(b), LimitAnswer(b)), SIDES),
        r"\text{For a nonzero }t,\ t^2/|t|=|t|.",
        rf"f(x)={a}|x-{c}|+{b}\quad(x\ne {c}),\qquad \lim_{{x\to{c}}}f(x)={b}.",
    )


def squeeze_at_infinity(a: int, b: int, c: int) -> Built:
    return function_limit(
        (a + b * sp.cos(c * X)) / X**2,
        sp.oo,
        0,
        r"\text{The numerator stays between two constants. The denominator grows.}",
        rf"\frac{{{a - b}}}{{x^2}}\le f(x)\le \frac{{{a + b}}}{{x^2}}\quad(x\ne0)."
        r"\quad\text{Both outer terms tend to zero.}",
    )


def infinitesimal_inverse_trig(a: int, b: int, c: int) -> Built:
    t = X - c
    return function_limit(
        sp.asin(a * t) / sp.atan(b * t),
        c,
        sp.Rational(a, b),
        r"\text{The derivatives of arcsine and arctangent at zero both equal }1.",
        rf"\arcsin({a}(x-{c}))\sim{a}(x-{c}),"
        rf"\qquad\arctan({b}(x-{c}))\sim{b}(x-{c}).",
    )


def horizontal_asymptote(a: int, b: int, c: int) -> Built:
    e = sp.exp(c * X)
    right = a + b
    expr = (right * e + b) / (e + 1)
    return finish(
        r"\text{Give all vertical asymptote locations as a set and both asymptotic line}"
        r"\text{ expressions at }-\infty\text{ and }+\infty:\quad f(x)=" + tex(expr),
        OrderedAnswer(
            (
                RealSetAnswer(sp.S.EmptySet),
                FormulaAnswer(b, REAL_X),
                FormulaAnswer(right, REAL_X),
            ),
            ASYMPTOTES,
        ),
        r"\text{The denominator is strictly positive, so there is no vertical asymptote.}",
        rf"\lim_{{x\to-\infty}}e^{{{c}x}}=0\ \Rightarrow\ f(x)\to{b}."
        rf"\quad f(x)=\frac{{{right}+{b}e^{{-{c}x}}}}{{1+e^{{-{c}x}}}}\to{right}"
        r"\quad(x\to+\infty).",
    )


def discontinuity_removable(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Give the discontinuity location, both one-sided limits and its type:}\quad "
        rf"f(x)=\begin{{cases}}"
        rf"\frac{{{a}(x^2-{c * c})}}{{x-{c}}},&x\ne{c}\\"
        rf"{2 * a * c + b},&x={c}\end{{cases}}.",
        OrderedAnswer(
            (
                FormulaAnswer(c),
                LimitAnswer(2 * a * c),
                LimitAnswer(2 * a * c),
                CategoryAnswer("removable", DISCONTINUITY),
            ),
            DISCONTINUITY_LABELS,
        ),
        r"\text{Cancel the factor }x-c\text{ away from the join.}",
        rf"f(x)={a}(x+{c})\quad(x\ne{c}),\qquad "
        rf"\lim_{{x\to{c}}}f(x)={2 * a * c}\ne f({c})={2 * a * c + b}.",
    )


def discontinuity_infinite(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Give the discontinuity location, both one-sided limits and its type:}\quad "
        rf"f(x)=\begin{{cases}}{a}/(x-{c})^2+{b},&x\ne{c}\\"
        rf"{b},&x={c}\end{{cases}}.",
        OrderedAnswer(
            (
                FormulaAnswer(c),
                LimitAnswer(sp.oo),
                LimitAnswer(sp.oo),
                CategoryAnswer("infinite", DISCONTINUITY),
            ),
            DISCONTINUITY_LABELS,
        ),
        r"\text{The denominator tends to zero through positive values on each side.}",
        rf"f(x)-{b}=\frac{{{a}}}{{(x-{c})^2}}\to+\infty"
        r"\quad\text{from both sides. There are no other singularities.}",
    )


def cubic_brackets(a: int, b: int) -> list[tuple[Fraction, Fraction]]:
    lo, hi = Fraction(0), Fraction(a + 1)
    brackets = []
    for _ in range(5):
        mid = (lo + hi) / 2
        residual = mid**3 + (b + 1) * mid - a
        if residual == 0:
            lo = hi = mid
        elif residual < 0:
            lo = mid
        else:
            hi = mid
        brackets.append((lo, hi))
    return brackets


def certified_cubic(a: int, b: int, c: int) -> Built:
    brackets = cubic_brackets(a, b)
    lo, hi = brackets[-1]
    upper_value = (a + 1) ** 3 + (b + 1) * (a + 1) - a
    midpoint, error = c + (lo + hi) / 2, (hi - lo) / 2
    return finish(
        r"\text{Bisect the unique root bracket five times. Give the final midpoint and half-width.}"
        r"\text{ If a midpoint is an exact root, report it with zero error:}\quad "
        rf"(x-{c})^3+{b + 1}(x-{c})-{a}=0,\qquad x\in[{c},{c + a + 1}].",
        OrderedAnswer(
            (FormulaAnswer(sp.Rational(midpoint)), FormulaAnswer(sp.Rational(error))), ROOT
        ),
        rf"\text{{In }}t=x-{c},\quad g'(t)=3t^2+{b + 1}>0,\quad g(0)=-{a},"
        rf"\quad g({a + 1})={upper_value}>0.",
        r"\text{The signs bracket the unique root at each step:}\quad "
        + r"\ \to\ ".join(bracket(left + c, right + c) for left, right in brackets),
    )


def radical_asymptote(a: int, b: int, c: int) -> Built:
    expr = c + a * (X - b) / sp.sqrt(X**2 - b**2)
    return finish(
        r"\text{Give all vertical asymptote locations as a set and both asymptotic line}"
        r"\text{ expressions at }-\infty\text{ and }+\infty:\quad f(x)=" + tex(expr),
        OrderedAnswer(
            (
                RealSetAnswer(sp.FiniteSet(-b)),
                FormulaAnswer(c - a, REAL_X),
                FormulaAnswer(c + a, REAL_X),
            ),
            ASYMPTOTES,
        ),
        rf"\text{{The real domain is }}(-\infty,-{b})\cup({b},\infty)."
        rf"\quad f(x)\to-\infty\quad(x\to-{b}^-).",
        rf"x\to{b}^+:\quad \frac{{x-{b}}}{{\sqrt{{(x-{b})(x+{b})}}}}"
        rf"=\sqrt{{\frac{{x-{b}}}{{x+{b}}}}}\to0."
        r"\quad\text{At infinity divide by }|x|\text{ to obtain the two horizontal lines.}",
    )


def high_order_pole(a: int, b: int, c: int) -> Built:
    power = 2 * (c + 1)
    line = a * X - c
    return finish(
        r"\text{Give all vertical asymptote locations as a set and both asymptotic line}"
        r"\text{ expressions at }-\infty\text{ and }+\infty:\quad f(x)="
        + tex(line + (a + b) / (X - b) ** power),
        OrderedAnswer(
            (
                RealSetAnswer(sp.FiniteSet(b)),
                FormulaAnswer(line, REAL_X),
                FormulaAnswer(line, REAL_X),
            ),
            ASYMPTOTES,
        ),
        rf"\text{{The positive remainder diverges on both sides of }}x={b}"
        rf"\text{{ because the pole has even order }}{power}.",
        rf"f(x)-({tex(line)})=\frac{{{a + b}}}{{(x-{b})^{{{power}}}}}\to0"
        r"\quad(x\to\pm\infty).",
    )


def conjugate_at_infinity(a: int, b: int, c: int) -> Built:
    expr = sp.sqrt(X**2 + a * X + c) - X + b
    return function_limit(
        expr,
        sp.oo,
        b + sp.Rational(a, 2),
        r"\text{For large positive }x\text{ the radicand is positive. Rationalize the difference.}",
        rf"f(x)={b}+\frac{{{a}+{c}/x}}{{\sqrt{{1+{a}/x+{c}/x^2}}+1}}"
        rf"\to{b}+\frac{{{a}}}{{2}}.",
    )


def removable_trigonometric(a: int, b: int, c: int) -> Built:
    t = X - c
    expr = a * sp.sin(b * t) ** 2 / (1 - sp.cos(b * t))
    return function_limit(
        expr,
        c,
        2 * a,
        r"\text{Factor }\sin^2 u=1-\cos^2 u\text{ and cancel at nearby nonzero }u.",
        rf"f(x)={a}(1+\cos({b}(x-{c})))\to {2 * a}.",
    )


def power_difference(a: int, b: int, c: int) -> Built:
    left, right = sp.Rational(a, 2), sp.Rational(b + 10, 2)
    t = X / c
    return function_limit(
        (t**left - t**right) / (X - c),
        c,
        (left - right) / c,
        r"\text{Rescale the variable. At }t=1\text{ both powers equal }1.",
        rf"\frac1{{{c}}}\left(\frac{{t^{{{tex(left)}}}-1}}{{t-1}}"
        rf"-\frac{{t^{{{tex(right)}}}-1}}{{t-1}}\right)"
        rf"\to\frac{{{tex(left)}-{tex(right)}}}{{{c}}}.",
    )


def finite_heine_limit(a: int, b: int, c: int) -> Built:
    return function_limit(
        (X - b) ** 3 + a,
        b + c,
        a + c**3,
        r"\text{Take any sequence }x_n\to b+c\text{ with }x_n\ne b+c.",
        rf"x_n-{b}\to {c}\quad\Longrightarrow\quad (x_n-{b})^3+{a}\to {c**3 + a}."
        r"\quad\text{By the sequential criterion this is the function limit.}",
    )


def heine_at_infinity(a: int, b: int, c: int) -> Built:
    return function_limit(
        (a * X + b) / (X * X + c),
        -sp.oo,
        0,
        r"\text{Take any sequence }x_n\to-\infty\text{ and divide by }x_n^2\text{ eventually.}",
        rf"f(x_n)=\frac{{{a}/x_n+{b}/x_n^2}}{{1+{c}/x_n^2}}\to0."
        r"\quad\text{Apply the sequential criterion.}",
    )


UNRESTRICTED_JOIN = ("Constrained parameter", "Other parameter values")
TWO_LOCATIONS = ("First discontinuity", "Second discontinuity")


def continuity_free_parameter(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Find the value of }p\text{ and the set of }q\text{ for continuity on }\mathbb R:"
        rf"\quad f(x)=\begin{{cases}}px^2+{c},&x<-{a}\\"
        rf"{b}x+{c},&-{a}\le x\le0\\x^3+qx+{c},&x>0\end{{cases}}.",
        OrderedAnswer(
            (FormulaAnswer(-sp.Rational(b, a)), RealSetAnswer(sp.S.Reals)),
            UNRESTRICTED_JOIN,
        ),
        r"\text{At zero the middle and right branches agree for every }q.",
        rf"x=-{a}:\quad {a * a}p+{c}={c}-{a * b}"
        rf"\quad\Longrightarrow\quad p=-\frac{{{b}}}{{{a}}},\quad q\in\mathbb R.",
    )


def discontinuity_pole_and_hole(a: int, b: int, c: int) -> Built:
    hole_limit = sp.Rational(c, a + b)
    return finish(
        r"\text{Give the two discontinuities in increasing order. For each give its location,}"
        r"\text{ both one-sided limits and type:}\quad "
        rf"f(x)=\begin{{cases}}\frac{{{c}(x-{b})}}{{(x+{a})(x-{b})}},"
        rf"&x\notin\{{-{a},{b}\}}\\0,&x\in\{{-{a},{b}\}}\end{{cases}}.",
        OrderedAnswer(
            (
                OrderedAnswer(
                    (
                        FormulaAnswer(-a),
                        LimitAnswer(-sp.oo),
                        LimitAnswer(sp.oo),
                        CategoryAnswer("infinite", DISCONTINUITY),
                    ),
                    DISCONTINUITY_LABELS,
                ),
                OrderedAnswer(
                    (
                        FormulaAnswer(b),
                        LimitAnswer(hole_limit),
                        LimitAnswer(hole_limit),
                        CategoryAnswer("removable", DISCONTINUITY),
                    ),
                    DISCONTINUITY_LABELS,
                ),
            ),
            TWO_LOCATIONS,
        ),
        rf"\text{{Away from the two assigned points, }}f(x)=\frac{{{c}}}{{x+{a}}}.",
        rf"x=-{a}:\quad L_-=-\infty,\ L_+=+\infty;\qquad "
        rf"x={b}:\quad L_-=L_+=\frac{{{c}}}{{{a + b}}}\ne f({b})=0.",
    )


def unique_log_exponential_root(a: int, b: int, c: int) -> Built:
    base = b + 1
    coefficient = c + 1
    root = base ** (1 + a % 2)
    t = X / root
    expr = coefficient * X + sp.log(X) / sp.log(base) + sp.exp(t - 1)
    target = coefficient * root + 2 + a % 2
    return finish(
        r"\text{Find the unique positive solution:}\quad " + tex(expr) + "=" + tex(target) + ".",
        FormulaAnswer(root),
        rf"\text{{All three terms are strictly increasing on }}(0,\infty)"
        rf"\text{{ since the logarithm has base }}{base}>1.",
        rf"x={root}:\quad {coefficient}x={coefficient * root},\quad "
        rf"\log_{{{base}}}x={1 + a % 2},\quad e^{{x/{root}-1}}=1."
        rf"\quad\text{{Their sum is }}{target}.",
    )


DOMAIN_ASYMPTOTES = ("Real domain", *ASYMPTOTES)


def rational_pole_and_domain(a: int, b: int, c: int) -> Built:
    line = a * X - c
    expr = sp.together(line + b / (X - c))
    return finish(
        r"\text{Give the real domain, all vertical asymptote locations as a set, and both lines}"
        r"\text{ at }-\infty\text{ and }+\infty:\quad f(x)=" + tex(expr),
        OrderedAnswer(
            (
                RealSetAnswer(sp.S.Reals - sp.FiniteSet(c)),
                RealSetAnswer(sp.FiniteSet(c)),
                FormulaAnswer(line, REAL_X),
                FormulaAnswer(line, REAL_X),
            ),
            DOMAIN_ASYMPTOTES,
        ),
        rf"\text{{At }}x={c}\text{{ the denominator vanishes but the numerator is }}{b}\ne0.",
        rf"f(x)={tex(line)}+\frac{{{b}}}{{x-{c}}}\quad(x\ne{c})."
        r"\quad\text{The remainder diverges at the pole and vanishes at both infinities.}",
    )


def exponential_pole(a: int, b: int, c: int) -> Built:
    base = a + 1
    expr = b * base**X / (base**X - base**c)
    return finish(
        r"\text{Give all vertical asymptote locations as a set and both asymptotic line}"
        r"\text{ expressions at }-\infty\text{ and }+\infty:\quad f(x)=" + tex(expr),
        OrderedAnswer(
            (
                RealSetAnswer(sp.FiniteSet(c)),
                FormulaAnswer(0, REAL_X),
                FormulaAnswer(b, REAL_X),
            ),
            ASYMPTOTES,
        ),
        rf"\text{{The denominator is strictly increasing with a simple zero at }}x={c}."
        r"\quad\text{The numerator there is nonzero.}",
        rf"x\to-\infty:\quad {base}^x\to0,\ f(x)\to0."
        rf"\quad x\to+\infty:\quad f(x)=\frac{{{b}}}{{1-{base}^{{{c}-x}}}}\to {b}.",
    )


# #258: the remaining function-limit source references of #236.


def scaled(k: int) -> str:
    return "" if k == 1 else str(k)


def rational_substitution(a: int, b: int, c: int) -> Built:
    expr = (X**2 - a) / (X**2 - b * X + b * b)
    value = sp.Rational(c * c - a, c * c - b * c + b * b)
    return function_limit(
        expr,
        c,
        value,
        r"\text{The denominator }x^2-" + scaled(b) + rf"x+{b * b}"
        r"\text{ has negative discriminant, so the quotient is continuous. Substitute.}",
        rf"\frac{{{c}^2-{a}}}{{{c}^2-{b}\cdot{c}+{b * b}}}={tex(value)}.",
    )


def radical_quotient_zero(a: int, b: int, c: int) -> Built:
    value = sp.Rational(b, c)
    return function_limit(
        rf"\frac{{{scaled(a)}x+{b}\sqrt{{x}}}}{{{scaled(c)}\sqrt{{x}}}}",
        0,
        value,
        r"\text{For }x>0\text{ cancel the common factor }\sqrt{x}.",
        rf"f(x)=\frac{{{scaled(a)}\sqrt{{x}}+{b}}}{{{c}}}\to{tex(value)}.",
        direction="+",
    )


def power_difference_quotient(a: int, b: int, c: int) -> Built:
    low, high = a + 1, a + b + 1
    expr = (X**low - c**low) / (X**high - c**high)
    value = sp.Rational(low, high * c ** (high - low))
    return function_limit(
        expr,
        c,
        value,
        rf"\text{{Factor }}x^k-{c}^k=(x-{c})(x^{{k-1}}+{c}x^{{k-2}}+\dots+{c}^{{k-1}})"
        r"\text{ in both and cancel }x-" + str(c) + ".",
        rf"f(x)=\frac{{x^{{{low - 1}}}+\dots+{c}^{{{low - 1}}}}}"
        rf"{{x^{{{high - 1}}}+\dots+{c}^{{{high - 1}}}}}"
        rf"\to\frac{{{low}\cdot{c}^{{{low - 1}}}}}{{{high}\cdot{c}^{{{high - 1}}}}}={tex(value)}.",
    )


def leading_power_quotient(a: int, b: int, c: int) -> Built:
    power = b + 1
    expr = (a * X**3 + 1) ** power / ((X + 1) ** (power + 2) * (c * X**2 + 1) ** (power - 1))
    value = sp.Rational(a**power, c ** (power - 1))
    return function_limit(
        expr,
        sp.oo,
        value,
        rf"\text{{Both sides have degree }}{3 * power}."
        r"\text{ Divide every factor by its power of }x.",
        rf"f(x)=\frac{{({a}+x^{{-3}})^{{{power}}}}}"
        rf"{{(1+x^{{-1}})^{{{power + 2}}}({c}+x^{{-2}})^{{{power - 1}}}}}"
        rf"\to\frac{{{a}^{{{power}}}}}{{{c}^{{{power - 1}}}}}={tex(value)}.",
    )


def conjugate_minus_infinity(a: int, b: int, c: int) -> Built:
    slope = b - 3
    radicand = a * a * X**2 + slope * X + c
    value = sp.Rational(-slope, 2 * a)
    return function_limit(
        rf"\left(\sqrt{{{tex(radicand)}}}+{scaled(a)}x\right)",
        -sp.oo,
        value,
        r"\text{Rationalize. For }x<0,\ \sqrt{x^2}=-x.",
        rf"f(x)=\frac{{{tex(slope * X + c)}}}{{\sqrt{{{tex(radicand)}}}-{scaled(a)}x}}"
        rf"=\frac{{{tex(slope + c / X)}}}{{-\sqrt{{{tex(a * a + slope / X + c / X**2)}}}-{a}}}"
        rf"\to{tex(value)}.",
    )


def tangent_ratio(a: int, b: int, c: int) -> Built:
    tan2 = sp.tan(X) ** 2
    value = sp.Rational(a, c)
    return function_limit(
        (a * tan2 + b) / (c * tan2 + b + c),
        sp.pi / 2,
        value,
        r"\text{As }x\to\pi/2^-,\ \tan^2x\to\infty.\text{ Divide by }\tan^2x.",
        rf"f(x)=\frac{{{a}+{b}/\tan^2x}}{{{c}+{b + c}/\tan^2x}}\to{tex(value)}.",
        direction="-",
    )


def radical_linear_ratio(a: int, b: int, c: int) -> Built:
    value = sp.Rational(a, c)
    radicand = tex(a * a * X**2 + X)
    return function_limit(
        rf"\frac{{\sqrt{{{radicand}}}+{b}}}{{{tex(c * X + 1)}}}",
        sp.oo,
        value,
        r"\text{Divide the numerator and denominator by }x>0.",
        rf"f(x)=\frac{{\sqrt{{{a * a}+1/x}}+{b}/x}}{{{c}+1/x}}\to{tex(value)}.",
    )


def cancelling_reciprocals(a: int, b: int, c: int) -> Built:
    power = b + 1
    value = sp.Rational(c * (1 - power), 2)
    return function_limit(
        rf"{scaled(c)}\left(\frac{{1}}{{1-x}}-\frac{{{power}}}{{1-x^{{{power}}}}}\right)",
        1,
        value,
        rf"\text{{Use the common denominator }}1-x^{{{power}}}"
        rf"=(1-x)(1+x+\dots+x^{{{power - 1}}}).",
        rf"\frac{{1}}{{1-x}}-\frac{{{power}}}{{1-x^{{{power}}}}}"
        rf"=\frac{{\sum_{{k=0}}^{{{power - 1}}}(x^k-1)}}{{1-x^{{{power}}}}}"
        rf"=-\frac{{\sum_{{k=1}}^{{{power - 1}}}(1+x+\dots+x^{{k-1}})}}"
        rf"{{1+x+\dots+x^{{{power - 1}}}}}\to-\frac{{1+2+\dots+{power - 1}}}{{{power}}}"
        rf"=-\frac{{{power - 1}}}{{2}}.",
    )


def bounded_inverse_trig(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Give both one-sided limits and the two-sided limit at }x=0:\quad "
        rf"f(x)={scaled(a)}x\arctan\frac{{{b}}}{{x}}+{c}.",
        OrderedAnswer((LimitAnswer(c), LimitAnswer(c), LimitAnswer(c)), SIDES),
        r"\text{The arctangent is bounded: }|\arctan u|<\pi/2.",
        rf"|f(x)-{c}|\le\frac{{{a}\pi}}{{2}}|x|\to0\text{{ from both sides,}}"
        rf"\quad\arctan\frac{{{b}}}{{x}}\to\mp\frac{{\pi}}{{2}}\text{{ only changes the sign}}.",
    )


def squeeze_arctan(a: int, b: int, c: int) -> Built:
    return function_limit(
        rf"\left({scaled(a)}x^2\arctan\frac{{{b}}}{{x}}+{c}\right)",
        0,
        c,
        r"\text{Squeeze with }|\arctan u|<\pi/2.",
        rf"{c}-\frac{{{a}\pi}}{{2}}x^2\le f(x)\le{c}+\frac{{{a}\pi}}{{2}}x^2,"
        rf"\qquad\text{{both bounds tend to }}{c}.",
    )


def sine_product_square(a: int, b: int, c: int) -> Built:
    value = sp.Rational(a * b, c)
    return function_limit(
        sp.sin(a * X) * sp.sin(b * X) / (c * X**2),
        0,
        value,
        r"\text{Use }\sin u\sim u\text{ for each factor.}",
        rf"f(x)=\frac{{{a * b}}}{{{c}}}\cdot\frac{{\sin {scaled(a)}x}}{{{scaled(a)}x}}"
        rf"\cdot\frac{{\sin {scaled(b)}x}}{{{scaled(b)}x}}\to{tex(value)}.",
    )


def sine_radical(a: int, b: int, c: int) -> Built:
    point = c * c
    return function_limit(
        rf"\frac{{\sin\left({scaled(a)}(x-{point})\right)}}{{\sqrt{{x}}-{c}}}",
        point,
        2 * a * c,
        rf"\text{{Write }}x-{point}=(\sqrt{{x}}-{c})(\sqrt{{x}}+{c})"
        r"\text{ and use }\sin u\sim u.",
        rf"f(x)=\frac{{\sin\left({scaled(a)}(x-{point})\right)}}{{{scaled(a)}(x-{point})}}"
        rf"\cdot{scaled(a)}(\sqrt{{x}}+{c})\to{a}\cdot{2 * c}={2 * a * c}.",
    )


def arctan_at_infinity(a: int, b: int, c: int) -> Built:
    power = 1 + c % 2
    expected = a * b if power == 1 else sp.oo
    shown = "x" if power == 1 else "x^2"
    tail = rf"={a * b}" if power == 1 else rf"={a * b}x\to\infty"
    return function_limit(
        rf"{scaled(a)}{shown}\arctan\frac{{{b}}}{{x}}",
        sp.oo,
        expected,
        r"\text{Use }\arctan u\sim u\text{ with }u=" + rf"{b}/x\to0^+.",
        rf"f(x)={scaled(a)}{shown}\cdot\frac{{{b}}}{{x}}\cdot\frac{{\arctan({b}/x)}}{{{b}/x}},"
        rf"\qquad {scaled(a)}{shown}\cdot\frac{{{b}}}{{x}}{tail}.",
    )


def cosine_ratio_half_pi(a: int, b: int, c: int) -> Built:
    top, bottom = 2 * a - 1, 2 * b - 1
    if top == bottom:
        bottom += 2
    sign = (-1) ** ((top - bottom) // 2)
    value = sp.Rational(sign * c * top, bottom)
    t = sp.Symbol("t")
    return function_limit(
        c * sp.cos(top * X) / sp.cos(bottom * X),
        sp.pi / 2,
        value,
        r"\text{Put }x=\pi/2+t.\text{ For odd }k,\ \cos(k\pi/2+kt)=-\sin(k\pi/2)\sin kt.",
        rf"f=\frac{{{scaled(c)}\sin({top}\pi/2)\,{tex(sp.sin(top * t))}}}"
        rf"{{\sin({bottom}\pi/2)\,{tex(sp.sin(bottom * t))}}}"
        rf"\to\frac{{{c}\cdot({(-1) ** ((top - 1) // 2)})\cdot{top}}}"
        rf"{{({(-1) ** ((bottom - 1) // 2)})\cdot{bottom}}}={tex(value)}.",
    )


def log_cube_root(a: int, b: int, c: int) -> Built:
    power = 1 + c % 3
    denominator = {1: r"\sqrt[3]{x}", 2: r"\sqrt[3]{x^2}", 3: "x"}[power]
    expected = sp.Rational(a, b) if power == 1 else sp.oo
    tail = (
        rf"\to\frac{{{a}}}{{{b}}}"
        if power == 1
        else rf"\sim\frac{{{a}}}{{{b}}}x^{{-{power - 1}/3}}\to+\infty"
    )
    return function_limit(
        rf"\frac{{\log\left(1+{scaled(a)}\sqrt[3]{{x}}\right)}}{{{scaled(b)}{denominator}}}",
        0,
        expected,
        r"\text{Use }\log(1+u)\sim u\text{ with }u=" + scaled(a) + r"\sqrt[3]{x}\to0^+.",
        rf"f(x)=\frac{{\log(1+u)}}{{u}}\cdot\frac{{{scaled(a)}\sqrt[3]{{x}}}}"
        rf"{{{scaled(b)}{denominator}}}{tail}.",
        direction="+",
    )


def log_near_one(a: int, b: int, c: int) -> Built:
    expr = sp.log(a * X**2 - a * c * c + 1) / (b * (X + c))
    value = sp.Rational(-2 * a * c, b)
    return function_limit(
        expr,
        -c,
        value,
        rf"\text{{Use }}\log(1+u)\sim u\text{{ with }}u={scaled(a)}(x^2-{c * c})\to0.",
        rf"f(x)=\frac{{\log(1+u)}}{{u}}\cdot\frac{{{scaled(a)}(x-{c})(x+{c})}}{{{b}(x+{c})}}"
        rf"\to\frac{{{a}\cdot(-{2 * c})}}{{{b}}}={tex(value)}.",
    )


def tangent_power(a: int, b: int, c: int) -> Built:
    expr = (1 + a * sp.tan(b * X)) ** sp.cot(c * X)
    value = sp.exp(sp.Rational(a * b, c))
    return function_limit(
        expr,
        0,
        value,
        r"\text{Take logarithms and use }\log(1+u)\sim u,\ \tan u\sim u.",
        rf"\log f(x)=\frac{{\log\left(1+{scaled(a)}\tan {scaled(b)}x\right)}}{{\tan {scaled(c)}x}}"
        rf"\sim\frac{{{a * b}x}}{{{c}x}}\to{tex(sp.Rational(a * b, c))}.",
    )


def root_difference(a: int, b: int, c: int) -> Built:
    first, second = c + 1, c + 2
    value = sp.Rational(a, first) + sp.Rational(b, second)
    return function_limit(
        rf"\frac{{\sqrt[{first}]{{1+{scaled(a)}x}}-\sqrt[{second}]{{1-{scaled(b)}x}}}}{{x}}",
        0,
        value,
        r"\text{Use }(1+u)^r-1\sim ru\text{ on each root after adding and subtracting }1.",
        rf"\frac{{(1+{a}x)^{{1/{first}}}-1}}{{x}}\to\frac{{{a}}}{{{first}}},\qquad"
        rf"\frac{{1-(1-{b}x)^{{1/{second}}}}}{{x}}\to\frac{{{b}}}{{{second}}},"
        rf"\qquad f(x)\to{tex(value)}.",
    )


def sine_quadratic_ratio(a: int, b: int, c: int) -> Built:
    denominator = sp.expand((X - c) * (X - c + a))
    value = sp.Rational(2 * b * c, a)
    return function_limit(
        rf"\frac{{\sin\left({tex(b * X**2 - b * c * c)}\right)}}{{{tex(denominator)}}}",
        c,
        value,
        r"\text{Use }\sin u\sim u\text{ and factor both polynomials.}",
        rf"f(x)\sim\frac{{{scaled(b)}(x-{c})(x+{c})}}{{(x-{c})\,({tex(X - c + a)})}}"
        rf"=\frac{{{scaled(b)}(x+{c})}}{{{tex(X - c + a)}}}\to{tex(value)}.",
    )


def log_difference_infinity(a: int, b: int, c: int) -> Built:
    value = sp.Rational(a * b, c)
    return function_limit(
        rf"{scaled(a)}x\left(\log({tex(c * X + b)})-\log({tex(c * X)})\right)",
        sp.oo,
        value,
        r"\text{Combine the logarithms and use }\log(1+u)\sim u.",
        rf"f(x)={scaled(a)}x\log\left(1+\frac{{{b}}}{{{scaled(c)}x}}\right)"
        rf"\sim{scaled(a)}x\cdot\frac{{{b}}}{{{scaled(c)}x}}\to{tex(value)}.",
    )


def log_quadratic_at_point(a: int, b: int, c: int) -> Built:
    shift = c * c - b * c - 1
    expr = sp.log(X**2 - b * X - shift) / (X - c)
    return function_limit(
        expr,
        c,
        2 * c - b,
        rf"\text{{The argument equals }}1+(x-{c})({tex(X + c - b)})."
        r"\text{ Use }\log(1+u)\sim u.",
        rf"f(x)\sim\frac{{(x-{c})({tex(X + c - b)})}}{{x-{c}}}\to{2 * c - b}.",
    )


def sine_power_product(a: int, b: int, c: int) -> Built:
    expr = sp.sin(a * X**5) / (sp.sin(b * X**2) * sp.sin(c * X**3))
    value = sp.Rational(a, b * c)
    return function_limit(
        expr,
        0,
        value,
        r"\text{Replace each sine by its argument, }\sin u\sim u.",
        rf"f(x)\sim\frac{{{scaled(a)}x^5}}{{{scaled(b)}x^2\cdot{scaled(c)}x^3}}={tex(value)}.",
    )


# #259: asymptotes, parameter joins and discontinuities still pending for #236.

ENDS = ("Vertical locations", "Left slope", "Left offset", "Right slope", "Right offset")
RIGHT_END = ("Vertical locations", "Right slope", "Right offset")
CONTINUITY_CLASSES = ("continuous", *DISCONTINUITY)
CONTINUITY_AT = ("Left limit", "Right limit", "Classification")
SLOPE_RULE = (
    r"\text{ At each end give the slope }m=\lim f(x)/x\text{ and the offset }"
    r"\lim(f(x)-mx)\text{; enter does\_not\_exist for the offset when }m"
    r"\text{ is not finite.}"
)


def ends(vertical: object, *limits: object) -> tuple[ComputationalAnswer, ...]:
    first: ComputationalAnswer = (
        vertical if isinstance(vertical, PeriodicSetAnswer) else RealSetAnswer(vertical)
    )
    return (first, *(LimitAnswer(limit) for limit in limits))


DOMAIN_START = r"\text{{The real domain is }}{}.\text{{ Give the vertical asymptote locations.}}"
RIGHT_RULE = SLOPE_RULE.replace("At each end", r"At }+\infty\text{")


def radical_growth_asymptotes(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{The real domain is }[0,\infty).\text{ Give the vertical asymptote locations.}"
        + SLOPE_RULE.replace("At each end", "At }+\\infty\\text{")
        + rf"\quad f(x)=\frac{{{scaled(a)}x\sqrt{{x}}+{b}}}{{x+{c}}}.",
        OrderedAnswer(ends(sp.S.EmptySet, 0, sp.oo), RIGHT_END),
        rf"\text{{The denominator }}x+{c}\text{{ is positive on the domain, so there is no pole.}}",
        rf"\frac{{f(x)}}{{x}}=\frac{{{scaled(a)}x\sqrt{{x}}+{b}}}{{x^2+{c}x}}\to0,\qquad"
        rf"f(x)=\frac{{{scaled(a)}\sqrt{{x}}+{b}/x}}{{1+{c}/x}}\to\infty."
        r"\quad\text{No asymptote at }+\infty.",
    )


def oscillatory_remainder(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Give the vertical asymptote locations.}"
        + SLOPE_RULE
        + rf"\quad f(x)=\frac{{{scaled(a)}x^2+{c}x+{scaled(b)}\sin x}}{{x}}.",
        OrderedAnswer(ends(sp.S.EmptySet, a, c, a, c), ENDS),
        rf"\text{{Near }}0\text{{ use }}\sin x/x\to1:\ f(x)\to{b + c},"
        r"\text{ a finite limit, so }x=0\text{ is not a vertical asymptote.}",
        rf"f(x)-{scaled(a)}x={c}+{scaled(b)}\frac{{\sin x}}{{x}}\to{c}\quad(x\to\pm\infty),"
        rf"\qquad\left|\frac{{\sin x}}{{x}}\right|\le\frac{{1}}{{|x|}}.",
    )


def exponential_zero_denominator(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Give the vertical asymptote locations.}"
        + SLOPE_RULE
        + rf"\quad f(x)=\frac{{{scaled(b)}\cos {scaled(c)}x}}{{e^{{{scaled(a)}x}}-1}}.",
        OrderedAnswer(ends(sp.FiniteSet(0), 0, DNE, 0, 0), ENDS),
        rf"\text{{The denominator vanishes only at }}0\text{{, where the numerator is }}{b}\ne0.",
        rf"x\to-\infty:\ f(x)+{scaled(b)}\cos {scaled(c)}x\to0\text{{, which oscillates, so }}"
        r"f(x)/x\to0\text{ and }\lim f\text{ does not exist.}\quad"
        rf"x\to+\infty:\ |f(x)|\le\frac{{{b}}}{{e^{{{scaled(a)}x}}-1}}\to0.",
    )


def trig_periodic_poles(a: int, b: int, c: int) -> Built:
    numerator = rf"{scaled(a)}\sin 2x+{scaled(b)}\cos x"
    return finish(
        r"\text{Give the vertical asymptote locations as a period and a base set in }"
        r"[0,2\pi)." + SLOPE_RULE + rf"\quad f(x)=\frac{{{numerator}}}{{\sin x-1}}+{c}.",
        OrderedAnswer(
            ends(PeriodicSetAnswer(2 * sp.pi, sp.FiniteSet(sp.pi / 2)), DNE, DNE, DNE, DNE),
            ENDS,
        ),
        r"\text{The denominator vanishes at }x=\pi/2+2k\pi."
        r"\text{ Put }x=\pi/2+t\text{ and expand both sides.}",
        rf"f=\frac{{-({2 * a + b})t+O(t^3)}}{{-t^2/2+O(t^4)}}+{c}"
        rf"\sim\frac{{{2 * (2 * a + b)}}}{{t}}"
        r"\to\pm\infty.\quad\text{The poles recur in every period, so }f(x)/x"
        r"\text{ has no limit at either end.}",
    )


def continuity_log_ratio(a: int, b: int, c: int) -> Built:
    value = c % 3 - 1
    kind = "continuous" if value == 0 else "removable"
    return finish(
        r"\text{The function is continuous for }x\ne0.\text{ Give the one-sided limits at }0"
        r"\text{ and classify }x=0:\quad f(x)=\begin{cases}"
        rf"\dfrac{{1}}{{\log({scaled(a)}x^2)-\log({scaled(a)}x^2+{b})}},&x\ne0\\{value},&x=0"
        r"\end{cases}.",
        OrderedAnswer(
            (LimitAnswer(0), LimitAnswer(0), CategoryAnswer(kind, CONTINUITY_CLASSES)),
            CONTINUITY_AT,
        ),
        r"\text{Combine the logarithms. The quotient inside is below }1"
        r"\text{ and tends to }0.",
        rf"\log\frac{{{scaled(a)}x^2}}{{{scaled(a)}x^2+{b}}}\to-\infty\ \Rightarrow\ f(x)\to0"
        rf"\text{{ from both sides}};\quad f(0)={value}"
        + (r"\text{, so }f\text{ is continuous.}" if value == 0 else r"\ne0\text{: removable.}"),
    )


def exp_join(a: int, b: int, c: int) -> Built:
    c = 1 + c % 2  # keep e^(ac) at most e^10 so the values stay readable
    join = (sp.exp(a * c) - 1) / c
    second = sp.simplify((join + b) / c**2)
    return finish(
        r"\text{Find the parameters }p,q\text{ for continuity on }\mathbb R:\quad "
        rf"f(x)=\begin{{cases}}x+p,&x\le0\\\dfrac{{e^{{{scaled(a)}x}}-1}}{{x}},&0<x\le{c}\\"
        rf"qx^2-{b},&x>{c}\end{{cases}}.",
        OrderedAnswer((FormulaAnswer(a), FormulaAnswer(second)), JOINS),
        r"\text{Each branch is continuous on its interval. Match the limits at both joins.}",
        rf"\lim_{{x\to0^+}}\frac{{e^{{{scaled(a)}x}}-1}}{{x}}={a}=p,\qquad"
        rf"q\cdot{c * c}-{b}={tex(join)}\ \Longrightarrow\ q={tex(second)}.",
    )


def quartic_cubic_oblique(a: int, b: int, c: int) -> Built:
    return finish(
        r"\text{Give the vertical asymptote locations.}"
        + SLOPE_RULE
        + rf"\quad f(x)=\frac{{{scaled(a)}x^4-{b}x^3}}{{x^3+{c}x}}.",
        OrderedAnswer(ends(sp.S.EmptySet, a, -b, a, -b), ENDS),
        rf"\text{{Cancel }}x\text{{ on }}x\ne0:\ f(x)=\frac{{{scaled(a)}x^3-{b}x^2}}{{x^2+{c}}}"
        r"\to0\text{ at }0\text{, so there is no vertical asymptote.}",
        rf"f(x)-({tex(a * X - b)})=\frac{{{tex(-a * c * X + b * c)}}}{{x^2+{c}}}\to0"
        r"\quad(x\to\pm\infty).",
    )


def radical_oblique_right(a: int, b: int, c: int) -> Built:
    low, high = a, a + 2 * b
    return finish(
        DOMAIN_START.format(rf"[{high},\infty)")
        + RIGHT_RULE
        + rf"\quad f(x)=\frac{{(x-{c})\sqrt{{x-{high}}}}}{{\sqrt{{x-{low}}}}}.",
        OrderedAnswer(ends(sp.S.EmptySet, 1, -b - c), RIGHT_END),
        rf"\text{{The denominator is at least }}\sqrt{{{high - low}}}\text{{ on the domain.}}",
        rf"f(x)=(x-{c})\sqrt{{1-\frac{{{2 * b}}}{{x-{low}}}}},\qquad"
        rf"f(x)-(x-{c})=-\frac{{{2 * b}(x-{c})}}"
        rf"{{(x-{low})\left(1+\sqrt{{1-{2 * b}/(x-{low})}}\right)}}\to-{b}.",
    )


def radical_quotient_right(a: int, b: int, c: int) -> Built:
    offset = sp.Rational(b * c, 2)
    return finish(
        DOMAIN_START.format(rf"({c},\infty)")
        + RIGHT_RULE
        + rf"\quad f(x)=\frac{{{scaled(b)}\sqrt{{x^3-{c**3}}}}}{{\sqrt{{x-{c}}}}}.",
        OrderedAnswer(ends(sp.S.EmptySet, b, offset), RIGHT_END),
        rf"\text{{For }}x>{c}:\ f(x)={scaled(b)}\sqrt{{x^2+{c}x+{c * c}}}"
        rf"\to{scaled(b)}\sqrt{{{3 * c * c}}}\ (x\to{c}^+)\text{{, so no vertical asymptote.}}",
        rf"f(x)-{scaled(b)}x=\frac{{{scaled(b)}({c}x+{c * c})}}{{\sqrt{{x^2+{c}x+{c * c}}}+x}}"
        rf"\to{tex(offset)}.",
    )


def rational_oblique_pole(a: int, b: int, c: int) -> Built:
    pole = a + b
    expr = X * (X - b) / (X - pole)
    return oblique_pole(expr, pole, X + a, pole * a)


def rational_oblique_pole_left(a: int, b: int, c: int) -> Built:
    pole = -(a + b)
    expr = X * (X + b) / (X - pole)
    return oblique_pole(expr, pole, X - a, -pole * a)


def oblique_pole(expr: sp.Expr, pole: int, line: sp.Expr, remainder: int) -> Built:
    return finish(
        r"\text{Give the real domain, the vertical asymptote locations and both asymptotic}"
        r"\text{ line expressions at }-\infty\text{ and }+\infty:\quad f(x)=" + tex(expr),
        OrderedAnswer(
            (
                RealSetAnswer(sp.Complement(sp.S.Reals, sp.FiniteSet(pole))),
                RealSetAnswer(sp.FiniteSet(pole)),
                FormulaAnswer(line, REAL_X),
                FormulaAnswer(line, REAL_X),
            ),
            DOMAIN_ASYMPTOTES,
        ),
        rf"\text{{Divide the numerator by }}{tex(X - pole)}."
        rf"\text{{ The numerator does not vanish at }}x={pole}.",
        rf"f(x)={tex(line)}+\frac{{{remainder}}}{{{tex(X - pole)}}},"
        r"\qquad\text{the remainder tends to }0\text{ at both ends and to }\pm\infty"
        rf"\text{{ at }}{pole}.",
    )
