"""First-kind improper integrals, exact convergence certificates and applications."""

from functools import cache

import sympy as sp

from app.engine.blocks.analysis_two import AnalysisTwoData, AnalysisTwoForm, B, X, finish


@cache
def evaluate(kind: str, form: AnalysisTwoForm) -> AnalysisTwoData:
    a, b, c = map(sp.Integer, (form.a, form.b, form.c))
    details: tuple[str, ...]
    if kind == "improper-p-test":
        p = 1 + form.c % 3
        finite = sp.log(B) if p == 1 else (1 - B ** (1 - p)) / (p - 1)
        value = sp.limit(finite, B, sp.oo)
        expected = int(p > 1)
        proof = int(value.is_finite is True)
        prompt = rf"Does \(\int_1^\infty x^{{-{p}}}\,dx\) converge? Enter 1 for yes, 0 for no."
        details = (
            rf"\int_1^B x^{{-{p}}}\,dx={sp.latex(finite)}",
            rf"B\to\infty:\quad {sp.latex(value)}",
        )
    elif kind == "improper-power-tail":
        expected = a / (c * b**c)
        primitive = -a / (c * X**c)
        if sp.simplify(sp.diff(primitive, X) - a / X ** (c + 1)) != 0:
            raise ValueError("Power-tail primitive failed")
        proof = sp.limit(primitive, X, sp.oo) - primitive.subs(X, b)
        prompt = rf"Evaluate \(\int_{{{b}}}^\infty \frac{{{a}}}{{x^{{{c + 1}}}}}\,dx\)."
        details = (
            rf"F(x)={sp.latex(primitive)},\quad x\geq {b}>0",
            rf"\lim_{{B\to\infty}}(F(B)-F({b}))={sp.latex(expected)}",
        )
    elif kind == "improper-exponential":
        expected = sp.exp(-a * b) / a
        primitive = -sp.exp(-a * X) / a
        proof = sp.limit(primitive, X, sp.oo) - primitive.subs(X, b)
        prompt = rf"Evaluate \(\int_{{{b}}}^\infty e^{{-{a}x}}\,dx\)."
        details = (rf"F(x)={sp.latex(primitive)}", rf"e^{{-{a}B}}\longrightarrow0\quad(B\to\infty)")
    elif kind == "improper-comparison":
        ratio = sp.limit(X**2 / (X**2 + b), X, sp.oo)
        expected = 1
        proof = int(ratio == 1 and sp.limit(1 - 1 / B, B, sp.oo).is_finite is True)
        prompt = (
            r"Use limit comparison to decide whether "
            rf"\(\int_1^\infty\frac1{{x^2+{b}}}\,dx\) converges. "
            "Enter 1 for yes, 0 for no."
        )
        details = (
            r"x\geq1:\quad f(x)>0,\quad g(x)=x^{-2}>0",
            rf"\lim_{{x\to\infty}}\frac{{f(x)}}{{g(x)}}=\lim_{{x\to\infty}}\frac{{x^2}}{{x^2+{b}}}=1",
            r"\int_1^\infty x^{-2}\,dx=1<\infty",
        )
    elif kind == "improper-arctangent":
        expected = a / b * (sp.pi / 2 - sp.atan(c / b))
        primitive = a / b * sp.atan(X / b)
        if sp.simplify(sp.diff(primitive, X) - a / (X**2 + b**2)) != 0:
            raise ValueError("Arctangent primitive failed")
        proof = sp.limit(primitive, X, sp.oo) - primitive.subs(X, c)
        prompt = rf"Evaluate \(\int_{{{c}}}^\infty\frac{{{a}}}{{x^2+{b**2}}}\,dx\)."
        details = (rf"F(x)={sp.latex(primitive)}", rf"\lim_{{x\to\infty}}\arctan(x/{b})=\pi/2")
    elif kind == "improper-log-test":
        p = 1 + form.c % 3
        transformed = sp.log(B) if p == 1 else (1 - B ** (1 - p)) / (p - 1)
        value = sp.limit(transformed, B, sp.oo)
        expected, proof = int(p > 1), int(value.is_finite is True)
        prompt = (
            rf"Does \(\int_e^\infty\frac1{{x(\ln x)^{{{p}}}}}\,dx\) converge? "
            "Enter 1 for yes, 0 for no."
        )
        details = (
            r"u=\ln x,\quad du=dx/x,\quad u\in[1,\infty)",
            rf"\int_1^\infty u^{{-{p}}}\,du={sp.latex(value)}",
        )
    elif kind == "improper-divergence":
        primitive = sp.log(X**2 + a) / 2
        limit = sp.limit(primitive - primitive.subs(X, 1), X, sp.oo)
        expected, proof = 0, int(limit.is_finite is True)
        prompt = (
            r"Use limit comparison to decide whether "
            rf"\(\int_1^\infty\frac{{x}}{{x^2+{a}}}\,dx\) converges. "
            "Enter 1 for yes, 0 for no."
        )
        details = (
            rf"\lim_{{x\to\infty}}\frac{{x/(x^2+{a})}}{{1/x}}=1",
            r"\int_1^B dx/x=\ln B\longrightarrow+\infty",
        )
    elif kind == "improper-decay-mass":
        expected = sp.exp(-a * b)
        primitive = -sp.exp(-a * X)
        proof = sp.limit(primitive, X, sp.oo) - primitive.subs(X, b)
        prompt = (
            rf"A rod on \(x\geq0\) has linear density \(\rho(x)={a}e^{{-{a}x}}\). "
            rf"Find its mass beyond \(x={b}\)."
        )
        details = (
            rf"M=\int_{{{b}}}^\infty {a}e^{{-{a}x}}\,dx",
            rf"M=\lim_{{B\to\infty}}[-e^{{-{a}x}}]_{{{b}}}^B",
        )
    elif kind == "improper-volume":
        expected = sp.pi * a**2
        proof = sp.limit(sp.pi * a**2 * (1 - 1 / B), B, sp.oo)
        prompt = (
            rf"Rotate \(y={a}/x,\ x\geq1\), about the x axis. "
            "Find the volume of the resulting unbounded solid."
        )
        details = (
            rf"A(x)=\pi y^2=\frac{{{a**2}\pi}}{{x^2}}",
            rf"V=\lim_{{B\to\infty}}\int_1^B\frac{{{a**2}\pi}}{{x^2}}\,dx",
            rf"V=\lim_{{B\to\infty}}{a**2}\pi(1-1/B)={sp.latex(expected)}",
        )
    else:
        raise ValueError("Unknown improper-integral form")
    return finish(prompt, expected, proof, details)
