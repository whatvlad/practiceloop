"""Local algebra exercises must be registered for production replay."""

import pytest

from app.engine.generators.catalogue import registry


def test_local_rank_generator_is_available_for_production_replay() -> None:
    from app.engine.practice import replay

    generator = registry().get("local-rank-v1")
    task = generator.build(generator.draw(123))
    restored = replay({"generator_version": generator.version, "code": task.code})
    assert restored == task


@pytest.mark.parametrize(
    "version",
    [
        "local-complex-v1",
        "local-conversion-v1",
        "local-conversion-polar-v1",
        "local-determinant-v4",
        "local-inverse-v1",
        "local-matrix-sized-v1",
        "local-matrix-division-v3",
        "local-system-v1",
        "local-polynomial-division-v1",
        "local-polynomial-scalar-v1",
        "local-polynomial-roots-v1",
        "local-partial-fractions-v1",
    ],
)
def test_local_generators_are_registered(version: str) -> None:
    assert registry().get(version).version == version


def test_rank_catalogue_seeds_cover_all_sizes_and_levels() -> None:
    from app.engine.algebra_practice.catalogue_seeds import rank_seeds
    from app.engine.algebra_practice.rank import LocalRankGenerator

    generator = LocalRankGenerator()
    seeds = list(rank_seeds(variation=0))
    assert len(seeds) == 48
    actual = set()
    for seed in seeds:
        parameters = generator.draw(seed)
        actual.add((parameters.level, len(parameters.matrix), len(parameters.matrix[0])))
    assert actual == {
        (level, rows, cols) for level in (1, 2, 3) for rows in range(2, 6) for cols in range(2, 6)
    }


def test_matrix_catalogue_seeds_cover_every_compatible_dimension() -> None:
    from app.engine.algebra_practice.catalogue_seeds import matrix_seeds
    from app.engine.algebra_practice.local_matrix_generator import LocalMatrixGenerator

    generator = LocalMatrixGenerator()
    seeds = list(matrix_seeds(level=1, variation=0))
    assert len(seeds) == 200
    settings = set()
    for seed in seeds:
        params = generator.draw(seed)
        settings.add((params.operation, params.rowsA, params.colsA, params.rowsB, params.colsB))
    assert len(settings) == 200


def test_matrix_catalogue_has_every_setting() -> None:
    from app.engine.algebra_practice.catalogue_seeds import matrix_seeds
    from app.engine.catalogue import build
    from app.engine.codes import parse_code
    from app.engine.topics.catalogue import topics

    generators = registry()
    catalogue = build({"matrix-operations": topics()["matrix-operations"]}, generators, pool_size=1)
    for cell in catalogue.cells:
        seeds = {
            parse_code(problem.code, generators).seed
            for problem in cell.problems
            if problem.generator_version in {"local-matrix-sized-v1", "local-matrix-division-v3"}
        }
        assert set(matrix_seeds(cell.level, 0)) <= seeds
        assert set(matrix_seeds(cell.level, 1)) <= seeds


@pytest.mark.parametrize(
    ("slug", "version"),
    [
        ("determinants", "local-determinant-v4"),
        ("inverse-matrices", "local-inverse-v1"),
        ("linear-systems", "local-system-v1"),
    ],
)
def test_square_matrix_catalogue_covers_sizes(slug: str, version: str) -> None:
    from app.engine.catalogue import build
    from app.engine.codes import parse_code
    from app.engine.topics.catalogue import topics

    generators = registry()
    catalogue = build({slug: topics()[slug]}, generators, pool_size=8)
    for cell in catalogue.cells:
        if cell.level > 3:
            continue
        sizes = {
            (parse_code(problem.code, generators).seed // 10**12) % 4 + 2
            for problem in cell.problems
            if problem.generator_version == version
        }
        assert sizes == {2, 3, 4, 5}


@pytest.mark.parametrize(
    ("slug", "version"),
    [
        ("determinants", "local-determinant-v4"),
        ("inverse-matrices", "local-inverse-v1"),
        ("linear-systems", "local-system-v1"),
    ],
)
def test_square_matrix_api_selects_size(
    slug: str, version: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.api.practice import GenerateBody
    from app.engine import practice
    from app.engine.algebra_practice.local_determinant_generator import determinant_seed
    from app.engine.catalogue import StoredProblem
    from app.engine.rendering import render

    assert GenerateBody(topic=slug, difficulty=1, squareSize=4).squareSize == 4
    generator = practice._registry().get(version)
    task = generator.build(generator.draw(determinant_seed(1, 4, 0)))
    candidate = StoredProblem.from_issued(render(task, practice._registry()))
    monkeypatch.setattr(practice, "pool", lambda _topic, _level: (candidate,))
    issued = practice.issue(slug, 1, square_size=4)
    assert issued.record["code"] == task.code
    assert practice.public_settings(issued.record)["squareSize"] == 4


@pytest.mark.parametrize(
    ("slug", "modes"),
    [
        ("complex-arithmetic", {"multiply", "divide"}),
        ("polynomial-division", {"division", "remainder", "divisibility"}),
        ("complex-conversion", {"alg-trig", "alg-exp", "trig-alg", "exp-alg"}),
        ("polynomial-roots", {"roots"}),
        ("partial-fractions", {"fractions"}),
    ],
)
def test_mode_catalogue_has_all_local_modes(slug: str, modes: set[str]) -> None:
    from app.engine import practice
    from app.engine.catalogue import build
    from app.engine.topics.catalogue import topics

    catalogue = build({slug: topics()[slug]}, practice._registry(), pool_size=16)
    for cell in catalogue.cells:
        if cell.level <= 3:
            found = {
                practice.public_settings(p.issued().record).get("exerciseMode")
                for p in cell.problems
            }
            assert modes <= found


def test_polar_catalogue_includes_all_exercise_types() -> None:
    from app.engine import practice
    from app.engine.catalogue import build
    from app.engine.topics.catalogue import topics

    catalogue = build(
        {"complex-polar-form": topics()["complex-polar-form"]}, practice._registry(), pool_size=8
    )
    modes = {
        practice.public_settings(p.issued().record).get("exerciseMode")
        for cell in catalogue.cells
        for p in cell.problems
    }
    assert {"argument", "power", "root"} <= modes


def test_modulus_catalogue_guarantees_two_per_mode() -> None:
    from app.engine.algebra_practice.selection import modulus_selection
    from app.engine.catalogue import build
    from app.engine.codes import parse_code
    from app.engine.topics.catalogue import topics

    generators = registry()
    catalogue = build({"complex-numbers": topics()["complex-numbers"]}, generators, pool_size=16)
    for cell in catalogue.cells:
        if cell.level <= 3:
            present = {
                (p.generator_version, parse_code(p.code, generators).seed) for p in cell.problems
            }
            expected = {
                modulus_selection(cell.level, mode, variation)
                for mode in ("expression", "properties", "geometry")
                for variation in (0, 1)
            }
            assert expected <= present


def test_all_twelve_topics_can_issue_each_local_setting(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.engine import practice
    from app.engine.algebra_practice.catalogue_seeds import matrix_seeds, mode_seeds
    from app.engine.catalogue import build
    from app.engine.topics.catalogue import topics

    all_topics = topics()
    slugs = (
        "matrix-operations",
        "determinants",
        "inverse-matrices",
        "matrix-rank",
        "linear-systems",
        "complex-arithmetic",
        "complex-numbers",
        "complex-conversion",
        "complex-polar-form",
        "polynomial-division",
        "polynomial-roots",
        "partial-fractions",
    )
    catalogue = build(
        {slug: all_topics[slug] for slug in slugs}, practice._registry(), pool_size=16
    )
    cells = {(cell.topic, cell.level): cell.problems for cell in catalogue.cells}
    monkeypatch.setattr(practice, "pool", lambda slug, level: cells[(slug, level)])
    for level in (1, 2, 3):
        for seed in matrix_seeds(level, 0):
            generator = practice._registry().get("local-matrix-sized-v1")
            params = generator.draw(seed)
            dimensions = {
                "operation": params.operation,
                "rowsA": params.rowsA,
                "colsA": params.colsA,
                "rowsB": params.rowsB,
                "colsB": params.colsB,
            }
            issued = practice.issue("matrix-operations", level, matrix_dimensions=dimensions)
            assert practice.public_settings(issued.record)["matrixDimensions"] == dimensions
        for slug in ("determinants", "inverse-matrices", "linear-systems"):
            for size in range(2, 6):
                assert (
                    practice.public_settings(practice.issue(slug, level, square_size=size).record)[
                        "squareSize"
                    ]
                    == size
                )
        for rows in range(2, 6):
            for columns in range(2, 6):
                dims = {"rows": rows, "columns": columns}
                assert (
                    practice.public_settings(
                        practice.issue("matrix-rank", level, rank_dimensions=dims).record
                    )["rankDimensions"]
                    == dims
                )
        for mode in ("expression", "properties", "geometry"):
            assert (
                practice.public_settings(
                    practice.issue("complex-numbers", level, modulus_mode=mode).record
                )["modulusMode"]
                == mode
            )
        for slug in (
            "complex-arithmetic",
            "complex-conversion",
            "polynomial-division",
            "polynomial-roots",
            "partial-fractions",
        ):
            for mode, _, _ in mode_seeds(slug, level, 0):
                assert (
                    practice.public_settings(
                        practice.issue(slug, level, exercise_mode=mode).record
                    )["exerciseMode"]
                    == mode
                )
    for level, mode in enumerate(("argument", "power", "root"), 1):
        assert (
            practice.public_settings(
                practice.issue("complex-polar-form", level, exercise_mode=mode).record
            )["exerciseMode"]
            == mode
        )


def test_local_codes_reopen_with_original_level() -> None:
    from app.engine.algebra_practice.rank import LocalRankGenerator, rank_seed
    from app.engine.opening import rebuild

    generator = LocalRankGenerator()
    for level in (1, 2, 3):
        task = generator.build(generator.draw(rank_seed(level, 3, 4, 0)))
        opened = rebuild(task.code)
        assert (opened.topic, opened.difficulty) == ("matrix-rank", level)


def test_each_local_generator_reopens_in_its_topic_and_level() -> None:
    from app.engine import practice
    from app.engine.algebra_practice.catalogue_seeds import mode_seeds
    from app.engine.algebra_practice.local_determinant_generator import determinant_seed
    from app.engine.algebra_practice.local_matrix_generator import make_seed
    from app.engine.opening import rebuild

    generators = registry()
    for level in (1, 2, 3):
        samples = [
            (
                "matrix-operations",
                "local-matrix-sized-v1",
                make_seed("multiply", level, (2, 3, 3, 4), 0),
            )
        ]
        samples.append(
            (
                "matrix-operations",
                "local-matrix-division-v3",
                make_seed("divide", level, (2, 3, 3, 3), 0),
            )
        )
        samples += [
            (slug, version, determinant_seed(level, 3, 0))
            for slug, version in (
                ("determinants", "local-determinant-v4"),
                ("inverse-matrices", "local-inverse-v1"),
                ("linear-systems", "local-system-v1"),
            )
        ]
        for slug in (
            "complex-arithmetic",
            "complex-numbers",
            "complex-conversion",
            "complex-polar-form",
            "polynomial-division",
            "polynomial-roots",
            "partial-fractions",
        ):
            samples.extend((slug, version, seed) for _, version, seed in mode_seeds(slug, level, 0))
        for slug, version, seed in samples:
            generator = generators.get(version)
            task = generator.build(generator.draw(seed))
            opened = rebuild(task.code)
            assert (opened.topic, opened.difficulty) == (slug, level)
            assert practice.input_contract(opened.problem.issued().record) == getattr(
                task.answer, "contract", None
            )


def test_reading_local_input_contracts_avoids_sympy_at_request_time() -> None:
    import sys

    from app.engine import practice
    from app.engine.algebra_practice.catalogue_seeds import mode_seeds
    from app.engine.algebra_practice.local_determinant_generator import determinant_seed
    from app.engine.algebra_practice.local_matrix_generator import make_seed

    samples = [
        ("local-matrix-sized-v1", make_seed("multiply", 1, (2, 3, 3, 4), 0)),
        ("local-inverse-v1", determinant_seed(2, 3, 0)),
        ("local-system-v1", determinant_seed(2, 3, 0)),
    ]
    for slug in (
        "complex-numbers",
        "complex-conversion",
        "polynomial-division",
        "partial-fractions",
    ):
        samples.extend((version, seed) for _, version, seed in mode_seeds(slug, 2, 0))
    records = [
        {
            "generator_version": version,
            "code": practice._registry()
            .get(version)
            .build(practice._registry().get(version).draw(seed))
            .code,
        }
        for version, seed in samples
    ]
    calls: list[str] = []
    previous = sys.getprofile()

    def profile(frame, event, arg):
        if event == "call" and frame.f_globals.get("__name__", "").startswith("sympy"):
            calls.append(frame.f_code.co_name)

    sys.setprofile(profile)
    try:
        for record in records:
            practice.input_projection(record)
            practice.public_settings(record)
            practice.input_variables(record)
    finally:
        sys.setprofile(previous)
    assert calls == []


def test_every_matrix_setting_accepts_correct_answer_and_rejects_wrong_answer() -> None:
    from itertools import chain

    from app.engine import practice
    from app.engine.algebra_practice.catalogue_seeds import matrix_seeds
    from app.engine.algebra_practice.local_matrix_generator import OPERATIONS
    from app.math_input import parse_answer_input

    generators = practice._registry()
    for level in (1, 2, 3):
        for seed in chain(matrix_seeds(level, 0), matrix_seeds(level, 1)):
            operation = OPERATIONS[(seed // 10**12) // (3 * 5**4)]
            version = (
                "local-matrix-division-v3"
                if operation == "divide" and level > 1
                else "local-matrix-sized-v1"
            )
            generator = generators.get(version)
            task = generator.build(generator.draw(seed))
            record = {"generator_version": version, "code": task.code}
            values = [list(row) for row in task.answer.expected]

            def source(rows):
                return (
                    "("
                    + ";".join("(" + ";".join(str(value) for value in row) + ")" for row in rows)
                    + ")"
                )

            contract = practice.input_contract(record)
            assert (
                practice.check(
                    record, parse_answer_input(source(values), "tuple", contract=contract)
                )
                == "correct"
            )
            values[0][0] += 1
            assert (
                practice.check(
                    record, parse_answer_input(source(values), "tuple", contract=contract)
                )
                != "correct"
            )


def test_complex_exercise_has_solution_visual() -> None:
    from app.engine.algebra_practice.local_complex_generator import (
        LocalComplexGenerator,
        complex_seed,
    )
    from app.engine.rendering import render

    generator = LocalComplexGenerator()
    task = generator.build(generator.draw(complex_seed(1, "multiply", 1)))
    visual = render(task, registry()).visual
    assert visual is not None and visual["kind"] == "complex-plane"


def test_complex_operation_worksheet_does_not_claim_modulus() -> None:
    from app.services.worksheet_graphs import complex_plane

    graphic = complex_plane(
        {
            "kind": "complex-plane",
            "version": 1,
            "mode": "multiply",
            "first": [1.0, 2.0],
            "second": [2.0, 1.0],
            "result": [0.0, 5.0],
            "power": None,
        }
    )
    assert "modulus is the distance" not in graphic


def test_determinant_solution_has_diagram_data() -> None:
    from app.engine.algebra_practice.local_determinant_generator import (
        ExplainedDeterminantGenerator,
        determinant_seed,
    )
    from app.engine.rendering import render
    from app.visuals.spec import solution_payload

    generator = ExplainedDeterminantGenerator()
    task = generator.build(generator.draw(determinant_seed(1, 3, 0)))
    issued = render(task, registry())
    payload = solution_payload(list(issued.steps), issued.record)
    assert any("determinantMatrix" in step for step in payload["steps"])


def test_polynomial_root_solution_includes_theorem() -> None:
    from app.engine.algebra_practice.local_polynomial_roots_generator import (
        LocalPolynomialRootsGenerator,
    )
    from app.engine.rendering import render
    from app.visuals.spec import solution_payload

    generator = LocalPolynomialRootsGenerator()
    issued = render(generator.build(generator.draw(0)), registry())
    payload = solution_payload(list(issued.steps), issued.record)
    assert any(step.get("rules") for step in payload["steps"])


def test_saved_complex_solution_includes_its_visual(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.engine import practice
    from app.engine.algebra_practice.local_complex_generator import (
        LocalComplexGenerator,
        complex_seed,
    )
    from app.engine.rendering import render
    from app.visuals import spec

    generator = LocalComplexGenerator()
    task = generator.build(generator.draw(complex_seed(1, "divide", 1)))
    issued = render(task, registry())
    monkeypatch.setattr(practice, "pooled", lambda record: issued)
    spec._build.cache_clear()
    payload = spec.solution_payload(list(issued.steps), issued.record)
    assert payload["visual"]["kind"] == "complex-plane"
    assert any(step.get("rules") for step in payload["steps"])


def test_polar_power_includes_detailed_solution(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.engine import practice
    from app.engine.generators.complex_numbers import DeMoivre
    from app.engine.rendering import render
    from app.visuals import spec

    generator = DeMoivre()
    task = generator.build(generator.draw(12))
    issued = render(task, registry())
    monkeypatch.setattr(practice, "pooled", lambda record: issued)
    spec._build.cache_clear()
    payload = spec.solution_payload(list(issued.steps), issued.record)
    assert len(payload["steps"]) >= 10
    assert any(step.get("rules") for step in payload["steps"])


@pytest.mark.parametrize(
    ("slug", "mode"),
    [
        ("complex-arithmetic", "divide"),
        ("polynomial-division", "remainder"),
        ("complex-conversion", "alg-trig"),
        ("polynomial-roots", "roots"),
        ("partial-fractions", "fractions"),
        ("complex-polar-form", "power"),
    ],
)
def test_mode_api_selects_requested_problem(
    slug: str, mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.api.practice import GenerateBody
    from app.engine import practice
    from app.engine.algebra_practice.catalogue_seeds import mode_seeds
    from app.engine.catalogue import StoredProblem
    from app.engine.rendering import render

    level = 2 if slug == "complex-polar-form" and mode == "power" else 1
    assert GenerateBody(topic=slug, difficulty=level, exerciseMode=mode).exerciseMode == mode
    _, version, seed = next(item for item in mode_seeds(slug, level, 0) if item[0] == mode)
    generator = practice._registry().get(version)
    task = generator.build(generator.draw(seed))
    monkeypatch.setattr(
        practice,
        "pool",
        lambda _topic, _level: (StoredProblem.from_issued(render(task, practice._registry())),),
    )
    issued = practice.issue(slug, level, exercise_mode=mode)
    assert issued.record["code"] == task.code


def test_production_rank_catalogue_contains_every_supported_shape() -> None:
    from app.engine.catalogue import build
    from app.engine.codes import parse_code
    from app.engine.topics.catalogue import topics

    generators = registry()
    catalogue = build({"matrix-rank": topics()["matrix-rank"]}, generators, pool_size=16)
    rank_generator = generators.get("local-rank-v1")
    for cell in catalogue.cells:
        shapes = set()
        for problem in cell.problems:
            if problem.generator_version == rank_generator.version:
                params = rank_generator.draw(parse_code(problem.code, generators).seed)
                shapes.add((len(params.matrix), len(params.matrix[0])))
        assert shapes == {(rows, cols) for rows in range(2, 6) for cols in range(2, 6)}


def test_rank_catalogue_has_two_problems_per_shape() -> None:
    from app.engine.catalogue import build
    from app.engine.codes import parse_code
    from app.engine.topics.catalogue import topics

    generators = registry()
    catalogue = build({"matrix-rank": topics()["matrix-rank"]}, generators, pool_size=32)
    for cell in catalogue.cells:
        counts: dict[tuple[int, int], int] = {}
        generator = generators.get("local-rank-v1")
        for problem in cell.problems:
            if problem.generator_version == generator.version:
                p = generator.draw(parse_code(problem.code, generators).seed)
                shape = (len(p.matrix), len(p.matrix[0]))
                counts[shape] = counts.get(shape, 0) + 1
        assert set(counts.values()) == {2}


def test_rank_api_accepts_dimensions() -> None:
    from pydantic import ValidationError

    from app.api.practice import GenerateBody

    body = GenerateBody(topic="matrix-rank", difficulty=1, rankDimensions={"rows": 3, "columns": 5})
    assert body.rankDimensions is not None
    assert body.rankDimensions.model_dump() == {"rows": 3, "columns": 5}
    with pytest.raises(ValidationError):
        GenerateBody(topic="matrix-rank", difficulty=1, rankDimensions={"rows": 1, "columns": 5})


def test_matrix_api_accepts_custom_dimensions() -> None:
    from app.api.practice import GenerateBody

    dimensions = {"operation": "multiply", "rowsA": 2, "colsA": 3, "rowsB": 3, "colsB": 4}
    body = GenerateBody(topic="matrix-operations", difficulty=1, matrixDimensions=dimensions)
    assert body.matrixDimensions is not None
    assert body.matrixDimensions.model_dump() == dimensions


def test_matrix_selection_uses_matching_catalogue_problem(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.engine import practice
    from app.engine.algebra_practice.local_matrix_generator import LocalMatrixGenerator, make_seed
    from app.engine.catalogue import StoredProblem
    from app.engine.rendering import render

    generator = LocalMatrixGenerator()
    dims = {"operation": "multiply", "rowsA": 2, "colsA": 3, "rowsB": 3, "colsB": 4}
    task = generator.build(generator.draw(make_seed("multiply", 1, (2, 3, 3, 4), 0)))
    candidate = StoredProblem.from_issued(render(task, practice._registry()))
    monkeypatch.setattr(practice, "pool", lambda _topic, _level: (candidate,))
    issued = practice.issue("matrix-operations", 1, matrix_dimensions=dims)
    assert issued.record["code"] == task.code
    assert practice.public_settings(issued.record)["matrixDimensions"] == dims


def test_rank_selection_uses_matching_catalogue_problem(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.engine import practice
    from app.engine.algebra_practice.rank import LocalRankGenerator, rank_seed
    from app.engine.catalogue import StoredProblem
    from app.engine.rendering import render

    generator = LocalRankGenerator()
    tasks = [generator.build(generator.draw(rank_seed(1, r, c, 0))) for r, c in ((2, 2), (3, 5))]
    candidates = tuple(
        StoredProblem.from_issued(render(task, practice._registry())) for task in tasks
    )
    monkeypatch.setattr(practice, "pool", lambda _topic, _level: candidates)
    issued = practice.issue("matrix-rank", 1, rank_dimensions={"rows": 3, "columns": 5})
    assert issued.record["code"] == tasks[1].code
    assert practice.public_settings(issued.record)["rankDimensions"] == {"rows": 3, "columns": 5}
