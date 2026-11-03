"""Moments, joint laws and bounded descriptive-statistics prompts."""

import sympy as sp

from app.engine.answers.structured import BooleanAnswer, FiniteSetAnswer
from app.engine.blocks.distribution import FiniteDistribution, JointDistribution
from app.engine.blocks.statistics import PairedSample, Sample
from app.engine.generators._probability_common import (
    Built,
    ProbabilityParams,
    finish,
    finite,
    joint,
    joint_table,
    scalar,
    table,
    tex,
)

REASONS = {
    "moments-mean": "Multiply each outcome by its probability and sum.",
    "moments-variance": "Subtract the square of the mean from the second moment.",
    "moments-deviation": "Take the nonnegative square root of the variance.",
    "moments-affine-mean": "Expectation is linear, including the constant shift.",
    "moments-affine-variance": (
        "Scaling multiplies variance by the square of the scale; shifts do not change it."
    ),
    "moments-marginal": "Sum a joint table over the other variable.",
    "moments-conditional": "Divide the selected joint mass by the conditioning marginal.",
    "moments-covariance": "Subtract the product of the means from the expected product.",
    "moments-correlation": "Divide covariance by the product of standard deviations.",
    "moments-independence": "Check every joint mass against its product of marginals.",
    "sample-mean": "Add the observations and divide by their count.",
    "sample-weighted": "Weight each value by its stated frequency.",
    "sample-median": "Sort the sample and locate its middle observation or middle pair.",
    "sample-modes": "Count frequencies and retain every value attaining the maximum.",
    "sample-quartile": "Use the stated median-of-halves convention.",
    "sample-iqr": "Subtract the lower quartile from the upper quartile.",
    "sample-population-variance": "Divide the centered sum of squares by the population count.",
    "sample-sample-variance": "Divide the centered sum of squares by n minus one.",
    "sample-deviation": "Use the nonnegative square root of the unbiased sample variance.",
    "sample-correlation": (
        "Divide the centered cross-product by the geometric mean of centered square sums."
    ),
    "sample-slope": "Divide the centered cross-product by the centered x square sum.",
    "sample-intercept": (
        "Choose the intercept so the fitted line passes through the pair of sample means."
    ),
}


def paired(p: ProbabilityParams) -> PairedSample:
    return PairedSample(
        x=Sample(values=tuple(x + p.a - 3 for x in (-2, -1, 0, 1, 2, 3))),
        y=Sample(values=tuple(y + p.b - 3 for y in (-1, 1, -1, 2, 0, 3))),
    )


def evaluate(kind: str, p: ProbabilityParams) -> Built:
    a, b, c = p.a, p.b, p.c
    d: FiniteDistribution | JointDistribution
    if kind.startswith("moments-"):
        if kind in {
            "moments-marginal",
            "moments-conditional",
            "moments-covariance",
            "moments-correlation",
            "moments-independence",
        }:
            d = joint(p)
            description = rf"The joint law is \({joint_table(d)}\). "
            if kind == "moments-marginal":
                answer = d.marginal_x().masses[0]
                return finish(
                    description + "Find the marginal probability of X being zero.",
                    scalar(answer),
                    r"P(X=x)=\sum_yP(X=x,Y=y)",
                    table(d.marginal_x()),
                )
            if kind == "moments-conditional":
                answer = d.conditional(1, 1)
                return finish(
                    description + r"Find \(P(X=1\mid Y=2)\).",
                    scalar(answer),
                    r"P(X=1\mid Y=2)=\frac{P(X=1,Y=2)}{P(Y=2)}",
                    (
                        rf"\frac{{{tex(d.masses[1][1])}}}{{{tex(d.marginal_y().masses[1])}}}="
                        rf"{tex(answer)}"
                    ),
                )
            if kind == "moments-independence":
                products = tuple(
                    tuple(x * y for y in d.marginal_y().masses) for x in d.marginal_x().masses
                )
                return finish(
                    description + "Are X and Y independent? Answer Yes or No.",
                    BooleanAnswer(d.independent),
                    r"X\perp Y\iff p_{ij}=p_{i+}p_{+j}\text{ for every }i,j",
                    (
                        rf"(p_{{i+}}p_{{+j}})_{{ij}}={tex(sp.Matrix(products))},\quad "
                        rf"(p_{{ij}})_{{ij}}={tex(sp.Matrix(d.masses))}"
                    ),
                )
            cov = d.covariance
            if kind == "moments-covariance":
                return finish(
                    description + r"Find \(\operatorname{Cov}(X,Y)\).",
                    scalar(cov),
                    r"\operatorname{Cov}(X,Y)=E[XY]-E[X]E[Y]",
                    (
                        rf"E[X]={tex(d.marginal_x().moment(1))},\quad E[Y]="
                        rf"{tex(d.marginal_y().moment(1))},\quad\operatorname{{Cov}}(X,Y)="
                        rf"{tex(cov)}"
                    ),
                )
            variance_x, variance_y = d.marginal_x().variance, d.marginal_y().variance
            answer = sp.Rational(cov) / sp.sqrt(sp.Rational(variance_x * variance_y))
            return finish(
                description + "Find the correlation coefficient.",
                scalar(answer),
                r"\rho=\frac{\operatorname{Cov}(X,Y)}{\sqrt{\operatorname{Var}(X)\operatorname{Var}(Y)}}",
                (
                    rf"\rho=\frac{{{tex(cov)}}}{{\sqrt{{({tex(variance_x)})("
                    rf"{tex(variance_y)})}}}}={tex(answer)}"
                ),
            )
        d = finite(p)
        description = rf"Given \({table(d)}\), "
        if kind == "moments-mean":
            return finish(
                description + r"find \(E[X]\).",
                scalar(d.moment(1)),
                r"E[X]=\sum_xxp(x)",
                rf"E[X]={tex(d.moment(1))}",
            )
        if kind in {"moments-variance", "moments-deviation"}:
            answer = (
                sp.Rational(d.variance)
                if kind == "moments-variance"
                else sp.sqrt(sp.Rational(d.variance))
            )
            question = "variance" if kind == "moments-variance" else "standard deviation"
            return finish(
                description + f"find the {question} of X.",
                scalar(answer),
                r"\operatorname{Var}(X)=E[X^2]-E[X]^2,\quad\sigma_X=\sqrt{\operatorname{Var}(X)}",
                (
                    rf"E[X^2]={tex(d.moment(2))},\ E[X]={tex(d.moment(1))},\ "
                    rf"\operatorname{{Var}}(X)={tex(d.variance)}"
                ),
            )
        if kind == "moments-affine-mean":
            answer = c * d.moment(1) + a
            return finish(
                description + rf"let \(Y={c}X+{a}\). Find \(E[Y]\).",
                scalar(answer),
                r"E[rX+s]=rE[X]+s",
                rf"E[Y]={c}\cdot({tex(d.moment(1))})+{a}={tex(answer)}",
            )
        if kind == "moments-affine-variance":
            answer = c * c * d.variance
            return finish(
                description + rf"let \(Y={c}X+{a}\). Find \(\operatorname{{Var}}(Y)\).",
                scalar(answer),
                r"\operatorname{Var}(rX+s)=r^2\operatorname{Var}(X)",
                rf"\operatorname{{Var}}(Y)={c}^2\cdot {tex(d.variance)}={tex(answer)}",
            )
    if kind in {"sample-correlation", "sample-slope", "sample-intercept"}:
        dpaired = paired(p)
        data = tex(tuple(zip(dpaired.x.values, dpaired.y.values, strict=True)))
        answer = {
            "sample-correlation": dpaired.correlation,
            "sample-slope": dpaired.slope,
            "sample-intercept": dpaired.intercept,
        }[kind]
        question = {
            "sample-correlation": "Pearson correlation coefficient",
            "sample-slope": "least-squares slope",
            "sample-intercept": "least-squares intercept",
        }[kind]
        formula = (
            r"S_{xy}=\sum_i(x_i-\bar x)(y_i-\bar y),\ S_{xx}=\sum_i(x_i-\bar "
            r"x)^2,\ S_{yy}=\sum_i(y_i-\bar y)^2"
        )
        if kind == "sample-correlation":
            work = rf"r=\frac{{S_{{xy}}}}{{\sqrt{{S_{{xx}}S_{{yy}}}}}}={tex(answer)}"
        else:
            work = (
                rf"b_1=\frac{{S_{{xy}}}}{{S_{{xx}}}}={tex(dpaired.slope)},\quad "
                rf"b_0=\bar y-b_1\bar x={tex(dpaired.intercept)},\quad \widehat y="
                rf"{tex(dpaired.intercept)}+({tex(dpaired.slope)})x"
            )
        return finish(
            rf"For the paired observations \({data}\), find the {question} for regressing y on x.",
            scalar(answer),
            formula,
            work,
        )
    values = (a - 3, b - 3, c - 3, a - 3, b - 3, c - 2) + ((a - 2,) if c % 2 else ())
    sample = Sample(values=values)
    description = rf"For the observations \({tex(values)}\), "
    if kind == "sample-mean":
        return finish(
            description + "find their arithmetic mean.",
            scalar(sample.mean),
            r"\bar x=\frac1n\sum_ix_i",
            rf"\bar x=\frac{{{sum(values)}}}{{{len(values)}}}={tex(sample.mean)}",
        )
    if kind == "sample-weighted":
        d = FiniteDistribution.from_weights((-2, 0, 3), (a, b, c))
        answer = d.moment(1)
        return finish(
            (
                rf"Values \(-2,0,3\) have frequencies \({a},{b},{c}\), respectively. "
                rf"Find their weighted mean."
            ),
            scalar(answer),
            r"\bar x_w=\frac{\sum_jf_jx_j}{\sum_jf_j}",
            rf"\bar x_w=\frac{{-2\cdot {a}+0\cdot {b}+3\cdot {c}}}{{{a + b + c}}}={tex(answer)}",
        )
    if kind == "sample-median":
        return finish(
            description + "find the median.",
            scalar(sample.median),
            rf"x_{{(1)}}\le\cdots\le x_{{(n)}}:\quad {tex(tuple(sorted(values)))}",
            rf"n={len(values)},\quad\operatorname{{median}}={tex(sample.median)}",
        )
    if kind == "sample-modes":
        modes_answer = FiniteSetAnswer(sample.modes)
        return finish(
            description
            + "give all values tied for the largest observed frequency as a finite set.",
            modes_answer,
            r"\operatorname{modes}=\{x:f(x)=\max_tf(t)\}",
            rf"{tex(tuple(sorted(values)))},\quad\operatorname{{modes}}={modes_answer.latex()}",
        )
    if kind in {"sample-quartile", "sample-iqr"}:
        q1, q3 = sample.quartiles
        answer = q1 if kind == "sample-quartile" else q3 - q1
        question = "lower quartile Q1" if kind == "sample-quartile" else "interquartile range"
        return finish(
            description
            + (
                f"find the {question}. Use medians of the lower and upper halves, "
                f"excluding the overall median when n is odd."
            ),
            scalar(answer),
            (
                r"Q_1=\operatorname{median}(\text{lower half}),\quad "
                r"Q_3=\operatorname{median}(\text{upper half})"
            ),
            rf"Q_1={tex(q1)},\quad Q_3={tex(q3)},\quad Q_3-Q_1={tex(q3 - q1)}",
        )
    if kind in {"sample-population-variance", "sample-sample-variance", "sample-deviation"}:
        unbiased = kind != "sample-population-variance"
        v = sample.variance(unbiased)
        answer = sp.sqrt(sp.Rational(v)) if kind == "sample-deviation" else v
        question = (
            "population variance (divide by n)"
            if not unbiased
            else "unbiased sample variance (divide by n-1)"
            if kind == "sample-sample-variance"
            else "sample standard deviation, using the unbiased sample variance"
        )
        denominator = len(values) - int(unbiased)
        return finish(
            description + f"find the {question}.",
            scalar(answer),
            rf"v=\frac{{\sum_i(x_i-\bar x)^2}}{{{denominator}}}",
            (
                rf"\bar x={tex(sample.mean)},\quad v={tex(v)},\quad\sqrt v="
                rf"{tex(sp.sqrt(sp.Rational(v)))}"
            ),
        )
    raise ValueError("Unknown moments/statistics template")
