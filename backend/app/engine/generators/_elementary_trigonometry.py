"""Principal values, exact identity domains and complete periodic solution families."""

from collections.abc import Iterable
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer, PeriodicSetAnswer
from app.engine.answers.fourier import FourierAnswer
from app.engine.generators._elementary_common import Built, ElementaryParams, X, finish, tex


class PeriodicUnionAnswer(OrderedAnswer):
    def latex(self) -> str:
        return (
            r"\left("
            + r"\right)\cup\left(".join(component.latex() for component in self.components)
            + r"\right)"
        )


def canonical_points(values: Iterable[Any], period: Any) -> Any:
    return sp.FiniteSet(*(sp.simplify(sp.Mod(value, period)) for value in values))


def canonical_interval(lo: Any, hi: Any, period: Any, closed: bool = True) -> Any:
    # These families have width < period and the pre-shift lies within two cells.
    cell = sp.Interval.Ropen(0, period)
    return sp.Union(
        *(
            sp.Interval(lo + k * period, hi + k * period, not closed, not closed).intersect(cell)
            for k in range(-2, 3)
        )
    )


def periodic(statement: str, period: Any, base: Any, derivation: str) -> Built:
    answer = PeriodicSetAnswer(period, base)
    convention = (
        rf" Use canonical period \(T={tex(period)}\) and base \(B\subset[0,T)\); "
        r"your answer (T;B) means \(B+Tk,\ k\in\mathbb{Z}\)."
    )
    return finish(
        statement + convention,
        answer,
        r"\text{Solve on one half-open cell; retain all original exclusions,}"
        r"\text{ then translate by integer periods.}",
        derivation,
        (("Base solutions", base),),
    )


def evaluate(template: str, p: ElementaryParams) -> Built:
    a, b, c, v = p.a, p.b, p.c, p.variant
    x, pi = X, sp.pi
    phase = sp.Rational(a, 6) * pi
    u = b * x + phase
    if template.startswith("trig-domain-"):
        period = 2 * pi / b
        excluded: tuple[Any, ...]
        if template == "trig-domain-tan-ratio":
            identity = r"\frac{1+\tan u}{1+\cot u}=\tan u"
            excluded = (0, pi / 2, 3 * pi / 4, pi, 3 * pi / 2, 7 * pi / 4)
            reason = r"\sin u\ne0,\quad\cos u\ne0,\quad \sin u+\cos u\ne0."
        elif template == "trig-domain-tan-sum":
            identity = r"\tan u+\cot u=2/\sin(2u)"
            excluded = (0, pi / 2, pi, 3 * pi / 2)
            reason = r"\sin u\cos u\ne0;\quad \tan u+\cot u=\frac{\sin^2u+\cos^2u}{\sin u\cos u}."
        elif template == "trig-domain-half-angle":
            identity = (
                r"\sin u=\frac{2\tan(u/2)}{1+\tan^2(u/2)}"
                if v % 2
                else r"\cos u=\frac{1-\tan^2(u/2)}{1+\tan^2(u/2)}"
            )
            excluded = (pi,)
            reason = r"\cos(u/2)\ne0;\quad 1+\tan^2(u/2)>0."
        elif template == "trig-domain-double-angle":
            identity = r"\sin^4u+\cos^4u=1-\sin^2(2u)/2" if v % 2 else r"\cos^4u-\sin^4u=\cos(2u)"
            excluded = ()
            reason = (
                r"\sin^2u+\cos^2u=1,\quad 2\sin u\cos u=\sin2u;"
                r"\quad\text{both sides are defined for every real }u."
            )
        else:
            raise ValueError(template)
        poles = canonical_points(((angle - phase) / b for angle in excluded), period)
        base = sp.Interval.Ropen(0, period) - poles
        return periodic(
            f"Find the complete real domain on which \\({identity}\\) "
            f"is defined and valid, with \\(u={tex(u)}\\).",
            period,
            base,
            reason + rf"\quad\text{{Excluded base points: }}{tex(poles)}.",
        )
    if template.startswith("trig-linearization-"):
        angle = b * x
        cosine = bool(v % 2)
        fourth = template.endswith("fourth")
        power = 4 if fourth else 2
        trig = sp.cos(angle) if cosine else sp.sin(angle)
        sign = 1 if cosine else -1
        expected = (
            a * (3 + sign * 4 * sp.cos(2 * angle) + sp.cos(4 * angle)) / 8 + c
            if fourth
            else a * (1 + sign * sp.cos(2 * angle)) / 2 + c
        )
        return finish(
            f"Express \\({tex(a * trig**power + c)}\\) as a linear combination "
            "of cosines of multiple angles and a constant, with no powers of sine or cosine.",
            FourierAnswer(expected, (("x", "real"),), (2 * b, 4 * b) if fourth else (2 * b,)),
            r"\sin^2u=(1-\cos2u)/2,\quad\cos^2u=(1+\cos2u)/2.",
            rf"{tex(a * trig**power + c)}={tex(expected)}",
        )
    if template == "inverse-trig-values":
        values = (0, sp.Rational(1, 2), sp.sqrt(2) / 2, sp.sqrt(3) / 2, 1, -sp.sqrt(3) / 2)
        value = values[v]
        other = values[(v + b) % len(values)]
        if v < 3:
            expression = a * sp.asin(value) + b * sp.acos(other)
            statement = rf"{a}\arcsin({tex(value)})+{b}\arccos({tex(other)})"
            calculation = (
                rf"\arcsin({tex(value)})={tex(sp.asin(value))},"
                rf"\quad\arccos({tex(other)})={tex(sp.acos(other))}."
            )
        else:
            expression = a * sp.asin(value) / (b * sp.pi / 2)
            statement = rf"\frac{{{a}\arcsin({tex(value)})}}{{{b}\arcsin(1)}}"
            calculation = rf"\arcsin({tex(value)})={tex(sp.asin(value))},\quad\arcsin(1)=\pi/2."
        return finish(
            f"Compute the principal value of \\({statement}\\).",
            FormulaAnswer(expression),
            r"\arcsin z\in[-\pi/2,\pi/2],\quad\arccos z\in[0,\pi].",
            calculation,
        )
    if template == "inverse-trig-nested":
        h = sp.sqrt(a * a + b * b)
        if v % 3 == 0:
            statement, expected = rf"\sin(\arccos({tex(a / h)}))", b / h
            reason = (
                rf"\theta=\arccos({tex(a / h)})\in(0,\pi/2),"
                rf"\quad\sin\theta=\sqrt{{1-\cos^2\theta}}={tex(expected)}."
            )
        elif v % 3 == 1:
            statement, expected = rf"\tan(\arccos({tex(a / h)}))", sp.Rational(b, a)
            reason = (
                rf"\theta\in(0,\pi/2),\quad "
                rf"\tan\theta=\frac{{\sqrt{{1-({tex(a / h)})^2}}}}{{{tex(a / h)}}}={tex(expected)}."
            )
        else:
            statement, expected = rf"\sin(\arctan({tex(sp.Rational(a, b))}))", a / h
            reason = (
                rf"\theta\in(0,\pi/2),\quad\sin\theta="
                rf"\frac{{\tan\theta}}{{\sqrt{{1+\tan^2\theta}}}}={tex(expected)}."
            )
        return finish(
            f"Compute exactly \\({statement}\\).",
            FormulaAnswer(expected),
            r"\text{Use the principal branch before choosing a square-root sign.}",
            reason,
        )
    if template == "inverse-trig-cot-branch":
        angle = (pi / 6, 5 * pi / 6, 7 * pi / 6)[v] if v < 3 else sp.Integer(a + b + c)
        principal = angle - sp.floor(angle / pi + sp.Rational(1, 2)) * pi
        expected = pi / 2 - principal
        return finish(
            rf"Compute \(\operatorname{{arccot}}(\tan({tex(angle)}))\), "
            "using arccot with range (0,pi).",
            FormulaAnswer(expected),
            r"\operatorname{arccot}t=\pi/2-\arctan t,\quad\arctan t\in(-\pi/2,\pi/2).",
            rf"\arctan(\tan({tex(angle)}))={tex(principal)},"
            rf"\quad\operatorname{{arccot}}(\tan({tex(angle)}))={tex(expected)}.",
        )
    if template == "inverse-trig-atan-cot":
        value = (0, 1, sp.sqrt(3), 1 / sp.sqrt(3), -1, -sp.sqrt(3))[v]
        atan = sp.atan(value)
        acot = pi / 2 - atan
        expected = a * b * atan * acot if v % 2 else a * atan - b * acot
        statement = (
            rf"{a * b}\arctan({tex(value)})\operatorname{{arccot}}({tex(value)})"
            if v % 2
            else rf"{a}\arctan({tex(value)})-{b}\operatorname{{arccot}}({tex(value)})"
        )
        return finish(
            rf"Compute \({statement}\), "
            "using arccot with range (0,pi).",
            FormulaAnswer(expected),
            r"\operatorname{arccot}t=\pi/2-\arctan t.",
            rf"\arctan({tex(value)})={tex(atan)},\quad\operatorname{{arccot}}({tex(value)})={tex(acot)}.",
        )
    if template == "trig-equation-cos-mixed":
        first, second = 4 * pi / (9 * b), 4 * pi / (7 * b)
        left = PeriodicSetAnswer(first, canonical_points(((pi / 9 - phase) / b,), first))
        right = PeriodicSetAnswer(second, canonical_points(((-pi / 7 - phase) / b,), second))
        answer = PeriodicUnionAnswer((left, right), ("First branch", "Second branch"))
        statement = (
            rf"Find all solutions of \(\cos(4u)=\sin(u/2),\ u={tex(u)}\). "
            rf"Give the union of two periodic branches, ordered by periods \({tex(first)}\) "
            rf"then \({tex(second)}\). Each branch is (period;base points "
            "in its half-open period cell). Each integer index ranges "
            "independently over all integers."
        )
        return finish(
            statement,
            answer,
            r"\cos A=\cos B\iff A=B+2\pi k\ \text{or}\ A=-B+2\pi k.",
            r"4u=\pi/2-u/2+2\pi k\quad\text{or}\quad4u=-\pi/2+u/2+2\pi k.",
            (("First branch base", left.base), ("Second branch base", right.base)),
        )
    if template == "trig-equation-sine-sum":
        period = 2 * pi / b
        base = canonical_points(
            ((angle - phase) / b for angle in (0, pi, 2 * pi / 3, 4 * pi / 3)), period
        )
        return periodic(
            rf"Solve \(\sin u+\sin(2u)=0,\ u={tex(u)}\).",
            period,
            base,
            r"\sin u(1+2\cos u)=0\iff\sin u=0\ \text{or}\ \cos u=-1/2.",
        )
    if template == "trig-equation-tangent-sum":
        period = pi / b
        base = canonical_points(((angle - phase) / b for angle in (0, pi / 3, 2 * pi / 3)), period)
        return periodic(
            rf"Solve \(\tan u+\tan(2u)=\tan(3u),\ u={tex(u)}\), "
            "retaining every tangent pole exclusion.",
            period,
            base,
            r"\cos u\cos2u\cos3u\ne0;\quad\sin u\sin2u\sin3u=0."
            r"\quad u=k\pi/3\text{ are precisely the retained roots.}",
        )
    if template == "trig-equation-exponential":
        shift = v % 3
        alpha = (pi / 6, pi / 4, pi / 3)[shift]
        period = 2 * pi / b
        base = canonical_points(
            ((angle - phase) / b for angle in (alpha, pi - alpha, pi + alpha, 2 * pi - alpha)),
            period,
        )
        return periodic(
            rf"Solve \({a + 1}^{{{shift}+\cos^2 u}}={a + 1}^{{3\sin^2 u}},\ u={tex(u)}\).",
            period,
            base,
            rf"{a + 1}>1\Rightarrow {shift}+1-\sin^2u=3\sin^2u"
            rf"\Rightarrow\sin^2u={tex(sp.Rational(shift + 1, 4))}.",
        )
    if template == "trig-inequality-sine":
        alpha = (pi / 6, pi / 4, pi / 3)[v % 3]
        period = 2 * pi / b
        slope = -b if v >= 3 else b
        first, second = (alpha - phase) / slope, (pi - alpha - phase) / slope
        base = canonical_interval(min(first, second), max(first, second), period)
        return periodic(
            rf"Solve \(\sin u\ge {tex(sp.sin(alpha))},\ u={tex(slope * x + phase)}\).",
            period,
            base,
            rf"u\in[{tex(alpha)},{tex(pi - alpha)}]+2\pi k,\quad x=(u-{tex(phase)})/({slope}).",
        )
    if template == "trig-inequality-sine-cosine":
        period = 2 * pi / b
        alpha = sp.asin(sp.sqrt(6) / 4)
        base = canonical_interval(
            (alpha - pi / 4 - phase) / b, (pi - alpha - pi / 4 - phase) / b, period
        )
        return periodic(
            rf"Solve \(\cos u+\sin u\ge\sqrt{{3}}/2,\ u={tex(u)}\).",
            period,
            base,
            r"\cos u+\sin u=\sqrt2\sin(u+\pi/4),\quad \alpha=\arcsin(\sqrt6/4),"
            r"\quad u+\pi/4\in[\alpha,\pi-\alpha]+2\pi k.",
        )
    if template == "trig-inequality-cotangent":
        period = pi / b
        base = sp.Union(
            canonical_interval((pi / 4 - phase) / b, (pi / 2 - phase) / b, period, False),
            canonical_interval((3 * pi / 4 - phase) / b, (pi - phase) / b, period, False),
        )
        return periodic(
            rf"Solve \(\cot u-1/\cot u<0,\ u={tex(u)}\), retaining the domains of both quotients.",
            period,
            base,
            r"\sin u\cos u\ne0;\quad\cot u-1/\cot u=2\cot2u<0."
            r"\quad u\in(\pi/4,\pi/2)\cup(3\pi/4,\pi)+\pi k.",
        )
    raise ValueError(template)
