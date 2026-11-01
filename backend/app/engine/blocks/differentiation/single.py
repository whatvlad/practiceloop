"""Native single-variable rules and exact domain/step proofs (ADR-005)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from typing import Any, Literal, cast

import sympy as sp
from pydantic import Field, model_validator
from sympy.calculus.util import continuous_domain
from sympy.printing.latex import LatexPrinter
from sympy.printing.precedence import PRECEDENCE

from app.engine.answers._symbolic import X
from app.engine.models import Parameters
from app.engine.prng import DeterministicRNG

type TextKey = str
type MistakeCode = str
_U = sp.Symbol("u", real=True)
_POSITIVE = sp.Interval.open(0, sp.oo)
_NOT_ZERO = sp.Union(sp.Interval.open(-sp.oo, 0), sp.Interval.open(0, sp.oo))
_NOT_MINUS_ONE = sp.Union(sp.Interval.open(-sp.oo, -1), sp.Interval.open(-1, sp.oo))

type Role = Literal["function", "derivative"]


@dataclass(frozen=True)
class DerivativeStep:
    kind: TextKey
    role: Role
    expression: Any
    # Show roots and reciprocals as the powers a rewrite step names.
    powers: bool = False

    @property
    def latex(self) -> str:
        name = "f(x)" if self.role == "function" else "f'(x)"
        return f"{name} = {_StepPrinter(self.powers).doprint(self.expression)}"


class _StepPrinter(LatexPrinter):  # type: ignore[misc]
    """Prime notation for the rule being applied: `(x + 1)'` and `(e^u)'|_(u=2x)`."""

    def __init__(self, powers: bool = False) -> None:
        # A rewrite step shows roots and reciprocals as the powers it names.
        super().__init__({"order": "none", "root_notation": not powers})
        self._powers = powers

    def _print_Pow(self, expr: Any) -> str:
        if self._powers and expr.exp.is_negative:
            return rf"{self._print(expr.base)}^{{{self._print(expr.exp)}}}"
        return str(super()._print_Pow(expr))

    def _print_Mul(self, expr: Any) -> str:
        if not self._powers:
            return str(super()._print_Mul(expr))
        coefficient, factors = expr.as_coeff_mul()
        printed = " ".join(
            self._print(f) if f.is_Derivative else self.parenthesize(f, PRECEDENCE["Mul"])
            for f in factors
        )
        if coefficient == 1:
            return printed
        return ("-" if coefficient == -1 else self._print(coefficient) + " ") + printed

    def _print_Derivative(self, expr: Any) -> str:
        return rf"\left({self._print(expr.expr)}\right)'"

    def _print_Subs(self, expr: Any) -> str:
        (variable,), (point,) = expr.variables, expr.point
        inner = self._print(expr.expr)
        return rf"{inner}\Big|_{{{self._print(variable)} = {self._print(point)}}}"


type Mistakes = tuple[tuple[MistakeCode, Any], ...]


@dataclass(frozen=True)
class DerivativeTemplate:
    difficulty: int
    domain: Any
    # The rules the solution applies, in order; level 5 combines two.
    rules: tuple[str, ...]
    function: Callable[[Any], Any]
    derivative: Callable[[Any], Any]
    steps: Callable[[Any], tuple[DerivativeStep, ...]]
    # The wrong derivatives a learner writes after each common mistake.
    mistakes: Callable[[Any], Mistakes]


def _d(expression: Any, variable: Any = X) -> Any:
    return sp.Derivative(expression, variable)


def _chain(outer: Any, inner: Any) -> Any:
    """f(g(x))' = f'(u)|u=g(x) · g'(x), both factors unevaluated."""
    return sp.Mul(sp.Subs(_d(outer, _U), _U, inner), _d(inner), evaluate=False)


def _step(kind: TextKey, expression: Any) -> DerivativeStep:
    return DerivativeStep(kind, "derivative", expression)


def _rewrite(kind: TextKey, expression: Any, *, powers: bool = False) -> DerivativeStep:
    return DerivativeStep(kind, "function", expression, powers)


_SIN, _COS, _EXP, _LOG = sp.sin(X), sp.cos(X), sp.exp(X), sp.log(X)
_ROOT = sp.sqrt(X**2 + 1)
_HALF = sp.Pow(X, sp.S.Half, evaluate=False)
_RECIPROCAL = sp.Pow(X, -1, evaluate=False)

TEMPLATES: dict[str, DerivativeTemplate] = {
    # Level 1: one standard term.
    "power": DerivativeTemplate(
        1,
        sp.S.Reals,
        ("power_rule",),
        lambda a: a * X**4,
        lambda a: 4 * a * X**3,
        lambda a: (
            _step(
                "derivative_power",
                sp.Mul(4 * a, sp.Pow(X, sp.Add(4, -1, evaluate=False), evaluate=False)),
            ),
        ),
        lambda a: (("derivative_power", 4 * a * X**4), ("derivative_power", a * X**3)),
    ),
    "exponential": DerivativeTemplate(
        1,
        sp.S.Reals,
        ("standard_derivative",),
        lambda a: a * _EXP,
        lambda a: a * _EXP,
        lambda a: (_step("derivative_standard", a * _d(_EXP)),),
        lambda a: (),
    ),
    "sine": DerivativeTemplate(
        1,
        sp.S.Reals,
        ("standard_derivative",),
        lambda a: a * _SIN,
        lambda a: a * _COS,
        lambda a: (_step("derivative_standard", a * _d(_SIN)),),
        lambda a: (("derivative_trig_sign", -a * _COS),),
    ),
    "cosine": DerivativeTemplate(
        1,
        sp.S.Reals,
        ("standard_derivative",),
        lambda a: a * _COS,
        lambda a: -a * _SIN,
        lambda a: (_step("derivative_standard", a * _d(_COS)),),
        lambda a: (("derivative_trig_sign", a * _SIN),),
    ),
    "logarithm": DerivativeTemplate(
        1,
        _POSITIVE,
        ("standard_derivative",),
        lambda a: a * _LOG,
        lambda a: a / X,
        lambda a: (_step("derivative_standard", a * _d(_LOG)),),
        lambda a: (),
    ),
    # Level 2: one preparation before a standard derivative.
    "root_and_reciprocal": DerivativeTemplate(
        2,
        _POSITIVE,
        ("rewrite_as_powers", "power_rule"),
        lambda a: a * (2 * sp.sqrt(X) - 3 / X),
        lambda a: a * (1 / sp.sqrt(X) + 3 / X**2),
        lambda a: (
            _rewrite("derivative_rewrite_power", a * (2 * _HALF - 3 * _RECIPROCAL), powers=True),
            DerivativeStep(
                "derivative_power", "derivative", a * (2 * _d(_HALF) - 3 * _d(_RECIPROCAL)), True
            ),
        ),
        lambda a: (("derivative_power", a * (1 / sp.sqrt(X) - 3 / X**2)),),
    ),
    "linear_sine": DerivativeTemplate(
        2,
        sp.S.Reals,
        ("linear_inner",),
        lambda a: a * sp.sin(3 * X),
        lambda a: 3 * a * sp.cos(3 * X),
        lambda a: (_step("derivative_linear_inner", a * _chain(sp.sin(_U), 3 * X)),),
        lambda a: (
            ("derivative_chain", a * sp.cos(3 * X)),
            ("derivative_trig_sign", -3 * a * sp.cos(3 * X)),
        ),
    ),
    "linear_exponential": DerivativeTemplate(
        2,
        sp.S.Reals,
        ("linear_inner",),
        lambda a: a * sp.exp(2 * X),
        lambda a: 2 * a * sp.exp(2 * X),
        lambda a: (_step("derivative_linear_inner", a * _chain(sp.exp(_U), 2 * X)),),
        lambda a: (("derivative_chain", a * sp.exp(2 * X)),),
    ),
    # Level 3: one rule.
    "chain_exponential": DerivativeTemplate(
        3,
        sp.S.Reals,
        ("chain_rule",),
        lambda a: a * sp.exp(X**2),
        lambda a: 2 * a * X * sp.exp(X**2),
        lambda a: (_step("derivative_chain_rule", a * _chain(sp.exp(_U), X**2)),),
        lambda a: (("derivative_chain", a * sp.exp(X**2)),),
    ),
    "chain_power": DerivativeTemplate(
        3,
        sp.S.Reals,
        ("chain_rule",),
        lambda a: a * (X**2 + 1) ** 3,
        lambda a: 6 * a * X * (X**2 + 1) ** 2,
        lambda a: (_step("derivative_chain_rule", a * _chain(_U**3, X**2 + 1)),),
        lambda a: (("derivative_chain", 3 * a * (X**2 + 1) ** 2),),
    ),
    "product": DerivativeTemplate(
        3,
        sp.S.Reals,
        ("product_rule",),
        lambda a: a * X * _SIN,
        lambda a: a * (_SIN + X * _COS),
        lambda a: (_step("derivative_product_rule", a * (_d(X) * _SIN + X * _d(_SIN))),),
        lambda a: (
            ("derivative_factors", a * _COS),
            ("derivative_trig_sign", a * (_SIN - X * _COS)),
        ),
    ),
    "quotient": DerivativeTemplate(
        3,
        _NOT_MINUS_ONE,
        ("quotient_rule",),
        lambda a: a * X / (X + 1),
        lambda a: a / (X + 1) ** 2,
        lambda a: (
            _step(
                "derivative_quotient_rule",
                a * (_d(X) * (X + 1) - X * _d(X + 1)) / (X + 1) ** 2,
            ),
        ),
        lambda a: (("quotient_sign", -a / (X + 1) ** 2), ("derivative_factors", a)),
    ),
    # Level 4: one rule plus a simplifying rewrite.
    "log_product": DerivativeTemplate(
        4,
        _POSITIVE,
        ("log_laws", "standard_derivative"),
        lambda a: a * sp.log(X**2 * (X + 1)),
        lambda a: a * (2 / X + 1 / (X + 1)),
        lambda a: (
            _rewrite("derivative_log_laws", a * (2 * _LOG + sp.log(X + 1))),
            _step("derivative_terms", a * (2 * _d(_LOG) + _d(sp.log(X + 1)))),
        ),
        lambda a: (("derivative_chain", a / (X**2 * (X + 1))),),
    ),
    "log_quotient": DerivativeTemplate(
        4,
        _POSITIVE,
        ("log_laws", "standard_derivative"),
        lambda a: a * sp.log(X**2 / (X + 1)),
        lambda a: a * (2 / X - 1 / (X + 1)),
        lambda a: (
            _rewrite("derivative_log_laws", a * (2 * _LOG - sp.log(X + 1))),
            _step("derivative_terms", a * (2 * _d(_LOG) - _d(sp.log(X + 1)))),
        ),
        lambda a: (
            ("derivative_chain", a * (X + 1) / X**2),
            ("quotient_sign", a * (2 / X + 1 / (X + 1))),
        ),
    ),
    "root_chain": DerivativeTemplate(
        4,
        sp.S.Reals,
        ("rewrite_as_powers", "chain_rule"),
        lambda a: a * _ROOT,
        lambda a: a * X / _ROOT,
        lambda a: (
            _rewrite(
                "derivative_rewrite_power",
                a * sp.Pow(X**2 + 1, sp.S.Half, evaluate=False),
                powers=True,
            ),
            _step("derivative_chain_rule", a * _chain(sp.sqrt(_U), X**2 + 1)),
        ),
        lambda a: (("derivative_chain", a / (2 * _ROOT)),),
    ),
    "expand_quotient": DerivativeTemplate(
        4,
        _NOT_ZERO,
        ("split_fraction", "power_rule"),
        lambda a: a * (X + 1) ** 2 / X,
        lambda a: a * (1 - 1 / X**2),
        lambda a: (
            _rewrite(
                "split_fraction",
                a * sp.Add(X, 2, sp.Pow(X, -1, evaluate=False), evaluate=False),
            ),
            _step("derivative_terms", a * (_d(X) + _d(1 / X))),
        ),
        lambda a: (
            ("derivative_factors", 2 * a * (X + 1)),
            ("quotient_sign", a * (1 / X**2 - 1)),
        ),
    ),
    # Level 5: two compatible rules.
    "product_chain": DerivativeTemplate(
        5,
        sp.S.Reals,
        ("product_rule", "chain_rule"),
        lambda a: a * X**2 * sp.exp(3 * X),
        lambda a: a * (3 * X**2 + 2 * X) * sp.exp(3 * X),
        lambda a: (
            _step(
                "derivative_product_rule",
                a * (_d(X**2) * sp.exp(3 * X) + X**2 * _d(sp.exp(3 * X))),
            ),
            _step(
                "derivative_chain_rule",
                a * (2 * X * sp.exp(3 * X) + X**2 * _chain(sp.exp(_U), 3 * X)),
            ),
        ),
        lambda a: (
            ("derivative_chain", a * (X**2 + 2 * X) * sp.exp(3 * X)),
            ("derivative_factors", 6 * a * X * sp.exp(3 * X)),
        ),
    ),
    "quotient_chain": DerivativeTemplate(
        5,
        _NOT_ZERO,
        ("quotient_rule", "chain_rule"),
        lambda a: a * sp.sin(X**2) / X,
        lambda a: a * (2 * X**2 * sp.cos(X**2) - sp.sin(X**2)) / X**2,
        lambda a: (
            _step(
                "derivative_quotient_rule",
                a * (_d(sp.sin(X**2)) * X - sp.sin(X**2) * _d(X)) / X**2,
            ),
            _step(
                "derivative_chain_rule",
                a * (_chain(sp.sin(_U), X**2) * X - sp.sin(X**2)) / X**2,
            ),
        ),
        lambda a: (
            ("derivative_chain", a * (X * sp.cos(X**2) - sp.sin(X**2)) / X**2),
            ("quotient_sign", a * (sp.sin(X**2) - 2 * X**2 * sp.cos(X**2)) / X**2),
        ),
    ),
    "product_chain_trig": DerivativeTemplate(
        5,
        sp.S.Reals,
        ("product_rule", "chain_rule"),
        lambda a: a * X * sp.cos(2 * X),
        lambda a: a * (sp.cos(2 * X) - 2 * X * sp.sin(2 * X)),
        lambda a: (
            _step("derivative_product_rule", a * (_d(X) * sp.cos(2 * X) + X * _d(sp.cos(2 * X)))),
            _step("derivative_chain_rule", a * (sp.cos(2 * X) + X * _chain(sp.cos(_U), 2 * X))),
        ),
        lambda a: (
            ("derivative_chain", a * (sp.cos(2 * X) - X * sp.sin(2 * X))),
            ("derivative_trig_sign", a * (sp.cos(2 * X) + 2 * X * sp.sin(2 * X))),
        ),
    ),
}


@dataclass(frozen=True)
class DerivativeData:
    template: DerivativeTemplate
    function: Any
    derivative: Any
    solution_steps: tuple[DerivativeStep, ...]

    @property
    def domain(self) -> Any:
        return self.template.domain


class DerivativeForm(Parameters):
    template: str = Field(min_length=1, max_length=32)
    coefficient: Literal[-3, -2, -1, 1, 2, 3]

    @model_validator(mode="after")
    def known(self) -> DerivativeForm:
        if self.template not in TEMPLATES:
            raise ValueError("Unknown derivative form")
        return self

    @property
    def difficulty(self) -> int:
        return TEMPLATES[self.template].difficulty

    @classmethod
    def draw(cls, rng: DeterministicRNG) -> DerivativeForm:
        level = 1 + rng.randbelow(5)
        names = [name for name, t in TEMPLATES.items() if t.difficulty == level]
        coefficients = (-3, -2, -1, 1, 2, 3)
        return cls(
            template=names[rng.randbelow(len(names))],
            coefficient=cast(Literal[-3, -2, -1, 1, 2, 3], coefficients[rng.randbelow(6)]),
        )

    def evaluate(self) -> DerivativeData:
        return _evaluate(self)


@cache
def _evaluate(form: DerivativeForm) -> DerivativeData:
    template = TEMPLATES[form.template]
    a = sp.Integer(form.coefficient)
    derivative = template.derivative(a)
    data = DerivativeData(
        template,
        template.function(a),
        derivative,
        (*template.steps(a), DerivativeStep("derivative_result", "derivative", derivative)),
    )
    verify_derivative(data)
    return data


def _components(domain: Any) -> tuple[tuple[Any, Any], ...]:
    """(replacement for x, variable) per open interval, with a positive `t`."""
    if domain == sp.S.Reals:
        return ((X, X),)
    t = sp.Symbol("t", positive=True)
    result = []
    for part in domain.args if isinstance(domain, sp.Union) else (domain,):
        if part.start == -sp.oo:
            result.append((part.end - t, t))
        elif part.end == sp.oo:
            result.append((part.start + t, t))
        else:
            result.append((part.start + (part.end - part.start) * t / (1 + t), t))
    return tuple(result)


def _zero(expression: Any) -> bool:
    return bool(sp.simplify(sp.expand_log(sp.simplify(expression), force=False)) == 0)


def verify_derivative(problem: DerivativeData) -> None:
    """Prove the derivative and every displayed step on each component of the domain."""
    last = problem.solution_steps[-1] if problem.solution_steps else None
    if last != DerivativeStep("derivative_result", "derivative", problem.derivative):
        raise RuntimeError("Final step must contain the derivative")
    for expression in (problem.function, problem.derivative):
        defined = continuous_domain(expression, X, sp.S.Reals)
        if problem.domain.is_subset(defined) is not True:
            raise RuntimeError("Function is not defined throughout the domain")
    for replacement, variable in _components(problem.domain):
        function = problem.function.subs(X, replacement)
        derivative = problem.derivative.subs(X, replacement)
        chain = sp.diff(replacement, variable)
        if not _zero(sp.diff(function, variable) / chain - derivative):
            raise RuntimeError("Derivative failed symbolic verification")
        for step in problem.solution_steps:
            value = step.expression.doit().subs(X, replacement)
            target = function if step.role == "function" else derivative
            if not _zero(value - target):
                raise RuntimeError("Solution step failed symbolic verification")
