"""Exact solution sets from bounded factorizations, sign charts and monotone logs."""

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, RealSetAnswer
from app.engine.generators._elementary_common import Built, ElementaryParams, finish, tex


def evaluate(template: str, p: ElementaryParams) -> Built:
    a, b, c, v = p.a, p.b, p.c, p.variant
    if template == "equation-repeated-polynomial":
        equation = rf"x(x-{a})^2=0"
        solution = sp.FiniteSet(0, a)
        method = rf"x=0\quad\text{{or}}\quad (x-{a})^2=0."
    elif template == "equation-biquadratic":
        equation = rf"x^4+({a - b})x^2-{a * b}=0"
        solution = sp.FiniteSet(-sp.sqrt(b), sp.sqrt(b))
        method = rf"t=x^2\ge0,\quad (t+{a})(t-{b})=0\Rightarrow t={b}."
    elif template == "equation-rational-linear":
        pole = sp.Rational(c, 2)
        equation = rf"\frac{{{a}}}{{2x-{c}}}+\frac{{{b}}}{{x-{tex(pole)}}}=1"
        solution = sp.FiniteSet(pole + sp.Rational(a, 2) + b)
        method = rf"x\ne {tex(pole)},\quad {a}+{2 * b}=2x-{c}."
    elif template == "equation-rational-cancel":
        equation = rf"\frac{{x^2-{a * a}}}{{x^3-{a**3}}}=\frac{{x^2+{a * a}}}{{x^3+{a**3}}}"
        solution = sp.FiniteSet(0)
        method = rf"x\ne\pm {a};\quad {2 * a * a}x^2({a}-x)=0.\quad x={a}\text{{ is excluded.}}"
    elif template == "inequality-squared-factors":
        equation = rf"(4x^2-{a * a})^2\le {b * b}(2x+{a})^2"
        solution = sp.Union(
            sp.FiniteSet(-sp.Rational(a, 2)),
            sp.Interval(sp.Rational(a - b, 2), sp.Rational(a + b, 2)),
        )
        method = rf"(2x+{a})^2\big((2x-{a})^2-{b * b}\big)\le0."
    elif template == "inequality-odd-polynomial":
        equation = rf"x^5+({b - a})x^3-{a * b}x\ge0"
        radius = sp.sqrt(a)
        solution = sp.Union(sp.Interval(-radius, 0), sp.Interval(radius, sp.oo))
        method = rf"x(x^2-{a})(x^2+{b})\ge0,\quad x^2+{b}>0."
    elif template == "inequality-rational-sign":
        equation = rf"\frac{{x(x-{a})}}{{x+{b}}}>0"
        solution = sp.Union(sp.Interval.open(-b, 0), sp.Interval.open(a, sp.oo))
        method = rf"x\ne {-b};\quad \text{{critical points: }}{-b}<0<{a}."
    elif template == "inequality-rational-subtract":
        equation = rf"\frac{{x^2+{a}x}}{{x-{b}}}>x"
        solution = sp.Union(sp.Interval.open(-sp.oo, 0), sp.Interval.open(b, sp.oo))
        method = rf"x\ne {b};\quad \frac{{{a + b}x}}{{x-{b}}}>0."
    elif template == "exponential-linear":
        base = a + 1
        equation = rf"{base}^{{{b}x-{c}}}={base ** (v + 1)}"
        solution = sp.FiniteSet(sp.Rational(c + v + 1, b))
        method = rf"{base}>1;\quad {b}x-{c}={v + 1}."
    elif template == "exponential-substitution":
        base = c + 1
        first, second = sp.Rational(a, base), sp.Rational(b, base)
        equation = rf"{base * base}\cdot {base}^{{2x}}-{base * (a + b)}\cdot {base}^x+{a * b}=0"
        solution = sp.FiniteSet(sp.log(first) / sp.log(base), sp.log(second) / sp.log(base))
        method = (
            rf"t={base}^x>0,\quad({base}t-{a})({base}t-{b})=0;"
            rf"\quad t\in\{{{tex(first)},{tex(second)}\}},\quad x=\log_{{{base}}}t."
        )
    elif template == "exponential-reciprocal-exponent":
        base = sp.Rational(1, a + 1)
        equation = rf"\left({tex(base)}\right)^{{(x+{b})/x}}<\left({tex(base)}\right)^{{{c}}}"
        solution = sp.Interval.open(0, sp.oo if c == 1 else sp.Rational(b, c - 1))
        method = (
            rf"x\ne0;\quad 0<{tex(base)}<1\Rightarrow\frac{{x+{b}}}x>{c}"
            rf"\iff\frac{{{b}-({c - 1})x}}x>0."
        )
    elif template == "exponential-mixed-bases":
        first, second = a + 1, c + 1
        equation = rf"{first}^{{x+{b}}}={second}^{{2x+{c}}}"
        denominator = sp.log(sp.Rational(first, second**2))
        numerator = c * sp.log(second) - b * sp.log(first)
        solution = sp.S.EmptySet if first == second**2 else sp.FiniteSet(numerator / denominator)
        method = rf"x\log\left({tex(sp.Rational(first, second**2))}\right)={tex(numerator)}."
    elif template == "exponential-product-inequality":
        first, second = a + 1, b + 1
        equation = rf"{first}^x\cdot {second}^{{x+{c}}}<({first * second})^{{2x}}"
        boundary = c * sp.log(second) / sp.log(first * second)
        solution = sp.Interval.open(boundary, sp.oo)
        method = rf"{c}\log({second})<x\log({first * second}),\quad \log({first * second})>0."
    elif template == "exponential-reciprocal-substitution":
        base = a + 1
        equation = rf"{base}^x-{base}^{{-x}}>{c}"
        root = (c + sp.sqrt(c * c + 4)) / 2
        solution = sp.Interval.open(sp.log(root) / sp.log(base), sp.oo)
        method = rf"t={base}^x>0;\quad t^2-{c}t-1>0\iff t>{tex(root)}."
    elif template == "exponential-rational-inequality":
        base = b + 1
        equation = rf"\frac1{{{base}^x-{a}}}<\frac1{{{base}^{{2x}}-{a * a}}}"
        solution = sp.Interval.open(-sp.oo, sp.log(a) / sp.log(base))
        method = (
            rf"t={base}^x>0,\ t\ne {a};\quad\frac{{t+{a - 1}}}{{(t-{a})(t+{a})}}<0\iff 0<t<{a}."
        )
    elif template.startswith("log-value-"):
        base = a + 1
        if template == "log-value-product":
            expression = (
                rf"\log_{{{base}}}({tex(sp.Rational(base**b, c))})+\log_{{{base}}}({c})"
                if v % 2
                else rf"\log_{{{base}}}({base**b * c})-\log_{{{base}}}({c})"
            )
            expected = sp.Integer(b)
            method = rf"\text{{Combine the logarithms: }}\log_{{{base}}}({base**b})={b}."
        elif template == "log-value-change-base":
            other = b + 1
            expression = rf"\log_{{{base}}}({other})\cdot\log_{{{other}}}({base**c})"
            expected = sp.Integer(c)
            method = (
                rf"\frac{{\log({other})}}{{\log({base})}}"
                rf"\frac{{{c}\log({base})}}{{\log({other})}}={c}."
            )
        elif template == "log-value-root":
            rational = sp.Rational(b, c)
            expression = rf"\log_{{{base}}}\left({tex(sp.Pow(base, rational))}\right)"
            expected = rational
            method = rf"\log_{{{base}}}\left({base}^{{{tex(rational)}}}\right)={tex(rational)}."
        else:
            expression = (
                rf"\frac{{\log_{{{base}}}({base ** (a + b)})-\log_{{{base}}}({base**b})}}"
                rf"{{\log_{{{base}}}({base ** (b + c)})-\log_{{{base}}}({base**b})}}"
            )
            expected = sp.Rational(a, c)
            method = rf"\frac{{({a + b})-{b}}}{{({b + c})-{b}}}=\frac{{{a}}}{{{c}}}."
        return finish(
            f"Compute exactly \\({expression}\\).",
            FormulaAnswer(expected),
            r"\text{All bases are positive and unequal to one; apply logarithm laws.}",
            method,
        )
    elif template == "log-equation-power":
        base = b + 1
        equation = rf"{a}\log_{{{base}}}x=\log_{{{base}}}({(c + 1) ** b})"
        root = sp.Pow(c + 1, sp.Rational(b, a))
        solution = sp.FiniteSet(root)
        method = rf"x>0;\quad x^{a}={(c + 1) ** b}\Rightarrow x={tex(root)}."
    elif template == "log-equation-difference":
        base, power = c + 1, (c + 1) ** (v + 1)
        equation = rf"\log_{{{base}}}(x+{a})-\log_{{{base}}}(x-{b})={v + 1}"
        solution = sp.FiniteSet(sp.Rational(a + b * power, power - 1))
        method = (
            rf"x>{b};\quad\frac{{x+{a}}}{{x-{b}}}={power}"
            rf"\iff x=\frac{{{a + b * power}}}{{{power - 1}}}>{b}."
        )
    elif template == "log-equation-quadratic":
        base, power = c + 1, (c + 1) ** b
        equation = rf"\log_{{{base}}}(x^2-{a * b})={b}+\log_{{{base}}}(x-{a})"
        discriminant = power * power - 4 * a * (power - b)
        roots = (
            ()
            if discriminant < 0
            else ((power - sp.sqrt(discriminant)) / 2, (power + sp.sqrt(discriminant)) / 2)
        )
        solution = sp.FiniteSet(*(root for root in roots if root > a))
        method = (
            rf"x>{a},\ x^2>{a * b};\quad x^2-{power}x+{a * (power - b)}=0,"
            rf"\quad\Delta={discriminant}.\quad\text{{Retain only real roots }}x>{a}."
        )
    elif template == "log-inequality-linear":
        base = sp.Rational(1, b + 1) if v % 2 else sp.Integer(b + 1)
        threshold = base**a
        equation = rf"\log_{{{tex(base)}}}({a}-{c}x)>{a}"
        solution = (
            sp.Interval.open(sp.Rational(a - threshold, c), sp.Rational(a, c))
            if v % 2
            else sp.Interval.open(-sp.oo, sp.Rational(a - threshold, c))
        )
        method = rf"{a}-{c}x>0;\quad {a}-{c}x{'<' if v % 2 else '>'}{tex(threshold)}."
    elif template == "log-inequality-difference":
        coefficient, ratio = a + 1, v + 1
        equation = rf"\log({coefficient}x-{b})-\log(x-{c})>\log({ratio})"
        lower = max(sp.Integer(c), sp.Rational(b, coefficient))
        domain = sp.Interval.open(lower, sp.oo)
        slope, constant = coefficient - ratio, b - ratio * c
        if slope == 0:
            solution = domain if constant < 0 else sp.S.EmptySet
        else:
            boundary = sp.Rational(constant, slope)
            half = (
                sp.Interval.open(boundary, sp.oo)
                if slope > 0
                else sp.Interval.open(-sp.oo, boundary)
            )
            solution = domain.intersect(half)
        method = (
            rf"x>{tex(lower)};\quad\frac{{{coefficient}x-{b}}}{{x-{c}}}>{ratio}"
            rf"\iff ({slope})x>{constant}."
        )
    elif template == "log-inequality-opposite-bases":
        base, power = c + 1, (c + 1) ** v
        equation = rf"\log_{{{base}}}(x-{a})+\log_{{1/{base}}}(2x-{b})>{v}"
        lower = max(sp.Integer(a), sp.Rational(b, 2))
        upper = sp.Rational(a - power * b, 1 - 2 * power)
        solution = sp.Interval.open(lower, upper) if upper > lower else sp.S.EmptySet
        method = rf"x>{tex(lower)};\quad \frac{{x-{a}}}{{2x-{b}}}>{power}\iff x<{tex(upper)}."
    else:
        raise ValueError(template)
    answer = RealSetAnswer(solution)
    return finish(
        f"Find all real solutions of \\({equation}\\).",
        answer,
        r"\text{First retain the original domain, then use exact factorization or monotonicity.}",
        method,
        (("Solutions", solution),),
    )
