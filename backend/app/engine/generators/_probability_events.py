"""Events, finite counting, conditional probability and Bayes prompts."""

from fractions import Fraction as F
from math import comb

from app.engine.answers.structured import BooleanAnswer, FiniteSetAnswer
from app.engine.generators._probability_common import (
    Built,
    ProbabilityParams,
    finish,
    joint,
    joint_table,
    scalar,
    tex,
)

REASONS = {
    "events-equal": "Count favorable outcomes in the equally likely sample space.",
    "events-complement": "Subtract the event probability from one.",
    "events-at-least-one": "Use the complement of no successes in independent trials.",
    "events-union": "Subtract the intersection once when adding event probabilities.",
    "events-intersection": "Use inclusion-exclusion to recover the intersection.",
    "events-selection": "Divide the number of favorable unordered selections by all selections.",
    "events-set": "Apply the stated operation to the two finite event sets.",
    "events-independence": (
        "Independence requires the intersection to equal the product of marginals."
    ),
    "conditional-table": "Restrict to the conditioning column, whose probability is positive.",
    "conditional-replacement": "With replacement the second draw has the original composition.",
    "conditional-without": (
        "Without replacement remove the first drawn object before the next draw."
    ),
    "conditional-total": "Weight each conditional probability by its partition probability.",
    "conditional-bayes-two": "Divide the selected source's joint probability by total evidence.",
    "conditional-bayes-three": "Normalize the selected branch over all three possible sources.",
    "conditional-tree": "Multiply along each path and add the paths leading to the event.",
}


def evaluate(kind: str, p: ProbabilityParams) -> Built:
    a, b, c = p.a, p.b, p.c
    if kind == "events-equal":
        n = a + b
        answer = F(a, n)
        return finish(
            (
                rf"An experiment has \({n}\) equally likely outcomes, of which \({a}\) "
                rf"belong to event A. Find \(P(A)\)."
            ),
            scalar(answer),
            r"P(A)=\frac{|A|}{|\Omega|}",
            rf"P(A)=\frac{{{a}}}{{{n}}}={tex(answer)}",
        )
    if kind == "events-complement":
        value = F(a, a + b)
        return finish(
            rf"Given \(P(A)={tex(value)}\), find \(P(A^c)\).",
            scalar(1 - value),
            r"P(A^c)=1-P(A)",
            rf"1-{tex(value)}={tex(1 - value)}",
        )
    if kind == "events-at-least-one":
        probability = F(a, a + b)
        n = c + 1
        answer = 1 - (1 - probability) ** n
        return finish(
            (
                rf"There are \({n}\) independent trials, each with success probability "
                rf"\({tex(probability)}\). Find the probability of at least one "
                rf"success."
            ),
            scalar(answer),
            r"P(\text{at least one})=1-P(\text{none})",
            rf"1-(1-{tex(probability)})^{{{n}}}={tex(answer)}",
        )
    if kind in {"events-union", "events-intersection", "events-independence", "conditional-table"}:
        d = joint(p)
        pa = d.marginal_x().masses[0]
        pb = d.marginal_y().masses[0]
        intersection = d.masses[0][0]
        union = pa + pb - intersection
        if kind == "conditional-table":
            answer = d.conditional(0, 0)
            return finish(
                rf"The joint distribution is \({joint_table(d)}\). Find \(P(X=0\mid Y=0)\).",
                scalar(answer),
                r"P(X=0\mid Y=0)=\frac{P(X=0,Y=0)}{P(Y=0)}",
                rf"\frac{{{tex(intersection)}}}{{{tex(pb)}}}={tex(answer)}",
            )
        givens = rf"Let \(P(A)={tex(pa)},\ P(B)={tex(pb)}\). "
        if kind == "events-independence":
            decision = BooleanAnswer(intersection == pa * pb)
            return finish(
                givens
                + (
                    rf"Also \(P(A\cap B)={tex(intersection)}\). Are A and B independent? "
                    rf"Answer Yes or No."
                ),
                decision,
                r"A\perp B\iff P(A\cap B)=P(A)P(B)",
                rf"P(A)P(B)={tex(pa * pb)},\quad P(A\cap B)={tex(intersection)}",
            )
        if kind == "events-union":
            return finish(
                givens + rf"Also \(P(A\cap B)={tex(intersection)}\). Find \(P(A\cup B)\).",
                scalar(union),
                r"P(A\cup B)=P(A)+P(B)-P(A\cap B)",
                rf"{tex(pa)}+{tex(pb)}-{tex(intersection)}={tex(union)}",
            )
        return finish(
            givens + rf"Also \(P(A\cup B)={tex(union)}\). Find \(P(A\cap B)\).",
            scalar(intersection),
            r"P(A\cap B)=P(A)+P(B)-P(A\cup B)",
            rf"{tex(pa)}+{tex(pb)}-{tex(union)}={tex(intersection)}",
        )
    if kind == "events-selection":
        red, blue = a + 1, b + 1
        answer = F(comb(red, 2), comb(red + blue, 2))
        return finish(
            (
                rf"A bag has \({red}\) red and \({blue}\) blue balls. Two balls are "
                rf"selected uniformly without replacement. Find the probability that "
                rf"both are red."
            ),
            scalar(answer),
            r"P(\text{two red})=\frac{\binom R2}{\binom{R+B}2}",
            rf"\frac{{\binom{{{red}}}2}}{{\binom{{{red + blue}}}2}}={tex(answer)}",
        )
    if kind == "events-set":
        left = set(range(1, a + 2))
        right = set(range(b, 7))
        index = (c - 1) % 3
        operation = (r"\cup ", r"\cap ", r"\setminus ")[index]
        event_values = tuple(sorted((left | right, left & right, left - right)[index]))
        aset = FiniteSetAnswer(tuple(sorted(left))).latex()
        bset = FiniteSetAnswer(tuple(sorted(right))).latex()
        return finish(
            (
                rf"In \(\Omega=\{{1,2,3,4,5,6\}}\), let \(A={aset}\) and \(B={bset}\). "
                rf"Give the finite event set \(A{operation}B\)."
            ),
            FiniteSetAnswer(event_values),
            rf"A={aset},\quad B={bset}",
            rf"A{operation}B={FiniteSetAnswer(event_values).latex()}",
        )
    if kind in {"conditional-replacement", "conditional-without"}:
        red, blue = a + 1, b + 1
        replace = kind == "conditional-replacement"
        answer = F(red if replace else red - 1, red + blue if replace else red + blue - 1)
        mode = "with replacement" if replace else "without replacement"
        return finish(
            (
                rf"A bag has \({red}\) red and \({blue}\) blue balls. Two draws are "
                rf"made {mode}. Given that the first ball is red, find the probability "
                rf"that the second ball is red."
            ),
            scalar(answer),
            r"P(R_2\mid R_1)=\frac{\text{remaining red}}{\text{remaining total}}",
            rf"P(R_2\mid R_1)={tex(answer)}",
        )
    if kind in {"conditional-total", "conditional-bayes-two"}:
        prior = F(a, a + b)
        p1 = F(b, b + c)
        p2 = F(c, a + c)
        evidence = prior * p1 + (1 - prior) * p2
        answer = evidence if kind == "conditional-total" else prior * p1 / evidence
        question = r"P(E)" if kind == "conditional-total" else r"P(S_1\mid E)"
        formula = (
            r"P(E)=P(S_1)P(E\mid S_1)+P(S_2)P(E\mid S_2)"
            if kind == "conditional-total"
            else r"P(S_1\mid E)=\frac{P(S_1)P(E\mid S_1)}{P(E)}"
        )
        return finish(
            (
                rf"Sources \(S_1,S_2\) partition all cases. Given \(P(S_1)={tex(prior)}"
                rf",\ P(E\mid S_1)={tex(p1)},\ P(E\mid S_2)={tex(p2)}\), find \("
                rf"{question}\)."
            ),
            scalar(answer),
            formula,
            rf"P(E)={tex(evidence)},\quad {question}={tex(answer)}",
        )
    if kind == "conditional-bayes-three":
        weights = (a, b, c)
        priors = tuple(F(x, sum(weights)) for x in weights)
        success = (F(1, a + 1), F(1, b + 1), F(1, c + 1))
        evidence = sum((q * r for q, r in zip(priors, success, strict=True)), F())
        answer = priors[0] * success[0] / evidence
        givens = r",\ ".join(
            rf"P(S_{i + 1})={tex(q)},\ P(E\mid S_{i + 1})={tex(r)}"
            for i, (q, r) in enumerate(zip(priors, success, strict=True))
        )
        return finish(
            rf"Three sources partition all cases, with \({givens}\). Find \(P(S_1\mid E)\).",
            scalar(answer),
            r"P(S_1\mid E)=\frac{P(S_1)P(E\mid S_1)}{\sum_{i=1}^3P(S_i)P(E\mid S_i)}",
            rf"P(E)={tex(evidence)},\quad P(S_1\mid E)={tex(answer)}",
        )
    if kind == "conditional-tree":
        prior = F(a, a + b)
        first = F(b, b + c)
        second = F(c, a + c)
        answer = prior * first + (1 - prior) * second
        return finish(
            (
                rf"A tree first chooses branch L with probability \({tex(prior)}\), "
                rf"otherwise R. It ends in E with conditional probability \("
                rf"{tex(first)}\) from L and \({tex(second)}\) from R. Find the total "
                rf"probability of ending in E."
            ),
            scalar(answer),
            r"P(E)=P(L\cap E)+P(R\cap E)",
            rf"{tex(prior)}\cdot{tex(first)}+(1-{tex(prior)})\cdot{tex(second)}={tex(answer)}",
        )
    raise ValueError("Unknown event template")
