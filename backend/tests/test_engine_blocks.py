"""Bounded, deterministic mathematical blocks for new-engine generators."""

import ast
from pathlib import Path

import pytest
import sympy as sp
from pydantic import ValidationError
from seed_sweep import sweep

from app.engine.blocks.integers import IntegerRange
from app.engine.blocks.polynomial import Polynomial
from app.engine.blocks.rational import PartialFractionRational
from app.engine.prng import DeterministicRNG

X = sp.Symbol("x", real=True)


@pytest.mark.parametrize(
    "params",
    [
        {"minimum": 2, "maximum": 1},
        {"minimum": -13, "maximum": 1},
        {"minimum": 0, "maximum": 13},
        {"minimum": 0, "maximum": 2, "exclude": (1, 1)},
        {"minimum": 0, "maximum": 2, "exclude": (3,)},
        {"minimum": 0, "maximum": 1, "exclude": (0, 1)},
        {"minimum": True, "maximum": 1},
    ],
)
def test_integer_range_rejects_invalid_constraints(params: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        IntegerRange.model_validate(params)


def test_integer_range_draw_is_reproducible_and_respects_exclusions() -> None:
    allowed = IntegerRange(minimum=-2, maximum=2, exclude=(-2, 0, 2))
    assert allowed.model_validate_json(allowed.model_dump_json()) == allowed
    for seed in sweep(1000):
        left = allowed.draw(DeterministicRNG(seed))
        assert left == allowed.draw(DeterministicRNG(seed))
        assert left in {-1, 1}
    assert IntegerRange(minimum=3, maximum=3).draw(DeterministicRNG(0)) == 3


@pytest.mark.parametrize(
    "coefficients",
    [(), (0,), (1, 0), (1,) * 7, (100_001,), (-100_001,), (True, 1)],
)
def test_polynomial_rejects_invalid_coefficients(coefficients: tuple[object, ...]) -> None:
    with pytest.raises(ValidationError):
        Polynomial.model_validate({"coefficients": coefficients})


def test_polynomial_from_coefficients_and_roots() -> None:
    polynomial = Polynomial(coefficients=(-4, 0, 3))
    assert polynomial.expression(X) == 3 * X**2 - 4
    assert Polynomial.model_validate_json(polynomial.model_dump_json()) == polynomial
    rooted = Polynomial.from_roots((0, 1, -2, 1), leading=-3)
    assert sp.expand(rooted.expression(X) + 3 * X * (X - 1) ** 2 * (X + 2)) == 0
    assert all(rooted.expression(X).subs(X, root) == 0 for root in (0, 1, -2))
    assert Polynomial.from_roots((), leading=2).expression(X) == 2
    for roots, leading in (((7,), 1), ((True,), 1), ((1,) * 6, 1), ((0,), 0), ((0,), 7)):
        with pytest.raises(ValueError):
            Polynomial.from_roots(roots, leading=leading)


def test_polynomial_draw_is_bounded_and_deterministic() -> None:
    assert Polynomial.draw(DeterministicRNG(123), 3).coefficients == (1, 0, -4, 5)
    for degree in range(6):
        for seed in sweep(1000):
            result = Polynomial.draw(DeterministicRNG(seed), degree)
            assert result == Polynomial.draw(DeterministicRNG(seed), degree)
            assert len(result.coefficients) == degree + 1
            assert result.coefficients[-1] != 0
            assert all(abs(coefficient) <= 6 for coefficient in result.coefficients)
    for invalid in (-1, 6, True):
        with pytest.raises(ValueError):
            Polynomial.draw(DeterministicRNG(0), invalid)


@pytest.mark.parametrize(
    ("poles", "numerators"),
    [
        ((), ()),
        ((0,), ()),
        ((0, 0), (1, 2)),
        ((7,), (1,)),
        ((0,), (0,)),
        ((0,), (7,)),
        ((True,), (1,)),
        ((0, 1, 2, 3, 4), (1, 1, 1, 1, 1)),
    ],
)
def test_rational_rejects_invalid_terms(
    poles: tuple[object, ...], numerators: tuple[int, ...]
) -> None:
    with pytest.raises(ValidationError):
        PartialFractionRational.model_validate({"poles": poles, "numerators": numerators})


def test_rational_decomposition_and_combined_expression_are_equal() -> None:
    block = PartialFractionRational(poles=(-2, 1, 3), numerators=(2, -3, 1))
    assert block.model_validate_json(block.model_dump_json()) == block
    assert sp.cancel(block.combined(X) - block.decomposition(X)) == 0
    for pole, numerator in zip(block.poles, block.numerators, strict=True):
        assert sp.limit((X - pole) * block.combined(X), X, pole) == numerator


def test_rational_combines_known_fractions() -> None:
    block = PartialFractionRational(poles=(-2, 1, 3), numerators=(2, -3, 1))
    expected = (22 - 4 * X) / ((X + 2) * (X - 1) * (X - 3))
    assert sp.cancel(block.combined(X) - expected) == 0


def test_rational_draw_is_bounded_deterministic_and_keeps_all_poles() -> None:
    pinned = PartialFractionRational.draw(DeterministicRNG(123), 3)
    assert pinned.poles == (1, 0, 2)
    assert pinned.numerators == (-1, 5, -1)
    for terms in range(1, 5):
        for seed in sweep(1000):
            result = PartialFractionRational.draw(DeterministicRNG(seed), terms)
            assert result == PartialFractionRational.draw(DeterministicRNG(seed), terms)
            assert len(set(result.poles)) == terms
            assert all(abs(pole) <= 6 for pole in result.poles)
            assert all(1 <= abs(value) <= 6 for value in result.numerators)
        for seed in range(10):
            result = PartialFractionRational.draw(DeterministicRNG(seed), terms)
            assert sp.cancel(result.combined(X) - result.decomposition(X)) == 0
    for invalid in (0, 5, True):
        with pytest.raises(ValueError):
            PartialFractionRational.draw(DeterministicRNG(0), invalid)


def test_blocks_do_not_import_topics_generators_or_content() -> None:
    blocks = Path(__file__).resolve().parents[1] / "app" / "engine" / "blocks"
    forbidden = ("app.engine.topics", "app.engine.generators", "app.generators", "app.content")
    for path in blocks.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(not name.name.startswith(forbidden) for name in node.names), path
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(forbidden), path
                assert not (
                    node.level > 0 and node.module.split(".")[0] in {"topics", "generators"}
                )
