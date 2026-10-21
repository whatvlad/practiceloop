"""#36 feedback codes for a declared mistake. Kept free of SymPy for the API process."""

from typing import Literal, get_args

type MistakeCode = Literal[
    "power_rule",
    "trig_sign",
    "chain_factor",
    "log_absolute",
    "split_product",
    "parts_sign",
    "cycle_factor",
    "partial_fraction_sign",
    "definite_not_evaluated",
    "bounds_reversed",
    "definite_constant",
    "missing_jacobian",
    "derivative_power",
    "derivative_trig_sign",
    "derivative_chain",
    "derivative_factors",
    "quotient_sign",
    "derivative_constant",
]
MISTAKE_CODES: frozenset[str] = frozenset(get_args(MistakeCode.__value__))
