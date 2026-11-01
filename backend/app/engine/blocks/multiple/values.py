"""Clean exact scalar values for definite and multiple integral forms."""

from typing import Any

import sympy as sp

_MAX_NUMERATOR, _MAX_DENOMINATOR = 30, 12
_MAX_VALUE_OPS = 8
_CLEAN_ATOMS = (sp.Rational, sp.log, sp.exp, sp.NumberSymbol)


def value_latex(value: Any) -> str:
    """Leading symbolic term first: `e - 1`, not `-1 + e`."""
    return str(sp.latex(value, order="rev-lex"))


def is_clean_value(value: Any) -> bool:
    """Small exact rationals, π, e, and logarithms or powers of them; never zero."""
    if not value.is_number or value.is_real is not True or value.is_zero is not False:
        return False
    if value.atoms(sp.Float) or sp.count_ops(value) > _MAX_VALUE_OPS:
        return False
    for node in sp.preorder_traversal(value):
        if isinstance(node, sp.Rational) and (
            abs(node.p) > _MAX_NUMERATOR or node.q > _MAX_DENOMINATOR
        ):
            return False
        if node.is_Atom and not isinstance(node, _CLEAN_ATOMS):
            return False
        if node.is_Function and not isinstance(node, (sp.log, sp.exp)):
            return False
    return True
