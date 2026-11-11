"""All real parameters producing perpendicular vector expressions."""

import pytest
import sympy as sp

from app.engine.generators.eigen_geometry import (
    PerpendicularParameter,
    PerpendicularParameters,
    parameter_seed,
)
from app.engine.opening import rebuild
from app.math_input import MathInputError, parse_answer_input


@pytest.mark.parametrize("level", (1, 2, 3))
def test_parameter_finds_both_roots_and_diagram_shows_a_valid_choice(level: int) -> None:
    generator = PerpendicularParameter()
    for variation in range(8):
        params = generator.draw(parameter_seed(level, variation))
        task = generator.build(params)
        squared_u, squared_v = generator.squared_lengths(params)
        coefficient = 2 if level == 3 else 1
        root = sp.sqrt(squared_u / (coefficient * squared_v))
        assert set(task.answer.expected) == {root, -root}
        source = "{" + ",".join(sp.sstr(value).replace("**", "^") for value in (-root, root)) + "}"
        assert task.answer.check(parse_answer_input(source, "finite_set")) == "correct"
        assert (
            task.answer.check(
                parse_answer_input("{" + sp.sstr(root).replace("**", "^") + "}", "finite_set")
            )
            == "incorrect"
        )
        with pytest.raises(MathInputError):
            parse_answer_input("1,2", "finite_set")
        opened = rebuild(task.code)
        assert (opened.topic, opened.difficulty) == ("vectors", level)
        issued = opened.problem.issued()
        assert issued.statement_visual is not None
        assert all(step.get("visual") and step.get("rules") for step in issued.steps)
        assert all("alpha" not in line["label"] for line in issued.statement_visual["lines"])
        final = issued.steps[-1]["visual"]
        constructed = [
            sp.Matrix(line["end"]) for line in final["lines"] if "alpha" in line["label"]
        ]
        assert len(constructed) == 2
        assert abs(float(constructed[0].dot(constructed[1]))) < 1e-6


def test_source_lengths_give_both_three_fifths_roots() -> None:
    params = PerpendicularParameters(seed=0, level=1, a=3, b=5, u=(3, 0, 0), v=(0, 5, 0))
    answer = PerpendicularParameter().build(params).answer
    assert answer.check(parse_answer_input("{-3/5,3/5}", "finite_set")) == "correct"
    assert answer.check(parse_answer_input("{3/5}", "finite_set")) == "incorrect"
