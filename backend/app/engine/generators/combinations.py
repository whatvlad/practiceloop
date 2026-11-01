"""Combination counts using integer arithmetic."""

from math import comb

from app.engine.answers.number import NumberAnswer
from app.engine.generators.common import Seed, code
from app.engine.models import Step, Task
from app.engine.prng import DeterministicRNG


class Combinations:
    version = "combinations-v1"
    params = Seed
    answer = NumberAnswer
    requires: tuple[str, ...] = ()

    def draw(self, seed: int) -> Seed:
        return Seed(seed=seed)

    def build(self, params: Seed) -> Task:
        rng = DeterministicRNG(params.seed)
        n = 2 + rng.randbelow(19)
        k = rng.randbelow(n + 1)
        value = comb(n, k)
        return Task(
            statement=rf"Calculate \(\binom{{{n}}}{{{k}}}\).",
            steps=(Step("combinations", rf"\binom{{{n}}}{{{k}}} = {value}"),),
            answer=NumberAnswer(value),
            metadata={"n": n, "k": k},
            code=code(self, "CMB", "combinations", params.seed),
            generator_version=self.version,
        )
