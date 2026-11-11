"""Self-review exercises whose reference work is revealed through normal practice."""

from dataclasses import dataclass
from typing import Any, ClassVar

from app.engine.codes import encode
from app.engine.generators._limit_visuals import plot
from app.engine.generators.analysis_limits import LimitParams
from app.engine.models import Outcome, Step, Task
from app.engine.prng import DeterministicRNG
from app.math_input import MathNode


@dataclass(frozen=True, slots=True)
class ReferenceAnswer:
    conclusion: str
    kind: ClassVar[str] = "self_review"

    def latex(self) -> str:
        return self.conclusion

    def check(self, tree: MathNode) -> Outcome:
        return "inconclusive"


@dataclass(frozen=True, slots=True)
class SelfReview:
    prefix: str
    template: str
    difficulty: int
    params = LimitParams
    answer = ReferenceAnswer
    topic = "functions-and-sequences"
    code_version = 1
    requires: tuple[str, ...] = ()
    step_text: ClassVar[dict[str, str]] = {
        "definition": "Start from the definition.",
        "difference": "Compare the two function values.",
        "graph": "Transform the key points and join the corresponding segments.",
    }

    @property
    def family(self) -> str:
        return f"analysis1-review-{self.template}"

    @property
    def version(self) -> str:
        return f"{self.family}-v1"

    def draw(self, seed: int) -> LimitParams:
        rng = DeterministicRNG(seed)
        return LimitParams(
            seed=seed, a=2 + rng.randbelow(4), b=2 + rng.randbelow(4), c=2 + rng.randbelow(4)
        )

    def build(self, p: LimitParams) -> Task:
        steps: tuple[Step, ...]
        if self.template == "increasing-affine":
            statement = (
                rf"\text{{Prove from the definition that }} f(x)={p.a}x-{p.b}"
                r"\text{ is strictly increasing on }\mathbb R."
            )
            steps = (
                Step("definition", r"x_1<x_2\ \Longrightarrow\ x_2-x_1>0."),
                Step("difference", rf"f(x_2)-f(x_1)={p.a}(x_2-x_1)>0."),
            )
            conclusion = r"\text{Strictly increasing on }\mathbb R."
        elif self.template == "decreasing-quadratic":
            statement = (
                rf"\text{{Prove from the definition that }} f(x)={p.a}(x-{p.b})^2+{p.c}"
                rf"\text{{ is strictly decreasing on }}(-\infty,{p.b}]."
            )
            steps = (
                Step(
                    "definition",
                    rf"x_1<x_2\le {p.b}\ \Longrightarrow\ x_2-x_1>0,\quad x_1+x_2-2\cdot {p.b}<0.",
                ),
                Step("difference", rf"f(x_2)-f(x_1)={p.a}(x_2-x_1)(x_1+x_2-2\cdot {p.b})<0."),
            )
            conclusion = rf"\text{{Strictly decreasing on }}(-\infty,{p.b}]."
        elif self.template == "injective-cubic":
            statement = (
                rf"\text{{Prove that }}f(x)={p.a}x^3+{p.b}x-{p.c}"
                r"\text{ is injective on }\mathbb R."
            )
            steps = (
                Step("definition", r"\text{Assume } f(u)=f(v)\text{ and show }u=v."),
                Step(
                    "difference",
                    rf"0=(u-v)\big[{p.a}(u^2+uv+v^2)+{p.b}\big]."
                    r"\quad u^2+uv+v^2=(u+v/2)^2+3v^2/4\ge0.",
                ),
            )
            conclusion = r"\text{The bracket is positive, so }u=v."
        elif self.template == "injective-reciprocal":
            statement = (
                rf"\text{{Prove that }}f(x)={p.a}/(x-{p.b})+{p.c}"
                rf"\text{{ is injective on }}({p.b},\infty)."
            )
            steps = (
                Step("definition", rf"u,v>{p.b},\quad f(u)=f(v)."),
                Step(
                    "difference",
                    rf"0=\frac{{{p.a}(v-u)}}{{(u-{p.b})(v-{p.b})}}"
                    r"\quad\Longrightarrow\quad u=v.",
                ),
            )
            conclusion = r"\text{Equal function values force equal inputs.}"
        else:
            expression, rule, _ = self._transform(p)
            statement = rf"\text{{Sketch }}y={expression}\text{{ from the given graph of }}f."
            steps = (Step("graph", rule),)
            conclusion = rf"\text{{Reference graph of }}y={expression}."
        return Task(
            rf"\({statement}\)",
            steps,
            ReferenceAnswer(conclusion),
            {"difficulty": self.difficulty},
            encode(self.prefix, self.code_version, p.seed),
            self.version,
        )

    def _transform(self, p: LimitParams) -> tuple[str, str, list[tuple[float, float]]]:
        # The original function has a constant left ray and two linear pieces.
        points: list[tuple[float, float]] = [
            (-p.a - 2, p.b),
            (-p.a, p.b),
            (0, -p.c),
            (p.a, p.b),
            (p.a + 2, p.b + 2 * (p.b + p.c) / p.a),
        ]
        match self.template:
            case "vertical-shift":
                return (
                    rf"f(x)+{p.c}",
                    rf"(x,y)\mapsto(x,y+{p.c}).",
                    [(x, y + p.c) for x, y in points],
                )
            case "horizontal-shift":
                return (
                    rf"f(x+{p.a})",
                    rf"(x,y)\mapsto(x-{p.a},y).",
                    [(x - p.a, y) for x, y in points],
                )
            case "reflect-horizontal":
                return "-f(x)", r"(x,y)\mapsto(x,-y).", [(x, -y) for x, y in points]
            case "reflect-vertical":
                return "f(-x)", r"(x,y)\mapsto(-x,y).", [(-x, y) for x, y in reversed(points)]
            case "vertical-scale":
                return (
                    rf"f(x)/{p.b}",
                    rf"(x,y)\mapsto(x,y/{p.b}).",
                    [(x, y / p.b) for x, y in points],
                )
            case "horizontal-scale":
                return (
                    rf"f({p.a}x)",
                    rf"(x,y)\mapsto(x/{p.a},y).",
                    [(x / p.a, y) for x, y in points],
                )
            case "absolute-output":
                roots: list[tuple[float, float]] = [
                    (-p.a * p.c / (p.b + p.c), 0),
                    (p.a * p.c / (p.b + p.c), 0),
                ]
                return (
                    r"|f(x)|",
                    r"(x,y)\mapsto(x,|y|)\text{, splitting each segment at its zero.}",
                    sorted([(x, abs(y)) for x, y in points] + roots),
                )
            case "absolute-input":
                right = points[2:]
                return (
                    "f(|x|)",
                    r"\text{Keep the right half and reflect it across the vertical axis.}",
                    [(-x, y) for x, y in reversed(right[1:])] + right,
                )
            case _:
                raise ValueError("Unknown graph transformation")

    @staticmethod
    def _diagram(title: str, points: list[tuple[float, float]], description: str) -> dict[str, Any]:
        return plot(
            title,
            description,
            [
                {
                    "label": "Left ray",
                    "points": [list(xy) for xy in reversed(points[:2])],
                    "arrow": True,
                },
                {"label": "Middle segments", "points": [list(xy) for xy in points[1:-1]]},
                {"label": "Right ray", "points": [list(xy) for xy in points[-2:]], "arrow": True},
            ],
        )

    def prompt_visual(self, p: LimitParams) -> dict[str, Any] | None:
        if self.template in PROOFS:
            return None
        return self._diagram(
            "Given graph",
            [
                (-p.a - 2, p.b),
                (-p.a, p.b),
                (0, -p.c),
                (p.a, p.b),
                (p.a + 2, p.b + 2 * (p.b + p.c) / p.a),
            ],
            f"Knots at ({-p.a},{p.b}), (0,{-p.c}) and ({p.a},{p.b}). The rays continue as shown.",
        )

    def solution_visual(self, p: LimitParams) -> dict[str, Any] | None:
        if self.template in PROOFS:
            return None
        _, _, points = self._transform(p)
        return self._diagram(
            "Reference sketch", points, "The corresponding transformed segments and rays."
        )


PROOFS = ("increasing-affine", "decreasing-quadratic", "injective-cubic", "injective-reciprocal")


def generators() -> tuple[SelfReview, ...]:
    return tuple(
        SelfReview(prefix, template, level)
        for prefix, template, level in (
            ("RVA", PROOFS[0], 1),
            ("RVB", PROOFS[1], 2),
            ("RVC", "vertical-shift", 1),
            ("RVD", "horizontal-shift", 1),
            ("RVE", "reflect-horizontal", 1),
            ("RVF", "reflect-vertical", 1),
            ("RVG", "vertical-scale", 2),
            ("RVH", "horizontal-scale", 2),
            ("RVI", "absolute-output", 3),
            ("RVJ", "absolute-input", 3),
            ("RVK", "injective-cubic", 2),
            ("RVL", "injective-reciprocal", 2),
        )
    )
