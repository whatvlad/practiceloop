"""Exact real-constant identities needed by first-kind integral answers."""

from typing import Any

import sympy as sp


def canonical_arctangents(expression: Any) -> Any:
    """Use atan(q) = pi/2 - atan(1/q) for rational q>1, on the real branch.

    The positive-axis identity follows from a zero derivative of
    atan(t)+atan(1/t), and its exact value pi/2 at t=1. No numerical equality
    or complex logarithm branch is used to accept a learner answer.
    """
    if not expression.has(sp.atan):
        return expression
    replacements = {}
    for value in expression.atoms(sp.atan):
        argument = value.args[0]
        if argument.is_Rational is True and argument > 1:
            replacements[value] = sp.pi / 2 - sp.atan(1 / argument)
    return expression.xreplace(replacements)
