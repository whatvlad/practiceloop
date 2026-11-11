"""Convexity, inflections, joint monotonicity/convexity, polynomial reconstruction (#263)."""

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer, RealSetAnswer
from app.engine.blocks.analysis_one import X
from app.engine.generators._derivatives import REAL_X
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._sequence_limits import finish

CONVEXITY = ("Convex on", "Concave on", "Inflection points")
EMPTY = sp.S.EmptySet


def scaled(k: int) -> str:
    return "" if k == 1 else str(k)


def iv(low: object, high: object) -> sp.Set:
    return sp.Interval.open(low, high)


def convexity(
    shown: str, convex: sp.Set, concave: sp.Set, points: list[sp.Expr], derivation: str
) -> Built:
    return finish(
        r"\text{Give the union of the open intervals where the graph is convex, the same for}"
        r"\text{ concave, and the set of inflection abscissas (}\{\}\text{ for none):}"
        rf"\quad f(x)={shown}.",
        OrderedAnswer(
            (RealSetAnswer(convex), RealSetAnswer(concave), RealSetAnswer(sp.FiniteSet(*points))),
            CONVEXITY,
        ),
        r"\text{Read the sign of }f''\text{ on the domain; an inflection needs a sign change at a}"
        r"\text{ point of the domain.}",
        derivation,
    )


# AM1/69 and exam forms.


def convex_cubic(a: int, b: int, c: int) -> Built:
    f = a * X * (X - b) * (X - b - c)
    point = sp.Rational(2 * b + c, 3)
    return convexity(
        tex(f),
        iv(point, sp.oo),
        iv(-sp.oo, point),
        [point],
        rf"f''(x)={6 * a}x-{2 * a * (2 * b + c)}=0\iff x={tex(point)}.",
    )


def convex_exponential_product(a: int, b: int, c: int) -> Built:
    point = b + sp.Rational(2, a)
    return convexity(
        tex((X - b) * sp.exp(-a * X)),
        iv(point, sp.oo),
        iv(-sp.oo, point),
        [point],
        rf"f''(x)=e^{{-{a}x}}\left({a * a}(x-{b})-{2 * a}\right).",
    )


def convex_cubic_quotient(a: int, b: int, c: int) -> Built:
    k = 3 * c * c
    edge = 3 * c
    return convexity(
        rf"\frac{{x^3}}{{x^2+{k}}}",
        sp.Union(iv(-sp.oo, -edge), iv(0, edge)),
        sp.Union(iv(-edge, 0), iv(edge, sp.oo)),
        [-edge, sp.Integer(0), edge],
        rf"f''(x)=\frac{{{2 * k}x({3 * k}-x^2)}}{{(x^2+{k})^3}}.",
    )


def convex_log_quadratic(a: int, b: int, c: int) -> Built:
    return convexity(
        rf"{scaled(a)}\ln({c * c}+x^2)",
        iv(-c, c),
        sp.Union(iv(-sp.oo, -c), iv(c, sp.oo)),
        [sp.Integer(-c), sp.Integer(c)],
        rf"f''(x)=\frac{{{2 * a}({c * c}-x^2)}}{{({c * c}+x^2)^2}}.",
    )


def convex_reciprocal(a: int, b: int, c: int) -> Built:
    return convexity(
        rf"\frac{{{a}}}{{{c * c}-x^2}}",
        iv(-c, c),
        sp.Union(iv(-sp.oo, -c), iv(c, sp.oo)),
        [],
        rf"f''(x)=\frac{{{2 * a}(3x^2+{c * c})}}{{({c * c}-x^2)^3}}"
        r"\text{; the sign changes only at}"
        rf"\ x=\pm{c}\notin D.",
    )


def convex_log_absolute(a: int, b: int, c: int) -> Built:
    k = 1 + a % 2
    m = 2 * b * k**3
    return convexity(
        rf"x-\frac{{{b}}}{{3}}x^3-{m}\ln|x|",
        sp.Union(iv(-sp.oo, 0), iv(0, k)),
        iv(k, sp.oo),
        [sp.Integer(k)],
        rf"f''(x)=-{2 * b}x+\frac{{{m}}}{{x^2}}=\frac{{{2 * b}({k**3}-x^3)}}{{x^2}}.",
    )


def convex_trig(a: int, b: int, c: int) -> Built:
    end = 2 * sp.pi / b
    return convexity(
        rf"{scaled(a)}\left(\sin {scaled(b)}x+\tfrac18\sin {2 * b}x\right),\ 0<x<{tex(end)}",
        iv(sp.pi / b, end),
        iv(0, sp.pi / b),
        [sp.pi / b],
        rf"f''(x)=-{a * b * b}\sin({scaled(b)}x)\left(1+\cos {scaled(b)}x\right).",
    )


def convex_exponential_arctan(a: int, b: int, c: int) -> Built:
    point = sp.Rational(a, 2)
    return convexity(
        rf"e^{{{scaled(a)}\arctan x}}",
        iv(-sp.oo, point),
        iv(point, sp.oo),
        [point],
        rf"f''(x)=\frac{{{a}e^{{{scaled(a)}\arctan x}}({a}-2x)}}{{(1+x^2)^2}}.",
    )


def convex_log_root(a: int, b: int, c: int) -> Built:
    point = b * sp.exp(sp.Rational(8, 3))
    inner = rf"\frac{{x}}{{{b}}}" if b > 1 else "x"
    return convexity(
        rf"\frac{{{scaled(a)}\ln {inner}}}{{\sqrt{{x}}}}",
        iv(point, sp.oo),
        iv(0, point),
        [point],
        rf"f''(x)=\frac{{{a}(3\ln(x/{b})-8)}}{{4x^{{5/2}}}}.",
    )


def convex_reversed_exponential(a: int, b: int, c: int) -> Built:
    point = c - sp.Rational(2, a)
    return convexity(
        tex((c - X) * sp.exp(a * X)),
        iv(-sp.oo, point),
        iv(point, sp.oo),
        [point],
        rf"f''(x)=e^{{{a}x}}\left({a * a}({c}-x)-{2 * a}\right).",
    )


# Exam family: where a function is monotone and convex or concave at once.


def jointly(shown: str, wanted: str, value: sp.Set, derivation: str) -> Built:
    return finish(
        rf"\text{{Give the union of the open intervals on which }}f\text{{ is {wanted}:}}"
        rf"\quad f(x)={shown}.",
        RealSetAnswer(value),
        r"\text{Intersect the set where }f'\text{ has the required sign with the set where}"
        r"\ f''\text{ has the required sign.}",
        derivation,
    )


def increasing_convex_quadratic_exponential(a: int, b: int, c: int) -> Built:
    low, high = -sp.sqrt(c + 2), 1 - sp.sqrt(c + 3)
    return jointly(
        rf"(x^2+2x-{c})e^{{-x}}",
        "both increasing and convex",
        iv(low, high),
        rf"f'(x)=e^{{-x}}({c + 2}-x^2),\quad f''(x)=e^{{-x}}(x^2-2x-{c + 2}).",
    )


def increasing_convex_root_log(a: int, b: int, c: int) -> Built:
    inner = rf"\frac{{x}}{{{b}}}" if b > 1 else "x"
    return jointly(
        rf"{scaled(a)}\sqrt{{x}}\ln {inner}",
        "both increasing and convex",
        iv(b * sp.exp(-2), b),
        rf"f'(x)=\frac{{{a}(\ln(x/{b})+2)}}{{2\sqrt x}},\quad f''(x)=-\frac{{{a}\ln(x/{b})}}"
        rf"{{4x^{{3/2}}}}.",
    )


def decreasing_concave_quadratic_exponential(a: int, b: int, c: int) -> Built:
    return jointly(
        rf"(x^2-6x+{c})e^{{x}}",
        "both decreasing and concave",
        iv(2 - sp.sqrt(10 - c), 1 + sp.sqrt(11 - c)),
        rf"f'(x)=e^x(x^2-4x+{c - 6}),\quad f''(x)=e^x(x^2-2x+{c - 10}).",
    )


def increasing_concave_arccot(a: int, b: int, c: int) -> Built:
    r = sp.sqrt(c - 1)
    value = iv(-sp.oo, 0) if c == 1 else sp.Union(iv(-sp.oo, -r), iv(0, r))
    return jointly(
        rf"\frac{{x^3}}{{3}}+{c * c if c > 1 else ''}\operatorname{{arccot}}\frac{{1}}{{x}}",
        "both increasing and concave",
        value,
        rf"f'(x)=x^2+\frac{{{c * c}}}{{1+x^2}}>0,\quad f''(x)=2x\left(1-"
        rf"\frac{{{c * c}}}{{(1+x^2)^2}}"
        r"\right),\ x\ne0.",
    )


# AM1/51: polynomials of lowest degree from extremum and inflection data.


def polynomial_extrema(a: int, b: int, c: int) -> Built:
    low, high = a, a + b
    lead = -c
    p = lead * (X**3 - sp.Rational(3 * (low + high), 2) * X**2 + 3 * low * high * X) + (a + 1)
    p = sp.expand(p)
    return finish(
        rf"\text{{Find the polynomial of least degree with leading coefficient }}{lead}"
        rf"\text{{ that has a strict local minimum at }}x={low}\text{{, a strict local maximum at}}"
        rf"\ x={high}\text{{ and the value }}{a + 1}\text{{ at }}x=0.",
        FormulaAnswer(p, REAL_X),
        r"\text{The derivative vanishes at both points and changes sign there: degree }3.",
        rf"p'(x)={3 * lead}(x-{low})(x-{high}),\qquad p(0)={a + 1},\qquad p(x)={tex(p)}.",
    )


def polynomial_inflection(a: int, b: int, c: int) -> Built:
    point, value, slope, lead = a, b, c, (-1) ** (a + b) * (1 + c % 2)
    p = sp.expand(value + slope * (X - point) + lead * (X - point) ** 3)
    return finish(
        rf"\text{{Find the polynomial of least degree with leading coefficient }}{lead}"
        rf"\text{{ whose graph has an inflection point at }}x={point}\text{{, where its value is}}"
        rf"\ {value}\text{{ and its derivative is }}{slope}.",
        FormulaAnswer(p, REAL_X),
        r"p''\text{ must change sign at the point, so the degree is at least }3.",
        rf"p(x)={value}+{slope}(x-{point})+({lead})(x-{point})^3={tex(p)}.",
    )
