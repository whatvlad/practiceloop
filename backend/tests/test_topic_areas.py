"""Curriculum grouping and compatibility of pre-#144 mixed requests."""

from uuid import uuid4

import pytest

from app.api import practice
from app.core.auth import VerifiedUser


def test_catalogue_groups_existing_topics_and_hides_empty_algebra() -> None:
    body = practice.topics(VerifiedUser(uuid4(), None))
    assert [area["slug"] for area in body["areas"]] == ["mathematical-analysis"]
    assert {item["area"] for item in body["items"]} == {"mathematical-analysis"}
    assert {item["slug"] for item in body["items"]} == {
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
    assert practice.mixed_topics("algebra", level) == ([], [])
