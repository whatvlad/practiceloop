"""Topic-specific formulas for local complex-number solutions."""

MODULUS = {
    "title": "Modulus of a complex number",
    "latex": r"|a+bi|=\sqrt{a^2+b^2}",
    "explanation": "The modulus is the distance from the origin in the complex plane.",
}
ARGUMENT = {
    "title": "Argument from algebraic form",
    "latex": r"\cos\varphi=\frac{a}{r},\quad\sin\varphi=\frac{b}{r},\quad r>0",
    "explanation": "Both signs determine the quadrant; the argument is undefined at zero.",
}
POLAR = {
    "title": "Trigonometric form",
    "latex": r"z=r(\cos\varphi+i\sin\varphi),\quad r=|z|",
    "explanation": "The modulus is the distance from the origin; the argument is the angle.",
}
EULER = {
    "title": "Euler's formula",
    "latex": r"e^{i\varphi}=\cos\varphi+i\sin\varphi",
    "explanation": "Euler's formula connects exponential and trigonometric representations.",
}
DEMOIVRE = {
    "title": "De Moivre's formula",
    "latex": r"[r(\cos\varphi+i\sin\varphi)]^n=r^n[\cos(n\varphi)+i\sin(n\varphi)]",
    "explanation": "Raise the modulus to n and multiply the argument by n, for integer n.",
}
ROOTS = {
    "title": "Roots of a nonzero complex number",
    "latex": (
        r"z_k=\sqrt[n]{r}\left(\cos\frac{\varphi+2k\pi}{n}"
        r"+i\sin\frac{\varphi+2k\pi}{n}\right),\quad k=0,\ldots,n-1"
    ),
    "explanation": "The n roots share a modulus and their arguments are spaced by 2π/n.",
}
QUOTIENT = {
    "title": "Division by a complex number",
    "latex": r"\frac{z}{w}=\frac{z\overline{w}}{|w|^2},\quad w\ne 0",
    "explanation": "Multiplying by the conjugate makes the denominator real and nonzero.",
}
MODULUS_PROPERTIES = {
    "title": "Properties of the modulus",
    "latex": r"|zw|=|z||w|,\quad |z/w|=|z|/|w|\ (w\ne0),\quad |z^n|=|z|^n",
    "explanation": "Evaluate products, quotients and powers using the moduli of their factors.",
}
MODULUS_DISTANCE = {
    "title": "Modulus as distance",
    "latex": r"|z-z_0|=r,\quad r>0",
    "explanation": "The points at distance r from z0 form a circle with centre z0 and radius r.",
}


def complex_rules(version: str, key: str) -> list[dict[str, str]]:
    by_version = {
        "local-complex-v1": {"conjugate": QUOTIENT},
        "local-modulus-v1": {"formula": MODULUS, "substitute": MODULUS},
        "local-modulus-practice-v1": {
            "formula": MODULUS,
            "property": MODULUS_PROPERTIES,
            "components": MODULUS,
            "conjugate": QUOTIENT,
        },
        "local-modulus-circle-v1": {"distance": MODULUS_DISTANCE},
        "local-conversion-v1": {"modulus": MODULUS, "trig_values": ARGUMENT, "euler": EULER},
        "local-conversion-polar-v1": {
            "modulus": MODULUS,
            "trig_values": ARGUMENT,
            "euler": EULER,
        },
        "complex-argument-v1": {"modulus": MODULUS, "trig": ARGUMENT},
        "complex-root-v1": {"polar": POLAR, "formula": ROOTS},
    }
    rule = by_version.get(version, {}).get(key)
    return [rule] if rule else []
