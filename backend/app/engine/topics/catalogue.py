"""Private topic views over the registered v1 generators."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from app.engine.generators.common import Seed
from app.engine.models import Parameters, Task
from app.engine.prng import DeterministicRNG, draw_valid
from app.engine.registry import Registry


def _any(_: Parameters) -> bool:
    return True


def _rational(params: Parameters) -> bool:
    # These v1 generators use the first PRNG draw to select the function family.
    return isinstance(params, Seed) and bool(DeterministicRNG(params.seed).randbelow(2))


def _polynomial(params: Parameters) -> bool:
    return isinstance(params, Seed) and not _rational(params)


@dataclass(frozen=True, slots=True)
class Choice:
    generator: str
    predicate: Callable[[Parameters], bool] = _any
    wrapper: str | None = None


@dataclass(frozen=True, slots=True)
class Topic:
    slug: str
    area: str
    levels: Mapping[int, tuple[Choice, ...]]
    mixed_weight: int

    def __post_init__(self) -> None:
        if not self.slug or not self.area or type(self.mixed_weight) is not int:
            raise ValueError("Topic needs a slug, area and integer mixed weight")
        if self.mixed_weight < 1 or not self.levels:
            raise ValueError("Topic needs positive mixed weight and at least one level")
        if any(
            type(level) is not int or not 1 <= level <= 5 or not choices
            for level, choices in self.levels.items()
        ):
            raise ValueError("Topic levels must be nonempty and numbered 1 through 5")

    def generate(self, level: int, seed: int, generators: Registry) -> Task:
        if type(level) is not int or level not in self.levels:
            raise ValueError("Unknown topic level")
        rng = DeterministicRNG(seed)
        choices = self.levels[level]
        choice = choices[rng.randbelow(len(choices))]
        generator = generators.get(choice.generator)
        wrapper = generators.get(choice.wrapper) if choice.wrapper else None
        if wrapper is not None and generator.version not in wrapper.requires:
            raise ValueError("Wrapper must depend on its generator")

        def draw() -> tuple[int, Parameters]:
            candidate_seed = rng.randbelow(10**16)
            return candidate_seed, generator.draw(candidate_seed)

        candidate_seed, params = draw_valid(draw, lambda item: choice.predicate(item[1]))
        if wrapper is not None:
            return wrapper.build(wrapper.draw(candidate_seed))
        return generator.build(params)


def topics() -> dict[str, Topic]:
    result = (
        Topic("partial-fractions", "algebra", {1: (Choice("partial-fractions-v1"),)}, 1),
        Topic(
            "derivatives",
            "analysis",
            {
                1: (Choice("derivative-v1", _polynomial),),
                2: (Choice("derivative-v1", _rational),),
            },
            1,
        ),
        Topic(
            "indefinite-integrals",
            "analysis",
            {
                1: (Choice("indefinite-v1", _polynomial),),
                2: (Choice("indefinite-v1", _rational),),
            },
            1,
        ),
        Topic(
            "definite-integrals",
            "analysis",
            {
                1: (Choice("indefinite-v1", _polynomial, "definite-v1"),),
                2: (Choice("indefinite-v1", _rational, "definite-v1"),),
            },
            1,
        ),
        Topic("combinations", "combinatorics", {1: (Choice("combinations-v1"),)}, 1),
    )
    return {topic.slug: topic for topic in result}
