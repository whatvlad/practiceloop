"""Exact rational derivative certificates, including real logarithms and steps."""

from typing import Any

import sympy as sp
from sympy.calculus.util import continuous_domain
from sympy.polys.polyerrors import CoercionFailed, PolynomialError


def _rational(value: Any, variable: Any) -> bool:
    if value.is_rational_function(variable) is not True:
        return False
    return all(
        sp.Poly(part, variable, domain=sp.QQ).degree() <= 12 for part in value.as_numer_denom()
    )


def certifies_rational_primitive(
    candidate: Any, integrand: Any, variable: Any, domain: Any
) -> bool:
    """Return True only after an exact identity and a real-domain certificate.

    d(log|p|)/dx = p'/p wherever real p is nonzero. Only rational QQ terms,
    rational multiples of log|QQ polynomials| of degree <=2 and a single formal
    indefinite integral of a QQ rational function are supported. All other cases
    return False to the caller's general proof, never a guessed equality.
    """
    pieces = domain.args if isinstance(domain, sp.Union) else (domain,)
    if domain != sp.S.Reals and (
        not pieces or any(not isinstance(piece, sp.Interval) or piece.is_empty for piece in pieces)
    ):
        return False
    try:
        if not _rational(integrand, variable):
            return False
        if isinstance(candidate, sp.Integral):
            if candidate.limits != ((variable,),) or not _rational(candidate.function, variable):
                return False
            derivative = expression = candidate.function
        else:
            terms = sp.Add.make_args(candidate)
            if len(terms) > 16:
                return False
            derivative = sp.S.Zero
            expression = candidate
            for term in terms:
                coefficient, rest = term.as_coeff_Mul()
                if rest.func == sp.log and rest.args[0].func == sp.Abs:
                    polynomial = sp.Poly(rest.args[0].args[0], variable, domain=sp.QQ)
                    if coefficient.is_Rational is not True or not 1 <= polynomial.degree() <= 2:
                        return False
                    value = polynomial.as_expr()
                    derivative += coefficient * sp.diff(value, variable) / value
                else:
                    if not _rational(term, variable):
                        return False
                    derivative += sp.diff(term, variable)
        if sp.cancel(derivative - integrand) != 0:
            return False
        defined = continuous_domain(expression, variable, sp.S.Reals)
        return bool(domain - defined == sp.S.EmptySet)
    except (PolynomialError, CoercionFailed, NotImplementedError, ValueError, TypeError):
        return False
