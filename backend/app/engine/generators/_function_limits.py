"""Bounded function limits, joins, asymptotes and root certificates."""

from fractions import Fraction

import sympy as sp

from app.engine.answers.computational import (
    CategoryAnswer,
    FormulaAnswer,
    LimitAnswer,
    OrderedAnswer,
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
    expr: sp.Expr,
    at: object,
    expected: object,
    method: str,
    derivation: str,
    *,
    direction: str = "",
) -> Built:
    side = "^" + direction if direction else ""
    return finish(
        r"\text{Evaluate:}\quad \lim_{x\to " + tex(at) + side + "}" + tex(expr),
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
