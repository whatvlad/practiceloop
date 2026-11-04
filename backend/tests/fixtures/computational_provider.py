"""Installed only temporarily by the Linux worker regression, never a served topic."""

from dataclasses import replace

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer, RealSetAnswer
from app.engine.generators.combinations import Combinations
from app.engine.models import Step
from app.math_input.contracts import InputContract


class ContractExample(Combinations):
    version = "worker-contract-example-v1"
    prefix = "WCT"
    family = "worker-contract-example"
    answer = OrderedAnswer
    step_text = {"result": "Read the exact set and ordered formula."}

    def input_contract(self, params):
        return InputContract(
            "tuple",
            components=(
                InputContract("real_set"),
                InputContract("formula", symbols=(("a", "positive"), ("x", "real"))),
            ),
            labels=("Domain", "Expression"),
        )

    def build(self, params):
        base = super().build(params)
        a, x = sp.symbols("a x", real=True)
        answer = OrderedAnswer(
            (
                RealSetAnswer(sp.S.Reals - sp.FiniteSet(0)),
                FormulaAnswer(a * (x + 1), (("a", "positive"), ("x", "real"))),
            ),
            ("Domain", "Expression"),
        )
        return replace(base, answer=answer, steps=(Step("result", answer.latex()),))


def generators():
    return (ContractExample(),)
