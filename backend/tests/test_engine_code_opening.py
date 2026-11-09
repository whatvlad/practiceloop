"""#198: permanent codes preserve every shipped golden task and its private boundary."""

import json
import sys
from pathlib import Path
from types import FrameType
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api import codes
from app.core.auth import current_user
from app.engine import practice as engine_practice
from app.engine.catalogue import StoredProblem
from app.engine.codes import encode, parse_code
from app.engine.opening import OpenedCode, _cell, rebuild
from app.engine.rendering import statement_latex
from app.main import app
from app.services.math_worker import MathWorkerError, open_problem_code

GOLDEN = json.loads(
    (Path(__file__).parent / "fixtures/engine_golden_v1.json").read_text(encoding="utf-8")
)
SAMPLES = [sample for samples in GOLDEN.values() for sample in samples]


def _served(code: str) -> StoredProblem | None:
    """The task as practice issues it, or None when no practice view serves this draw."""
    generators = engine_practice._registry()
    parsed = parse_code(code, generators)
    generator = generators.get_code(parsed.prefix, parsed.version)
    params = generator.draw(parsed.seed)
    try:
        _cell(generator.version, params)
    except ValueError:
        return None
    return StoredProblem.from_issued(engine_practice._public(generator.build(params)))


@pytest.mark.parametrize("sample", SAMPLES, ids=lambda sample: sample["code"])
def test_every_golden_code_opens_the_exact_shipped_task(sample: dict[str, Any]) -> None:
    served = _served(sample["code"])
    if served is None:
        # Catalogue-only generators serve chosen seeds; other draws were never issued.
        with pytest.raises(ValueError, match="No practice view"):
            rebuild(sample["code"])
        return
    for spelling in (sample["code"], sample["code"].lower(), sample["code"].replace("-", " ")):
        opened = rebuild(spelling)
        assert opened.problem.code == sample["code"]
        assert opened.problem.statement == statement_latex(sample["statement"])
        assert opened.problem.answer_latex == sample["answer_latex"]
        # Practice rendering may present the pinned steps differently (polar-form walkthroughs),
        # so the opened steps are those practice issues for the same draw.
        assert opened.problem.steps == served.steps
        assert opened.topic in codes.engine.ENGINE_TOPICS
        assert opened.difficulty in codes.engine.levels(opened.topic)


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    codes._opened.cache_clear()
    codes.lookup_limit.reset()

    def no_identity():
        pytest.fail("Public lookup requested an identity")

    app.dependency_overrides[current_user] = no_identity
    with TestClient(app) as result:
        yield result
    app.dependency_overrides.pop(current_user)
    codes._opened.cache_clear()


def test_public_code_lookup_projects_only_the_statement_without_symbolic_work(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private = rebuild(SAMPLES[0]["code"])
    monkeypatch.setattr(codes, "open_problem_code", lambda _: private.model_dump_json().encode())
    calls = []

    def profile(frame: FrameType, event: str, _: Any) -> None:
        if event == "call" and frame.f_globals.get("__name__", "").startswith("sympy"):
            calls.append(frame.f_code.co_name)

    previous = sys.getprofile()
    sys.setprofile(profile)
    try:
        body = codes.lookup(private.problem.code.lower())
    finally:
        sys.setprofile(previous)
    response = client.get("/codes", params={"code": private.problem.code.lower()})
    assert response.status_code == 200 and response.json() == body
    assert response.json() == {
        "problem": {
            "topic": private.topic,
            "difficulty": private.difficulty,
            "problemLatex": private.problem.statement,
        }
    }
    assert response.headers["cache-control"] == "no-store"
    assert not calls


@pytest.mark.parametrize(
    "code",
    [
        "nonsense",
        encode("ZZZ", 1, 0),
        encode("CMB", 9999, 0),
        encode("CMB", 1, 0)[:-2] + "99",
        "x" * 129,
        "\u03c0",
    ],
)
def test_invalid_unknown_and_wrong_checksum_codes_fail_before_symbolic_work(
    code: str,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        codes, "open_problem_code", lambda _: pytest.fail("Invalid code reached worker")
    )
    response = client.get("/codes", params={"code": code})
    assert response.status_code in (400, 422)
    assert set(response.json()) == {"error"}


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize(
    "sample", [s[0] for s in GOLDEN.values()], ids=lambda sample: sample["code"]
)
def test_each_version_rebuilds_in_the_limited_worker(sample: dict[str, Any]) -> None:
    opened = OpenedCode.model_validate_json(open_problem_code(sample["code"]))
    assert opened.problem.statement == statement_latex(sample["statement"])
    assert opened.problem.answer_latex == sample["answer_latex"]


def test_code_worker_failure_is_retryable_and_releases_the_shared_slot(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def failed(_: str) -> bytes:
        raise MathWorkerError("private worker detail")

    monkeypatch.setattr(codes, "open_problem_code", failed)
    response = client.get("/codes", params={"code": encode("CMB", 1, 198)})
    assert response.status_code == 503
    assert response.json()["error"]["retryable"]
    assert "private worker detail" not in response.text
    assert codes.CHECK_SLOTS.acquire(blocking=False)
    codes.CHECK_SLOTS.release()
