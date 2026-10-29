"""Curriculum grouping and compatibility of pre-#144 mixed requests."""

from uuid import uuid4

import pytest

from app.api import practice
from app.core.auth import VerifiedUser
from app.generators.core import catalogue


def test_catalogue_lists_algebra_and_syllabus_topics() -> None:
    body = practice.topics(VerifiedUser(uuid4(), None))
    assert [area["slug"] for area in body["areas"]] == ["algebra", "mathematical-analysis"]
    assert {item["area"] for item in body["items"]} == {"algebra", "mathematical-analysis"}
    assert {item["slug"] for item in body["items"]} == {
        "matrices",
        "complex-numbers",
        "fundamental-theorem-algebra",
        "partial-fractions",
        "basic-integrals",
        "substitution",
        "integration-by-parts",
        "rational-functions",
        "trigonometric-integrals",
        "definite-integrals",
        "double-integrals",
        "triple-integrals",
        "derivatives",
        "partial-derivatives",
        "functions-and-sequences",
        "limits-and-continuity",
        "improper-integrals",
        "series",
        "multivariable-functions",
        "differential-equations",
    }


@pytest.mark.parametrize("level", range(1, 6))
def test_combined_mixed_pool_preserves_weights_and_legacy_boundaries(level: int) -> None:
    integrals, integral_weights = practice.mixed_topics("integrals", level)
    derivatives, derivative_weights = practice.mixed_topics("derivatives", level)
    combined, weights = practice.mixed_topics("mathematical-analysis", level)
    assert set(integrals).isdisjoint(derivatives)
    assert dict(zip(combined, weights, strict=True)) == {
        **dict(zip(integrals, integral_weights, strict=True)),
        **dict(zip(derivatives, derivative_weights, strict=True)),
    }
    assert set(derivatives) == {"derivatives", "partial-derivatives"}
    assert "definite-integrals" not in combined
    algebra, algebra_weights = practice.mixed_topics("algebra", level)
    assert set(algebra) == {
        "matrices",
        "complex-numbers",
        "fundamental-theorem-algebra",
        "partial-fractions",
    }
    assert algebra_weights == [1, 1, 1, 1]


@pytest.mark.parametrize(
    "topic",
    (
        "matrices",
        "complex-numbers",
        "fundamental-theorem-algebra",
        "partial-fractions",
        "functions-and-sequences",
        "limits-and-continuity",
        "improper-integrals",
        "series",
        "multivariable-functions",
        "differential-equations",
    ),
)
def test_syllabus_topics_have_replayable_problems(topic: str) -> None:
    exercise = catalogue(topic, 1)[0]
    assert exercise.record["generator_version"] == "symbolic-v1"
    assert exercise.statement
    assert exercise.answer
