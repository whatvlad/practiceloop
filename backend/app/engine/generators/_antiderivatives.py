"""Elementary, parts and substitution antiderivatives (#265)."""

import sympy as sp

from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.blocks.analysis_one import X
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._sequence_limits import finish

POSITIVE = sp.Interval.open(0, sp.oo)
REALS = sp.S.Reals


def primitive_of(integrand: sp.Expr) -> sp.Expr:
    result = sp.integrate(integrand, X)
    if result.has(sp.Integral) or result.has(sp.Piecewise):
        raise ValueError("No closed primitive")
    return result


def antiderivative(
    integrand: sp.Expr,
    domain: sp.Set,
    method: str,
    *,
    shown: str | None = None,
    primitive: sp.Expr | None = None,
    checked: sp.Expr | None = None,
) -> Built:
    """``checked`` is an equal form of the integrand on the domain that the checker decides."""
    result = primitive_of(integrand) if primitive is None else primitive
    return finish(
        rf"\text{{Find }}\int {shown or tex(integrand)}\,dx\text{{ for }}x\in{tex(domain)}.",
        AntiderivativeAnswer(integrand if checked is None else checked, result, domain),
        method,
        rf"\int {shown or tex(integrand)}\,dx={tex(result)}+C.",
    )


def fixed_primitive(
    shown: str, primitive: sp.Expr, domain: sp.Set, method: str, derivation: str
) -> Built:
    """Ask for the primitive vanishing at 0, checked as an identity on the stated interval."""
    value = sp.simplify(primitive - primitive.subs(X, 0))
    return finish(
        rf"\text{{Find the primitive }}F\text{{ of }}{shown}\text{{ on }}{tex(domain)}"
        r"\text{ with }F(x)\to0\text{ as }x\to0.",
        DomainFormulaAnswer(value, domain),
        method,
        derivation + rf",\qquad F(x)={tex(value)}.",
    )


def scaled(k: int) -> str:
    return "" if k == 1 else str(k)


# AM1/50: elementary rules after simplifying the integrand.


def sum_of_powers(a: int, b: int, c: int) -> Built:
    f = a * X ** (b + 1) + c / X - (b + 2) * sp.sqrt(X)
    return antiderivative(f, POSITIVE, r"\text{Integrate term by term with the power rule.}")


def conjugate_quotient(a: int, b: int, c: int) -> Built:
    f = (c * c - X) / (c + sp.sqrt(X))
    return antiderivative(
        f,
        POSITIVE,
        rf"{c * c}-x=({c}-\sqrt x)({c}+\sqrt x)\text{{, so the integrand is }}{c}-\sqrt x.",
        shown=rf"\frac{{{c * c}-x}}{{{c}+\sqrt{{x}}}}",
        primitive=c * X - sp.Rational(2, 3) * X ** sp.Rational(3, 2),
    )


def polynomial_division(a: int, b: int, c: int) -> Built:
    f = X**4 / (X**2 + c * c)
    return antiderivative(
        f, REALS, rf"x^4=(x^2+{c * c})(x^2-{c * c})+{c**4}\text{{: divide first.}}"
    )


def double_angle_quotient(a: int, b: int, c: int) -> Built:
    domain = sp.Interval.open(-3 * sp.pi / (4 * b), sp.pi / (4 * b))
    return fixed_primitive(
        rf"\frac{{{scaled(a)}\cos {2 * b}x}}{{\cos {scaled(b)}x-\sin {scaled(b)}x}}",
        a * (sp.sin(b * X) - sp.cos(b * X)) / b,
        domain,
        r"\cos2u=(\cos u-\sin u)(\cos u+\sin u)\text{: cancel.}",
        rf"\int{scaled(a)}(\cos {scaled(b)}x+\sin {scaled(b)}x)\,dx",
    )


def root_powers(a: int, b: int, c: int) -> Built:
    f = (X**a + b * X ** sp.Rational(2, 3) - c) / sp.sqrt(X)
    return antiderivative(
        f,
        POSITIVE,
        r"\text{Divide each term by }\sqrt x\text{ and use the power rule.}",
        shown=rf"\frac{{x^{{{a}}}+{scaled(b)}\sqrt[3]{{x^2}}-{c}}}{{\sqrt x}}",
        primitive=X ** (a + sp.Rational(1, 2)) / (a + sp.Rational(1, 2))
        + sp.Rational(6 * b, 7) * X ** sp.Rational(7, 6)
        - 2 * c * sp.sqrt(X),
    )


def exponential_product(a: int, b: int, c: int) -> Built:
    base = b + 1
    f = sp.exp(-a * X) * base ** (c * X)
    rate = c * sp.log(base) - a
    return antiderivative(
        f,
        REALS,
        rf"e^{{-{a}x}}{base}^{{{c}x}}=e^{{({tex(rate)})x}}.",
        primitive=sp.exp(rate * X) / rate,
    )


# AM1/52 and exam forms: integration by parts.


def parts(integrand: sp.Expr, domain: sp.Set, method: str, **kwargs: object) -> Built:
    return antiderivative(integrand, domain, method, **kwargs)  # type: ignore[arg-type]


def linear_exponential(a: int, b: int, c: int) -> Built:
    return parts((X + b) * sp.exp(-a * X), REALS, r"u=x+b,\ dv=e^{-ax}dx.")


def square_exponential(a: int, b: int, c: int) -> Built:
    return parts((X + b) ** 2 * sp.exp(a * X), REALS, r"\text{Integrate by parts twice.}")


def root_arctan(a: int, b: int, c: int) -> Built:
    return parts(
        a * sp.sqrt(X) * sp.atan(sp.sqrt(X)),
        POSITIVE,
        r"u=\arctan\sqrt x,\ dv=\sqrt x\,dx\text{, then divide the rational part.}",
        primitive=a
        * (
            sp.Rational(2, 3) * X ** sp.Rational(3, 2) * sp.atan(sp.sqrt(X))
            - X / 3
            + sp.log(1 + X) / 3
        ),
    )


def secant_square(a: int, b: int, c: int) -> Built:
    domain = sp.Interval.open(0, sp.pi / (2 * b))
    return fixed_primitive(
        rf"\frac{{{scaled(a)}x}}{{\cos^2 {scaled(b)}x}}",
        a * (X * sp.tan(b * X) / b + sp.log(sp.cos(b * X)) / b**2),
        domain,
        r"u=x,\ dv=\frac{dx}{\cos^2bx},\ v=\frac{\tan bx}{b}.",
        rf"\int=\frac{{{a}x\tan {scaled(b)}x}}{{{b}}}-\frac{{{a}}}{{{b}}}\int\tan {scaled(b)}x\,dx",
    )


def square_sine(a: int, b: int, c: int) -> Built:
    return parts(a * X**2 * sp.sin(b * X), REALS, r"\text{Integrate by parts twice.}")


def arccos_over_root(a: int, b: int, c: int) -> Built:
    return parts(
        a * sp.acos(X) / sp.sqrt(X + 1),
        sp.Interval.open(-1, 1),
        r"u=\arccos x,\ dv=\frac{dx}{\sqrt{x+1}},\ v=2\sqrt{x+1}.",
        primitive=a * (2 * sp.sqrt(X + 1) * sp.acos(X) - 4 * sp.sqrt(1 - X)),
    )


def logarithm(a: int, b: int, c: int) -> Built:
    return parts(
        a * sp.log(X + b),
        sp.Interval.open(-b, sp.oo),
        r"u=\ln(x+b),\ dv=dx.",
        primitive=a * ((X + b) * sp.log(X + b) - X),
    )


def arccos_scaled(a: int, b: int, c: int) -> Built:
    return parts(
        a * sp.acos(X / b),
        sp.Interval.open(-b, b),
        r"u=\arccos(x/b),\ dv=dx.",
        primitive=a * (X * sp.acos(X / b) - sp.sqrt(b * b - X**2)),
    )


def exponential_sine(a: int, b: int, c: int) -> Built:
    return parts(
        sp.exp(a * X) * sp.sin(b * X),
        REALS,
        r"\text{Integrate by parts twice and solve for the integral.}",
        primitive=sp.exp(a * X) * (a * sp.sin(b * X) - b * sp.cos(b * X)) / (a * a + b * b),
    )


def distinct(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a != b else (a, b + 1)


def sine_sine(a: int, b: int, c: int) -> Built:
    p, q = distinct(a, b)
    return parts(
        sp.sin(p * X) * sp.sin(q * X), REALS, r"\sin p\sin q=\tfrac12(\cos(p-q)-\cos(p+q))."
    )


def sine_cosine(a: int, b: int, c: int) -> Built:
    p, q = distinct(a, b)
    return parts(
        sp.sin(p * X) * sp.cos(q * X), REALS, r"\sin p\cos q=\tfrac12(\sin(p+q)+\sin(p-q))."
    )


def cosine_cosine(a: int, b: int, c: int) -> Built:
    p, q = distinct(a, b)
    return parts(
        sp.cos(p * X) * sp.cos(q * X), REALS, r"\cos p\cos q=\tfrac12(\cos(p-q)+\cos(p+q))."
    )


def sine_square(a: int, b: int, c: int) -> Built:
    return parts(
        b * sp.sin(a * X) ** 2,
        REALS,
        r"\sin^2u=\tfrac12(1-\cos2u)\text{ (or by parts).}",
        primitive=b * (X / 2 - sp.sin(2 * a * X) / (4 * a)),
    )


def cosine_fourth(a: int, b: int, c: int) -> Built:
    return parts(
        b * sp.cos(a * X) ** 4,
        REALS,
        r"\cos^4u=\tfrac38+\tfrac12\cos2u+\tfrac18\cos4u.",
        primitive=b * (3 * X / 8 + sp.sin(2 * a * X) / (4 * a) + sp.sin(4 * a * X) / (32 * a)),
    )


def logarithm_quadratic(a: int, b: int, c: int) -> Built:
    return parts(
        a * sp.log(b * b + X**2),
        REALS,
        r"u=\ln(b^2+x^2),\ dv=dx\text{, then }\frac{x^2}{b^2+x^2}=1-\frac{b^2}{b^2+x^2}.",
        primitive=a * (X * sp.log(b * b + X**2) - 2 * X + 2 * b * sp.atan(X / b)),
    )


def linear_sine_exponential(a: int, b: int, c: int) -> Built:
    return parts(X * sp.sin(b * X) * sp.exp(a * X), REALS, r"\text{Parts with }u=x\text{, twice.}")


def arccot_linear(a: int, b: int, c: int) -> Built:
    f = a * X * sp.acot(b * X)
    return parts(
        f,
        POSITIVE,
        r"u=\operatorname{arccot}bx,\ dv=x\,dx.",
        shown=rf"{scaled(a)}x\operatorname{{arccot}}({scaled(b)}x)",
        primitive=a
        * (X**2 * (sp.pi / 2 - sp.atan(b * X)) / 2 + X / (2 * b) - sp.atan(b * X) / (2 * b * b)),
        checked=a * X * (sp.pi / 2 - sp.atan(b * X)),
    )


# AM1/53 and exam forms: substitution.


def substitution(integrand: sp.Expr, domain: sp.Set, method: str, **kwargs: object) -> Built:
    return antiderivative(integrand, domain, method, **kwargs)  # type: ignore[arg-type]


def cosine_root(a: int, b: int, c: int) -> Built:
    return substitution(
        a * sp.cos(b * sp.sqrt(X)) / sp.sqrt(X),
        POSITIVE,
        r"t=\sqrt x,\ dt=\frac{dx}{2\sqrt x}.",
        primitive=2 * a * sp.sin(b * sp.sqrt(X)) / b,
    )


def root_over_x(a: int, b: int, c: int) -> Built:
    t = sp.sqrt(1 + b * X)
    return substitution(
        sp.sqrt(1 + b * X) / X,
        POSITIVE,
        r"t=\sqrt{1+bx}\text{, then partial fractions in }t.",
        primitive=2 * t + sp.log((t - 1) / (t + 1)),
    )


def cosine_over_root_sine(a: int, b: int, c: int) -> Built:
    k = b + 1
    return substitution(
        a * sp.cos(X) / sp.sqrt(k + sp.sin(X)),
        REALS,
        r"t=" + str(k) + r"+\sin x.",
        primitive=2 * a * sp.sqrt(k + sp.sin(X)),
    )


def sine_of_quadratic(a: int, b: int, c: int) -> Built:
    return substitution(
        c * X * sp.sin(a * X**2 + b),
        REALS,
        r"t=ax^2+b.",
        primitive=-c * sp.cos(a * X**2 + b) / (2 * a),
    )


def reciprocal_cosh(a: int, b: int, c: int) -> Built:
    return substitution(
        1 / sp.cosh(a * X),
        REALS,
        r"\frac{1}{\cosh u}=\frac{2e^u}{e^{2u}+1}\text{; put }t=e^{u}.",
        shown=rf"\frac{{1}}{{\cosh {scaled(a)}x}}",
        primitive=2 * sp.atan(sp.exp(a * X)) / a,
        checked=2 * sp.exp(a * X) / (sp.exp(2 * a * X) + 1),
    )


def linear_power(a: int, b: int, c: int) -> Built:
    power = c + 5
    return substitution(
        (b - a * X) ** power,
        REALS,
        r"t=b-ax.",
        primitive=-((b - a * X) ** (power + 1)) / (a * (power + 1)),
    )


def fifth_root(a: int, b: int, c: int) -> Built:
    inner = a * X**3 + b
    return substitution(
        X**2 * inner ** sp.Rational(1, 5),
        POSITIVE,
        r"t=ax^3+b.",
        shown=rf"x^2\sqrt[5]{{{tex(inner)}}}",
        primitive=5 * inner ** sp.Rational(6, 5) / (18 * a),
    )


def reciprocal_root_sum(a: int, b: int, c: int) -> Built:
    return substitution(
        1 / (b + sp.sqrt(X)),
        POSITIVE,
        r"t=\sqrt x,\ dx=2t\,dt.",
        primitive=2 * sp.sqrt(X) - 2 * b * sp.log(b + sp.sqrt(X)),
    )


def logarithm_power(a: int, b: int, c: int) -> Built:
    return substitution(
        a * sp.log(X) ** b / X,
        POSITIVE,
        r"t=\ln x.",
        primitive=a * sp.log(X) ** (b + 1) / (b + 1),
    )


def exponential_arctan(a: int, b: int, c: int) -> Built:
    return substitution(
        sp.exp(a * X) / (sp.exp(2 * a * X) + b * b),
        REALS,
        r"t=e^{ax}.",
        primitive=sp.atan(sp.exp(a * X) / b) / (a * b),
    )


def sine_over_cosine(a: int, b: int, c: int) -> Built:
    q, p = a, a + b
    return substitution(
        c * sp.sin(X) / (p - q * sp.cos(X)),
        REALS,
        r"t=p-q\cos x,\ dt=q\sin x\,dx.",
        primitive=c * sp.log(p - q * sp.cos(X)) / q,
    )


def cubic_exponential(a: int, b: int, c: int) -> Built:
    return substitution(
        X**3 * sp.exp(a * X**2),
        REALS,
        r"t=x^2\text{, then parts.}",
        primitive=sp.exp(a * X**2) * (a * X**2 - 1) / (2 * a * a),
    )


def root_over_linear(a: int, b: int, c: int) -> Built:
    return substitution(
        sp.sqrt(X) / (X + b * b),
        POSITIVE,
        r"t=\sqrt x,\ \frac{2t^2}{t^2+b^2}=2-\frac{2b^2}{t^2+b^2}.",
        primitive=2 * sp.sqrt(X) - 2 * b * sp.atan(sp.sqrt(X) / b),
    )


def logarithm_arctan(a: int, b: int, c: int) -> Built:
    return substitution(
        sp.log(a * sp.atan(X)) / (1 + X**2),
        POSITIVE,
        r"t=\arctan x\text{, then parts for }\int\ln(at)\,dt.",
        primitive=sp.atan(X) * (sp.log(a * sp.atan(X)) - 1),
    )


def sine_cosine_arctan(a: int, b: int, c: int) -> Built:
    s = sp.sin(X)
    return substitution(
        s * sp.cos(X) * sp.atan(b * s),
        REALS,
        r"t=\sin x\text{, then parts for }\int t\arctan(bt)\,dt.",
        primitive=(b * b * s**2 + 1) * sp.atan(b * s) / (2 * b * b) - s / (2 * b),
    )


def root_quotient_value(a: int, b: int, c: int) -> Built:
    """The exam primitive through t=sqrt(x), fixed by a stated value at x=1."""
    t = sp.Symbol("t", positive=True)
    inner = sp.integrate(sp.expand(sp.cancel(2 * t * (t**4 + t) / (t + 1))), t)
    value = sp.Rational(c, 3)
    general = inner.subs(t, sp.sqrt(X))
    primitive = sp.expand(general - general.subs(X, 1) + value)
    return finish(
        r"\text{With }x=t^2\ (t\ge0)\text{ find the primitive }F\text{ of }"
        r"\frac{x^2+\sqrt x}{\sqrt x+1}\text{ on }(0,\infty)\text{ with }F(1)=" + tex(value) + ".",
        DomainFormulaAnswer(primitive, POSITIVE),
        r"dx=2t\,dt:\ \int\frac{t^4+t}{t+1}\,2t\,dt=\int2t^2(t^2-t+1)\,dt.",
        rf"F(x)={tex(primitive)}.",
    )
