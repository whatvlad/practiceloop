"""Finite variables and standard discrete distribution prompts."""

from fractions import Fraction as F
from typing import cast

from app.engine.answers.structured import FiniteSetAnswer
from app.engine.blocks.distribution import FiniteDistribution, StandardDistribution, StandardKind
from app.engine.generators._probability_common import (
    Built,
    ProbabilityParams,
    finish,
    finite,
    scalar,
    table,
    tex,
)

REASONS = {
    "finite-normalize": "The probability masses must sum to one.",
    "finite-point": "Read the mass at the requested outcome.",
    "finite-cdf": "Add all masses at or below the CDF argument.",
    "finite-tail": "Add all masses strictly above the threshold.",
    "finite-support": "Keep exactly the outcomes with positive probability.",
    "finite-jump": "A CDF jump is the probability at its jump location.",
    "finite-transform": "Merge masses whenever different original outcomes have the same image.",
    "discrete-bernoulli": "Use the Bernoulli mass function on zero and one.",
    "discrete-binomial": "Choose the success positions and multiply the independent probabilities.",
    "discrete-geometric": "Fail on the preceding trials, then succeed on this trial.",
    "discrete-hypergeometric": "Count selections of successes and failures without replacement.",
    "discrete-poisson": "Apply the Poisson mass formula with the stated rate.",
}


def evaluate(kind: str, p: ProbabilityParams) -> Built:
    a, b, c = p.a, p.b, p.c
    d = finite(p)
    if kind == "finite-normalize":
        answer = F(1, a + b + c)
        return finish(
            (
                rf"The finite variable takes values \(-{a},0,{b}\) with masses \({a}k,"
                rf"{b}k,{c}k\), respectively. Find the normalizing constant k."
            ),
            scalar(answer),
            r"\sum_xP(X=x)=1",
            rf"({a}+{b}+{c})k=1,\quad k={tex(answer)}",
        )
    if kind in {"finite-point", "finite-cdf", "finite-tail"}:
        answer = (
            d.masses[1]
            if kind == "finite-point"
            else d.cdf(F(0))
            if kind == "finite-cdf"
            else d.probability((p.b,))
        )
        question = {
            "finite-point": r"P(X=0)",
            "finite-cdf": r"F_X(0)=P(X\le0)",
            "finite-tail": r"P(X>0)",
        }[kind]
        formula = (
            r"F_X(t)=\sum_{x\le t}P(X=x)"
            if kind == "finite-cdf"
            else r"P(X\in A)=\sum_{x\in A}P(X=x)"
        )
        return finish(
            rf"Given \({table(d)}\), calculate \({question}\).",
            scalar(answer),
            formula,
            rf"{question}={tex(answer)}",
        )
    if kind == "finite-support":
        d = FiniteDistribution.from_weights((-a, 0, b), (a, 0, c))
        support = FiniteSetAnswer(d.support)
        return finish(
            rf"Given \({table(d)}\), give the finite support of X as a set.",
            support,
            r"\operatorname{supp}(X)=\{x:P(X=x)>0\}",
            rf"P(X=0)=0,\quad\operatorname{{supp}}(X)={support.latex()}",
        )
    if kind == "finite-jump":
        first = d.masses[0]
        through = d.masses[0] + d.masses[1]
        cdf = (
            rf"F_X(x)=\begin{{cases}}0&x<-{a}\\{tex(first)}&-{a}\le x<0\\"
            rf"{tex(through)}&0\le x<{b}\\1&x\ge {b}\end{{cases}}"
        )
        answer = d.masses[1]
        return finish(
            rf"The CDF is \({cdf}\). Find \(P(X=0)\).",
            scalar(answer),
            r"P(X=0)=F_X(0)-F_X(0^-)",
            rf"{tex(through)}-{tex(first)}={tex(answer)}",
        )
    if kind == "finite-transform":
        d = FiniteDistribution.from_weights((-a, 0, a), (a, b, c))
        image = d.pushforward(tuple(abs(x) for x in d.values))
        answer = image.probability((a,))
        return finish(
            rf"Given \({table(d)}\), let \(Y=|X|\). Find \(P(Y={a})\).",
            scalar(answer),
            rf"\{{|X|={a}\}}=\{{X=-{a}\}}\cup\{{X={a}\}}",
            rf"P(Y={a})={tex(d.masses[0])}+{tex(d.masses[2])}={tex(answer)},\quad {table(image)}",
        )
    family = kind.removeprefix("discrete-")
    dstd = StandardDistribution(
        kind=cast(StandardKind, family),
        n=a + 2,
        numerator=b,
        denominator=b + c,
        population=a + b + c + 2,
        successes=a + 1,
        draws=b + 1,
        rate=a,
    )
    if family == "bernoulli":
        k = c % 2
        description = rf"X is Bernoulli with \(p={tex(dstd.p)}\)."
        formula = r"P(X=k)=p^k(1-p)^{1-k},\quad k\in\{0,1\}"
    elif family == "binomial":
        k = b % (dstd.n + 1)
        description = (
            rf"X counts successes in \({dstd.n}\) independent trials, each with "
            rf"success probability \({tex(dstd.p)}\)."
        )
        formula = r"P(X=k)=\binom nkp^k(1-p)^{n-k}"
    elif family == "geometric":
        k = a + 1
        description = (
            rf"Independent trials succeed with probability \({tex(dstd.p)}\). X is "
            rf"the trial number of the first success, with support "
            rf"\(\{{1,2,\ldots\}}\)."
        )
        formula = r"P(X=k)=(1-p)^{k-1}p"
    elif family == "hypergeometric":
        k = min(a + 1, b + 1)
        description = (
            rf"A population of \({dstd.population}\) objects has \({dstd.successes}"
            rf"\) successes. A uniform sample of \({dstd.draws}\) is taken without "
            rf"replacement. X counts sampled successes."
        )
        formula = r"P(X=k)=\frac{\binom Kk\binom{N-K}{n-k}}{\binom Nn}"
    elif family == "poisson":
        k = b
        description = rf"X has a Poisson distribution with rate \(\lambda={a}\)."
        formula = r"P(X=k)=e^{-\lambda}\frac{\lambda^k}{k!}"
    else:
        raise ValueError("Unknown discrete template")
    answer = dstd.pmf(k)
    return finish(
        description + rf" Find \(P(X={k})\).", scalar(answer), formula, rf"P(X={k})={tex(answer)}"
    )
