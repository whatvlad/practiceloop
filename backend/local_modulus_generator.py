"""Local complex modulus exercises with exact solutions."""

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.answers.expression import ExpressionAnswer
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG

VARIATIONS = 10**12


class ModulusParameters(Drawn):
    level: int
    real: int
    imaginary: int


class LocalModulusGenerator:
    version, prefix, family, code_version = "local-modulus-v1", "LMOD", "local-modulus", 1
    params, answer, requires = ModulusParameters, ExpressionAnswer, ()
    step_text = {
        "rewrite": "Write the original expression.",
        "identify": "Identify the real part a and imaginary coefficient b in z = a + bi.",
        "formula": "The modulus of a + bi is the square root of a squared plus b squared.",
        "substitute": "Substitute the real and imaginary coefficients, including their signs.",
        "squares": "Square both coefficients and add the results.",
        "result": "Simplify the nonnegative square root.",
    }

    def draw(self, seed: int) -> ModulusParameters:
        level = seed // VARIATIONS + 1
        if level not in (1, 2, 3):
            raise ValueError("Invalid modulus seed")
        rng = DeterministicRNG(seed)
        bound = (3, 7, 12)[level - 1]
        return ModulusParameters(
            seed=seed,
            level=level,
            real=rng.randbelow(2 * bound + 1) - bound,
            imaginary=rng.randbelow(2 * bound + 1) - bound,
        )

    def build(self, params: ModulusParameters) -> Task:
        a, b = params.real, params.imaginary
        value = sp.sqrt(a * a + b * b)
        z = a + b * sp.I
        expression = rf"\left|{sp.latex(z)}\right|"
        return Task(
            statement=rf"Calculate \({expression}\).",
            steps=(
                Step("rewrite", expression),
                Step("identify", rf"a={a},\quad b={b}"),
                Step("formula", r"|a+bi|=\sqrt{a^2+b^2}"),
                Step("substitute", rf"\sqrt{{({a})^2+({b})^2}}"),
                Step("squares", rf"\sqrt{{{a * a}+{b * b}}}=\sqrt{{{a * a + b * b}}}"),
                Step("result", sp.latex(value)),
            ),
            answer=ExpressionAnswer(value, {}),
            metadata={"difficulty": params.level, "template": "modulus"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class ModulusPracticeParameters(Drawn):
    level: int
    mode: str
    a: int
    b: int
    c: int
    d: int


class LocalModulusPractice:
    version, prefix, family, code_version = (
        "local-modulus-practice-v1",
        "LMEX",
        "local-modulus-practice",
        1,
    )
    params, answer, requires = ModulusPracticeParameters, ExpressionAnswer, ()
    step_text = {
        "rewrite": "Write the original expression.",
        "simplify": "Simplify the expression inside the modulus and collect like parts.",
        "arithmetic": "Perform the indicated operation on the real and imaginary parts.",
        "conjugate": "Multiply the numerator and denominator by the conjugate of the denominator.",
        "identify": "Identify the real part and the coefficient of i.",
        "formula": "The modulus is the square root of the sum of the squared components.",
        "substitute": "Substitute the real and imaginary coefficients and simplify.",
        "property": "Apply the modulus properties to the product, quotient or power.",
        "components": "Calculate the modulus of each complex number.",
        "evaluate": "Substitute the moduli and simplify the resulting real expression.",
        "result": "Write the exact nonnegative result.",
    }

    def draw(self, seed: int) -> ModulusPracticeParameters:
        index = seed // VARIATIONS
        if not 0 <= index < 6:
            raise ValueError("Invalid modulus exercise seed")
        level, mode = index % 3 + 1, ("expression", "properties")[index // 3]
        rng = DeterministicRNG(seed)
        pool = (-4, -3, -2, -1, 1, 2, 3, 4)
        a, b, c, d = (pool[rng.randbelow(len(pool))] for _ in range(4))
        return ModulusPracticeParameters(seed=seed, level=level, mode=mode, a=a, b=b, c=c, d=d)

    @staticmethod
    def value(p: ModulusPracticeParameters):
        z, w = p.a + p.b * sp.I, p.c + p.d * sp.I
        if p.mode == "expression":
            return (z + w, z * w, z / w)[p.level - 1]
        return (z * w, z**2 * w, z**3 / w)[p.level - 1]

    def build(self, p: ModulusPracticeParameters) -> Task:
        z, w = p.a + p.b * sp.I, p.c + p.d * sp.I
        zt, wt = sp.latex(z), sp.latex(w)
        expressions = (
            (rf"({zt})+({wt})", rf"({zt})({wt})", rf"\frac{{{zt}}}{{{wt}}}")
            if p.mode == "expression"
            else (rf"({zt})({wt})", rf"({zt})^2({wt})", rf"\frac{{({zt})^3}}{{{wt}}}")
        )
        expression = rf"\left|{expressions[p.level - 1]}\right|"
        value = sp.expand_complex(self.value(p))
        a, b = sp.simplify(sp.re(value)), sp.simplify(sp.im(value))
        result = sp.simplify(sp.sqrt(a**2 + b**2))
        steps = [Step("rewrite", expression)]
        if p.mode == "expression":
            if p.level == 1:
                arithmetic = rf"({p.a})+({p.c})+\left(({p.b})+({p.d})\right)i"
            elif p.level == 2:
                arithmetic = (
                    rf"({p.a})({p.c})-({p.b})({p.d})"
                    rf"+\left(({p.a})({p.d})+({p.b})({p.c})\right)i"
                )
            else:
                conjugate = sp.latex(sp.conjugate(w))
                steps.append(
                    Step("conjugate", rf"\frac{{({zt})({conjugate})}}{{({wt})({conjugate})}}")
                )
                arithmetic = (
                    rf"\frac{{({p.a})({p.c})+({p.b})({p.d})"
                    rf"+\left(({p.b})({p.c})-({p.a})({p.d})\right)i}}"
                    rf"{{({p.c})^2+({p.d})^2}}"
                )
            steps.append(Step("arithmetic", arithmetic))
            steps.extend(
                (
                    Step("simplify", rf"{expression}=\left|{sp.latex(value)}\right|"),
                    Step("identify", rf"a={sp.latex(a)},\quad b={sp.latex(b)}"),
                    Step("formula", r"|a+bi|=\sqrt{a^2+b^2}"),
                    Step(
                        "substitute",
                        rf"\sqrt{{({sp.latex(a)})^2+({sp.latex(b)})^2}}={sp.latex(result)}",
                    ),
                )
            )
        else:
            mz, mw = sp.sqrt(p.a**2 + p.b**2), sp.sqrt(p.c**2 + p.d**2)
            symbolic = (r"|z||w|", r"|z|^2|w|", r"\frac{|z|^3}{|w|}")[p.level - 1]
            mt, nt = sp.latex(mz), sp.latex(mw)
            numeric = (rf"({mt})({nt})", rf"({mt})^2({nt})", rf"\frac{{({mt})^3}}{{{nt}}}")[
                p.level - 1
            ]
            steps.extend(
                (
                    Step("property", rf"z={zt},\quad w={wt},\quad {expression}={symbolic}"),
                    Step(
                        "components",
                        rf"|z|=\sqrt{{({p.a})^2+({p.b})^2}}={mt},\quad "
                        rf"|w|=\sqrt{{({p.c})^2+({p.d})^2}}={nt}",
                    ),
                    Step("evaluate", rf"{symbolic}={numeric}={sp.latex(result)}"),
                )
            )
        steps.append(Step("result", sp.latex(result)))
        return Task(
            statement=rf"Calculate \({expression}\).",
            steps=tuple(steps),
            answer=ExpressionAnswer(result, {}),
            metadata={"difficulty": p.level, "template": p.mode},
            code=encode(self.prefix, self.code_version, p.seed),
            generator_version=self.version,
        )


class CircleParameters(Drawn):
    level: int
    a: int
    b: int
    c: int
    d: int
    scale: int

    @property
    def center_x(self):
        return sp.Rational(self.a, self.scale)

    @property
    def center_y(self):
        return sp.Rational(self.b, self.scale)

    @property
    def radius(self):
        return sp.sqrt(self.c**2 + self.d**2) / self.scale


class LocalModulusCircle:
    version, prefix, family, code_version = (
        "local-modulus-circle-v1",
        "LMC",
        "local-modulus-circle",
        1,
    )
    params, answer, requires = CircleParameters, OrderedAnswer, ()
    step_text = {
        "rewrite": "Write the original expression.",
        "right": "Evaluate the modulus on the right-hand side.",
        "factor": "Factor out the positive coefficient and divide both sides by it.",
        "distance": "The modulus is the distance between z and the indicated complex number.",
        "coordinates": "Read the centre and the radius from the distance equation.",
        "result": "Write the centre coordinates and radius.",
    }

    def input_contract(self, params: CircleParameters):
        return self.build(params).answer.contract

    def draw(self, seed: int) -> CircleParameters:
        level = seed // VARIATIONS + 1
        if level not in (1, 2, 3):
            raise ValueError("Invalid circle seed")
        rng = DeterministicRNG(seed)
        a, b = (rng.randbelow(9) - 4 for _ in range(2))
        c, d = ((1 + rng.randbelow(4)), (0 if level == 1 else 1 + rng.randbelow(4)))
        return CircleParameters(
            seed=seed,
            level=level,
            a=a,
            b=b,
            c=c,
            d=d,
            scale=1 if level < 3 else 2 + rng.randbelow(2),
        )

    def build(self, p: CircleParameters) -> Task:
        z0 = p.center_x + p.center_y * sp.I
        original_center = p.a + p.b * sp.I
        right = sp.Integer(p.c) if p.level == 1 else p.c + p.d * sp.I
        lhs = rf"{p.scale}z" if p.scale > 1 else "z"
        rhs = sp.latex(right) if p.level == 1 else rf"\left|{sp.latex(right)}\right|"
        expression = rf"\left|{lhs}-\left({sp.latex(original_center)}\right)\right|={rhs}"
        radius = p.radius
        steps = [
            Step("rewrite", expression),
            Step("right", rf"\left|{sp.latex(right)}\right|={sp.latex(sp.Abs(right))}"),
            Step("factor", rf"\left|z-\left({sp.latex(z0)}\right)\right|={sp.latex(radius)}"),
            Step("distance", r"|z-z_0|=r"),
            Step("coordinates", rf"z_0={sp.latex(z0)},\quad r={sp.latex(radius)}"),
            Step(
                "result",
                rf"\begin{{gathered}}(x_0,y_0)=({sp.latex(p.center_x)},{sp.latex(p.center_y)})"
                rf"\\r={sp.latex(radius)}\end{{gathered}}",
            ),
        ]
        return Task(
            statement=rf"Find the centre coordinates and radius of the locus: \({expression}\).",
            steps=tuple(steps),
            answer=OrderedAnswer(
                tuple(FormulaAnswer(v) for v in (p.center_x, p.center_y, radius)),
                ("Centre x", "Centre y", "Radius"),
            ),
            metadata={"difficulty": p.level, "template": "geometry"},
            code=encode(self.prefix, self.code_version, p.seed),
            generator_version=self.version,
        )
