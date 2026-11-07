"""Isolated local demo. Run bound to 127.0.0.1; never mount in production."""

import re
import secrets
from functools import cache
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.api.practice import MatrixOptions
from app.engine.codes import parse_code
from app.engine.generators.catalogue import registry
from app.engine.practice import matrix_classification, matrix_options_supported
from app.engine.rendering import render
from app.engine.topics.catalogue import topics
from app.math_input.parser import MathInputError, MathNode
from app.math_input.structured import parse_answer_input
from local_determinant_generator import (
    ColoredDeterminantGenerator,
    DetailedDeterminantGenerator,
    ExplainedDeterminantGenerator,
    LocalDeterminantGenerator,
    determinant_seed,
)
from local_inverse_generator import LocalInverseGenerator, inverse_seed
from local_matrix_generator import (
    VARIATIONS,
    LeveledMatrixDivisionGenerator,
    LocalMatrixDivisionGenerator,
    LocalMatrixGenerator,
    make_seed,
)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Generate(Request):
    level: int = Field(ge=1, le=3)
    matrixOptions: MatrixOptions | None = None
    dimensions: "MatrixDimensions | None" = None
    determinantSize: int | None = Field(default=None, ge=2, le=5)
    inverseSize: int | None = Field(default=None, ge=2, le=5)


class MatrixDimensions(Request):
    operation: Literal["add", "subtract", "multiply", "divide"]
    rowsA: int = Field(ge=1, le=5)
    colsA: int = Field(ge=1, le=5)
    rowsB: int = Field(ge=1, le=5)
    colsB: int = Field(ge=1, le=5)


class Code(Request):
    code: str = Field(min_length=1, max_length=64)


class Check(Code):
    answer: str = Field(max_length=256)


@cache
def _registry():
    result = registry()
    result.register(LocalMatrixGenerator())
    result.register(LocalMatrixDivisionGenerator())
    result.register(LeveledMatrixDivisionGenerator())
    result.register(LocalDeterminantGenerator())
    result.register(DetailedDeterminantGenerator())
    result.register(ColoredDeterminantGenerator())
    result.register(ExplainedDeterminantGenerator())
    result.register(LocalInverseGenerator())
    return result


def _task(code: str):
    try:
        parsed = parse_code(code, _registry())
        generator = _registry().get_code(parsed.prefix, parsed.version)
        choices = topics()["matrix-operations"].levels.values()
        if generator.version not in {
            LocalMatrixGenerator.version,
            LocalMatrixDivisionGenerator.version,
            LeveledMatrixDivisionGenerator.version,
            LocalDeterminantGenerator.version,
            DetailedDeterminantGenerator.version,
            ColoredDeterminantGenerator.version,
            ExplainedDeterminantGenerator.version,
            LocalInverseGenerator.version,
        } and generator.version not in {choice.generator for group in choices for choice in group}:
            raise ValueError("Not a current matrix exercise")
        return generator.build(generator.draw(parsed.seed))
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=404, detail="Unknown preview problem") from exc


@app.post("/generate")
def generate(body: Generate):
    if body.inverseSize is not None:
        if (
            body.matrixOptions is not None
            or body.dimensions is not None
            or body.determinantSize is not None
        ):
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        generator = _registry().get(LocalInverseGenerator.version)
        seed = inverse_seed(body.level, body.inverseSize, secrets.randbelow(VARIATIONS))
        task = generator.build(generator.draw(seed))
        rendered = render(task, _registry())
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": rendered.statement,
            "answerInput": task.answer.contract.public(),
        }
    if body.determinantSize is not None:
        if body.matrixOptions is not None or body.dimensions is not None:
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        generator = _registry().get(ExplainedDeterminantGenerator.version)
        seed = determinant_seed(body.level, body.determinantSize, secrets.randbelow(VARIATIONS))
        task = generator.build(generator.draw(seed))
        rendered = render(task, _registry())
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": rendered.statement,
            "answerInput": task.answer.contract.public(),
        }
    if body.dimensions is not None:
        if body.matrixOptions is not None:
            raise HTTPException(status_code=422, detail="Choose one set of matrix settings")
        dims = body.dimensions
        try:
            seed = make_seed(
                dims.operation,
                body.level,
                (dims.rowsA, dims.colsA, dims.rowsB, dims.colsB),
                secrets.randbelow(VARIATIONS),
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        generator = _registry().get(
            LeveledMatrixDivisionGenerator.version
            if dims.operation == "divide" and body.level > 1
            else LocalMatrixGenerator.version
        )
        task = generator.build(generator.draw(seed))
        rendered = render(task, _registry())
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": rendered.statement,
            "answerInput": task.answer.contract.public(),
        }
    if body.matrixOptions and not matrix_options_supported(
        body.level, body.matrixOptions.model_dump()
    ):
        raise HTTPException(status_code=422, detail="No exercises match these settings")
    for _ in range(256):
        task = topics()["matrix-operations"].generate(
            body.level, secrets.randbelow(10**16), _registry()
        )
        record = {"code": task.code, "generator_version": task.generator_version}
        if body.matrixOptions is None or matrix_classification(record) == (
            body.matrixOptions.operation,
            body.matrixOptions.size,
        ):
            break
    else:
        raise HTTPException(status_code=422, detail="No exercises match these settings")
    rendered = render(task, _registry())
    return {
        "code": task.code,
        "generatorVersion": task.generator_version,
        "statement": rendered.statement,
        "answerInput": task.answer.contract.public(),
    }


@app.post("/check")
def check(body: Check):
    task = _task(body.code)
    try:
        tree = parse_answer_input(body.answer, task.answer.kind, contract=task.answer.contract)
        if not _bounded_preview_tree(tree):
            return {"result": "invalid"}
        return {"result": task.answer.check(tree)}
    except MathInputError:
        return {"result": "invalid"}


def _bounded_preview_tree(root: MathNode) -> bool:
    """Keep local Windows checking small; production uses its isolated Linux worker."""
    stack = [root]
    count = functions = 0
    while stack:
        node = stack.pop()
        count += 1
        if count > 96:
            return False
        if node.kind == "number":
            numerator, denominator = node.value
            if abs(numerator) > 1000000 or not 0 < denominator <= 10000:
                return False
        elif node.kind == "symbol":
            if node.value != "theta":
                return False
        elif node.kind == "function":
            functions += 1
            if (
                functions > 24
                or node.value not in {"sin", "cos"}
                or len(node.children) != 1
                or node.children[0].kind != "symbol"
                or node.children[0].value != "theta"
            ):
                return False
        elif node.kind == "binary":
            if node.value not in {"+", "-", "*", "/", "^"}:
                return False
            if node.value == "^" and (
                node.children[1].kind != "number"
                or node.children[1].value not in {(0, 1), (1, 1), (2, 1)}
            ):
                return False
            if node.value == "/" and (
                node.children[1].kind != "number" or node.children[1].value[0] == 0
            ):
                return False
        elif node.kind not in {"tuple", "unary"}:
            return False
        stack.extend(node.children)
    return True


@app.post("/reveal-answer")
def reveal_answer(body: Code):
    rendered = render(_task(body.code), _registry())
    return {"answerLatex": rendered.answer_latex}


@app.post("/reveal-solution")
def reveal_solution(body: Code):
    task = _task(body.code)
    rendered = render(task, _registry())
    steps = []
    for raw, shown in zip(task.steps, rendered.steps, strict=True):
        item = dict(shown)
        if task.generator_version in {
            DetailedDeterminantGenerator.version,
            ColoredDeterminantGenerator.version,
            ExplainedDeterminantGenerator.version,
        } and raw.text_key in {
            "expand2",
            "sarrus",
            "laplace",
        }:
            match = re.search(r"\\det\\begin\{pmatrix\}(.+?)\\end\{pmatrix\}", raw.latex)
            if match:
                matrix = [
                    [int(value) for value in row.split("&")] for row in match.group(1).split(r"\\")
                ]
                if raw.text_key == "laplace":
                    row_match = re.search(r"\\text\{Row (\d+):\}", raw.latex)
                    if row_match:
                        row = int(row_match.group(1)) - 1
                        item["minorExpansion"] = {
                            "matrix": matrix,
                            "row": row,
                            "columns": [i for i, value in enumerate(matrix[row]) if value != 0],
                        }
                        if task.generator_version == ExplainedDeterminantGenerator.version:
                            item["say"] = (
                                f"Row {row + 1} has the most zeros, so it is used "
                                "for the expansion. "
                                "Each entry is multiplied by its cofactor sign and the determinant "
                                "of its minor."
                            )
                else:
                    item["determinantMatrix"] = matrix
        steps.append(item)
    return {"steps": steps}
