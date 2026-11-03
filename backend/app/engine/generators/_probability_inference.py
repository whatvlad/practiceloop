"""Declared-assumption inference tasks using supplied finite reference values."""

from fractions import Fraction as F

import sympy as sp

from app.engine.answers.structured import BooleanAnswer, IntervalAnswer
from app.engine.blocks.statistics import (
    T95,
    Z_TWO_SIDED,
    Sample,
    mean_interval,
    mean_statistic,
    reject,
)
from app.engine.generators._probability_common import Built, ProbabilityParams, finish, scalar, tex
from app.engine.generators._probability_statistics import paired

REASONS = {
    "ci-mean-z": "Use the known population sigma and the supplied two-sided normal critical value.",
    "ci-mean-t": (
        "Use the sample standard deviation and the supplied t critical value "
        "with n-1 degrees of freedom."
    ),
    "ci-lower": "Use the one-sided lower normal confidence bound, unbounded above.",
    "ci-upper": "Use the one-sided upper normal confidence bound, unbounded below.",
    "ci-proportion": (
        "Use the stated large-sample Wald formula and the observed success proportion."
    ),
    "ci-paired": (
        "Form the within-pair differences, then use their sample mean and "
        "sample standard deviation."
    ),
    "ci-difference": "Independent sample mean variances add; population sigmas are known.",
    "test-z-statistic": "Subtract the null mean and divide by the known standard error.",
    "test-z-decision": (
        "Compare the z statistic with the supplied critical region for the stated alternative."
    ),
    "test-t-statistic": "Estimate the mean's standard error using the sample standard deviation.",
    "test-t-decision": "Compare the t statistic with the supplied two-sided t critical value.",
    "test-proportion": (
        "Use the null probability, rather than the estimate, in the test standard error."
    ),
    "test-paired": "Test the mean of the within-pair differences with n-1 degrees of freedom.",
    "test-difference": (
        "Standardize the difference of independent means using the known population variances."
    ),
}


def _differences(p: ProbabilityParams) -> Sample:
    data = paired(p)
    return Sample(values=tuple(y - x for x, y in zip(data.x.values, data.y.values, strict=True)))


def evaluate(kind: str, p: ProbabilityParams) -> Built:
    a, b, c = p.a, p.b, p.c
    if kind in {"ci-mean-z", "ci-mean-t", "ci-lower", "ci-upper"}:
        average = sp.Integer(a - b)
        sigma = sp.Integer(c)
        if kind == "ci-mean-t":
            n = a + 3
            critical = T95[n - 1]
            coverage = 95
            assumption = (
                "An independent random sample comes from a normal population with "
                "unknown variance. "
            )
            data = (
                rf"The sample mean is \({tex(average)}\), sample standard deviation is "
                rf"\(s={c}\), and \(n={n}\). "
            )
            reference = (
                rf"Use the supplied rounded critical value \(t_{{0.975,{n - 1}}}="
                rf"{float(critical):.3f}\). "
            )
        else:
            n = (a + 1) ** 2
            coverage, critical = Z_TWO_SIDED[(b - 1) % 3]
            if kind in {"ci-lower", "ci-upper"}:
                coverage, critical = 95, F(329, 200)
            assumption = (
                "An independent random sample comes from a normal population with "
                "known population standard deviation. "
            )
            data = (
                rf"The sample mean is \({tex(average)}\), population \(\sigma={c}\), "
                rf"and \(n={n}\). "
            )
            reference = (
                rf"Use the supplied rounded normal critical value \(z={float(critical):.3f}\). "
            )
        lo, hi = mean_interval(average, sigma, n, critical)
        if kind == "ci-lower":
            answer = IntervalAnswer(lo, sp.oo, False, True)
            question = "Give the one-sided 95-percent lower confidence interval."
            formula = r"[\bar x-z\sigma/\sqrt n,\infty)"
        elif kind == "ci-upper":
            answer = IntervalAnswer(-sp.oo, hi, True, False)
            question = "Give the one-sided 95-percent upper confidence interval."
            formula = r"(-\infty,\bar x+z\sigma/\sqrt n]"
        else:
            answer = IntervalAnswer(lo, hi)
            question = f"Give the two-sided {coverage}-percent confidence interval."
            formula = (
                r"[\bar x-q\cdot\mathrm{SE},\bar x+q\cdot\mathrm{SE}],\quad\mathrm{SE}=s/\sqrt n"
                if kind == "ci-mean-t"
                else r"[\bar x-q\sigma/\sqrt n,\bar x+q\sigma/\sqrt n]"
            )
        return finish(
            assumption
            + data
            + reference
            + question
            + " Calculate endpoints exactly from the supplied critical value.",
            answer,
            formula,
            (
                rf"\bar x={tex(average)}"
                rf",\quad\mathrm{{SE}}=\frac{{{c}}}{{\sqrt{{{n}}}}},\quad "
                rf"q\cdot\mathrm{{SE}}="
                rf"{tex(sp.Rational(critical) * sigma / sp.sqrt(n))}"
            ),
        )
    if kind in {"ci-proportion", "test-proportion"}:
        n = 100 + 20 * (c - 1)
        successes = n // 2 + 5 * (a - 3)
        estimate = F(successes, n)
        critical = F(49, 25)
        description = (
            rf"An independent Bernoulli sample has \({successes}\) successes out "
            rf"of \({n}\) trials. "
        )
        if kind == "ci-proportion":
            if successes < 10 or n - successes < 10:
                raise ValueError("Insufficient observed counts for the normal approximation")
            margin = sp.Rational(critical) * sp.sqrt(sp.Rational(estimate * (1 - estimate), n))
            lo = sp.Rational(estimate) - margin
            hi = sp.Rational(estimate) + margin
            if not (bool(lo > 0) and bool(hi < 1)):
                raise ValueError("Generated proportion interval leaves [0,1]")
            return finish(
                description
                + (
                    "Use the large-sample Wald approximation (both observed counts are "
                    "at least 10). Give the approximate two-sided 95-percent confidence "
                    "interval using the supplied rounded critical value 1.960. Calculate "
                    "endpoints exactly from that value."
                ),
                IntervalAnswer(lo, hi),
                r"\widehat p\pm1.960\sqrt{\widehat p(1-\widehat p)/n}",
                (
                    rf"\widehat p={tex(estimate)},\quad\mathrm{{SE}}=\sqrt{{\frac{{("
                    rf"{tex(estimate)})(1-{tex(estimate)})}}{{{n}}}}}"
                ),
            )
        null = F(b, b + c)
        statistic = sp.Rational(estimate - null) / sp.sqrt(sp.Rational(null * (1 - null), n))
        if n * null < 10 or n * (1 - null) < 10:
            raise ValueError("Insufficient expected null counts")
        decision = reject(statistic, critical, "two")
        return finish(
            description
            + (
                rf"Test \(H_0:p={tex(null)}\) against \(H_a:p\ne{tex(null)}\) at "
                rf"\(\alpha=0.05\). Both expected null counts are at least 10. Use the "
                rf"normal approximation and supplied rounded critical value 1.960. "
                rf"Should H0 be rejected? Answer Yes or No."
            ),
            BooleanAnswer(decision),
            r"z=\frac{\widehat p-p_0}{\sqrt{p_0(1-p_0)/n}},\quad\text{reject if }|z|>1.960",
            rf"\widehat p={tex(estimate)},\quad z={tex(statistic)}",
        )
    if kind in {"ci-paired", "test-paired"}:
        paired_data = paired(p)
        differences = _differences(p)
        n = len(differences.values)
        critical = T95[n - 1]
        scale = sp.sqrt(sp.Rational(differences.variance()))
        description = (
            rf"The paired observations \((x_i,y_i)\) are \("
            rf"{tex(tuple(zip(paired_data.x.values, paired_data.y.values, strict=True)))}"
            rf"\). Pairs are independent, and \(D_i=Y_i-X_i\) are normal with "
            rf"unknown variance. "
        )
        reference = (
            rf"Use the supplied rounded two-sided 95-percent critical value "
            rf"\(t_{{0.975,{n - 1}}}={float(critical):.3f}\). "
        )
        calculation = (
            rf"D={tex(differences.values)},\quad\bar d={tex(differences.mean)}"
            rf",\quad s_D^2={tex(differences.variance())}"
        )
        if kind == "ci-paired":
            lo, hi = mean_interval(sp.Rational(differences.mean), scale, n, critical)
            return finish(
                description
                + reference
                + (
                    "Give the two-sided 95-percent confidence interval for the "
                    "population mean difference Y-X. Calculate endpoints exactly from "
                    "the supplied critical value."
                ),
                IntervalAnswer(lo, hi),
                r"\bar d\pm t_{0.975,n-1}s_D/\sqrt n",
                calculation,
            )
        statistic = mean_statistic(sp.Rational(differences.mean), sp.S.Zero, scale, n)
        return finish(
            description
            + reference
            + (
                "Test H0 that the population mean difference is zero against a "
                "two-sided alternative at alpha 0.05. Should H0 be rejected? Answer "
                "Yes or No."
            ),
            BooleanAnswer(reject(statistic, critical, "two")),
            rf"t=\frac{{\bar d}}{{s_D/\sqrt n}},\quad\text{{reject if }}|t|>{float(critical):.3f}",
            calculation + rf",\quad t={tex(statistic)}",
        )
    if kind in {"ci-difference", "test-difference"}:
        center = sp.Integer(a - b)
        se = sp.sqrt(sp.Rational(b * b, 16) + sp.Rational(c * c, 25))
        critical = F(49, 25)
        description = (
            rf"Independent random samples from two normal populations have "
            rf"\(n_1=16,n_2=25\), sample means \(\bar x_1={a - 3},\bar x_2={b - 3}"
            rf"\), and known population standard deviations \(\sigma_1={b}"
            rf",\sigma_2={c}\). Use the supplied rounded two-sided 95-percent "
            rf"critical value 1.960. "
        )
        calculation = (
            rf"\bar x_1-\bar x_2={tex(center)},\quad\mathrm{{SE}}=\sqrt{{\frac{{{b}"
            rf"^2}}{{16}}+\frac{{{c}^2}}{{25}}}}={tex(se)}"
        )
        if kind == "ci-difference":
            margin = sp.Rational(critical) * se
            return finish(
                description
                + (
                    "Give the two-sided 95-percent confidence interval for the "
                    "difference of population means (first minus second). Calculate "
                    "endpoints exactly from the supplied critical value."
                ),
                IntervalAnswer(center - margin, center + margin),
                r"(\bar x_1-\bar x_2)\pm1.960\sqrt{\sigma_1^2/n_1+\sigma_2^2/n_2}",
                calculation,
            )
        statistic = sp.simplify(center / se)
        return finish(
            description
            + (
                "Test equality of the two population means against a two-sided "
                "alternative at alpha 0.05. Should H0 be rejected? Answer Yes or No."
            ),
            BooleanAnswer(reject(statistic, critical, "two")),
            (
                r"z=\frac{\bar x_1-\bar "
                r"x_2}{\sqrt{\sigma_1^2/n_1+\sigma_2^2/n_2}},\quad\text{reject if "
                r"}|z|>1.960"
            ),
            calculation + rf",\quad z={tex(statistic)}",
        )
    if kind in {"test-z-statistic", "test-z-decision", "test-t-statistic", "test-t-decision"}:
        use_t = kind.startswith("test-t-")
        n = a + 3 if use_t else 25
        average = sp.Integer(b - 3 if use_t else a - 3)
        scale = sp.Integer(c if use_t else b)
        statistic = mean_statistic(average, sp.S.Zero, scale, n)
        tail = "two" if use_t else ("two", "upper", "lower")[(c - 1) % 3]
        critical = T95[n - 1] if use_t else F(49, 25) if tail == "two" else F(329, 200)
        name = "t" if use_t else "z"
        alternative = {"two": r"\mu\ne0", "upper": r"\mu>0", "lower": r"\mu<0"}[tail]
        scale_name = (
            "sample standard deviation s" if use_t else "known population standard deviation sigma"
        )
        description = (
            rf"An independent random sample from a normal population has \(n={n}"
            rf"\), sample mean \({tex(average)}\), and {scale_name} \({tex(scale)}"
            rf"\). "
        )
        if kind.endswith("statistic"):
            return finish(
                description
                + (
                    rf"For the null population mean \(\mu_0=0\), calculate the {name} test "
                    rf"statistic."
                ),
                scalar(statistic),
                rf"{name}=\frac{{\bar x-\mu_0}}{{{'s' if use_t else r'\sigma'}/\sqrt n}}",
                rf"{name}=\frac{{{tex(average)}-0}}{{{tex(scale)}/\sqrt{{{n}}}}}={tex(statistic)}",
            )
        region = (
            rf"|{name}|>{float(critical):.3f}"
            if tail == "two"
            else rf"{name}>{float(critical):.3f}"
            if tail == "upper"
            else rf"{name}<-{float(critical):.3f}"
        )
        reference = (
            rf"Use supplied rounded \(t_{{0.975,{n - 1}}}={float(critical):.3f}\). "
            if use_t
            else rf"Use the supplied rounded normal critical value \({float(critical):.3f}\). "
        )
        return finish(
            description
            + reference
            + (
                rf"Test \(H_0:\mu=0\) against \(H_a:{alternative}\) at "
                rf"\(\alpha=0.05\). Should H0 be rejected? Answer Yes or No."
            ),
            BooleanAnswer(reject(statistic, critical, tail)),
            rf"\text{{Reject }}H_0\text{{ if }}{region}",
            rf"{name}={tex(statistic)}",
        )
    raise ValueError("Unknown inference template")
