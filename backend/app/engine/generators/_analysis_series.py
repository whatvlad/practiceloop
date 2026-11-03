"""Numerical/power series, convergence certificates and analytic expansions."""

from functools import cache
from typing import Any

import sympy as sp

from app.engine.blocks.analysis_two import AnalysisTwoData, AnalysisTwoForm, B, N, X, finish


def _p_integral(p: int) -> Any:
    return sp.limit(sp.log(B) if p == 1 else (1 - B ** (1 - p)) / (p - 1), B, sp.oo)


@cache
def evaluate(kind: str, form: AnalysisTwoForm) -> AnalysisTwoData:
    a, b, c = map(sp.Integer, (form.a, form.b, form.c))
    details: tuple[str, ...]
    symbolic = False
    if kind == "series-p-test":
        p = 1 + form.c % 3
        expected = int(p > 1)
        proof = int(_p_integral(p).is_finite is True)
        prompt = (
            rf"Does \(\sum_{{n=1}}^\infty 1/n^{{{p}}}\) converge? "
            "Enter 1 for yes, 0 for no."
        )
        details = (
            rf"x^{{-{p}}}>0\text{{ and decreases for }}x\geq1",
            rf"\int_1^\infty x^{{-{p}}}\,dx={sp.latex(_p_integral(p))}",
        )
    elif kind == "series-term-test":
        amplitude = sp.limit(N / (N + a), N, sp.oo)
        expected, proof = 0, int(amplitude == 0)
        prompt = (
            rf"Does \(\sum_{{n=1}}^\infty (-1)^n n/(n+{a})\) converge? "
            "Enter 1 for yes, 0 for no."
        )
        details = (
            rf"n/(n+{a})\longrightarrow1",
            r"u_{2n}\to1,\quad u_{2n+1}\to-1",
            r"u_n\not\to0\implies\text{the series diverges}",
        )
    elif kind == "series-alternating":
        p = 1 + form.c % 2
        absolute = _p_integral(p).is_finite is True
        expected = 1 if p > 1 else 2
        proof = 1 if absolute else 2
        prompt = (
            rf"Classify \(\sum_{{n=1}}^\infty (-1)^{{n+1}}/n^{{{p}}}\): "
            "enter 1 for absolute convergence, 2 for conditional convergence."
        )
        details = (
            rf"b_n=n^{{-{p}}}>0,\quad b_{{n+1}}<b_n,\quad b_n\to0",
            r"\text{Leibniz: the alternating series converges}",
            rf"\sum |u_n|=\sum n^{{-{p}}};\quad p={p}",
        )
    elif kind == "series-comparison":
        expected = 1
        proof = int(sp.limit(N**2 / (N**2 + a), N, sp.oo) == 1)
        prompt = (
            rf"Use comparison for \(\sum_{{n=1}}^\infty 1/(n^2+{a})\). "
            "Enter 1 for convergence, 0 for divergence."
        )
        details = (
            rf"0<\frac1{{n^2+{a}}}\leq\frac1{{n^2}}",
            r"\sum n^{-2}\text{ converges, so comparison applies}",
        )
    elif kind == "series-root-test":
        q = a / (a + 1)
        expected = q
        proof = sp.limit((q**N / N) ** (1 / N), N, sp.oo)
        prompt = (
            rf"For \(u_n=({sp.latex(q)})^n/n\), find "
            r"\(\lim_{n\to\infty}\sqrt[n]{|u_n|}\) for the root test."
        )
        details = (
            rf"\sqrt[n]{{|u_n|}}={sp.latex(q)}\,n^{{-1/n}}",
            rf"n^{{-1/n}}\to1,\quad0<{sp.latex(q)}<1",
        )
    elif kind == "series-ratio-test":
        expected = 0
        proof = sp.limit(a / (N + 1), N, sp.oo)
        prompt = (
            rf"For \(u_n={a}^n/n!\), find "
            r"\(\lim_{n\to\infty}|u_{n+1}/u_n|\) for the ratio test."
        )
        details = (
            rf"\left|u_{{n+1}}/u_n\right|={a}/(n+1)\longrightarrow0<1",
            r"\sum u_n\text{ converges absolutely}",
        )
    elif kind == "series-log-test":
        p = 1 + form.c % 2
        upper = sp.log(sp.log(B)) if p == 1 else -1 / sp.log(B)
        value = sp.limit(upper - upper.subs(B, 2), B, sp.oo)
        expected, proof = int(p > 1), int(value.is_finite is True)
        prompt = (
            rf"Does \(\sum_{{n=2}}^\infty 1/(n(\ln n)^{{{p}}})\) converge? "
            "Enter 1 for yes, 0 for no."
        )
        details = (
            r"f(x)>0,\quad f'(x)<0\quad(x\geq2)",
            rf"\int_2^\infty\frac{{dx}}{{x(\ln x)^{{{p}}}}}={sp.latex(value)}",
        )
    elif kind == "series-power-radius":
        expected = 1 / a
        root = a * sp.exp(-sp.limit(b * sp.log(N + 1) / N, N, sp.oo))
        proof = 1 / root
        prompt = (
            r"Use Cauchy-Hadamard to find the radius of convergence of "
            rf"\(\sum_{{n=1}}^\infty {a}^n(x-{b})^n/(n+1)^{{{b}}}\)."
        )
        details = (
            rf"\sqrt[n]{{|c_n|}}={a}(n+1)^{{-{b}/n}}\longrightarrow {a}",
            rf"R=1/\limsup\sqrt[n]{{|c_n|}}=1/{a}",
        )
    elif kind == "series-power-interval":
        p = form.c % 3
        left = sp.limit(1 / N**p, N, sp.oo) == 0
        right = _p_integral(p).is_finite is True
        expected = (1 if p > 0 else 0) + (2 if p > 1 else 0)
        proof = int(left) + 2 * int(right)
        lo, hi = b - 1 / a, b + 1 / a
        interval = f"{'[' if left else '('}{sp.latex(lo)},{sp.latex(hi)}{']' if right else ')'}"
        prompt = (
            rf"For \(\sum_{{n=1}}^\infty {a}^n(x-{b})^n/n^{{{p}}}\), "
            "which convergence-interval endpoints are included? "
            "Enter 0 for neither, 1 for left only, 2 for right only, 3 for both."
        )
        details = (
            rf"|{a}(x-{b})|<1\iff {sp.latex(lo)}<x<{sp.latex(hi)}",
            rf"x={sp.latex(lo)}:\ \sum(-1)^n/n^{{{p}}}",
            rf"x={sp.latex(hi)}:\ \sum1/n^{{{p}}}",
            rf"I={interval}",
        )
    elif kind == "series-entire":
        expected = 1
        limit = sp.limit(sp.Abs(a * (X - b)) / (N + 1), N, sp.oo)
        proof = int(limit == 0)
        prompt = (
            rf"Does \(\sum_{{n=0}}^\infty {a}^n(x-{b})^n/n!\) "
            "converge for every real x? Enter 1 for yes, 0 for no."
        )
        details = (
            rf"|u_{{n+1}}/u_n|=|{a}(x-{b})|/(n+1)\longrightarrow0",
            r"R=\infty,\quad I=\mathbb R",
        )
    elif kind == "series-taylor":
        degree = 1 + form.c % 3
        function = sp.exp(a * (X - b))
        expected = sp.expand(sum(a**k * (X - b) ** k / sp.factorial(k) for k in range(degree + 1)))
        proof = sp.expand(sp.series(function, X, b, degree + 1).removeO())
        symbolic = True
        prompt = (
            rf"Find the Taylor polynomial through degree {degree} of "
            rf"\(f(x)=e^{{{a}(x-{b})}}\) about \(x={b}\)."
        )
        details = (
            rf"f^{{(n)}}({b})={a}^n",
            rf"f(x)=\sum_{{n=0}}^\infty\frac{{{a}^n(x-{b})^n}}{{n!}},\quad x\in\mathbb R",
        )
    elif kind in {"series-maclaurin-sine", "series-maclaurin-cosine"}:
        m = 1 + form.c % 3
        sine = kind == "series-maclaurin-sine"
        degree = 2 * m + int(sine)
        function = sp.sin(a * X) if sine else sp.cos(a * X)
        expected = sum(
            (-1) ** k * (a * X) ** (2 * k + int(sine)) / sp.factorial(2 * k + int(sine))
            for k in range(m + 1)
        )
        proof = sp.series(function, X, 0, degree + 1).removeO()
        symbolic = True
        prompt = (
            rf"Find the Maclaurin polynomial through degree {degree} of "
            rf"\(f(x)={sp.latex(function)}\)."
        )
        power = "2n+1" if sine else "2n"
        details = (
            rf"f(x)=\sum_{{n=0}}^\infty\frac{{(-1)^n({a}x)^{{{power}}}}}{{({power})!}}",
            r"R=\infty;\quad\text{retain powers up to the requested degree}",
        )
    elif kind == "series-maclaurin-log":
        degree = form.c
        expected = sp.Rational((-1) ** (degree + 1) * form.a**degree, degree)
        proof = sp.diff(sp.log(1 + a * X), X, degree).subs(X, 0) / sp.factorial(degree)
        prompt = (
            rf"Find the coefficient of \(x^{{{degree}}}\) in the Maclaurin "
            rf"series of \(\ln(1+{a}x)\)."
        )
        details = (
            rf"\ln(1+{a}x)=\sum_{{n=1}}^\infty\frac{{(-1)^{{n+1}}({a}x)^n}}{{n}}",
            rf"|{a}x|<1,\quad [x^n]f=\frac{{(-1)^{{n+1}}{a}^n}}{{n}}",
        )
    else:
        raise ValueError("Unknown series form")
    return finish(prompt, expected, proof, details, symbolic=symbolic)
