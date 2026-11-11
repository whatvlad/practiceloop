"""New geometry modes must run in the real resource-limited Linux worker."""

import sys

import pytest
import sympy as sp

from app.engine.algebra_practice.catalogue_seeds import mode_seeds
from app.engine.generators.catalogue import registry
from app.engine.opening import OpenedCode
from app.services.math_worker import check_answer, open_problem_code

pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")


def source(value):
    return sp.sstr(value).replace("**", "^")


@pytest.mark.parametrize("level", (1, 2, 3))
@pytest.mark.parametrize("index", range(10))
def test_modes_check_and_reopen_inside_limited_worker(level, index) -> None:
    _, version, seed = mode_seeds("vectors", level, 0)[index]
    generator = registry().get(version)
    task = generator.build(generator.draw(seed))
    answer = task.answer
    if answer.kind == "tuple":
        values = [component.expected for component in answer.components]
        correct = "(" + ";".join(source(value) for value in values) + ")"
        wrong = "(" + ";".join(source(value + int(i == 0)) for i, value in enumerate(values)) + ")"
    elif answer.kind == "finite_set":
        correct = "{" + ",".join(source(value) for value in answer.expected) + "}"
        wrong = "{" + source(answer.expected[0]) + "}"
    else:
        correct = source(answer.expected)
        wrong = f"({correct})+1"
    record = {"generator_version": version, "code": task.code}
    assert check_answer(correct, record).result == "correct"
    assert check_answer(wrong, record).result == "incorrect"
    assert check_answer("?", record).result == "invalid"
    opened = OpenedCode.model_validate_json(open_problem_code(task.code))
    assert (opened.topic, opened.difficulty) == ("vectors", level)
    assert opened.problem.issued().statement_visual is not None
