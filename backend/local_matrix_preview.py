"""Isolated local demo. Run bound to 127.0.0.1; never mount in production."""

import re
import secrets
from fractions import Fraction
from functools import cache
from typing import Literal

import sympy as sp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.api.practice import MatrixOptions
from app.engine.algebra_practice.local_complex_generator import LocalComplexGenerator, complex_seed
from app.engine.algebra_practice.local_conversion_generator import (
    DIRECTIONS,
    LocalConversionGenerator,
    LocalConversionToPolarGenerator,
)
from app.engine.algebra_practice.local_determinant_generator import (
    ColoredDeterminantGenerator,
    DetailedDeterminantGenerator,
    ExplainedDeterminantGenerator,
    LocalDeterminantGenerator,
    determinant_seed,
)
from app.engine.algebra_practice.local_inverse_generator import LocalInverseGenerator, inverse_seed
from app.engine.algebra_practice.local_matrix_generator import (
    VARIATIONS,
    LeveledMatrixDivisionGenerator,
    LocalMatrixDivisionGenerator,
    LocalMatrixGenerator,
    make_seed,
)
from app.engine.algebra_practice.local_polynomial_extras import (
    KINDS,
    PartialFractionsExtras,
    PolynomialExtras,
)
from app.engine.algebra_practice.local_polynomial_generator import (
    MODES,
    LocalPolynomialGenerator,
    LocalPolynomialScalarGenerator,
)
from app.engine.algebra_practice.local_polynomial_generator import (
    RULES as POLYNOMIAL_RULES,
)
from app.engine.algebra_practice.local_polynomial_roots_generator import (
    RULES as POLYNOMIAL_ROOT_RULES,
)
from app.engine.algebra_practice.local_polynomial_roots_generator import (
    LocalPolynomialRootsGenerator,
)
from app.engine.algebra_practice.local_system_generator import LocalSystemGenerator, system_seed
from app.engine.algebra_practice.rank import LocalRankGenerator, rank_seed
from app.engine.algebra_practice.selection import modulus_selection
from app.engine.codes import parse_code
from app.engine.generators.catalogue import registry
from app.engine.generators.complex_numbers import ComplexArgument, ComplexRoot, DeMoivre
from app.engine.practice import matrix_classification, matrix_options_supported
from app.engine.rendering import render
from app.engine.topics.catalogue import topics
from app.math_input.parser import MathInputError, MathNode
from app.math_input.structured import parse_answer_input
from local_complex_visual import complex_visual
from local_modulus_generator import LocalModulusCircle, LocalModulusGenerator, LocalModulusPractice
from local_polar_steps import de_moivre_steps
from local_solution_rules import ARGUMENT, DEMOIVRE, MODULUS, POLAR, complex_rules

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Generate(Request):
    level: int = Field(ge=1, le=3)
    matrixOptions: MatrixOptions | None = None
    dimensions: "MatrixDimensions | None" = None
    determinantSize: int | None = Field(default=None, ge=2, le=5)
    inverseSize: int | None = Field(default=None, ge=2, le=5)
    rankDimensions: "RankDimensions | None" = None
    systemSize: int | None = Field(default=None, ge=2, le=5)
    complexOperation: Literal["add", "subtract", "multiply", "divide"] | None = None
    complexModulus: Literal[True] | None = None
    modulusMode: Literal["expression", "properties", "geometry"] | None = None
    polynomialMode: Literal["division", "remainder", "divisibility"] | None = None
    polynomialRoots: Literal[True] | None = None
    polynomialExtra: Literal["add", "subtract", "multiply", "fundamental", "fractions"] | None = (
        None
    )
    polarMode: Literal["argument", "power", "root"] | None = None
    conversion: (
        Literal["alg-trig", "alg-exp", "trig-alg", "exp-alg", "trig-exp", "exp-trig"] | None
    ) = None


class MatrixDimensions(Request):
    operation: Literal["add", "subtract", "multiply", "divide"]
    rowsA: int = Field(ge=1, le=5)
    colsA: int = Field(ge=1, le=5)
    rowsB: int = Field(ge=1, le=5)
    colsB: int = Field(ge=1, le=5)


class RankDimensions(Request):
    rows: int = Field(ge=2, le=5)
    columns: int = Field(ge=2, le=5)


class Code(Request):
    code: str = Field(min_length=1, max_length=64)


class Check(Code):
    answer: str = Field(max_length=256)


@cache
def _registry():
    result = registry()
    result.register(LocalModulusGenerator())
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
            LocalRankGenerator.version,
            LocalSystemGenerator.version,
            LocalComplexGenerator.version,
            LocalModulusGenerator.version,
            LocalModulusPractice.version,
            LocalModulusCircle.version,
            LocalConversionGenerator.version,
            LocalConversionToPolarGenerator.version,
            LocalPolynomialGenerator.version,
            LocalPolynomialScalarGenerator.version,
            LocalPolynomialRootsGenerator.version,
            PolynomialExtras.version,
            PartialFractionsExtras.version,
            ComplexArgument.version,
            DeMoivre.version,
            ComplexRoot.version,
        } and generator.version not in {choice.generator for group in choices for choice in group}:
            raise ValueError("Not a current matrix exercise")
        return generator.build(generator.draw(parsed.seed))
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=404, detail="Unknown preview problem") from exc


@app.post("/generate")
def generate(body: Generate):
    if body.modulusMode is not None and body.complexModulus is None:
        raise HTTPException(status_code=422, detail="Choose the modulus exercise type")
    if body.polynomialExtra is not None:
        if any(
            value is not None
            for value in (
                body.polynomialRoots,
                body.polynomialMode,
                body.conversion,
                body.polarMode,
                body.complexModulus,
                body.complexOperation,
                body.systemSize,
                body.rankDimensions,
                body.inverseSize,
                body.determinantSize,
                body.dimensions,
                body.matrixOptions,
            )
        ):
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        generator = _registry().get(
            PartialFractionsExtras.version
            if body.polynomialExtra == "fractions"
            else PolynomialExtras.version
        )
        seed = ((body.level - 1) * len(KINDS) + KINDS.index(body.polynomialExtra)) * VARIATIONS
        task = generator.build(generator.draw(seed + secrets.randbelow(VARIATIONS)))
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": render(task, _registry()).statement,
            **(
                {"answerInput": task.answer.contract.public()}
                if task.answer.kind == "tuple"
                else {}
            ),
        }
    if body.polynomialRoots is not None:
        if any(
            value is not None
            for value in (
                body.polynomialMode,
                body.conversion,
                body.polarMode,
                body.complexModulus,
                body.complexOperation,
                body.systemSize,
                body.rankDimensions,
                body.inverseSize,
                body.determinantSize,
                body.dimensions,
                body.matrixOptions,
            )
        ):
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        generator = _registry().get(LocalPolynomialRootsGenerator.version)
        seed = (body.level - 1) * VARIATIONS + secrets.randbelow(VARIATIONS)
        task = generator.build(generator.draw(seed))
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": render(task, _registry()).statement,
            "answerInput": {"kind": "finite_set", "maxBytes": 256, "maxItems": 8},
        }
    if body.polynomialMode is not None:
        if any(
            value is not None
            for value in (
                body.conversion,
                body.polarMode,
                body.complexModulus,
                body.complexOperation,
                body.systemSize,
                body.rankDimensions,
                body.inverseSize,
                body.determinantSize,
                body.dimensions,
                body.matrixOptions,
            )
        ):
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        generator = _registry().get(
            LocalPolynomialGenerator.version
            if body.polynomialMode == "division"
            else LocalPolynomialScalarGenerator.version
        )
        seed = ((body.level - 1) * len(MODES) + MODES.index(body.polynomialMode)) * VARIATIONS
        task = generator.build(generator.draw(seed + secrets.randbelow(VARIATIONS)))
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": render(task, _registry()).statement,
            **(
                {"answerInput": task.answer.contract.public()}
                if task.answer.kind == "tuple"
                else {}
            ),
        }
    if body.conversion is not None:
        if any(
            value is not None
            for value in (
                body.polarMode,
                body.complexModulus,
                body.complexOperation,
                body.systemSize,
                body.rankDimensions,
                body.inverseSize,
                body.determinantSize,
                body.dimensions,
                body.matrixOptions,
            )
        ):
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        generator = _registry().get(
            LocalConversionGenerator.version
            if body.conversion.endswith("-alg")
            else LocalConversionToPolarGenerator.version
        )
        seed = ((body.level - 1) * len(DIRECTIONS) + DIRECTIONS.index(body.conversion)) * VARIATIONS
        task = generator.build(generator.draw(seed + secrets.randbelow(VARIATIONS)))
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": render(task, _registry()).statement,
            **(
                {"answerInput": task.answer.contract.public()}
                if task.answer.kind == "tuple"
                else {}
            ),
        }
    if body.polarMode is not None:
        if any(
            value is not None
            for value in (
                body.complexModulus,
                body.complexOperation,
                body.systemSize,
                body.rankDimensions,
                body.inverseSize,
                body.determinantSize,
                body.dimensions,
                body.matrixOptions,
            )
        ):
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        versions = {
            "argument": ComplexArgument.version,
            "power": DeMoivre.version,
            "root": ComplexRoot.version,
        }
        generator = _registry().get(versions[body.polarMode])
        task = generator.build(generator.draw(secrets.randbelow(10**16)))
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": render(task, _registry()).statement,
        }
    if body.complexModulus is not None:
        if any(
            value is not None
            for value in (
                body.complexOperation,
                body.systemSize,
                body.rankDimensions,
                body.inverseSize,
                body.determinantSize,
                body.dimensions,
                body.matrixOptions,
            )
        ):
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        mode = body.modulusMode
        if mode is None:
            version = LocalModulusGenerator.version
            seed = (body.level - 1) * VARIATIONS + secrets.randbelow(VARIATIONS)
        else:
            version, seed = modulus_selection(body.level, mode, secrets.randbelow(VARIATIONS))
        generator = _registry().get(version)
        task = generator.build(generator.draw(seed))
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": render(task, _registry()).statement,
            **({"answerInput": task.answer.contract.public()} if mode == "geometry" else {}),
        }
    if body.complexOperation is not None:
        if any(
            value is not None
            for value in (
                body.systemSize,
                body.rankDimensions,
                body.inverseSize,
                body.determinantSize,
                body.dimensions,
                body.matrixOptions,
            )
        ):
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        generator = _registry().get(LocalComplexGenerator.version)
        seed = complex_seed(body.level, body.complexOperation, secrets.randbelow(VARIATIONS))
        task = generator.build(generator.draw(seed))
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": render(task, _registry()).statement,
        }
    if body.systemSize is not None:
        if any(
            value is not None
            for value in (
                body.rankDimensions,
                body.inverseSize,
                body.determinantSize,
                body.dimensions,
                body.matrixOptions,
            )
        ):
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        generator = _registry().get(LocalSystemGenerator.version)
        seed = system_seed(body.level, body.systemSize, secrets.randbelow(VARIATIONS))
        task = generator.build(generator.draw(seed))
        rendered = render(task, _registry())
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": rendered.statement,
            "answerInput": task.answer.contract.public(),
        }
    if body.rankDimensions is not None:
        if (
            body.matrixOptions is not None
            or body.dimensions is not None
            or body.determinantSize is not None
            or body.inverseSize is not None
        ):
            raise HTTPException(status_code=422, detail="Choose one exercise type")
        dims = body.rankDimensions
        generator = _registry().get(LocalRankGenerator.version)
        seed = rank_seed(body.level, dims.rows, dims.columns, secrets.randbelow(VARIATIONS))
        task = generator.build(generator.draw(seed))
        rendered = render(task, _registry())
        return {
            "code": task.code,
            "generatorVersion": task.generator_version,
            "statement": rendered.statement,
            "answerInput": task.answer.contract.public(),
        }
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
        if body.matrixOptions is not None and task.generator_version.startswith("local-matrix-"):
            continue
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
        tree = parse_answer_input(
            body.answer,
            task.answer.kind,
            {"i"} if task.answer.kind == "complex" else None,
            contract=getattr(task.answer, "contract", None),
        )
        if not _bounded_preview_tree(tree):
            return {"result": "invalid"}
        return {"result": task.answer.check(tree)}
    except MathInputError:
        return {"result": "invalid"}


def _numeric_denominator(node: MathNode) -> Fraction | None:
    """Evaluate small rational-only denominators without symbolic evaluation."""

    def calculate(part: MathNode, depth: int) -> Fraction:
        if depth > 12:
            raise ValueError("Denominator is too deep")
        if part.kind == "number":
            value = Fraction(*part.value)
        elif part.kind == "unary" and part.value in {"+", "-"}:
            value = calculate(part.children[0], depth + 1)
            if part.value == "-":
                value = -value
        elif part.kind == "binary" and part.value in {"+", "-", "*", "/"}:
            a, b = (calculate(child, depth + 1) for child in part.children)
            if part.value == "+":
                value = a + b
            elif part.value == "-":
                value = a - b
            elif part.value == "*":
                value = a * b
            else:
                value = a / b
        else:
            raise ValueError("Not a rational expression")
        if abs(value.numerator) > 10_000_000 or value.denominator > 10_000:
            raise ValueError("Denominator outside the preview bound")
        return value

    try:
        return calculate(node, 0)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def _bounded_radical_denominator(node: MathNode) -> bool:
    """Prove nonzero for a small numeric expression with at most two rational radicals."""
    count = radicals = 0

    def calculate(part: MathNode, depth: int):
        nonlocal count, radicals
        count += 1
        if count > 12 or depth > 8:
            raise ValueError("Expression is too complex")
        if part.kind == "number":
            a, b = part.value
            if abs(a) > 10_000_000 or not 0 < b <= 10_000:
                raise ValueError("Number outside the preview bound")
            return sp.Rational(a, b)
        if part.kind == "unary" and part.value in {"+", "-"}:
            value = calculate(part.children[0], depth + 1)
            return -value if part.value == "-" else value
        if part.kind == "function" and part.value == "sqrt" and len(part.children) == 1:
            radicals += 1
            radicand = _numeric_denominator(part.children[0])
            if radicals > 2 or radicand is None or radicand < 0:
                raise ValueError("Unsupported radical")
            return sp.sqrt(sp.Rational(radicand.numerator, radicand.denominator))
        if part.kind == "binary" and part.value in {"+", "-", "*"}:
            a, b = (calculate(child, depth + 1) for child in part.children)
            return a + b if part.value == "+" else a - b if part.value == "-" else a * b
        raise ValueError("Unsupported denominator")

    try:
        value = calculate(node, 0)
        return value.is_finite is True and value.is_real is True and value.is_zero is False
    except (ValueError, ZeroDivisionError, OverflowError):
        return False


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
            if abs(numerator) > 10000000 or not 0 < denominator <= 10000:
                return False
        elif node.kind == "symbol":
            if node.value not in {"theta", "i", "pi", "x"}:
                return False
        elif node.kind == "function":
            functions += 1
            if node.value == "sqrt" and functions <= 24 and len(node.children) == 1:
                stack.extend(node.children)
                continue
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
                or node.children[1].value not in {(i, 1) for i in range(9)}
            ):
                return False
            if node.value == "/":
                divisor = node.children[1]
                denominator = _numeric_denominator(divisor)
                if denominator is None and divisor.kind == "function" and divisor.value == "sqrt":
                    radicand = _numeric_denominator(divisor.children[0])
                    if radicand is not None and radicand > 0:
                        denominator = Fraction(1)
                if denominator == 0:
                    return False
                if denominator is None and not _bounded_radical_denominator(divisor):
                    return False
        elif node.kind not in {"tuple", "finite_set", "unary"}:
            return False
        stack.extend(node.children)
    return True


@app.post("/reveal-answer")
def reveal_answer(body: Code):
    task = _task(body.code)
    if task.generator_version == LocalConversionToPolarGenerator.version:
        return {"answerLatex": task.steps[-1].latex}
    rendered = render(task, _registry())
    return {"answerLatex": rendered.answer_latex}


@app.post("/reveal-solution")
def reveal_solution(body: Code):
    task = _task(body.code)
    rendered = render(task, _registry())
    parsed = parse_code(body.code, _registry())
    generator = _registry().get_code(parsed.prefix, parsed.version)
    params = generator.draw(parsed.seed)
    visual = complex_visual(generator, params, task)
    if task.generator_version == DeMoivre.version:
        power_steps = de_moivre_steps(params)
        for index, rule in ((2, MODULUS), (3, ARGUMENT), (5, POLAR), (7, DEMOIVRE)):
            power_steps[index]["rules"] = [rule]
        return {"steps": power_steps, "visual": visual}
    steps = []
    if task.generator_version in {ComplexArgument.version, ComplexRoot.version}:
        match = re.search(r"\\\((.*?)\\\)", task.statement)
        if match:
            steps.append({"say": "Write the original expression.", "latex": match.group(1)})
    for raw, shown in zip(task.steps, rendered.steps, strict=True):
        item = dict(shown)
        if task.generator_version == PolynomialExtras.version and raw.text_key == "theorem":
            item["rules"] = [
                {
                    "title": "Fundamental theorem of algebra",
                    "latex": r"P(z)=a\prod_{j=1}^{k}(z-z_j)^{m_j},\quad\sum_{j=1}^{k}m_j=\deg P",
                    "explanation": (
                        "A complex polynomial splits into linear factors, counting multiplicities."
                    ),
                }
            ]
        if task.generator_version == PartialFractionsExtras.version and raw.text_key == "form":
            rule = (
                r"\frac{N(x)}{(x-a)(x^2+c)}=\frac{A}{x-a}+\frac{Bx+C}{x^2+c},\quad c>0"
                if params.level == 3
                else r"\frac{N(x)}{(x-a)^2(x-b)}=\frac{A}{x-a}+\frac{B}{(x-a)^2}+\frac{C}{x-b}"
                if params.level > 1
                else r"\frac{N(x)}{(x-a)(x-b)}=\frac{A}{x-a}+\frac{B}{x-b}"
            )
            item["rules"] = [
                {
                    "title": "Partial fraction decomposition",
                    "latex": rule,
                    "explanation": (
                        "Include every required factor power; use a linear numerator "
                        "for an irreducible quadratic."
                    ),
                }
            ]
        if task.generator_version == LocalPolynomialRootsGenerator.version:
            root_rules = POLYNOMIAL_ROOT_RULES.get(raw.text_key)
            if root_rules:
                item["rules"] = list(root_rules)
        used_complex_rules = complex_rules(task.generator_version, raw.text_key)
        if used_complex_rules:
            item["rules"] = used_complex_rules
        if task.generator_version in {
            LocalPolynomialGenerator.version,
            LocalPolynomialScalarGenerator.version,
        }:
            rules = POLYNOMIAL_RULES.get(raw.text_key)
            if rules:
                item["rules"] = list(rules)
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
    return {"steps": steps, **({"visual": visual} if visual else {})}
