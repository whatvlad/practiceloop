"""Differential error estimates, L'Hopital limits and differentiability joins (#261)."""

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.blocks.analysis_one import X
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._function_limits import function_limit
from app.engine.generators._sequence_limits import finish

JOIN = ("First parameter", "Second parameter")  # the JOINS contract labels


def scaled(k: int) -> str:
    return "" if k == 1 else str(k)


# AM1/44: absolute error estimates with the differential.


def error(statement: str, value: sp.Expr, method: str, derivation: str) -> Built:
    return finish(statement, FormulaAnswer(value), method, derivation)


def error_triangle_area(a: int, b: int, c: int) -> Built:
    side = 50 * (a + 1)
    angle, label = ((sp.pi / 3, r"\pi/3"), (sp.pi / 4, r"\pi/4"), (sp.pi / 6, r"\pi/6"))[b % 3]
    step = sp.Rational(c, 100)
    value = sp.nsimplify(sp.Rational(side * side, 2) * sp.cos(angle) * step)
    return error(
        rf"\text{{An isosceles triangle has legs }}{side}"
        r"\text{ m. The apex angle is measured as }"
        rf"{label}\text{{ with absolute error }}{tex(step)}"
        r"\text{ rad. Estimate the absolute error of}"
        r"\text{ the area with the differential (in m}^2\text{).}",
        value,
        r"P(\alpha)=\tfrac12 b^2\sin\alpha,\qquad \Delta P\approx|P'(\alpha)|\,\Delta\alpha.",
        rf"\Delta P\approx\tfrac12\cdot{side}^2\cos({label})\cdot{tex(step)}={tex(value)}.",
    )


def error_sphere_volume(a: int, b: int, c: int) -> Built:
    diameter = 2 * (a + 2)
    step = sp.Rational(b, 100)
    value = sp.pi * diameter**2 / 2 * step
    return error(
        rf"\text{{The diameter of a ball is measured as }}{diameter}"
        r"\text{ mm with absolute error }"
        rf"{tex(step)}\text{{ mm. Estimate the absolute error of its volume (in mm}}^3\text{{).}}",
        value,
        r"V(d)=\tfrac{\pi}{6}d^3,\qquad \Delta V\approx\tfrac{\pi}{2}d^2\,\Delta d.",
        rf"\Delta V\approx\tfrac{{\pi}}{{2}}\cdot{diameter}^2\cdot{tex(step)}={tex(value)}.",
    )


def error_fall_depth(a: int, b: int, c: int) -> Built:
    time = sp.Rational(30 + 2 * a + b, 10)
    step = sp.Rational(1, 10) if c % 2 else sp.Rational(1, 20)
    gravity = sp.Rational(98, 10)
    value = gravity * time * step
    return error(
        rf"\text{{A stone falls freely for }}{tex(time)}\text{{ s, measured with absolute error }}"
        rf"{tex(step)}\text{{ s. With }}g={tex(gravity)}"
        r"\text{ m/s}^2\text{ estimate the absolute}"
        r"\text{ error of the depth }h=gt^2/2\text{ (in m).}",
        value,
        r"\Delta h\approx g\,t\,\Delta t.",
        rf"\Delta h\approx{tex(gravity)}\cdot{tex(time)}\cdot{tex(step)}={tex(value)}.",
    )


def error_average_speed(a: int, b: int, c: int) -> Built:
    distance = 100 * (1 + a % 2)
    time = sp.Rational(1000 + 50 * b + 10 * c, 100) * (1 + a % 2)
    step = sp.Rational(1, 100)
    value = distance / time**2 * step
    return error(
        rf"\text{{A runner covers }}{distance}\text{{ m in }}{tex(time)}"
        r"\text{ s, timed with absolute}"
        rf"\text{{ error }}{tex(step)}\text{{ s. Estimate the absolute error of the average speed}}"
        r"\text{ (in m/s).}",
        value,
        r"v(t)=s/t,\qquad \Delta v\approx\frac{s}{t^2}\,\Delta t.",
        rf"\Delta v\approx\frac{{{distance}}}{{({tex(time)})^2}}\cdot{tex(step)}={tex(value)}.",
    )


# AM1/45 and exam forms: L'Hopital limits.


def lhopital(
    shown: str | sp.Expr, at: object, value: object, derivation: str, side: str = ""
) -> Built:
    return function_limit(
        shown,
        at,
        value,
        r"\text{Check the indeterminate form, then apply L'Hopital's rule (repeatedly if needed).}",
        derivation,
        direction=side,
    )


def log_exponential_growth(a: int, b: int, c: int) -> Built:
    base = a + 1
    value = sp.log(base) / c
    return lhopital(
        sp.log(base**X + b) / (c * X),
        sp.oo,
        value,
        rf"\frac{{{base}^x\ln{base}/({base}^x+{b})}}{{{c}}}\to\frac{{\ln{base}}}{{{c}}}.",
    )


def log_sine_ratio(a: int, b: int, c: int) -> Built:
    return lhopital(
        rf"\frac{{\ln\sin\frac{{\pi x}}{{{2 * a}}}}}{{{scaled(b)}\ln\frac{{x}}{{{a}}}}}",
        a,
        0,
        rf"\frac{{\frac{{\pi}}{{{2 * a}}}\cot\frac{{\pi x}}{{{2 * a}}}}}{{{b}/x}}\to"
        rf"\frac{{\frac{{\pi}}{{{2 * a}}}\cdot0}}{{{b}/{a}}}=0.",
    )


def arctan_difference(a: int, b: int, c: int) -> Built:
    power = 2 + c % 2
    value = 0 if power == 2 else sp.Rational(a**3, 3)
    return lhopital(
        (a * X - sp.atan(a * X)) / X**power,
        0,
        value,
        rf"\frac{{{a}-\frac{{{a}}}{{1+{a * a}x^2}}}}{{{power}x^{{{power - 1}}}}}"
        rf"=\frac{{{a**3}x^2}}{{{power}x^{{{power - 1}}}(1+{a * a}x^2)}}\to{tex(value)}.",
    )


def double_root_quotient(a: int, b: int, c: int) -> Built:
    n = b + 2
    value = sp.Rational(2 * (2 * n - 1), n - 1)
    return lhopital(
        (X ** (2 * n) - 2 * n * X + 2 * n - 1) / (X**n - n * X + n - 1),
        1,
        value,
        rf"\text{{Two applications: }}\frac{{{2 * n}({2 * n - 1})x^{{{2 * n - 2}}}}}"
        rf"{{{n}({n - 1})x^{{{n - 2}}}}}\to{tex(value)}.",
    )


def log_cosine_ratio(a: int, b: int, c: int) -> Built:
    if a == b:
        b = a + 1
    value = sp.Rational(a * a, b * b)
    return lhopital(
        sp.log(sp.cos(a * X)) / sp.log(sp.cos(b * X)),
        0,
        value,
        rf"\frac{{-{a}\tan {scaled(a)}x}}{{-{b}\tan {scaled(b)}x}}"
        rf"\to\frac{{{a}\cdot{a}}}{{{b}\cdot{b}}}"
        rf"={tex(value)}.",
    )


def root_arccot(a: int, b: int, c: int) -> Built:
    half = c % 2 == 1
    value = 0 if half else sp.Rational(a, b)
    power = r"\sqrt{x}" if half else "x"
    return lhopital(
        rf"{scaled(a)}{power}\operatorname{{arccot}}({scaled(b)}x)",
        sp.oo,
        value,
        rf"\frac{{\operatorname{{arccot}}({scaled(b)}x)}}{{1/({scaled(a)}{power})}}:\quad"
        rf"\frac{{-{b}/(1+{b * b}x^2)}}{{(\cdot)'}}\to{tex(value)}.",
    )


def power_log_zero(a: int, b: int, c: int) -> Built:
    return lhopital(
        a * X**b * sp.log(X),
        0,
        0,
        rf"\frac{{\ln x}}{{x^{{-{b}}}/{a}}}:\quad\frac{{1/x}}{{-{b}x^{{-{b + 1}}}/{a}}}"
        rf"=-\frac{{{a}x^{{{b}}}}}{{{b}}}\to0.",
        "+",
    )


def tangent_half_angle(a: int, b: int, c: int) -> Built:
    value = 2 * a * b
    return lhopital(
        rf"{scaled(a)}({scaled(b)}\pi-x)\tan\frac{{x}}{{{2 * b}}}",
        b * sp.pi,
        value,
        rf"\frac{{{scaled(a)}({scaled(b)}\pi-x)}}{{\cot\frac{{x}}{{{2 * b}}}}}:\quad"
        rf"\frac{{-{a}}}{{-\frac{{1}}{{{2 * b}}}\csc^2\frac{{x}}{{{2 * b}}}}}\to{value}.",
        "-",
    )


def cosine_difference(a: int, b: int, c: int) -> Built:
    k = 2 * a + (c % 3 - 1)
    gap = 2 * a - k
    value = sp.Rational(a, 6) if gap == 0 else (sp.oo if gap > 0 else -sp.oo)
    return lhopital(
        rf"\left(\frac{{{a}}}{{1-\cos x}}-\frac{{{k}}}{{x^2}}\right)",
        0,
        value,
        rf"\frac{{{a}x^2-{k}(1-\cos x)}}{{x^2(1-\cos x)}},\quad"
        rf"1-\cos x=\tfrac{{x^2}}{{2}}-\tfrac{{x^4}}{{24}}+\dots\ \Rightarrow\ "
        rf"\frac{{({tex(sp.Rational(gap, 2))})x^2+\tfrac{{{k}}}{{24}}x^4}}{{x^4/2}}"
        rf"\to{tex(value)}.",
        "+",
    )


def cotangent_difference(a: int, b: int, c: int) -> Built:
    k = a + (c % 3 - 1)
    value = 0 if k == a else (-sp.oo if a > k else sp.oo)
    return lhopital(
        rf"\left(\frac{{{a}}}{{x}}-{scaled(k)}\cot x\right)",
        0,
        value,
        rf"\frac{{{a}\sin x-{k}x\cos x}}{{x\sin x}},\quad\text{{numerator}}\sim{a - k}x,"
        rf"\ \text{{denominator}}\sim x^2,\ x\to0^-.",
        "-",
    )


def log_reciprocal_sum(a: int, b: int, c: int) -> Built:
    value = sp.Rational(a, 2)
    return lhopital(
        rf"{scaled(a)}\left(\frac{{1}}{{\ln x}}+\frac{{1}}{{1-x}}\right)",
        1,
        value,
        r"\frac{1-x+\ln x}{(1-x)\ln x}:\ \frac{-1+1/x}{-\ln x+(1-x)/x}"
        r"=\frac{1-x}{-x\ln x+1-x}:\ \frac{-1}{-\ln x-2}\to\frac12.",
    )


def log_power_zero(a: int, b: int, c: int) -> Built:
    return lhopital(
        rf"\left(-{scaled(a)}\ln x\right)^{{{scaled(b)}x}}",
        0,
        1,
        rf"\ln f={b}x\ln(-{a}\ln x)=\frac{{{b}\ln(-{a}\ln x)}}{{1/x}}:\ "
        r"\frac{1/(x\ln x)}{-1/x^2}=-\frac{x}{\ln x}\to0,\quad f\to e^0=1.",
        "+",
    )


def arctan_power(a: int, b: int, c: int) -> Built:
    value = sp.exp(-sp.Rational(2 * b, a) / sp.pi)
    return lhopital(
        rf"\left(\frac{{2}}{{\pi}}\arctan {scaled(a)}x\right)^{{{scaled(b)}x}}",
        sp.oo,
        value,
        rf"\ln f=\frac{{{b}\ln(\frac{{2}}{{\pi}}\arctan {scaled(a)}x)}}{{1/x}}:\ "
        rf"\frac{{{b}\cdot\frac{{{a}}}{{(1+{a * a}x^2)\arctan {scaled(a)}x}}}}{{-1/x^2}}"
        rf"\to-\frac{{{2 * b}}}{{{a}\pi}}.",
    )


def log_exponent_power(a: int, b: int, c: int) -> Built:
    return lhopital(
        rf"(1+{scaled(a)}x)^{{{scaled(b)}\ln x}}",
        0,
        1,
        rf"\ln f={b}\ln x\ln(1+{a}x)\sim{a * b}x\ln x\to0,\quad f\to1.",
        "+",
    )


def tangent_cosine_power(a: int, b: int, c: int) -> Built:
    return lhopital(
        rf"\left({scaled(a)}\tan x\right)^{{{scaled(b)}\cos x}}",
        sp.pi / 2,
        1,
        rf"\ln f=\frac{{{b}\ln({a}\tan x)}}{{\sec x}}:\ "
        rf"\frac{{{b}\sec^2x/\tan x}}{{\sec x\tan x}}={b}\frac{{\cos x}}{{\sin^2x}}\to0.",
        "-",
    )


def exponential_cosh(a: int, b: int, c: int) -> Built:
    return lhopital(
        (sp.exp(a * X) + sp.exp(-a * X) - 2) / (b * X**2),
        0,
        sp.Rational(a * a, b),
        rf"\text{{Twice: }}\frac{{{a * a}(e^{{{a}x}}+e^{{-{a}x}})}}{{{2 * b}}}\to"
        rf"{tex(sp.Rational(a * a, b))}.",
    )


def one_minus_power(a: int, b: int, c: int) -> Built:
    return lhopital(
        rf"\left({scaled(a)}(1-x)\right)^{{\sin {scaled(b)}\pi x}}",
        1,
        1,
        rf"\ln f=\frac{{\ln({a}(1-x))}}{{1/\sin({b}\pi x)}}:\ "
        r"\sin(b\pi x)\sim\pm b\pi(1-x),\ (1-x)\ln(1-x)\to0,\quad f\to1.",
        "-",
    )


def tangent_log(a: int, b: int, c: int) -> Built:
    return lhopital(
        rf"\tan({scaled(a)}x)\,\ln x",
        0,
        0,
        rf"\frac{{\ln x}}{{\cot {scaled(a)}x}}:\ \frac{{1/x}}{{-{a}\csc^2 {scaled(a)}x}}"
        rf"=-\frac{{\sin^2 {scaled(a)}x}}{{{a}x}}\to0.",
        "+",
    )


def log_tangent_product(a: int, b: int, c: int) -> Built:
    return lhopital(
        rf"{scaled(a)}x\ln\left(\tan {scaled(b)}x\right)",
        0,
        0,
        rf"\frac{{\ln\tan {scaled(b)}x}}{{1/({a}x)}}:\ "
        rf"\frac{{{b}/(\sin {scaled(b)}x\cos {scaled(b)}x)}}{{-1/({a}x^2)}}\to0.",
        "+",
    )


# Exam family: parameters that make a two-branch function differentiable.


def differentiable_join(a: int, b: int, c: int) -> Built:
    p, q = a + b, sp.Integer(1)
    return finish(
        r"\text{Find }p,q\text{ so that }f\text{ is differentiable at }0:\quad "
        rf"f(x)=\begin{{cases}}e^{{{scaled(a)}x}}+{scaled(b)}x,&x\le0\\x^2+px+q,&x>0"
        r"\end{cases}.",
        OrderedAnswer((FormulaAnswer(p), FormulaAnswer(q)), JOIN),
        r"\text{Continuity matches the values at }0\text{; differentiability matches the}"
        r"\text{ one-sided derivatives.}",
        rf"f(0^-)=1=q,\qquad f'_-(0)={a}+{b}=f'_+(0)=p.",
    )
