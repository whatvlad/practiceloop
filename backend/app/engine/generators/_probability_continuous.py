"""Certified continuous densities and supplied-table normal questions."""

from fractions import Fraction as F
from typing import Any

import sympy as sp

from app.engine.answers.structured import IntervalAnswer
from app.engine.blocks.distribution import (
    DensitySegment,
    ExponentialDistribution,
    NormalDistribution,
    PolynomialDensity,
    UniformDistribution,
)
from app.engine.blocks.statistics import NORMAL_CDF
from app.engine.generators._probability_common import Built, ProbabilityParams, finish, scalar, tex

REASONS = {
    "continuous-uniform": (
        "A uniform probability is the covered length divided by total support length."
    ),
    "continuous-normalize": (
        "Integrate the nonnegative polynomial shape and normalize its total area."
    ),
    "continuous-support": "The support is the closure of the interval with positive density.",
    "continuous-piecewise-cdf": (
        "Integrate from the left support endpoint, retaining preceding segment mass."
    ),
    "continuous-interval": (
        "Integrate on each portion of the event that lies in the density support."
    ),
    "continuous-exponential-tail": "Use the exponential survival function.",
    "continuous-memoryless": "Divide the two survival probabilities; the elapsed time cancels.",
    "continuous-exponential-quantile": "Isolate the exponential, then take the real logarithm.",
    "continuous-normal-standardize": "Subtract the normal mean and divide by sigma.",
    "continuous-normal-probability": (
        "Standardize and use the explicitly supplied rounded normal table entry."
    ),
    "continuous-normal-quantile": (
        "Transform the supplied standardized quantile back with mean plus sigma times z."
    ),
}


def _density(p: ProbabilityParams) -> PolynomialDensity:
    return PolynomialDensity(
        segments=(
            DensitySegment(lower=-p.a, upper=0, coefficients=(p.c, 1)),
            DensitySegment(lower=0, upper=p.b, coefficients=(p.b, 1)),
        )
    )


def _cdf(d: PolynomialDensity) -> str:
    x = sp.Symbol("x", real=True)
    first, second = d.segments

    def primitive(segment: DensitySegment) -> Any:
        return sum(
            sp.Rational(c, i + 1) * (x - segment.lower) ** (i + 1)
            for i, c in enumerate(segment.coefficients)
        ) / sp.Rational(d.normalizer)

    left = sp.expand(primitive(first))
    right = sp.expand(primitive(second) + left.subs(x, first.upper))
    return (
        rf"F_X(x)=\begin{{cases}}0&x<{first.lower}\\{tex(left)}&{first.lower}"
        rf"\le x<0\\{tex(right)}&0\le x<{second.upper}\\1&x\ge {second.upper}"
        rf"\end{{cases}}"
    )


def evaluate(kind: str, p: ProbabilityParams) -> Built:
    a, b, c = p.a, p.b, p.c
    d: UniformDistribution | PolynomialDensity | ExponentialDistribution
    if kind == "continuous-uniform":
        d = UniformDistribution(lower=-a, upper=b)
        answer = d.probability(F(0), F(b, 2))
        return finish(
            rf"X is uniform on \([-{a},{b}]\). Find \(P(0\le X\le {tex(F(b, 2))})\).",
            scalar(answer),
            r"P(u\le X\le v)=\frac{v-u}{b-a}",
            rf"\frac{{{tex(F(b, 2))}-0}}{{{b}-(-{a})}}={tex(answer)}",
        )
    if kind == "continuous-normalize":
        d = PolynomialDensity(segments=(DensitySegment(lower=0, upper=2, coefficients=(a, b, c)),))
        answer = 1 / d.normalizer
        return finish(
            (
                rf"A density is \(f(x)=k({a}+{b}x+{c}x^2)\) for \(0\le x\le2\), and "
                rf"zero elsewhere. Find k."
            ),
            scalar(answer),
            r"1=\int_0^2f(x)\,dx",
            (
                rf"1=k\left[{a}x+\frac{{{b}}}2x^2+\frac{{{c}}}3x^3\right]_0^2=k\cdot"
                rf"{tex(d.normalizer)}"
            ),
        )
    if kind == "continuous-support":
        segment = DensitySegment(lower=-a, upper=b, coefficients=(0, 1))
        d = PolynomialDensity(segments=(segment,))
        interval = IntervalAnswer(-a, b)
        return finish(
            (
                rf"The density is \(f(x)=\frac{{x+{a}}}{{{tex(d.normalizer)}}}\) on "
                rf"\([-{a},{b}]\), and zero elsewhere. Give its topological support as "
                rf"one interval, including boundary points."
            ),
            interval,
            rf"f(x)>0\quad\text{{for }}-{a}<x<{b}",
            rf"\operatorname{{supp}}(X)=\overline{{(-{a},{b})}}={interval.latex()}",
        )
    if kind in {"continuous-piecewise-cdf", "continuous-interval"}:
        d = _density(p)
        normalizer = tex(d.normalizer)
        density = (
            rf"f(x)=\frac1{{{normalizer}}}\begin{{cases}}{c}+(x+{a})&-{a}\le x<0\\"
            rf"{b}+x&0\le x\le {b}\\0&\text{{otherwise}}\end{{cases}}"
        )
        if kind == "continuous-piecewise-cdf":
            point = F(b, 2)
            answer = d.probability(F(-12), point)
            return finish(
                rf"For the density \({density}\), find \(F_X({tex(point)})\).",
                scalar(answer),
                _cdf(d),
                rf"F_X({tex(point)})={tex(answer)}",
            )
        lo, hi = F(-a, 2), F(b, 2)
        answer = d.probability(lo, hi)
        return finish(
            rf"For the density \({density}\), find \(P({tex(lo)}\le X\le{tex(hi)})\).",
            scalar(answer),
            r"P(u\le X\le v)=\int_u^0f(x)\,dx+\int_0^vf(x)\,dx",
            rf"P({tex(lo)}\le X\le{tex(hi)})={tex(answer)},\quad {_cdf(d)}",
        )
    if kind.startswith("continuous-exponential") or kind == "continuous-memoryless":
        d = ExponentialDistribution(rate=F(a, a + b))
        rate = tex(d.rate)
        if kind == "continuous-exponential-tail":
            answer = d.survival(F(c))
            return finish(
                (
                    rf"X is exponential with rate \(\lambda={rate}\), on \([0,\infty)\). "
                    rf"Find \(P(X>{c})\)."
                ),
                scalar(answer),
                r"P(X>t)=e^{-\lambda t}",
                rf"P(X>{c})=e^{{-({rate}){c}}}={tex(answer)}",
            )
        if kind == "continuous-memoryless":
            answer = d.survival(F(c))
            return finish(
                rf"X is exponential with rate \({rate}\). Find \(P(X>{b + c}\mid X>{b})\).",
                scalar(answer),
                r"P(X>s+t\mid X>s)=\frac{e^{-\lambda(s+t)}}{e^{-\lambda s}}=e^{-\lambda t}",
                rf"P(X>{b + c}\mid X>{b})=P(X>{c})={tex(answer)}",
            )
        probability = F(b, b + c)
        answer = d.quantile(probability)
        return finish(
            (
                rf"X is exponential with rate \({rate}\). Find the quantile q such "
                rf"that \(P(X\le q)={tex(probability)}\)."
            ),
            scalar(answer),
            r"1-e^{-\lambda q}=p\quad\Longrightarrow\quad q=-\frac{\ln(1-p)}\lambda",
            rf"q=-\frac{{\ln(1-{tex(probability)})}}{{{rate}}}={tex(answer)}",
        )
    dnormal = NormalDistribution(mean=a - 3, sigma=b)
    z = tuple(NORMAL_CDF)[c - 1]
    point = F(dnormal.mean) + dnormal.sigma * z
    description = (
        rf"X is normal with mean \(\mu={dnormal.mean}\) and standard deviation "
        rf"\(\sigma={dnormal.sigma}\). "
    )
    if kind == "continuous-normal-standardize":
        return finish(
            description + rf"Find the standardized z score corresponding to \(x={tex(point)}\).",
            scalar(dnormal.standardize(point)),
            r"z=\frac{x-\mu}{\sigma}",
            rf"z=\frac{{{tex(point)}-({dnormal.mean})}}{{{dnormal.sigma}}}={tex(z)}",
        )
    reference = (
        rf"The supplied rounded table row is \(z={tex(z)},\ \Phi(z)\approx "
        rf"{float(NORMAL_CDF[z]):.5f}\). "
    )
    if kind == "continuous-normal-probability":
        negative = a % 2 == 0
        query = F(dnormal.mean) + dnormal.sigma * (-z if negative else z)
        answer = 1 - NORMAL_CDF[z] if negative else NORMAL_CDF[z]
        return finish(
            description
            + reference
            + (
                rf"Using this table value, calculate the approximate probability "
                rf"\(P(X\le {tex(query)})\). Enter the resulting decimal or an "
                rf"equivalent exact fraction."
            ),
            scalar(answer),
            r"P(X\le x)=\Phi((x-\mu)/\sigma),\quad\Phi(-z)=1-\Phi(z)",
            rf"\Phi({tex(-z if negative else z)})\approx {float(answer):.5f}={tex(answer)}",
        )
    if kind == "continuous-normal-quantile":
        return finish(
            description
            + reference
            + (
                "Use this row as the quantile approximation. Report the "
                "corresponding x value exactly from the supplied z."
            ),
            scalar(point),
            r"x=\mu+\sigma z",
            rf"x={dnormal.mean}+{dnormal.sigma}\cdot {tex(z)}={tex(point)}",
        )
    raise ValueError("Unknown continuous template")
