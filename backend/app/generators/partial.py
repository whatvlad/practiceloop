"""#101: partial-v1, partial derivatives and coordinate changes (ADR-005).

A record is `{generator_version, template, coefficient}`. The template fixes the
function or map, the variable it is differentiated in, the variables the answer
may use and their real domains. Replay validates the whole record before any
symbolic construction, then proves the answer from the definition: `sp.diff`
for partials, direct substitution for the chain rule, the determinant for a
Jacobian. Each template also declares the wrong answers its common mistakes
produce, for `generators/mistakes.py`-style diagnosis.
"""

from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from typing import Any, Literal

import sympy as sp
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.content.catalogue import TEXT, TextKey
from app.generators.basic import X
from app.schemas.feedback import MistakeCode

VERSION = "partial-v1"
TOPIC = "partial-derivatives"

# Declared variables and their ADR-005 domains: x, y, z real; r > 0; theta real.
Y, Z = sp.symbols("y z", real=True)
Y_POSITIVE = sp.Symbol("y", positive=True)
R = sp.Symbol("r", positive=True)
THETA = sp.Symbol("theta", real=True)

type Kind = Literal["first", "second", "chain", "jacobian"]


class PartialParameters(BaseModel):
    """Private replay record; everything else belongs to the template."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    generator_version: Literal["partial-v1"]
    template: str = Field(max_length=32)
    coefficient: int = Field(ge=-3, le=3)

    @field_validator("coefficient")
    @classmethod
    def nonzero_coefficient(cls, value: int) -> int:
        if value == 0:
            raise ValueError("Coefficient must be nonzero")
        return value


@dataclass(frozen=True)
class PartialStep:
    kind: TextKey
    latex: str

    @property
    def say(self) -> str:
        return TEXT[self.kind]


@dataclass(frozen=True)
class Built:
    """What a template builder returns for one coefficient."""

    statement: str
    answer: Any
    steps: tuple[PartialStep, ...]
    mistakes: tuple[tuple[MistakeCode, Any], ...]
    # Independent proof of the answer, computed from the definition.
    proof: Any
    # Both orders of a mixed partial, when the template guarantees smoothness.
    mixed: tuple[Any, Any] | None = None


type Builder = Callable[[Any], Built]


@dataclass(frozen=True)
class PartialTemplate:
    difficulty: int
    kind: Kind
    variables: tuple[Any, ...]
    build: Builder
    coefficients: tuple[int, ...] = (-3, -2, -1, 1, 2, 3)


@dataclass(frozen=True)
class PartialProblem:
    parameters: PartialParameters
    template: PartialTemplate
    statement: str
    answer: Any
    solution_steps: tuple[PartialStep, ...]
    mistakes: tuple[tuple[MistakeCode, Any], ...]

    topic = TOPIC

    @property
    def difficulty(self) -> int:
        return self.template.difficulty

    @property
    def variables(self) -> tuple[Any, ...]:
        return self.template.variables

    @property
    def answer_latex(self) -> str:
        return str(sp.latex(self.answer))


def _l(expression: Any) -> str:
    return str(sp.latex(expression))


def _domain(variables: tuple[Any, ...]) -> str:
    """`x, y ∈ ℝ`, `y > 0`, `r > 0, θ ∈ ℝ`: the domains the answer is checked on."""
    real = [_l(v) for v in variables if not v.is_positive]
    positive = [_l(v) + " > 0" for v in variables if v.is_positive]
    parts = positive + ([", ".join(real) + r" \in \mathbb{R}"] if real else [])
    return r"\quad(" + r",\ ".join(parts) + ")"


def _held(variables: tuple[Any, ...], variable: Any) -> str:
    """The variables held constant while differentiating in `variable`."""
    others = ", ".join(_l(v) for v in variables if v != variable)
    return others + r"\ \text{constant}"


def _d(variable: Any) -> str:
    return rf"\frac{{\partial}}{{\partial {_l(variable)}}}"


def _first(function: Any, variable: Any, variables: tuple[Any, ...]) -> tuple[Any, PartialStep]:
    derivative = sp.diff(function, variable)
    if derivative.is_Mul or derivative.is_Add and len(derivative.free_symbols) > 1:
        derivative = sp.factor(derivative)
    step = PartialStep(
        "partial_hold",
        rf"{_held(variables, variable)}:\quad {_d(variable)}\left({_l(function)}\right)"
        rf" = {_l(derivative)}",
    )
    return derivative, step


def _first_template(
    function: Callable[[Any], Any],
    variable: Any,
    variables: tuple[Any, ...],
    mistakes: Callable[[Any], tuple[tuple[MistakeCode, Any], ...]],
) -> Builder:
    def build(a: Any) -> Built:
        f = function(a)
        answer, step = _first(f, variable, variables)
        return Built(
            rf"{_d(variable)}\left({_l(f)}\right){_domain(variables)}",
            answer,
            (step,),
            mistakes(a),
            sp.diff(f, variable),
        )

    return build


def _second_template(
    function: Callable[[Any], Any],
    order: tuple[Any, Any],
    variables: tuple[Any, ...],
    mistakes: Callable[[Any], tuple[tuple[MistakeCode, Any], ...]],
) -> Builder:
    """`order` = (first, second): differentiate in `first`, then in `second`."""

    def build(a: Any) -> Built:
        f = function(a)
        first, second = order
        inner, step_one = _first(f, first, variables)
        outer = sp.diff(inner, second)
        answer = sp.factor(outer)
        steps = [
            step_one,
            PartialStep(
                "partial_second",
                rf"{_held(variables, second)}:\quad {_d(second)}\left({_l(inner)}\right)"
                rf" = {_l(answer)}",
            ),
        ]
        mixed = None
        if first != second:
            other = sp.diff(f, second, first)
            mixed = (outer, other)
            steps.append(
                PartialStep(
                    "partial_mixed_check",
                    rf"\frac{{\partial^2 f}}{{\partial {_l(first)}\,\partial {_l(second)}}}"
                    rf" = {_l(sp.factor(other))}",
                )
            )
            symbol = rf"\frac{{\partial^2}}{{\partial {_l(second)}\,\partial {_l(first)}}}"
        else:
            symbol = rf"\frac{{\partial^2}}{{\partial {_l(first)}^2}}"
        return Built(
            rf"{symbol}\left({_l(f)}\right){_domain(variables)}",
            answer,
            tuple(steps),
            mistakes(a),
            sp.diff(f, first, second),
            mixed,
        )

    return build


_POLAR = ((X, R * sp.cos(THETA)), (Y, R * sp.sin(THETA)))
_CYLINDRICAL = (*_POLAR, (Z, Z))


def _chain_template(
    function: Callable[[Any], Any],
    old: tuple[Any, ...],
    new: tuple[Any, ...],
    variable: Any,
    answer: Callable[[Any], Any],
) -> Builder:
    """Differentiate f(old) in a new coordinate; the answer is in the new variables.

    The dropped-term mistakes are the chain-rule sum without one of its nonzero
    terms, so they are derived from the same terms the solution shows.
    """
    mapping = _CYLINDRICAL if Z in old else _POLAR
    substitution = dict(mapping)

    def build(a: Any) -> Built:
        f = function(a)
        terms = []
        derivatives = []
        for symbol, image in mapping:
            outer = sp.diff(f, symbol)
            inner = sp.diff(image, variable)
            derivatives.append(
                rf"\frac{{\partial f}}{{\partial {_l(symbol)}}} = {_l(outer)},\ "
                rf"\frac{{\partial {_l(symbol)}}}{{\partial {_l(variable)}}} = {_l(inner)}"
            )
            terms.append(outer.subs(substitution) * inner)
        nonzero = [term for term in terms if term != 0]
        total = sp.Add(*terms)
        correct = answer(a)
        names = ", ".join(_l(v) for v in new)
        statement = (
            rf"f = {_l(f)},\quad "
            + r",\ ".join(rf"{_l(s)} = {_l(i)}" for s, i in mapping if s != i)
            + rf":\quad \frac{{\partial f}}{{\partial {_l(variable)}}}"
            rf"\ \text{{in}}\ {names}{_domain(new)}"
        )
        sum_latex = " + ".join(
            rf"\frac{{\partial f}}{{\partial {_l(s)}}}\frac{{\partial {_l(s)}}}"
            rf"{{\partial {_l(variable)}}}"
            for s, _ in mapping
        )
        steps = (
            PartialStep(
                "coordinate_substitute",
                r",\quad ".join(rf"{_l(s)} = {_l(i)}" for s, i in mapping),
            ),
            PartialStep("chain_partials", r";\quad ".join(derivatives)),
            PartialStep(
                "chain_rule_sum",
                rf"\frac{{\partial f}}{{\partial {_l(variable)}}} = {sum_latex} = {_l(total)}",
            ),
            PartialStep("simplify_result", _l(correct)),
        )
        mistakes: tuple[tuple[MistakeCode, Any], ...] = ()
        if len(nonzero) > 1:
            mistakes = tuple(
                ("partial_chain_term", sp.Add(*(t for t in nonzero if t is not dropped)))
                for dropped in nonzero
            )
        return Built(
            statement,
            correct,
            steps,
            mistakes,
            sp.diff(f.subs(substitution, simultaneous=True), variable),
        )

    return build


def _jacobian_template(cylindrical: bool, scales: Callable[[Any], tuple[Any, Any]]) -> Builder:
    def build(a: Any) -> Built:
        p, q = scales(a)
        images = [p * R * sp.cos(THETA), q * R * sp.sin(THETA)]
        new = [R, THETA]
        old = [X, Y]
        if cylindrical:
            images.append(Z)
            new.append(Z)
            old.append(Z)
        matrix = sp.Matrix(images).jacobian(new)
        determinant = sp.simplify(matrix.det())
        answer = p * q * R
        maps = r",\ ".join(rf"{_l(s)} = {_l(i)}" for s, i in zip(old, images, strict=True))
        olds = ", ".join(_l(v) for v in old)
        news = ", ".join(_l(v) for v in new)
        statement = (
            rf"{maps}:\quad \frac{{\partial({olds})}}{{\partial({news})}}"
            rf"{_domain(tuple(new))}"
        )
        expanded = sp.expand(matrix.det())
        steps = (
            PartialStep("jacobian_matrix", _l(matrix)),
            PartialStep("jacobian_determinant", rf"\det = {_l(expanded)} = {_l(answer)}"),
        )
        return Built(
            statement,
            answer,
            steps,
            (
                ("jacobian_missing_r", p * q),
                # cos² + sin² written as cos² − sin²: the determinant's sign error.
                ("jacobian_sign", p * q * R * sp.cos(2 * THETA)),
            ),
            determinant,
        )

    return build


_XY, _XYZ, _XY_POSITIVE = (X, Y), (X, Y, Z), (X, Y_POSITIVE)
_POLAR_NEW, _CYLINDRICAL_NEW = (R, THETA), (R, THETA, Z)
_E_XY = sp.exp(X * Y)
_COS, _SIN = sp.cos(THETA), sp.sin(THETA)

TEMPLATES: dict[str, PartialTemplate] = {
    # Level 1: first partial of a polynomial in x, y.
    "polynomial_x": PartialTemplate(
        1,
        "first",
        _XY,
        _first_template(
            lambda a: a * X**3 * Y + 2 * Y**2,
            X,
            _XY,
            lambda a: (("partial_held_constant", 3 * a * X**2 * Y + 4 * Y),),
        ),
    ),
    "polynomial_y": PartialTemplate(
        1,
        "first",
        _XY,
        _first_template(
            lambda a: a * X**2 * Y**3 + 3 * X,
            Y,
            _XY,
            lambda a: (("partial_held_constant", 3 * a * X**2 * Y**2 + 3),),
        ),
    ),
    # Level 2: one single-variable rule inside the partial.
    "exponential_product": PartialTemplate(
        2,
        "first",
        _XY,
        _first_template(
            lambda a: a * _E_XY,
            Y,
            _XY,
            lambda a: (
                ("derivative_chain", a * _E_XY),
                ("partial_held_constant", a * (X + Y) * _E_XY),
            ),
        ),
    ),
    "logarithm_factor": PartialTemplate(
        2,
        "first",
        _XY_POSITIVE,
        _first_template(
            lambda a: a * X * sp.log(Y_POSITIVE),
            X,
            _XY_POSITIVE,
            lambda a: (("partial_held_constant", a * sp.log(Y_POSITIVE) + a * X / Y_POSITIVE),),
        ),
    ),
    "sine_inner": PartialTemplate(
        2,
        "first",
        _XY,
        _first_template(
            lambda a: a * sp.sin(X * Y**2),
            X,
            _XY,
            lambda a: (
                ("derivative_chain", a * sp.cos(X * Y**2)),
                ("partial_held_constant", a * (Y**2 + 2 * X * Y) * sp.cos(X * Y**2)),
            ),
        ),
    ),
    # Level 3: second and mixed partials, or a first partial of f(x, y, z).
    "mixed_exponential": PartialTemplate(
        3,
        "second",
        _XY,
        _second_template(
            lambda a: a * X**2 * _E_XY,
            (Y, X),
            _XY,
            lambda a: (("derivative_chain", 3 * a * X**2 * _E_XY),),
        ),
    ),
    "second_power": PartialTemplate(
        3,
        "second",
        _XY,
        _second_template(
            lambda a: a * X**3 * Y**2,
            (X, X),
            _XY,
            lambda a: (("partial_held_constant", 6 * a * X**2 * Y),),
        ),
    ),
    "mixed_three": PartialTemplate(
        3,
        "second",
        _XYZ,
        _second_template(
            lambda a: a * X * Y**2 * Z**3,
            (Y, Z),
            _XYZ,
            lambda a: (("partial_held_constant", 6 * a * Y * Z**2 * (X + Y)),),
        ),
    ),
    "three_variables": PartialTemplate(
        3,
        "first",
        _XYZ,
        _first_template(
            lambda a: a * X * Y**2 * Z**3,
            Z,
            _XYZ,
            lambda a: (
                (
                    "partial_held_constant",
                    a * (Y**2 * Z**3 + 2 * X * Y * Z**3 + 3 * X * Y**2 * Z**2),
                ),
            ),
        ),
    ),
    # Level 4: the chain rule after a change to polar or cylindrical coordinates.
    "polar_angle": PartialTemplate(
        4,
        "chain",
        _POLAR_NEW,
        _chain_template(
            lambda a: a * X * Y, _XY, _POLAR_NEW, THETA, lambda a: a * R**2 * sp.cos(2 * THETA)
        ),
    ),
    "polar_radius": PartialTemplate(
        4,
        "chain",
        _POLAR_NEW,
        _chain_template(
            lambda a: a * X**2 * Y, _XY, _POLAR_NEW, R, lambda a: 3 * a * R**2 * _COS**2 * _SIN
        ),
    ),
    "cylindrical_angle": PartialTemplate(
        4,
        "chain",
        _CYLINDRICAL_NEW,
        _chain_template(
            lambda a: a * (X + Y) * Z,
            _XYZ,
            _CYLINDRICAL_NEW,
            THETA,
            lambda a: a * R * Z * (_COS - _SIN),
        ),
    ),
    "cylindrical_radius": PartialTemplate(
        4,
        "chain",
        _CYLINDRICAL_NEW,
        _chain_template(
            lambda a: a * X * Y * Z,
            _XYZ,
            _CYLINDRICAL_NEW,
            R,
            lambda a: a * R * Z * sp.sin(2 * THETA),
        ),
    ),
    # Level 5: the Jacobian determinant of a scaled polar or cylindrical map.
    "scaled_polar": PartialTemplate(
        5,
        "jacobian",
        _POLAR_NEW,
        _jacobian_template(False, lambda a: (a, a + 1)),
        (1, 2, 3),
    ),
    "scaled_cylindrical": PartialTemplate(
        5,
        "jacobian",
        _CYLINDRICAL_NEW,
        _jacobian_template(True, lambda a: (a, a)),
        (1, 2, 3),
    ),
}


def records(difficulty: int) -> list[dict[str, object]]:
    """Every record of one level, in template then coefficient order."""
    return [
        dict(generator_version=VERSION, template=name, coefficient=a)
        for name, template in TEMPLATES.items()
        if template.difficulty == difficulty
        for a in template.coefficients
    ]


def replay_partial(record: dict[str, object], *, verify: bool = True) -> PartialProblem:
    """Validate the entire primitive record before constructing symbolic expressions.

    `verify=False` is only for the answer worker: generation already proved it.
    """
    parameters = PartialParameters.model_validate(record)
    template = TEMPLATES.get(parameters.template)
    if template is None:
        raise ValueError("Unknown partial template")
    if parameters.coefficient not in template.coefficients:
        raise ValueError("Coefficient is outside the template's range")
    built = _build(parameters.template, parameters.coefficient)
    problem = PartialProblem(
        parameters,
        template,
        built.statement,
        built.answer,
        built.steps,
        built.mistakes,
    )
    if verify:
        verify_partial(problem, built)
    return problem


@cache
def _build(name: str, coefficient: int) -> Built:
    return TEMPLATES[name].build(sp.Integer(coefficient))


def verify_partial(problem: PartialProblem, built: Built | None = None) -> None:
    """Prove the answer from the definition and check every declared property."""
    built = built or _build(problem.parameters.template, problem.parameters.coefficient)
    variables = set(problem.variables)
    if not problem.answer.free_symbols <= variables:
        raise RuntimeError("Answer uses an undeclared variable")
    if not problem.answer.free_symbols:
        raise RuntimeError("Answer must be an expression in the declared variables")
    if problem.answer.is_real is not True:
        raise RuntimeError("Answer is not real on the declared domain")
    if sp.simplify(problem.answer - built.proof) != 0:
        raise RuntimeError("Answer failed symbolic verification")
    if built.mixed is not None and sp.simplify(built.mixed[0] - built.mixed[1]) != 0:
        raise RuntimeError("Mixed partials differ although the template is smooth")
    if not problem.solution_steps or problem.answer_latex not in problem.solution_steps[-1].latex:
        raise RuntimeError("Final step must contain the answer")
    for _code, wrong in problem.mistakes:
        if not wrong.free_symbols <= variables:
            raise RuntimeError("Declared mistake uses an undeclared variable")
        if sp.simplify(wrong - problem.answer) == 0:
            raise RuntimeError("Declared mistake equals the answer")
