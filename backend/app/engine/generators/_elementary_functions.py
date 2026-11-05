"""Whole natural domains, parity, four compositions and branch-aware inverses."""

import sympy as sp

from app.engine.answers.computational import (
    CategoryAnswer,
    ComputationalAnswer,
    OrderedAnswer,
    RealSetAnswer,
)
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.generators._elementary_common import (
    Built,
    ElementaryParams,
    X,
    finish,
    tex,
)
from app.engine.models import Answer


def evaluate(template: str, p: ElementaryParams) -> Built:
    a, b, c, v = p.a, p.b, p.c, p.variant
    x = X
    answer: Answer
    if template.startswith("domain-"):
        if template == "domain-rational":
            formula = rf"\frac{{{c}x}}{{(x-{a})(x+{b})}}"
            domain = sp.S.Reals - sp.FiniteSet(-b, a)
            method = rf"(x-{a})(x+{b})\ne 0\iff x\ne {a},\ x\ne {-b}."
        elif template == "domain-quartic-root":
            formula = rf"\sqrt{{{a**4}-x^4}}"
            domain = sp.Interval(-a, a)
            method = rf"x^4\le {a**4}\iff |x|\le {a}."
        elif template == "domain-root-quotient":
            formula = rf"\frac{{\sqrt{{{b}-x}}}}{{\sqrt{{x+{a}}}}}"
            domain = sp.Interval.Lopen(-a, b)
            method = rf"{b}-x\ge0,\quad x+{a}>0."
        elif template == "domain-root-rational":
            formula = rf"\frac{{\sqrt{{{a}-x}}}}{{x^2+{b}}}"
            domain = sp.Interval(-sp.oo, a)
            method = rf"x^2+{b}>0\text{{ on all reals}};\quad {a}-x\ge0."
        elif template == "domain-exponential-root":
            formula = rf"\exp\left(\sqrt{{{b * b}-(x-{a})^2}}\right)"
            domain = sp.Interval(a - b, a + b)
            method = rf"{b * b}-(x-{a})^2\ge0\iff |x-{a}|\le {b}."
        elif template == "domain-quadratic-rational":
            sign = 1 if v % 2 else -1
            formula = rf"\frac{{x(x+({sign * a}))}}{{x+({sign * b})}}"
            domain = sp.S.Reals - sp.FiniteSet(-sign * b)
            method = (
                rf"x+({sign * b})\ne0;\quad\text{{retain this exclusion even if a factor cancels.}}"
            )
        elif template == "domain-log-ratio":
            formula = rf"\log\left(\frac{{x-{a}}}{{x+{b}}}\right)"
            domain = sp.Union(sp.Interval.open(-sp.oo, -b), sp.Interval.open(a, sp.oo))
            method = (
                rf"\frac{{x-{a}}}{{x+{b}}}>0,\quad x\ne {-b};"
                r"\quad \text{numerator and denominator have the same sign.}"
            )
        elif template == "domain-arcsin-affine":
            formula = rf"\arcsin({a}x-{b})"
            domain = sp.Interval(sp.Rational(b - 1, a), sp.Rational(b + 1, a))
            method = rf"-1\le {a}x-{b}\le1."
        elif template == "domain-arccos-square":
            q = sp.Rational(v + 1, 8)
            formula = rf"\arccos\left((x-{a})^2+{tex(q)}\right)"
            radius = sp.sqrt(1 - q)
            domain = sp.Interval(a - radius, a + radius)
            method = rf"-1\le (x-{a})^2+{tex(q)}\le1\iff |x-{a}|\le {tex(radius)}."
        elif template == "domain-arcsin-square":
            formula = rf"\arcsin(x^2-{a})"
            domain = sp.Union(
                sp.Interval(-sp.sqrt(a + 1), -sp.sqrt(a - 1)),
                sp.Interval(sp.sqrt(a - 1), sp.sqrt(a + 1)),
            )
            method = rf"-1\le x^2-{a}\le1\iff {a - 1}\le x^2\le {a + 1}."
        elif template == "domain-arctan-rational":
            formula = rf"\arctan\left(\frac{{{b}}}{{x-{a}}}\right)"
            domain = sp.S.Reals - sp.FiniteSet(a)
            method = rf"\arctan\text{{ accepts every real input, but }}x\ne {a}."
        elif template == "domain-arccot-affine":
            formula = rf"\operatorname{{arccot}}({a}x+{b})"
            domain = sp.S.Reals
            method = r"\operatorname{arccot}:\mathbb{R}\longrightarrow(0,\pi)."
        else:
            raise ValueError(template)
        answer = RealSetAnswer(domain)
        return finish(
            f"Find the complete natural real domain of \\(f(x)={formula}\\).",
            answer,
            method,
            rf"D_f={tex(domain)}",
            (("Domain", domain),),
        )
    if template == "parity":
        choices = ("even", "odd", "neither")
        cases = (
            (sp.sqrt(x**6 + a), sp.S.Reals, "even"),
            (sp.Abs(x**7 + b * x**3 - c * x), sp.S.Reals, "even"),
            (a * x / (x**4 + b), sp.S.Reals, "odd"),
            (x + sp.Rational(a, 1) / x, sp.S.Reals - sp.FiniteSet(0), "odd"),
            (x**3 + a, sp.S.Reals, "neither"),
            (sp.sqrt(x + a), sp.Interval(-a, sp.oo), "neither"),
        )
        expression, domain, expected = cases[v]
        symmetric = domain == sp.imageset(sp.Lambda(x, -x), domain)
        calculation = rf"f(-x)={tex(expression.subs(x, -x))},\quad D_f={tex(domain)}."
        if not symmetric:
            calculation += r"\quad D_f\ne-D_f."
        return finish(
            f"Classify \\(f(x)={tex(expression)}\\) as even, odd, or neither "
            "on its natural domain.",
            CategoryAnswer(expected, choices),
            r"\text{First check domain symmetry, then compare }f(-x),f(x),-f(x).",
            calculation,
        )
    if template.startswith("composition-"):
        if template == "composition-affine":
            f, g = a * x - b, c * x + a
            domains = (sp.S.Reals,) * 4
        elif template == "composition-reciprocal-square":
            shift = (v % 3 - 1) * b
            f, g = a / x, x**2 + shift
            excluded = sp.S.Reals - sp.FiniteSet(0)
            zeros = sp.FiniteSet(-sp.sqrt(-shift), sp.sqrt(-shift)) if shift <= 0 else sp.S.EmptySet
            domains = (excluded, sp.S.Reals - zeros, excluded, sp.S.Reals)
        elif template == "composition-root-power":
            f, g = sp.sqrt(a * x), b * x**4
            domains = (sp.Interval(0, sp.oo), sp.S.Reals, sp.Interval(0, sp.oo), sp.S.Reals)
        elif template == "composition-abs-root":
            f, g = c * sp.Abs(x), sp.sqrt(b * x + a)
            domains = (
                sp.S.Reals,
                sp.Interval(-sp.Rational(a, b), sp.oo),
                sp.S.Reals,
                sp.Interval(-sp.Rational(a, b), sp.oo),
            )
        else:
            raise ValueError(template)
        expressions = (f.subs(x, f), f.subs(x, g), g.subs(x, f), g.subs(x, g))
        components: list[ComputationalAnswer] = []
        labels: list[str] = []
        derivations = []
        for name, expression, domain in zip(
            ("FF", "FG", "GF", "GG"), expressions, domains, strict=True
        ):
            components.extend((DomainFormulaAnswer(expression, domain), RealSetAnswer(domain)))
            labels.extend((name + " expression", name + " domain"))
            derivations.append(rf"{name}(x)={tex(expression)},\quad D_{{{name}}}={tex(domain)}")
        answer = OrderedAnswer(tuple(components), tuple(labels))
        return finish(
            rf"Given \(f(x)={tex(f)},\quad g(x)={tex(g)}\), find FF, FG, GF and GG, "
            "where FG means f after g. Give each expression and its full domain, "
            "in that order. Retain restrictions before simplifying.",
            answer,
            r"D_{f\circ g}=\{x\in D_g:g(x)\in D_f\}.",
            r"\begin{gathered}" + r"\\".join(derivations) + r"\end{gathered}",
            tuple(zip(("FF", "FG", "GF", "GG"), domains, strict=True)),
        )
    if template.startswith("inverse-"):
        if template == "inverse-mobius":
            expression = (x + a) / (x - b)
            inverse = (b * x + a) / (x - 1)
            source_domain, domain = sp.S.Reals - sp.FiniteSet(b), sp.S.Reals - sp.FiniteSet(1)
        elif template == "inverse-quadratic-branch":
            branch = 1 if v % 2 else -1
            expression = (x - a) ** 2 - b
            source_domain = sp.Interval(a, sp.oo) if branch > 0 else sp.Interval(-sp.oo, a)
            inverse, domain = a + branch * sp.sqrt(x + b), sp.Interval(-b, sp.oo)
        elif template == "inverse-negative-fourth":
            expression = -a * x**4
            inverse, domain, source_domain = (
                -(sp.Pow(-x / sp.Integer(a), sp.Rational(1, 4))),
                sp.Interval(-sp.oo, 0),
                sp.Interval(-sp.oo, 0),
            )
        elif template == "inverse-exponential":
            base = sp.Integer(c + 1) if v % 2 else sp.E
            expression = base ** (a * x - b)
            inverse, domain, source_domain = (
                (sp.log(x) / sp.log(base) + b) / a,
                sp.Interval.open(0, sp.oo),
                sp.S.Reals,
            )
        elif template == "inverse-logarithm":
            expression = sp.log(x + a) / sp.log(b + 1)
            inverse, domain, source_domain = (
                (b + 1) ** x - a,
                sp.S.Reals,
                sp.Interval.open(-a, sp.oo),
            )
        elif template == "inverse-semicircle-branch":
            expression = b - sp.sqrt(a * a - x * x)
            inverse = -sp.sqrt(a * a - (b - x) ** 2)
            source_domain, domain = sp.Interval(-a, 0), sp.Interval(b - a, b)
        else:
            raise ValueError(template)
        answer = OrderedAnswer(
            (
                DomainFormulaAnswer(inverse, domain),
                RealSetAnswer(domain),
                RealSetAnswer(source_domain),
            ),
            ("Inverse expression", "Inverse domain", "Inverse range"),
        )
        return finish(
            f"Find the inverse of \\(f(x)={tex(expression)}\\) "
            f"restricted to \\(D_f={tex(source_domain)}\\). Give its formula, domain and range.",
            answer,
            r"y=f(x)\text{; solve for the unique }x\in D_f\text{, then interchange variables.}",
            rf"f^{{-1}}(x)={tex(inverse)},\quad D_{{f^{{-1}}}}={tex(domain)},"
            rf"\quad R_{{f^{{-1}}}}={tex(source_domain)}.",
            (("Inverse domain", domain), ("Inverse range", source_domain)),
        )
    raise ValueError(template)
