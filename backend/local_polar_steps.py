"""Detailed local explanations for De Moivre power exercises."""

import sympy as sp

from app.engine.generators.complex_numbers import DeMoivreParams, _base, _cis, _principal


def de_moivre_steps(params: DeMoivreParams) -> list[dict[str, str]]:
    z = _base(params.base)
    a, b = sp.re(z), sp.im(z)
    modulus, angle = sp.Abs(z), sp.arg(z)
    n = params.power
    power, powered_angle = modulus**n, n * angle
    reduced = _principal(powered_angle)
    cosine, sine = sp.cos(reduced), sp.sin(reduced)
    result = sp.expand(power * (cosine + sp.I * sine))
    latex = sp.latex

    def step(say: str, expression: str) -> dict[str, str]:
        return {"say": say, "latex": expression}

    return [
        step("Write the original expression.", rf"\left({latex(z)}\right)^{{{n}}}"),
        step(
            "Identify the real part and the coefficient of i in the algebraic form a + bi.",
            rf"a={latex(a)},\quad b={latex(b)}",
        ),
        step(
            "Find the modulus by squaring and adding the real and imaginary coefficients.",
            rf"r=\sqrt{{a^2+b^2}}=\sqrt{{({latex(a)})^2+({latex(b)})^2}}={latex(modulus)}",
        ),
        step(
            "Divide each coefficient by the modulus to find cosine and sine of the argument.",
            rf"\cos\varphi=\frac{{a}}{{r}}={latex(sp.simplify(a / modulus))},\quad "
            rf"\sin\varphi=\frac{{b}}{{r}}={latex(sp.simplify(b / modulus))}",
        ),
        step(
            "Choose the argument in radians whose cosine and sine match these values and signs.",
            rf"\varphi={latex(angle)}",
        ),
        step(
            "Substitute the modulus and argument into the trigonometric form.",
            rf"z={latex(modulus)}\left({_cis(angle)}\right)",
        ),
        step(
            "De Moivre's formula raises the modulus to the power and multiplies the argument "
            "by the same power.",
            r"\left[r(\cos\varphi+i\sin\varphi)\right]^n="
            r"r^n\left(\cos(n\varphi)+i\sin(n\varphi)\right)",
        ),
        step(
            "Apply the formula before simplifying the modulus or angle.",
            rf"z^{{{n}}}=\left({latex(modulus)}\right)^{{{n}}}"
            rf"\left(\cos\left({n}\cdot\left({latex(angle)}\right)\right)"
            rf"+i\sin\left({n}\cdot\left({latex(angle)}\right)\right)\right)",
        ),
        step(
            "Evaluate the power of the modulus and the product for the angle.",
            rf"r^{{{n}}}={latex(power)},\quad {n}\varphi={latex(powered_angle)}",
        ),
        step(
            "Reduce the angle by whole turns of 2π; sine and cosine are unchanged.",
            rf"{latex(powered_angle)}\equiv {latex(reduced)}\pmod{{2\pi}}",
        ),
        step(
            "Evaluate the cosine and sine of the reduced angle.",
            rf"z^{{{n}}}={latex(power)}\left(({latex(cosine)})+i({latex(sine)})\right)",
        ),
        step(
            "Multiply and write the result in algebraic form a + bi.", rf"z^{{{n}}}={latex(result)}"
        ),
    ]
