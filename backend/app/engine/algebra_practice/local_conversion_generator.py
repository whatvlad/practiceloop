"""Local conversions between algebraic, trigonometric and exponential forms."""

from typing import Any

import sympy as sp

from app.engine.answers.complex import ComplexAnswer
from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.codes import encode
from app.engine.generators.complex_numbers import NICE, _cis, _principal, _rectangular
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG
from app.math_input import VariableDomain
from app.math_input.contracts import InputContract

VARIATIONS = 10**12
DIRECTIONS = ("alg-trig", "alg-exp", "trig-alg", "exp-alg", "trig-exp", "exp-trig")


class ConversionParameters(Drawn):
    level: int
    direction: str
    angle: int
    modulus: int


class LocalConversionGenerator:
    version, prefix, family, code_version = "local-conversion-v1", "LCV", "local-conversion", 1
    params, requires = ConversionParameters, ()
    answer: Any = ComplexAnswer

    def input_variables(self, params: ConversionParameters) -> dict[str, VariableDomain]:
        return {"i": "imaginary"}

    step_text = {
        "rewrite": "Write the original expression.",
        "parts": "Identify the real part a and the coefficient b of i.",
        "modulus": "Calculate the modulus from the real and imaginary parts.",
        "trig_values": (
            "Divide the real and imaginary parts by the modulus to obtain cosine and sine."
        ),
        "angle": (
            "Choose the principal argument in radians using both signs to identify the quadrant."
        ),
        "given": "Identify the modulus and argument from the given form.",
        "euler": "Euler's formula relates exponential and trigonometric forms.",
        "evaluate": "Evaluate the cosine and sine, then multiply each by the modulus.",
        "result": "Write the same number in the requested form.",
    }

    def draw(self, seed: int) -> ConversionParameters:
        index = seed // VARIATIONS
        if not 0 <= index < 18:
            raise ValueError("Invalid conversion seed")
        level, direction = index // 6 + 1, DIRECTIONS[index % 6]
        rng = DeterministicRNG(seed)
        candidates = [
            i for i, angle in enumerate(NICE) if level != 1 or (angle / (sp.pi / 4)).is_integer
        ]
        return ConversionParameters(
            seed=seed,
            level=level,
            direction=direction,
            angle=candidates[rng.randbelow(len(candidates))],
            modulus=1 + rng.randbelow((2, 3, 5)[level - 1]),
        )

    def build(self, params: ConversionParameters) -> Task:
        source, target = params.direction.split("-")
        r = sp.Integer(params.modulus)
        phi = _principal(NICE[params.angle])
        z = _rectangular(r, phi)
        a, b = sp.re(z), sp.im(z)
        latex = sp.latex
        forms = {
            "alg": latex(z),
            "trig": rf"{latex(r)}\left({_cis(phi)}\right)",
            "exp": rf"{latex(r)}e^{{i\left({latex(phi)}\right)}}",
        }
        names = {"alg": "algebraic", "trig": "trigonometric", "exp": "exponential"}
        expression = rf"z={forms[source]}"
        steps = [Step("rewrite", expression)]
        if source == "alg":
            steps.extend(
                (
                    Step("parts", rf"a={latex(a)},\quad b={latex(b)}"),
                    Step("modulus", rf"r=\sqrt{{({latex(a)})^2+({latex(b)})^2}}={latex(r)}"),
                    Step(
                        "trig_values",
                        rf"\cos\varphi={latex(sp.simplify(a / r))},\quad "
                        rf"\sin\varphi={latex(sp.simplify(b / r))}",
                    ),
                    Step("angle", rf"\varphi={latex(phi)}"),
                )
            )
        else:
            steps.append(Step("given", rf"r={latex(r)},\quad\varphi={latex(phi)}"))
        if "exp" in (source, target):
            steps.append(Step("euler", r"e^{i\varphi}=\cos\varphi+i\sin\varphi"))
        if target == "alg":
            steps.append(
                Step(
                    "evaluate",
                    rf"z={latex(r)}\left(({latex(sp.cos(phi))})"
                    rf"+i({latex(sp.sin(phi))})\right)",
                )
            )
        steps.append(Step("result", rf"z={forms[target]}"))
        answer = (
            ComplexAnswer(z)
            if target == "alg"
            else OrderedAnswer(
                (FormulaAnswer(r), FormulaAnswer(phi)), ("Modulus r", "Principal argument")
            )
        )
        instruction = f"Convert to {names[target]} form" + (
            " using the principal argument in radians" if target != "alg" else ""
        )
        return Task(
            statement=rf"{instruction}: \({expression}\).",
            steps=tuple(steps),
            answer=answer,
            metadata={"difficulty": params.level, "template": params.direction},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class LocalConversionToPolarGenerator(LocalConversionGenerator):
    version, prefix, family = "local-conversion-polar-v1", "LCP", "local-conversion-polar"
    answer = OrderedAnswer

    def input_contract(self, params: ConversionParameters) -> InputContract:
        return OrderedAnswer(
            (FormulaAnswer(params.modulus), FormulaAnswer(_principal(NICE[params.angle]))),
            ("Modulus r", "Principal argument"),
        ).contract
