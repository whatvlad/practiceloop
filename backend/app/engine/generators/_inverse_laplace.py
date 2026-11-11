"""Inverse Laplace transforms and forced IVPs from AM2A/14.3–14.4."""

from dataclasses import replace

import sympy as sp

from app.engine.answers.computational import OrderedAnswer, RealSetAnswer
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._laplace_transforms import S, T, right_of
from app.engine.generators._separable_odes import visual
from app.engine.generators._sequence_limits import finish

TIME = sp.Interval(0, sp.oo)
RESPONSE = ("Time function", "Convergence set")


def response(
    statement: str,
    value: sp.Expr,
    boundary: int,
    derivation: str,
    inversion: str,
) -> Built:
    convergence = right_of(boundary)
    answer = OrderedAnswer(
        (
            DomainFormulaAnswer(value, TIME, "t"),
            RealSetAnswer(convergence),
        ),
        RESPONSE,
    )
    built = finish(
        statement + r"\quad\text{Give the exact continuous time function for }t\ge0"
        r"\text{ and the real convergence set of its Laplace transform.}",
        answer,
        derivation,
        inversion + rf"\quad f(t)={tex(value)},\quad s\in{tex(convergence)}.",
    )
    evaluate = sp.lambdify(T, value, "math")
    return replace(
        built,
        visual=visual(
            [("Time function", 0, 1.1, evaluate)], [("At zero", 0, float(value.subs(T, 0)))]
        ),
    )


def inverse(
    value: sp.Expr, transform: sp.Expr, boundary: int, derivation: str, detail: str
) -> Built:
    return response(
        rf"\text{{Invert the Laplace transform }}F(s)={tex(transform)}.",
        value,
        boundary,
        derivation,
        detail,
    )


def inverse_simple_pole(a: int, b: int, c: int) -> Built:
    return inverse(
        (b + c) * sp.exp(-a * T),
        (b + c) / (S + a),
        -a,
        r"\mathcal L\{e^{\lambda t}\}=1/(s-\lambda)\quad(s>\lambda).",
        rf"\lambda=-{a}\text{{, and the numerator is a constant factor.}}",
    )


def inverse_shifted_numerator(a: int, b: int, c: int) -> Built:
    denominator = S**2 + 2 * c * S + c * c + b * b
    value = sp.exp(-c * T) * (a * sp.cos(b * T) + sp.Rational(b - a * c, b) * sp.sin(b * T))
    return inverse(
        value,
        (a * S + b) / denominator,
        -c,
        rf"q=s+{c},\quad F(s)=\frac{{{a}q+({b - a * c})}}{{q^2+{b * b}}}.",
        r"\text{Invert the cosine and sine terms, then multiply by the exponential shift.}",
    )


def inverse_distinct_real(a: int, b: int, c: int) -> Built:
    transform = c / ((S - a) * (S - a - b))
    fraction = sp.Rational(c, b)
    value = fraction * (sp.exp((a + b) * T) - sp.exp(a * T))
    return inverse(
        value,
        transform,
        a + b,
        rf"F(s)={tex(fraction)}\left(\frac1{{s-{a + b}}}-\frac1{{s-{a}}}\right).",
        r"\text{Both simple-pole terms are present, so the larger pole determines convergence.}",
    )


def inverse_real_and_complex(a: int, b: int, c: int) -> Built:
    transform = (S + a + b) / ((S + a) * (S - b) * (S * S + c * c))
    left = -sp.Rational(b, (a + b) * (a * a + c * c))
    right = sp.Rational(a + 2 * b, (a + b) * (b * b + c * c))
    cos = -left - right
    sin = a * left - b * right
    value = (
        left * sp.exp(-a * T)
        + right * sp.exp(b * T)
        + cos * sp.cos(c * T)
        + (sin / c) * sp.sin(c * T)
    )
    partial = left / (S + a) + right / (S - b) + (cos * S + sin) / (S * S + c * c)
    return inverse(
        value,
        transform,
        b,
        rf"\text{{Match the real-pole residues and the remaining quadratic numerator. }}"
        rf"F(s)={tex(partial)}.",
        r"\text{Invert the real poles and the sine-cosine pair separately.}",
    )


def inverse_repeated_symmetric_poles(a: int, b: int, c: int) -> Built:
    transform = c * (S * S + b * b) / (S * S * (S * S - a * a) ** 2)
    first = sp.Rational(c * b * b, a**4)
    third = c + first * a * a
    sinh_factor = -first / a - third / (2 * a**3)
    cosh_factor = third / (2 * a * a)
    value = (
        first * T
        + (cosh_factor * T + sinh_factor) * sp.exp(a * T) / 2
        + (cosh_factor * T - sinh_factor) * sp.exp(-a * T) / 2
    )
    return inverse(
        value,
        transform,
        a,
        rf"F(s)=\frac{{{tex(first)}}}{{s^2}}"
        rf"-\frac{{{tex(first)}}}{{s^2-{a * a}}}"
        rf"+\frac{{{tex(third)}}}{{(s^2-{a * a})^2}}.",
        rf"\mathcal L^{{-1}}\{{(s^2-{a * a})^{{-2}}\}}"
        rf"=\frac{{{a}t\cosh({a}t)-\sinh({a}t)}}{{{2 * a**3}}}."
        r"\quad\text{Write the hyperbolic functions in exponentials.}",
    )


def inverse_completed_square(a: int, b: int, c: int) -> Built:
    frequency = a + b
    transform = (S + c + frequency) / ((S + c) ** 2 + frequency**2)
    value = sp.exp(-c * T) * (sp.cos(frequency * T) + sp.sin(frequency * T))
    return inverse(
        value,
        transform,
        -c,
        rf"\text{{The denominator is }}(s+{c})^2+{frequency**2}"
        rf"\text{{ and the numerator splits as }}(s+{c})+{frequency}.",
        r"\text{The two numerators match shifted cosine and sine transforms.}",
    )


def forced(
    equation: str,
    initial: str,
    value: sp.Expr,
    transform: sp.Expr,
    boundary: int,
    inversion: str,
    *,
    second_order: bool = False,
) -> Built:
    derivative = r"\mathcal L\{y'\}=sY-y(0)."
    if second_order:
        derivative += r"\quad\mathcal L\{y''\}=s^2Y-sy(0)-y'(0)."
    return response(
        rf"\text{{Solve by Laplace transforms }}{equation},\quad {initial}.",
        value,
        boundary,
        derivative + rf"\quad Y(s)={tex(transform)}.",
        inversion,
    )


def laplace_constant_forcing(a: int, b: int, c: int) -> Built:
    offset = sp.Rational(b, a)
    y = (c + offset) * sp.exp(a * T) - offset
    return forced(
        rf"y'-{a}y={b}",
        rf"y(0)={c}",
        y,
        (c + b / S) / (S - a),
        a,
        rf"Y(s)=\frac{{{tex(c + offset)}}}{{s-{a}}}-\frac{{{tex(offset)}}}s.",
    )


def laplace_sine_forcing(a: int, b: int, c: int) -> Built:
    den = a * a + c * c
    y = sp.Rational(b, den) * (c * sp.exp(a * T) - a * sp.sin(c * T) - c * sp.cos(c * T))
    return forced(
        rf"y'-{a}y={b}\sin({c}t)",
        r"y(0)=0",
        y,
        b * c / ((S * S + c * c) * (S - a)),
        a,
        rf"\text{{The residue at }}s={a}\text{{ is }}{tex(sp.Rational(b * c, den))}."
        r"\quad\text{The remaining quadratic numerator gives the sine and cosine terms.}",
    )


def laplace_velocity_decay(a: int, b: int, c: int) -> Built:
    offset = sp.Rational(c, a)
    y = b + offset * (1 - sp.exp(-a * T))
    return forced(
        rf"y''+{a}y'=0",
        rf"y(0)={b},\quad y'(0)={c}",
        y,
        (b * S + c + a * b) / (S * (S + a)),
        0,
        rf"Y(s)=\frac{{{tex(b + offset)}}}s-\frac{{{tex(offset)}}}{{s+{a}}}.",
        second_order=True,
    )


def laplace_resonant_decay(a: int, b: int, c: int) -> Built:
    baseline = sp.Rational(b - c * a, a * a)
    y = baseline - (baseline + sp.Rational(b, a) * T) * sp.exp(-a * T)
    transform = (b / (S + a) - c) / (S * (S + a))
    detail = (
        r"\text{The constant term vanishes for these parameters, leaving a repeated pole.}"
        if baseline == 0
        else r"\text{The nonzero constant term has a pole at }s=0."
    )
    return forced(
        rf"y''+{a}y'={b}e^{{-{a}t}}",
        rf"y(0)=0,\quad y'(0)=-{c}",
        y,
        transform,
        -a if baseline == 0 else 0,
        rf"Y(s)=\frac{{{tex(baseline)}}}s-\frac{{{tex(baseline)}}}{{s+{a}}}"
        rf"-\frac{{{tex(sp.Rational(b, a))}}}{{(s+{a})^2}}.\quad" + detail,
        second_order=True,
    )


def laplace_growing_oscillator(a: int, b: int, c: int) -> Built:
    d = a * a + b * b - c * c
    den = d * d + 4 * a * a * c * c
    sin = sp.Rational(d, den)
    cos = sp.Rational(2 * a * c, den)
    transient = (1 - c * sin + a * cos) / b
    y = (
        sin * sp.sin(c * T)
        + cos * sp.cos(c * T)
        + sp.exp(a * T) * (-cos * sp.cos(b * T) + transient * sp.sin(b * T))
    )
    transform = (1 + c / (S * S + c * c)) / ((S - a) ** 2 + b * b)
    return forced(
        rf"y''-{2 * a}y'+{a * a + b * b}y=\sin({c}t)",
        r"y(0)=0,\quad y'(0)=1",
        y,
        transform,
        a,
        r"\text{Split }Y\text{ over the forcing and shifted oscillator quadratics.}"
        rf"\quad\text{{The forcing coefficients are }}{tex(sin)}\text{{ and }}{tex(cos)}"
        r"\text{ for sine and cosine. The shifted pair supplies the initial data.}",
        second_order=True,
    )


def laplace_affine_acceleration(a: int, b: int, c: int) -> Built:
    quadratic = -sp.Rational(c, 4 * a)
    linear = (2 * quadratic - b) / (2 * a)
    exponential = -linear / (2 * a)
    y = quadratic * T * T + linear * T + exponential * (sp.exp(2 * a * T) - 1)
    return forced(
        rf"y''-{2 * a}y'={b}+{c}t",
        r"y(0)=0,\quad y'(0)=0",
        y,
        (b / S + c / S**2) / (S * (S - 2 * a)),
        2 * a,
        r"\text{Split at the repeated zero pole and the simple positive pole.}"
        rf"\quad\text{{The coefficients of }}t^2,t,e^{{{2 * a}t}}-1"
        rf"\text{{ are }}{tex(quadratic)},{tex(linear)},{tex(exponential)}.",
        second_order=True,
    )


def laplace_repeated_root(a: int, b: int, c: int) -> Built:
    k = b * c
    quadratic = sp.Rational(k, a * a)
    linear = -sp.Rational(4 * k, a**3)
    offset = sp.Rational(6 * k, a**4)
    decay = -sp.Rational(2 * k, a**3)
    y = quadratic * T * T + linear * T + offset + (decay * T - offset) * sp.exp(-a * T)
    return forced(
        rf"y''+{2 * a}y'+{a * a}y={k}t^2",
        r"y(0)=0,\quad y'(0)=0",
        y,
        2 * k / (S**3 * (S + a) ** 2),
        0,
        r"\text{The zero pole produces a quadratic and the repeated negative pole produces}"
        r" a linear factor times an exponential.}"
        rf"\quad\text{{The quadratic, linear and constant coefficients are }}"
        rf"{tex(quadratic)},{tex(linear)},{tex(offset)}.",
        second_order=True,
    )


def laplace_damped_exponential_forcing(a: int, b: int, c: int) -> Built:
    shift = a - c
    den = shift * shift + b * b
    slope = sp.Rational(1, den)
    offset = -sp.Rational(2 * shift, den**2)
    sin = (2 - slope - shift * offset) / b
    y = (slope * T + offset) * sp.exp(-c * T) + sp.exp(-a * T) * (
        -offset * sp.cos(b * T) + sin * sp.sin(b * T)
    )
    return forced(
        rf"y''+{2 * a}y'+{a * a + b * b}y=t e^{{-{c}t}}",
        r"y(0)=0,\quad y'(0)=2",
        y,
        (2 + 1 / (S + c) ** 2) / ((S + a) ** 2 + b * b),
        -min(a, c),
        rf"\text{{The double pole at }}-{c}\text{{ contributes }}e^{{-{c}t}}"
        rf"\left({tex(slope)}t+({tex(offset)})\right)."
        r"\quad\text{The remaining conjugate pair gives the damped sine and cosine terms.}",
        second_order=True,
    )
