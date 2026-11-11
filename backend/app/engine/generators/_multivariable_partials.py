"""First partial derivatives and Euler identities from AM2A/6.1 through 6.3."""

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._sequence_limits import finish
from app.math_input.contracts import Domain

XY: tuple[tuple[str, Domain], ...] = (("x", "positive"), ("y", "positive"))
XYZ: tuple[tuple[str, Domain], ...] = (*XY, ("z", "positive"))
X, Y, Z = sp.symbols("x y z", positive=True)
PARTIALS = ("Partial in x", "Partial in y")
TRIPLE_PARTIALS = (*PARTIALS, "Partial in z")
EULER = (*PARTIALS, "Constant multiplier")


def at_point(expression: str, y: int, proof: str) -> Built:
    answer = OrderedAnswer((FormulaAnswer(0), FormulaAnswer(0)), PARTIALS)
    return finish(
        rf"\text{{Use the definition to compute both first "
        rf"partial derivatives of }}f(x,y)={expression}"
        rf"\text{{ at }}(0,{y}).",
        answer,
        proof,
        rf"(f_x(0,{y}),f_y(0,{y}))=(0,0).",
    )


def quotient_at_point(a: int, b: int, c: int) -> Built:
    return at_point(
        tex(a * X**2 / (c * Y)),
        b,
        rf"\frac{{f(h,{b})-f(0,{b})}}{{h}}=\frac{{{a}h}}{{{b * c}}}\to0,"
        rf"\qquad\frac{{f(0,{b}+h)-f(0,{b})}}{{h}}=0.",
    )


def radical_at_origin(a: int, b: int, c: int) -> Built:
    return at_point(
        tex(sp.sqrt(a * X**6 + (b + c) * Y**4)),
        0,
        rf"\frac{{f(h,0)-f(0,0)}}{{h}}=\frac{{\sqrt{{{a}}}|h|^3}}{{h}}\to0,"
        rf"\qquad\frac{{f(0,h)-f(0,0)}}{{h}}=\sqrt{{{b + c}}}h\to0.",
    )


def derivatives(
    expression: sp.Expr,
    rule: str,
    *,
    three_variables: bool = False,
    euler: sp.Expr | None = None,
    logarithmic: bool = False,
    values: tuple[sp.Expr, ...] | None = None,
) -> Built:
    variables = (X, Y, Z) if three_variables else (X, Y)
    symbols = XYZ if three_variables else XY
    names = ",".join(map(str, variables))
    domain = r">0,\ ".join(map(str, variables)) + ">0"
    if values is None:
        values = tuple(sp.diff(expression, variable) for variable in variables)
    parts = tuple(FormulaAnswer(value, symbols) for value in values)
    labels = TRIPLE_PARTIALS if three_variables else PARTIALS
    prompt = (
        rf"\text{{Find all first partial derivatives of }}f({names})={tex(expression)},"
        rf"\quad {domain}."
    )
    result = r",\quad ".join(
        rf"f_{{{variable}}}={tex(value)}" for variable, value in zip(variables, values, strict=True)
    )
    if euler is not None:
        labels = EULER
        parts = (*parts, FormulaAnswer(euler))
        equation = r"x f_x+y f_y=K" if logarithmic else r"x f_x+y f_y=K f"
        prompt += rf"\quad\text{{Also give the constant }}K\text{{ such that }}{equation}."
        result += rf".\quad {equation.replace('K', tex(euler))}."
    return finish(prompt, OrderedAnswer(parts, labels), rule, result)


def rational_partials(a: int, b: int, c: int) -> Built:
    return derivatives(
        (a * X**2 - b * Y**3) / (c * X * Y**2),
        r"\text{Separate the terms as powers of }x,y\text{ and hold the other variable fixed.}",
    )


def arctangent_quotient_partials(a: int, b: int, c: int) -> Built:
    denominator = (X + c * Y) ** 2 + (a - b * X * Y) ** 2
    return derivatives(
        sp.atan((a - b * X * Y) / (X + c * Y)),
        r"\text{Differentiate the quotient }u\text{ first and apply }(\arctan u)'=u'/(1+u^2).",
        values=(-(a + b * c * Y**2) / denominator, -(a * c + b * X**2) / denominator),
    )


def exponential_cosine_partials(a: int, b: int, c: int) -> Built:
    return derivatives(
        sp.exp(a * sp.cos(b * X / (c * Y))),
        r"\text{Apply the chain rule in order to the exponential, cosine and coordinate quotient.}",
    )


def radial_product_partials(a: int, b: int, c: int) -> Built:
    return derivatives(
        a * Y * sp.sqrt(b * X**2 + c * Y**2),
        r"\text{Apply the chain rule to the root. The }y"
        r"\text{ derivative also uses the product rule.}",
    )


def logarithmic_radial_partials(a: int, b: int, c: int) -> Built:
    return derivatives(
        a * sp.log(sp.sqrt(b**2 * X**2 + c * Y**2) - b * X),
        rf"\text{{The radial root exceeds }}{b}x\text{{ on the stated domain.}}"
        r"\text{ Divide each argument derivative by the argument.}",
    )


def three_variable_polynomial_quotient(a: int, b: int, c: int) -> Built:
    return derivatives(
        a * Z**2 + b * X * Z / Y + c * Y * Z**3,
        r"\text{In each derivative treat the other two coordinates as constants.}",
        three_variables=True,
    )


def three_variable_radial_quotient(a: int, b: int, c: int) -> Built:
    return derivatives(
        a * X / (b * Y**2 + c * Z**2),
        r"\text{The denominator is independent of }x\text{. Use the reciprocal rule for }y,z.",
        three_variables=True,
    )


def nested_partial(expression: sp.Expr, coordinate: sp.Symbol, rule: str) -> Built:
    value = sp.diff(expression, coordinate)
    return finish(
        rf"\text{{Find }}f_{{{coordinate}}}\text{{ for }}f(x,y,z)={tex(expression)},"
        r"\quad x,y,z>0.",
        FormulaAnswer(value, XYZ),
        rule,
        rf"f_{{{coordinate}}}={tex(value)}.",
    )


def nested_trigonometric(a: int, b: int, c: int, coordinate: sp.Symbol) -> Built:
    return nested_partial(
        sp.cos(a * X * sp.sin(b * Y * sp.cos(c * Z))),
        coordinate,
        r"\text{Differentiate from the outer cosine "
        r"inward until reaching the selected coordinate.}",
    )


def nested_radical(a: int, b: int, c: int, coordinate: sp.Symbol) -> Built:
    return nested_partial(
        sp.sqrt(a * X**2 + sp.sqrt(b * Y**2 + sp.sqrt(c * Z**2 + 1))),
        coordinate,
        r"\text{Each root on the path to the selected "
        r"coordinate contributes a factor }1/(2\sqrt{u}).",
    )


def nested_trigonometric_x(a: int, b: int, c: int) -> Built:
    return nested_trigonometric(a, b, c, X)


def nested_trigonometric_y(a: int, b: int, c: int) -> Built:
    return nested_trigonometric(a, b, c, Y)


def nested_trigonometric_z(a: int, b: int, c: int) -> Built:
    return nested_trigonometric(a, b, c, Z)


def nested_radical_x(a: int, b: int, c: int) -> Built:
    return nested_radical(a, b, c, X)


def nested_radical_y(a: int, b: int, c: int) -> Built:
    return nested_radical(a, b, c, Y)


def nested_radical_z(a: int, b: int, c: int) -> Built:
    return nested_radical(a, b, c, Z)


def logarithmic_euler_partials(a: int, b: int, c: int) -> Built:
    return derivatives(
        sp.log(a * X**2 + b * X * Y + c * Y**2),
        r"\text{The argument }Q\text{ has degree two, so }xQ_x+yQ_y=2Q\text{. Divide by }Q.",
        euler=sp.Integer(2),
        logarithmic=True,
    )


def homogeneous_euler_partials(a: int, b: int, c: int) -> Built:
    return derivatives(
        a * sp.sqrt(X) * sp.sin(b * Y / (c * X)),
        r"\text{The ratio }y/x\text{ has degree zero. Its "
        r"chain rule contributions cancel in }xf_x+yf_y.",
        euler=sp.Rational(1, 2),
    )
