"""#100: triple-v1, triple integrals in Cartesian and cylindrical coordinates (ADR-005).

Every template is a fixed solid and integrand. The record only picks the template
and a positive coefficient that scales the integrand, so the value, the solution
and every declared mistake scale with it. Values and mistake values are written
down at coefficient 1 and proven with SymPy whenever a record is verified; the
answer worker replays with `verify=False` and never integrates.
"""

from dataclasses import dataclass
from typing import Any, Literal

import sympy as sp
from pydantic import BaseModel, ConfigDict, Field

from app.content.catalogue import TEXT
from app.generators.definite import is_clean_value, value_latex
from app.generators.multiple import (
    THETA,
    Setup,
    X,
    Y,
    integrate_setup,
    iterated_latex,
    iterated_steps,
)
from app.generators.multiple import R as R_SYMBOL
from app.schemas.feedback import MistakeCode

VERSION = "triple-v1"
TOPIC = "triple-integrals"
Z = sp.Symbol("z", real=True)
R = R_SYMBOL
COEFFICIENTS = (1, 2, 3)
_PI = sp.pi
# Cartesian coordinates of a cylindrical point; the integrands must agree under it.
_TO_CYLINDRICAL = {X: R * sp.cos(THETA), Y: R * sp.sin(THETA)}


@dataclass(frozen=True)
class TripleTemplate:
    difficulty: int
    # KaTeX with `{f}` for the integrand at the record's coefficient.
    statement: str
    # The integrand as the statement shows it, in x, y and z.
    integrand: Any
    # The set-up the solution uses, at coefficient 1.
    setup: Setup
    value: Any
    # The same integral in the other system, shown as a check; None for boxes.
    other: Setup | None = None
    # Wrong set-ups and the value each gives at coefficient 1.
    mistakes: tuple[tuple[MistakeCode, Setup, Any], ...] = ()


def _cartesian(integrand: Any, *bounds: tuple[Any, Any, Any]) -> Setup:
    return Setup("cartesian", sp.sympify(integrand), tuple(bounds))


def _cylindrical(integrand: Any, *bounds: tuple[Any, Any, Any]) -> Setup:
    return Setup("cylindrical", sp.sympify(integrand), tuple(bounds))


def _disk(radius: Any, low: Any, high: Any, integrand: Any = 1) -> Setup:
    """Cartesian bounds of a solid over the disk x^2 + y^2 <= radius^2."""
    half = sp.sqrt(radius**2 - X**2)
    return _cartesian(integrand, (Z, low, high), (Y, -half, half), (X, -radius, radius))


def _missing_r(setup: Setup) -> Setup:
    """The cylindrical integral written without the Jacobian factor r."""
    return Setup("cartesian", setup.integrand, setup.bounds)


_BOX = r"\iiint_E {f}\,dV,\quad E = {box}\quad\text{(Cartesian coordinates)}"
_CYLINDER = r"\iiint_E {f}\,dV,\quad E:\ {solid}\quad\text{(cylindrical coordinates)}"
_SOLID = r"\iiint_E {f}\,dV,\quad E:\ {solid}"
_TURN = (THETA, 0, 2 * _PI)

_CYL_MOMENT = _cylindrical(R**2, (Z, 0, 3), (R, 0, 1), _TURN)
_CYL_HEIGHT = _cylindrical(Z, (Z, 0, 2), (R, 0, 1), _TURN)
_CONE = _cylindrical(1, (Z, R, 2), (R, 0, 2), _TURN)
_PARABOLOID = _cylindrical(1, (Z, 0, 4 - R**2), (R, 0, 2), _TURN)
_QUARTER_EXP = _cylindrical(Z * sp.exp(R**2), (Z, 0, 2), (R, 0, 1), (THETA, 0, _PI / 2))
_HALF_LOG = _cylindrical(2 * Z / (1 + R**2), (Z, 0, 1), (R, 0, 1), (THETA, 0, _PI))
_SIMPLEX = _cartesian(X, (Z, 0, 2 - X - Y), (Y, 0, 2 - X), (X, 0, 2))
_TETRAHEDRON = _cartesian(1, (Z, 0, 2 - 2 * X - Y), (Y, 0, 2 - 2 * X), (X, 0, 1))

TEMPLATES: dict[str, TripleTemplate] = {
    # Level 1: a box and a product of one-variable factors.
    "box_product": TripleTemplate(
        1,
        _BOX.replace("{box}", r"[0,1]\times[0,2]\times[0,1]"),
        X * Y * Z,
        _cartesian(X * Y * Z, (Z, 0, 1), (Y, 0, 2), (X, 0, 1)),
        sp.Rational(1, 2),
    ),
    "box_power": TripleTemplate(
        1,
        _BOX.replace("{box}", r"[0,2]\times[0,1]\times[0,3]"),
        X * Y**2 * Z,
        _cartesian(X * Y**2 * Z, (Z, 0, 3), (Y, 0, 1), (X, 0, 2)),
        sp.Integer(3),
    ),
    # Level 2: a box whose inner results depend on the outer variables.
    "box_sum": TripleTemplate(
        2,
        _BOX.replace("{box}", r"[0,1]\times[0,1]\times[0,2]"),
        X + Y * Z,
        _cartesian(X + Y * Z, (Z, 0, 2), (Y, 0, 1), (X, 0, 1)),
        sp.Integer(2),
    ),
    "box_linear": TripleTemplate(
        2,
        _BOX.replace("{box}", r"[0,2]\times[0,1]\times[0,1]"),
        X + Y + Z,
        _cartesian(X + Y + Z, (Z, 0, 1), (Y, 0, 1), (X, 0, 2)),
        sp.Integer(4),
    ),
    # Level 3: one stated method, a simplex in Cartesian or a cylinder in cylindrical.
    "simplex": TripleTemplate(
        3,
        r"\int_0^2\int_0^{2-x}\int_0^{2-x-y} {f}\,dz\,dy\,dx",
        X,
        _SIMPLEX,
        sp.Rational(2, 3),
        mistakes=(("z_bounds", _cartesian(X, (Z, 0, 2), *_SIMPLEX.bounds[1:]), sp.Rational(8, 3)),),
    ),
    "cylinder_moment": TripleTemplate(
        3,
        _CYLINDER.replace("{solid}", r"x^2 + y^2 \le 1,\ 0 \le z \le 3"),
        X**2 + Y**2,
        _CYL_MOMENT,
        3 * _PI / 2,
        _disk(1, 0, 3, X**2 + Y**2),
        (("missing_jacobian", _missing_r(_CYL_MOMENT), 2 * _PI),),
    ),
    "cylinder_height": TripleTemplate(
        3,
        _CYLINDER.replace("{solid}", r"x^2 + y^2 \le 1,\ 0 \le z \le 2"),
        Z,
        _CYL_HEIGHT,
        2 * _PI,
        _disk(1, 0, 2, Z),
        (("missing_jacobian", _missing_r(_CYL_HEIGHT), 4 * _PI),),
    ),
    # Level 4: bounds from a described solid; the learner chooses the system.
    "cone": TripleTemplate(
        4,
        _SOLID.replace("{solid}", r"\sqrt{x^2 + y^2} \le z \le 2"),
        sp.Integer(1),
        _CONE,
        8 * _PI / 3,
        _disk(2, sp.sqrt(X**2 + Y**2), 2),
        (
            ("missing_jacobian", _missing_r(_CONE), 4 * _PI),
            ("z_bounds", _cylindrical(1, (Z, 0, 2), *_CONE.bounds[1:]), 8 * _PI),
        ),
    ),
    "paraboloid": TripleTemplate(
        4,
        _SOLID.replace("{solid}", r"0 \le z \le 4 - x^2 - y^2"),
        sp.Integer(1),
        _PARABOLOID,
        8 * _PI,
        _disk(2, 0, 4 - X**2 - Y**2),
        (
            ("missing_jacobian", _missing_r(_PARABOLOID), 32 * _PI / 3),
            ("z_bounds", _cylindrical(1, (Z, 0, 4), *_PARABOLOID.bounds[1:]), 16 * _PI),
        ),
    ),
    "tetrahedron": TripleTemplate(
        4,
        _SOLID.replace("{solid}", r"x \ge 0,\ y \ge 0,\ z \ge 0,\ 2x + y + z \le 2"),
        sp.Integer(1),
        _TETRAHEDRON,
        sp.Rational(2, 3),
        mistakes=(("z_bounds", _cartesian(1, (Z, 0, 2), *_TETRAHEDRON.bounds[1:]), sp.Integer(2)),),
    ),
    # Level 5: a Cartesian integral that is only clean in cylindrical, plus u = r^2.
    "quarter_exponential": TripleTemplate(
        5,
        r"\int_0^1\int_0^{\sqrt{1-x^2}}\int_0^2 {f}\,dz\,dy\,dx",
        Z * sp.exp(X**2 + Y**2),
        _QUARTER_EXP,
        _PI * (sp.E - 1) / 2,
        _cartesian(Z * sp.exp(X**2 + Y**2), (Z, 0, 2), (Y, 0, sp.sqrt(1 - X**2)), (X, 0, 1)),
    ),
    "half_logarithm": TripleTemplate(
        5,
        r"\int_{-1}^1\int_0^{\sqrt{1-x^2}}\int_0^1 {f}\,dz\,dy\,dx",
        2 * Z / (1 + X**2 + Y**2),
        _HALF_LOG,
        _PI * sp.log(2) / 2,
        _cartesian(2 * Z / (1 + X**2 + Y**2), (Z, 0, 1), (Y, 0, sp.sqrt(1 - X**2)), (X, -1, 1)),
        (("missing_jacobian", _missing_r(_HALF_LOG), _PI**2 / 4),),
    ),
}


class TripleParameters(BaseModel):
    """Private replay record; the solid belongs to the template, never to the record."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    generator_version: Literal["triple-v1"]
    template: str = Field(max_length=32)
    coefficient: int = Field(ge=1, le=3)


@dataclass(frozen=True)
class TripleProblem:
    parameters: TripleParameters
    template: TripleTemplate
    value: Any
    # (code, wrong value) at this record's coefficient.
    mistakes: tuple[tuple[MistakeCode, Any], ...]

    topic = TOPIC

    @property
    def difficulty(self) -> int:
        return self.template.difficulty

    @property
    def coefficient(self) -> Any:
        return sp.Integer(self.parameters.coefficient)

    @property
    def integrand(self) -> Any:
        return self.coefficient * self.template.integrand

    @property
    def setup(self) -> Setup:
        return _scaled(self.template.setup, self.coefficient)

    @property
    def integrand_latex(self) -> str:
        return _integrand_latex(self.coefficient, self.template.integrand)

    @property
    def statement(self) -> str:
        return self.template.statement.replace("{f}", self.integrand_latex)

    @property
    def answer_latex(self) -> str:
        return value_latex(self.value)

    @property
    def solution_steps(self) -> tuple[dict[str, str], ...]:
        setup = self.setup
        steps = [{"say": TEXT["triple_solid"], "latex": solid_latex(setup)}]
        if setup.system == "cylindrical":
            steps.append(
                {
                    "say": TEXT["triple_cylindrical"],
                    "latex": r"x = r\cos\theta,\ y = r\sin\theta,\ dV = r\,dz\,dr\,d\theta",
                }
            )
        steps.append(
            {
                "say": TEXT["triple_setup"],
                "latex": rf"\iiint_E {self.integrand_latex}\,dV = " + iterated_latex(setup),
            }
        )
        steps.extend(iterated_steps(setup))
        if self.template.other is not None:
            steps.append(
                {
                    "say": TEXT["triple_check"],
                    "latex": iterated_latex(_scaled(self.template.other, self.coefficient))
                    + " = "
                    + value_latex(self.value),
                }
            )
        steps.append({"say": TEXT["triple_value"], "latex": value_latex(self.value)})
        return tuple(steps)


def _scaled(setup: Setup, coefficient: Any) -> Setup:
    return Setup(setup.system, coefficient * setup.integrand, setup.bounds)


def _integrand_latex(coefficient: Any, integrand: Any) -> str:
    """`2\\left(x + y z\\right)` rather than an expanded `2 x + 2 y z`."""
    if not isinstance(integrand, sp.Add):
        return str(sp.latex(coefficient * integrand))
    bracketed = rf"\left({sp.latex(integrand)}\right)"
    return bracketed if coefficient == 1 else f"{coefficient}{bracketed}"


def solid_latex(setup: Setup) -> str:
    """The solid as one inequality per variable, outermost first."""
    return r",\ ".join(
        rf"{sp.latex(low)} \le {sp.latex(variable)} \le {sp.latex(high)}"
        for variable, low, high in reversed(setup.bounds)
    )


def records(difficulty: int) -> list[dict[str, object]]:
    return [
        dict(generator_version=VERSION, template=name, coefficient=a)
        for name, template in TEMPLATES.items()
        if template.difficulty == difficulty
        for a in COEFFICIENTS
    ]


def replay_triple(record: dict[str, object], *, verify: bool = True) -> TripleProblem:
    """Validate the whole record before any symbolic work.

    `verify=False` is only for the answer worker: the catalogue proved the record.
    """
    parameters = TripleParameters.model_validate(record)
    if parameters.template not in TEMPLATES:
        raise ValueError("Unknown triple template")
    template = TEMPLATES[parameters.template]
    a = sp.Integer(parameters.coefficient)
    problem = TripleProblem(
        parameters,
        template,
        a * template.value,
        tuple((code, a * wrong) for code, _, wrong in template.mistakes),
    )
    if verify:
        verify_triple(template)
    return problem


def verify_triple(template: TripleTemplate) -> None:
    """Prove the written-down value and mistake values, and that they are clean.

    The statement's Cartesian integrand must equal the solution's integrand after
    x = r cos θ, y = r sin θ. The other system's set-up is cross-checked in the
    tests, because exact Cartesian integrals over a disk exceed the worker budget.
    """
    setup = template.setup
    expected = (
        template.integrand.subs(_TO_CYLINDRICAL)
        if setup.system == "cylindrical"
        else (template.integrand)
    )
    if sp.simplify(expected - setup.integrand) != 0:
        raise RuntimeError("Solution integrand differs from the statement")
    if [variable for variable, _, _ in setup.bounds][0] != Z:
        raise RuntimeError("The innermost integration must be in z")
    if sp.simplify(integrate_setup(setup) - template.value) != 0:
        raise RuntimeError("Written-down value differs from the integral")
    for coefficient in COEFFICIENTS:
        if not is_clean_value(coefficient * template.value):
            raise RuntimeError("Triple value is not pedagogically clean")
    for _, wrong_setup, wrong in template.mistakes:
        if sp.simplify(integrate_setup(wrong_setup) - wrong) != 0:
            raise RuntimeError("Written-down mistake value differs from its integral")
        if wrong.is_number is not True or wrong.atoms(sp.Float):
            raise RuntimeError("A declared mistake must give an exact number")
        if sp.simplify(wrong - template.value) == 0 or sp.simplify(wrong + template.value) == 0:
            raise RuntimeError("A declared mistake must differ from the value and its negative")
