"""Private topic views over the registered v1 generators."""

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from functools import partial

from app.engine.blocks.integral_forms.form import BOUNDS, METHODS
from app.engine.generators.algebra import AlgebraParams, algebra_generators
from app.engine.generators.algebra_expansion import (
    PolynomialQuotient,
    QuadraticRemainder,
    RemainderTheorem,
)
from app.engine.generators.algebra_expressions import RationalizeDenominator, SimplifyRadicals
from app.engine.generators.analysis import AnalysisParams, analysis_generators
from app.engine.generators.definite import DefiniteParams
from app.engine.generators.derivative import DerivativeParams
from app.engine.generators.differentiation import (
    PartialDerivativeParams,
    PartialDerivatives,
    SingleDerivativeParams,
    SingleDerivatives,
)
from app.engine.generators.indefinite import IndefiniteParams
from app.engine.generators.integrals import IntegralParams, integral_generators
from app.engine.generators.multiple import DoubleIntegrals, MultipleParams, TripleIntegrals
from app.engine.models import Drawn, Task
from app.engine.prng import DeterministicRNG
from app.engine.registry import Registry

logger = logging.getLogger(__name__)

# The public areas of the practice API; engine topics use no others.
AREAS = frozenset({"algebra", "mathematical-analysis"})
MAX_DRAWS = 64


def _any(_: Drawn) -> bool:
    return True


def _rational(params: Drawn) -> bool:
    if isinstance(params, DefiniteParams):
        params = params.integral
    if not isinstance(params, IndefiniteParams | DerivativeParams):
        raise ValueError("These parameters have no function family")
    return params.rational


def _polynomial(params: Drawn) -> bool:
    return not _rational(params)


@dataclass(frozen=True, slots=True)
class Choice:
    generator: str
    predicate: Callable[[Drawn], bool] = _any


@dataclass(frozen=True, slots=True)
class Topic:
    """One declarative entry: the practice API builds its topic list from it (#191)."""

    slug: str
    area: str
    levels: Mapping[int, tuple[Choice, ...]]
    # #36: a fixed, published share of mixed practice in the topic's area.
    mixed_weight: int
    # The learner-facing name, as in the Supabase `topics` row.
    title: str = field(kw_only=True)
    # ADR-007: writing space after a level-1 problem on a printed worksheet, in cm.
    space_cm: float = field(kw_only=True)
    # Issued by the practice API. A symbolic topic waits for the deploy-time catalogue (#192).
    served: bool = field(default=False, kw_only=True)
    # The ADR-006 visual of the worked solution; None when the topic has none.
    visual: str | None = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        if not self.slug or type(self.mixed_weight) is not int:
            raise ValueError("Topic needs a slug and integer mixed weight")
        if not self.title or self.space_cm <= 0:
            raise ValueError("Topic needs a title and positive worksheet space")
        if self.area not in AREAS:
            raise ValueError(f"Unknown topic area: {self.area}")
        if self.mixed_weight < 0 or not self.levels:
            raise ValueError("Topic needs nonnegative mixed weight and at least one level")
        if any(
            type(level) is not int or not 1 <= level <= 5 or not choices
            for level, choices in self.levels.items()
        ):
            raise ValueError("Topic levels must be nonempty and numbered 1 through 5")

    def generate(self, level: int, seed: int, generators: Registry) -> Task:
        """Draw candidates in order until one passes the level filter and builds."""
        if type(level) is not int or level not in self.levels:
            raise ValueError("Unknown topic level")
        rng = DeterministicRNG(seed)
        choices = self.levels[level]
        choice = choices[rng.randbelow(len(choices))]
        generator = generators.get(choice.generator)
        for _ in range(MAX_DRAWS):
            params = generator.draw(rng.randbelow(10**16))
            if not choice.predicate(params):
                continue
            try:
                return generator.build(params)
            except ValueError:
                # Every seed of a shipped version is expected to build; a miss is
                # logged and skipped instead of reaching the learner.
                logger.warning(
                    "%s did not build seed %d; drawing the next candidate",
                    generator.version,
                    params.seed,
                    exc_info=True,
                )
        raise ValueError(f"No valid candidate after {MAX_DRAWS} draws")


def _integral_level(level: int, params: Drawn) -> bool:
    if not isinstance(params, IntegralParams):
        raise ValueError("Expected native integral parameters")
    return params.form.difficulty == level


def _multiple_level(level: int, params: Drawn) -> bool:
    if not isinstance(params, MultipleParams):
        raise ValueError("Expected native multiple-integral parameters")
    return params.form.difficulty == level


def _differentiation_level(level: int, params: Drawn) -> bool:
    if not isinstance(params, SingleDerivativeParams | PartialDerivativeParams):
        raise ValueError("Expected differentiation parameters")
    return params.form.difficulty == level


def topics() -> dict[str, Topic]:
    declared = {
        "indefinite-integrals": Topic(
            "indefinite-integrals",
            "mathematical-analysis",
            {1: (Choice("indefinite-v1", _polynomial),), 2: (Choice("indefinite-v1", _rational),)},
            1,
            title="Indefinite integrals",
            space_cm=3,
        )
    }
    for algebra_generator, (slug, title, space) in zip(
        algebra_generators(),
        (
            ("matrices", "Matrices", 4),
            ("complex-numbers", "Complex numbers", 4),
            ("fundamental-theorem-algebra", "Fundamental theorem of algebra", 5),
            ("partial-fractions", "Partial fractions", 5),
        ),
        strict=True,
    ):
        declared[slug] = Topic(
            slug,
            "algebra",
            {
                level: (Choice(algebra_generator.version, partial(_algebra_level, level)),)
                for level in range(1, 6)
            },
            1,
            title=title,
            space_cm=space,
            served=True,
        )
    declared["algebraic-expressions"] = Topic(
        "algebraic-expressions",
        "algebra",
        {1: (Choice(SimplifyRadicals.version),), 2: (Choice(RationalizeDenominator.version),)},
        0,
        title="Algebraic expressions",
        space_cm=4,
        served=True,
    )
    declared["polynomial-division"] = Topic(
        "polynomial-division",
        "algebra",
        {
            1: (Choice(RemainderTheorem.version),),
            2: (Choice(PolynomialQuotient.version), Choice(QuadraticRemainder.version)),
        },
        0,
        title="Polynomial division",
        space_cm=5,
        served=True,
    )
    declared["combinations"] = Topic(
        "combinations",
        "algebra",
        {1: (Choice("combinations-v1"),)},
        1,
        title="Combinations",
        space_cm=4,
        served=True,
    )
    families = {
        "basic": ("basic-integrals", "Basic integrals", 1, 3),
        "substitution": ("substitution", "Substitution", 2, 4),
        "parts": ("integration-by-parts", "Integration by parts", 2, 5),
        "rational": ("rational-functions", "Rational functions", 2, 5),
        "trigonometric": ("trigonometric-integrals", "Trigonometric integrals", 2, 5),
    }
    generators = integral_generators()
    for family, (slug, title, weight, space) in families.items():
        indefinite = next(g for g in generators if g.form_family == family and not g.bounded)
        definite = next(g for g in generators if g.form_family == family and g.bounded)
        offered = sorted({t.difficulty for t in METHODS[family].TEMPLATES.values()})
        declared[slug] = Topic(
            slug,
            "mathematical-analysis",
            {
                level: (Choice(indefinite.version, partial(_integral_level, level)),)
                + (
                    (Choice(definite.version, partial(_integral_level, level)),)
                    if any(
                        f == family and METHODS[f].TEMPLATES[n].difficulty == level
                        for f, n in BOUNDS
                    )
                    else ()
                )
                for level in offered
            },
            weight,
            title=title,
            space_cm=space,
            served=True,
            visual="single-integral",
        )
    declared["definite-integrals"] = Topic(
        "definite-integrals",
        "mathematical-analysis",
        {
            level: tuple(
                Choice(g.version, partial(_integral_level, level))
                for g in generators
                if g.bounded
                and any(
                    f == g.form_family and METHODS[f].TEMPLATES[n].difficulty == level
                    for f, n in BOUNDS
                )
            )
            for level in range(1, 6)
        },
        0,
        title="Definite integrals",
        space_cm=5,
        served=True,
        visual="single-integral",
    )
    for generator, slug, title, space, visual in (
        (DoubleIntegrals(), "double-integrals", "Double integrals", 6, "region2d"),
        (TripleIntegrals(), "triple-integrals", "Triple integrals", 7, "solid3d"),
    ):
        declared[slug] = Topic(
            slug,
            "mathematical-analysis",
            {
                level: (Choice(generator.version, partial(_multiple_level, level)),)
                for level in range(1, 6)
            },
            2,
            title=title,
            space_cm=space,
            served=True,
            visual=visual,
        )
    for differentiation_generator, slug, title, space in (
        (SingleDerivatives(), "derivatives", "Derivatives", 3),
        (PartialDerivatives(), "partial-derivatives", "Partial derivatives", 4),
    ):
        declared[slug] = Topic(
            slug,
            "mathematical-analysis",
            {
                level: (
                    Choice(
                        differentiation_generator.version, partial(_differentiation_level, level)
                    ),
                )
                for level in range(1, 6)
            },
            1,
            title=title,
            space_cm=space,
            served=True,
        )
    for analysis_generator, (slug, title, space) in zip(
        analysis_generators(),
        (
            ("functions-and-sequences", "Functions and sequences", 4),
            ("limits-and-continuity", "Limits and continuity", 4),
            ("improper-integrals", "Improper integrals", 5),
            ("series", "Series", 4),
            ("multivariable-functions", "Multivariable functions", 5),
            ("differential-equations", "Differential equations", 5),
        ),
        strict=True,
    ):
        declared[slug] = Topic(
            slug,
            "mathematical-analysis",
            {
                level: (Choice(analysis_generator.version, partial(_analysis_level, level)),)
                for level in range(1, 6)
            },
            1,
            title=title,
            space_cm=space,
            served=True,
        )
    return declared


def _algebra_level(level: int, params: Drawn) -> bool:
    if not isinstance(params, AlgebraParams):
        raise ValueError("Expected Algebra parameters")
    return params.difficulty == level


def _analysis_level(level: int, params: Drawn) -> bool:
    if not isinstance(params, AnalysisParams):
        raise ValueError("Expected analysis parameters")
    return params.difficulty == level
