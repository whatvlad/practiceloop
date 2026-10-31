"""Stable streams and typo-detecting codes for the private generator engine."""

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_engine_core import TinyGenerator

from app.engine.codes import ProblemCode, format_code, parse_code
from app.engine.prng import DeterministicRNG, draw_valid
from app.engine.registry import Registry


def test_rng_sequence_is_pinned_and_bounds_are_checked() -> None:
    rng = DeterministicRNG(4821930017734529)
    assert [rng.randbelow(1000000) for _ in range(8)] == [
        643336,
        886885,
        105137,
        131278,
        277244,
        481070,
        500323,
        330206,
    ]
    with pytest.raises(ValueError):
        DeterministicRNG(-1)
    with pytest.raises(ValueError):
        DeterministicRNG(10**16)
    with pytest.raises(ValueError):
        DeterministicRNG(True)
    for upper in (0, -1, True, (1 << 256) + 1):
        with pytest.raises(ValueError):
            rng.randbelow(upper)
    assert rng.randbelow(1) == 0


def test_rejection_is_deterministic_and_stops_at_cap() -> None:
    def sample() -> int:
        rng = DeterministicRNG(123)
        return draw_valid(lambda: rng.randbelow(100), lambda candidate: candidate >= 90)

    assert sample() == sample() == 99
    draws: list[int] = []

    def reject() -> int:
        draws.append(1)
        return 0

    with pytest.raises(ValueError, match="after 3 draws"):
        draw_valid(reject, lambda _: False, max_attempts=3)
    assert len(draws) == 3
    for invalid in (0, 65, True):
        with pytest.raises(ValueError, match="1 through 64"):
            draw_valid(reject, lambda _: True, max_attempts=invalid)


def test_randbelow_retries_out_of_range_hashes_and_caps_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.engine import prng

    calls: list[bytes] = []

    def hash_candidate(data: bytes) -> SimpleNamespace:
        calls.append(data)
        value = (1 << 256) - 1 if len(calls) == 1 else 4
        return SimpleNamespace(digest=lambda: value.to_bytes(32, "big"))

    monkeypatch.setattr(prng, "sha256", hash_candidate)
    assert DeterministicRNG(123).randbelow(3) == 1
    assert [int.from_bytes(data[-8:], "big") for data in calls] == [0, 1]

    monkeypatch.setattr(prng, "sha256", lambda _: SimpleNamespace(digest=lambda: b"\xff" * 32))
    with pytest.raises(RuntimeError, match="rejection limit"):
        DeterministicRNG(123).randbelow(3)


def test_new_engine_does_not_import_global_random() -> None:
    engine = Path(__file__).resolve().parents[1] / "app" / "engine"
    for path in engine.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name.split(".")[0] != "random" for alias in node.names), path
            if isinstance(node, ast.ImportFrom):
                assert node.module is None or node.module.split(".")[0] != "random", path


@pytest.fixture
def registry() -> Registry:
    result = Registry()
    result.register(TinyGenerator(version="tiny-v1"))
    result.register(TinyGenerator(version="tiny-v2"))
    result.register(TinyGenerator(version="other-v1"))
    result.register_code("TNY", "tiny", 1, "tiny-v1")
    result.register_code("TNY", "tiny", 2, "tiny-v2")
    result.register_code("OTH", "other", 1, "other-v1")
    return result


def test_codes_round_trip_and_normalise_separators(registry: Registry) -> None:
    for seed in (0, 1, 10, 4821930017734529, 9999999999999999):
        for version in (1, 2):
            code = ProblemCode("TNY", version, seed)
            formatted = format_code(code, registry)
            assert parse_code(formatted, registry) == code
            assert parse_code(formatted.lower().replace("-", " "), registry) == code
            assert parse_code(formatted.replace("-", ""), registry) == code
            assert registry.get_code(code.prefix, code.version).version == f"tiny-v{version}"
    rng = DeterministicRNG(7)
    for _ in range(1000):
        code = ProblemCode("TNY", 1, rng.randbelow(10**16))
        assert parse_code(format_code(code, registry), registry) == code


def test_every_single_digit_change_is_rejected(registry: Registry) -> None:
    for version in (1, 2):
        source = format_code(ProblemCode("TNY", version, 4821930017734529), registry)
        for position, old in enumerate(source):
            if not old.isdigit():
                continue
            for replacement in "0123456789":
                if replacement == old:
                    continue
                with pytest.raises(ValueError):
                    parse_code(source[:position] + replacement + source[position + 1 :], registry)


def test_every_swap_of_distinct_seed_digits_is_rejected(registry: Registry) -> None:
    source = format_code(ProblemCode("TNY", 1, 4821930017734529), registry)
    seed_start = source.index("-", source.index("-") + 1) + 1
    for left in range(seed_start, seed_start + 16):
        for right in range(left + 1, seed_start + 16):
            if source[left] == source[right]:
                continue
            changed = list(source)
            changed[left], changed[right] = changed[right], changed[left]
            with pytest.raises(ValueError):
                parse_code("".join(changed), registry)


def test_registry_rejects_reused_prefixes_and_unknown_versions(registry: Registry) -> None:
    with pytest.raises(ValueError, match="another family"):
        registry.register_code("TNY", "other", 3, "other-v1")
    with pytest.raises(ValueError, match="already has a prefix"):
        registry.register_code("NEW", "tiny", 3, "tiny-v1")
    with pytest.raises(ValueError, match="Duplicate code version"):
        registry.register_code("TNY", "tiny", 1, "tiny-v1")
    with pytest.raises(ValueError, match="Unknown generator"):
        registry.register_code("NEW", "new", 1, "missing-v1")
    with pytest.raises(ValueError, match="Unknown code"):
        registry.get_code("TNY", 3)
    with pytest.raises(ValueError, match="Invalid code"):
        registry.get_code("TNY", True)
    with pytest.raises(ValueError, match="Unknown code"):
        parse_code("BAD-1-0000000000000000-00", registry)
    for invalid in ("TNY-1-0-00", "TNY-01-0000000000000000-00", "é" * 150):
        with pytest.raises(ValueError):
            parse_code(invalid, registry)
