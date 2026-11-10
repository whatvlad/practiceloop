"""Frozen providers for the computational sequence and continuity expansion (#236)."""

from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from pydantic import Field

from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.answers.computational import (
    CategoryAnswer,
    FormulaAnswer,
    LimitAnswer,
    OrderedAnswer,
    RealSetAnswer,
)
from app.engine.codes import encode
from app.engine.generators import _antiderivatives as antiderivatives
from app.engine.generators import _convexity as convexity
from app.engine.generators import _derivatives as derivatives
from app.engine.generators import _extrema as extrema
from app.engine.generators import _function_limits as functions
from app.engine.generators import _lhopital as lhopital
from app.engine.generators import _sequence_limits as sequences
from app.engine.generators import _taylor as taylor
from app.engine.generators._elementary_common import Built
from app.engine.models import Answer, Drawn, Task
from app.engine.prng import DeterministicRNG
from app.math_input.contracts import InputContract

LIMIT = InputContract("limit_result")
CONSTANT = InputContract("formula")
BOUNDS_KIND = InputContract("category", choices=sequences.BOUNDS)
BOUNDS = InputContract(
    "tuple", components=(BOUNDS_KIND, CONSTANT, CONSTANT), labels=sequences.BOUND_LABELS
)
UPPER = InputContract("tuple", components=(BOUNDS_KIND, CONSTANT), labels=sequences.UPPER_LABELS)
TAIL = InputContract(
    "tuple",
    components=(InputContract("category", choices=sequences.MONOTONICITY), CONSTANT),
    labels=sequences.MONOTONICITY_LABELS,
)
SIDES = InputContract("tuple", components=(LIMIT, LIMIT, LIMIT), labels=functions.SIDES)
ASYMPTOTES = InputContract(
    "tuple",
    components=(
        InputContract("real_set"),
        *(InputContract("formula", symbols=functions.REAL_X),) * 2,
    ),
    labels=functions.ASYMPTOTES,
)
DOMAIN_ASYMPTOTES = InputContract(
    "tuple",
    components=(InputContract("real_set"), *ASYMPTOTES.components),
    labels=functions.DOMAIN_ASYMPTOTES,
)
JOINS = InputContract("tuple", components=(CONSTANT, CONSTANT), labels=functions.JOINS)
DISCONTINUITY = InputContract(
    "tuple",
    components=(CONSTANT, LIMIT, LIMIT, InputContract("category", choices=functions.DISCONTINUITY)),
    labels=functions.DISCONTINUITY_LABELS,
)
FREE_JOIN = InputContract(
    "tuple", components=(CONSTANT, InputContract("real_set")), labels=functions.UNRESTRICTED_JOIN
)
TWO_DISCONTINUITIES = InputContract(
    "tuple", components=(DISCONTINUITY, DISCONTINUITY), labels=functions.TWO_LOCATIONS
)
ROOT = InputContract("tuple", components=(CONSTANT, CONSTANT), labels=functions.ROOT)
# #259: asymptotes by the slope and offset limits at each end of the domain.
REAL_SET = InputContract("real_set")
ENDS = InputContract(
    "tuple", components=(REAL_SET, LIMIT, LIMIT, LIMIT, LIMIT), labels=functions.ENDS
)
RIGHT_END = InputContract("tuple", components=(REAL_SET, LIMIT, LIMIT), labels=functions.RIGHT_END)
PERIODIC = InputContract("tuple", components=(CONSTANT, REAL_SET), labels=("Period", "Base set"))
PERIODIC_ENDS = InputContract(
    "tuple", components=(PERIODIC, LIMIT, LIMIT, LIMIT, LIMIT), labels=functions.ENDS
)
CONTINUITY_AT = InputContract(
    "tuple",
    components=(LIMIT, LIMIT, InputContract("category", choices=functions.CONTINUITY_CLASSES)),
    labels=functions.CONTINUITY_AT,
)
# #260: derivatives with domains and tangent lines.
LINE = InputContract("formula", symbols=derivatives.REAL_X)
DERIVATIVE = LINE
DERIVATIVE_DOMAIN = InputContract(
    "tuple", components=(LINE, REAL_SET), labels=derivatives.DERIVATIVE_DOMAIN
)
DERIVATIVE_EXCLUDED = InputContract(
    "tuple", components=(LINE, PERIODIC), labels=derivatives.DERIVATIVE_EXCLUDED
)
TANGENT_AT = InputContract("tuple", components=(CONSTANT, LINE), labels=derivatives.TANGENT_AT)
TANGENT_FIND = InputContract("tuple", components=(CONSTANT, LINE), labels=derivatives.TANGENT_FIND)
TANGENT_FULL = InputContract(
    "tuple", components=(CONSTANT, CONSTANT, LINE), labels=derivatives.TANGENT_FULL
)
TWO_TANGENTS = InputContract(
    "tuple", components=(TANGENT_FULL, TANGENT_FULL), labels=derivatives.TWO_TANGENTS
)
# #262: monotonicity, extrema and optimization.
MONOTONIC = InputContract("tuple", components=(REAL_SET, REAL_SET), labels=extrema.MONOTONIC)
EXTREMA = InputContract("tuple", components=(REAL_SET,) * 4, labels=extrema.EXTREMA)
GLOBAL = InputContract("tuple", components=(CONSTANT, CONSTANT), labels=extrema.GLOBAL)
DIMENSIONS = InputContract("tuple", components=(CONSTANT, CONSTANT), labels=extrema.DIMENSIONS)
BOX = InputContract("tuple", components=(CONSTANT, CONSTANT), labels=extrema.BOX)
ANGLE_RADIUS = InputContract("tuple", components=(CONSTANT, CONSTANT), labels=extrema.ANGLE_RADIUS)
# #263: convexity and polynomial reconstruction.
CONVEXITY = InputContract(
    "tuple", components=(REAL_SET, REAL_SET, REAL_SET), labels=convexity.CONVEXITY
)
# #264: Taylor formulas, error bounds and certified approximations.
TAYLOR = InputContract("tuple", components=(LINE, LINE), labels=taylor.TAYLOR)
APPROXIMATION = InputContract("tuple", components=(CONSTANT, CONSTANT), labels=taylor.APPROXIMATION)
ANSWERS: dict[str, type[Answer]] = {
    "category": CategoryAnswer,
    "formula": FormulaAnswer,
    "limit_result": LimitAnswer,
    "tuple": OrderedAnswer,
    "real_set": RealSetAnswer,
}

SEQUENCES = "functions-and-sequences"
FUNCTIONS = "limits-and-continuity"
DERIVATIVES = "differential-calculus"
BASIC = "basic-integrals"
PARTS = "integration-by-parts"
# Antiderivatives are not a computational kind: they carry no public input contract.
PRIMITIVE = None
# Explicit prefixes are permanent and independent of the order of these entries.
SPECS = (
    (sequences.bound_trigonometric, SEQUENCES, 2, "SLAA", BOUNDS),
    (sequences.bound_radical, SEQUENCES, 1, "SLAB", UPPER),
    (sequences.monotone_factorial, SEQUENCES, 4, "SLAC", TAIL),
    (sequences.monotone_radical, SEQUENCES, 3, "SLAD", TAIL),
    (sequences.definition_reciprocal, SEQUENCES, 2, "SLAE", LIMIT),
    (sequences.definition_growth, SEQUENCES, 2, "SLAF", LIMIT),
    (sequences.rational_leading, SEQUENCES, 3, "SLAG", LIMIT),
    (sequences.factorial_limit, SEQUENCES, 4, "SLAH", LIMIT),
    (sequences.conjugate_sequence, SEQUENCES, 4, "SLAI", LIMIT),
    (sequences.squeeze_oscillation, SEQUENCES, 3, "SLAJ", LIMIT),
    (sequences.squeeze_floor, SEQUENCES, 4, "SLAK", LIMIT),
    (sequences.squeeze_root, SEQUENCES, 4, "SLAL", LIMIT),
    (sequences.squeeze_sum, SEQUENCES, 5, "SLAM", LIMIT),
    (sequences.exponential_power, SEQUENCES, 4, "SLAN", LIMIT),
    (sequences.exponential_difference, SEQUENCES, 5, "SLAO", LIMIT),
    (sequences.infinite_exponential, SEQUENCES, 3, "SLAP", LIMIT),
    (sequences.bound_conjugate, SEQUENCES, 2, "SLAQ", BOUNDS),
    (sequences.monotone_ratio, SEQUENCES, 4, "SLAR", TAIL),
    (sequences.rational_zero, SEQUENCES, 2, "SLAS", LIMIT),
    (sequences.arithmetic_sum_ratio, SEQUENCES, 3, "SLAT", LIMIT),
    (sequences.root_exponential_ratio, SEQUENCES, 5, "SLAU", LIMIT),
    (sequences.logarithmic_power, SEQUENCES, 5, "SLAV", LIMIT),
    (sequences.infinite_factorial, SEQUENCES, 4, "SLAW", LIMIT),
    (sequences.divergent_oscillation, SEQUENCES, 3, "SLAX", LIMIT),
    (sequences.scaled_conjugate, SEQUENCES, 4, "SLAY", LIMIT),
    (functions.definition_pole, FUNCTIONS, 1, "FLAA", LIMIT),
    (functions.rational_cancellation, FUNCTIONS, 2, "FLAB", LIMIT),
    (functions.radical_cancellation, FUNCTIONS, 3, "FLAC", LIMIT),
    (functions.exponential_dominance, FUNCTIONS, 2, "FLAD", LIMIT),
    (functions.absolute_jump, FUNCTIONS, 2, "FLAE", SIDES),
    (functions.essential_exponential, FUNCTIONS, 4, "FLAF", SIDES),
    (functions.squeeze_function, FUNCTIONS, 3, "FLAG", LIMIT),
    (functions.infinitesimal_exp_sin, FUNCTIONS, 3, "FLAH", LIMIT),
    (functions.infinitesimal_log, FUNCTIONS, 4, "FLAI", LIMIT),
    (functions.infinitesimal_power, FUNCTIONS, 5, "FLAJ", LIMIT),
    (functions.asymptote_rational, FUNCTIONS, 4, "FLAK", ASYMPTOTES),
    (functions.asymptote_inverse_trig, FUNCTIONS, 4, "FLAL", ASYMPTOTES),
    (functions.continuity_sine, FUNCTIONS, 4, "FLAM", JOINS),
    (functions.continuity_reciprocal, FUNCTIONS, 3, "FLAN", CONSTANT),
    (functions.discontinuity_arctan, FUNCTIONS, 4, "FLAO", DISCONTINUITY),
    (functions.discontinuity_oscillatory, FUNCTIONS, 5, "FLAP", DISCONTINUITY),
    (functions.certified_root, FUNCTIONS, 5, "FLAQ", ROOT),
    (functions.two_sided_absolute, FUNCTIONS, 2, "FLAR", SIDES),
    (functions.squeeze_at_infinity, FUNCTIONS, 2, "FLAS", LIMIT),
    (functions.infinitesimal_inverse_trig, FUNCTIONS, 4, "FLAT", LIMIT),
    (functions.horizontal_asymptote, FUNCTIONS, 3, "FLAU", ASYMPTOTES),
    (functions.discontinuity_removable, FUNCTIONS, 3, "FLAV", DISCONTINUITY),
    (functions.discontinuity_infinite, FUNCTIONS, 3, "FLAW", DISCONTINUITY),
    (functions.certified_cubic, FUNCTIONS, 5, "FLAX", ROOT),
    (functions.radical_asymptote, FUNCTIONS, 5, "FLAY", ASYMPTOTES),
    (functions.high_order_pole, FUNCTIONS, 4, "FLAZ", ASYMPTOTES),
    (functions.conjugate_at_infinity, FUNCTIONS, 3, "FLBA", LIMIT),
    (functions.removable_trigonometric, FUNCTIONS, 2, "FLBB", LIMIT),
    (functions.power_difference, FUNCTIONS, 4, "FLBC", LIMIT),
    (functions.finite_heine_limit, FUNCTIONS, 1, "FLBD", LIMIT),
    (functions.heine_at_infinity, FUNCTIONS, 2, "FLBE", LIMIT),
    (functions.continuity_free_parameter, FUNCTIONS, 4, "FLBF", FREE_JOIN),
    (functions.discontinuity_pole_and_hole, FUNCTIONS, 5, "FLBG", TWO_DISCONTINUITIES),
    (functions.unique_log_exponential_root, FUNCTIONS, 4, "FLBH", CONSTANT),
    (functions.rational_pole_and_domain, FUNCTIONS, 4, "FLBI", DOMAIN_ASYMPTOTES),
    (functions.exponential_pole, FUNCTIONS, 4, "FLBJ", ASYMPTOTES),
    # #257
    (sequences.bound_root_exponential, SEQUENCES, 3, "SLAZ", BOUNDS),
    (sequences.bound_geometric_sum, SEQUENCES, 4, "SLBA", BOUNDS),
    (sequences.monotone_exponential_difference, SEQUENCES, 4, "SLBB", TAIL),
    (sequences.monotone_rational, SEQUENCES, 3, "SLBC", TAIL),
    (sequences.monotone_conjugate, SEQUENCES, 3, "SLBD", TAIL),
    (sequences.definition_root, SEQUENCES, 2, "SLBE", LIMIT),
    (sequences.definition_exponential, SEQUENCES, 2, "SLBF", LIMIT),
    (sequences.product_leading_orders, SEQUENCES, 4, "SLBG", LIMIT),
    (sequences.competing_exponentials, SEQUENCES, 4, "SLBH", LIMIT),
    (sequences.radical_degree, SEQUENCES, 3, "SLBI", LIMIT),
    (sequences.root_rational_sum, SEQUENCES, 4, "SLBJ", LIMIT),
    (sequences.negative_growing_power, SEQUENCES, 4, "SLBK", LIMIT),
    (sequences.product_of_powers, SEQUENCES, 5, "SLBL", LIMIT),
    (sequences.reciprocal_power, SEQUENCES, 3, "SLBM", LIMIT),
    (sequences.rational_growth, SEQUENCES, 2, "SLBN", LIMIT),
    (sequences.radical_difference_growth, SEQUENCES, 3, "SLBO", LIMIT),
    (sequences.inverse_trig_ratio, SEQUENCES, 3, "SLBP", LIMIT),
    (sequences.root_exponential_sum, SEQUENCES, 4, "SLBQ", LIMIT),
    (sequences.root_polynomial, SEQUENCES, 3, "SLBR", LIMIT),
    (sequences.quartic_conjugate, SEQUENCES, 4, "SLBS", LIMIT),
    (sequences.conjugate_ratio, SEQUENCES, 4, "SLBT", LIMIT),
    (sequences.factorial_degree_ratio, SEQUENCES, 4, "SLBU", LIMIT),
    (sequences.exponential_product_ratio, SEQUENCES, 4, "SLBV", LIMIT),
    (sequences.reciprocal_exponential_conjugate, SEQUENCES, 5, "SLBW", LIMIT),
    (sequences.product_radical, SEQUENCES, 3, "SLBX", LIMIT),
    (functions.rational_substitution, FUNCTIONS, 1, "FLBK", LIMIT),
    (functions.radical_quotient_zero, FUNCTIONS, 2, "FLBL", LIMIT),
    (functions.power_difference_quotient, FUNCTIONS, 3, "FLBM", LIMIT),
    (functions.leading_power_quotient, FUNCTIONS, 3, "FLBN", LIMIT),
    (functions.conjugate_minus_infinity, FUNCTIONS, 4, "FLBO", LIMIT),
    (functions.tangent_ratio, FUNCTIONS, 2, "FLBP", LIMIT),
    (functions.radical_linear_ratio, FUNCTIONS, 2, "FLBQ", LIMIT),
    (functions.cancelling_reciprocals, FUNCTIONS, 3, "FLBR", LIMIT),
    (functions.bounded_inverse_trig, FUNCTIONS, 3, "FLBS", SIDES),
    (functions.squeeze_arctan, FUNCTIONS, 3, "FLBT", LIMIT),
    (functions.sine_product_square, FUNCTIONS, 2, "FLBU", LIMIT),
    (functions.sine_radical, FUNCTIONS, 3, "FLBV", LIMIT),
    (functions.arctan_at_infinity, FUNCTIONS, 3, "FLBW", LIMIT),
    (functions.cosine_ratio_half_pi, FUNCTIONS, 4, "FLBX", LIMIT),
    (functions.log_cube_root, FUNCTIONS, 4, "FLBY", LIMIT),
    (functions.log_near_one, FUNCTIONS, 4, "FLBZ", LIMIT),
    (functions.tangent_power, FUNCTIONS, 5, "FLCA", LIMIT),
    (functions.root_difference, FUNCTIONS, 4, "FLCB", LIMIT),
    (functions.sine_quadratic_ratio, FUNCTIONS, 4, "FLCC", LIMIT),
    (functions.log_difference_infinity, FUNCTIONS, 3, "FLCD", LIMIT),
    (functions.log_quadratic_at_point, FUNCTIONS, 3, "FLCE", LIMIT),
    (functions.sine_power_product, FUNCTIONS, 3, "FLCF", LIMIT),
    (functions.radical_growth_asymptotes, FUNCTIONS, 4, "FLCG", RIGHT_END),
    (functions.oscillatory_remainder, FUNCTIONS, 4, "FLCH", ENDS),
    (functions.exponential_zero_denominator, FUNCTIONS, 5, "FLCI", ENDS),
    (functions.trig_periodic_poles, FUNCTIONS, 5, "FLCJ", PERIODIC_ENDS),
    (functions.continuity_log_ratio, FUNCTIONS, 4, "FLCK", CONTINUITY_AT),
    (functions.exp_join, FUNCTIONS, 5, "FLCL", JOINS),
    (functions.quartic_cubic_oblique, FUNCTIONS, 4, "FLCM", ENDS),
    (functions.radical_oblique_right, FUNCTIONS, 5, "FLCN", RIGHT_END),
    (functions.radical_quotient_right, FUNCTIONS, 4, "FLCO", RIGHT_END),
    (functions.rational_oblique_pole, FUNCTIONS, 3, "FLCP", DOMAIN_ASYMPTOTES),
    (functions.rational_oblique_pole_left, FUNCTIONS, 3, "FLCQ", DOMAIN_ASYMPTOTES),
    # #260
    (derivatives.definition_power, DERIVATIVES, 1, "DVAA", DERIVATIVE),
    (derivatives.definition_reciprocal, DERIVATIVES, 2, "DVAB", DERIVATIVE),
    (derivatives.definition_root, DERIVATIVES, 2, "DVAC", DERIVATIVE),
    (derivatives.definition_sine, DERIVATIVES, 3, "DVAD", DERIVATIVE),
    (derivatives.trig_sum, DERIVATIVES, 2, "DVAE", DERIVATIVE_EXCLUDED),
    (derivatives.exponential_quadratic, DERIVATIVES, 2, "DVAF", DERIVATIVE_DOMAIN),
    (derivatives.rational_quotient, DERIVATIVES, 2, "DVAG", DERIVATIVE_DOMAIN),
    (derivatives.exponential_square, DERIVATIVES, 3, "DVAH", DERIVATIVE_DOMAIN),
    (derivatives.log_arctan_root, DERIVATIVES, 4, "DVAI", DERIVATIVE_DOMAIN),
    (derivatives.exponential_arctan, DERIVATIVES, 3, "DVAJ", DERIVATIVE_DOMAIN),
    (derivatives.log_cosine, DERIVATIVES, 3, "DVAK", DERIVATIVE_DOMAIN),
    (derivatives.root_arccos, DERIVATIVES, 4, "DVAL", DERIVATIVE_DOMAIN),
    (derivatives.constant_over_power, DERIVATIVES, 2, "DVAM", DERIVATIVE_DOMAIN),
    (derivatives.exponential_trig_powers, DERIVATIVES, 4, "DVAN", DERIVATIVE_DOMAIN),
    (derivatives.power_of_exponential, DERIVATIVES, 2, "DVAO", DERIVATIVE_DOMAIN),
    (derivatives.variable_power, DERIVATIVES, 4, "DVAP", DERIVATIVE),
    (derivatives.inverse_trig_constant, DERIVATIVES, 3, "DVAQ", DERIVATIVE_DOMAIN),
    (derivatives.logarithm_constant, DERIVATIVES, 2, "DVAR", DERIVATIVE_DOMAIN),
    (derivatives.log_constant_quotient, DERIVATIVES, 1, "DVAS", DERIVATIVE_DOMAIN),
    (derivatives.constant_coefficients, DERIVATIVES, 1, "DVAT", DERIVATIVE_DOMAIN),
    (derivatives.root_exponential_domain, DERIVATIVES, 4, "DVAU", DERIVATIVE_DOMAIN),
    (derivatives.arcsine_shifted_square, DERIVATIVES, 4, "DVAV", DERIVATIVE_DOMAIN),
    (derivatives.tangent_arctan, DERIVATIVES, 2, "DVAW", TANGENT_AT),
    (derivatives.tangent_logarithm, DERIVATIVES, 2, "DVAX", TANGENT_AT),
    (derivatives.tangent_tangent_square, DERIVATIVES, 3, "DVAY", TANGENT_AT),
    (derivatives.tangent_root_exponential, DERIVATIVES, 3, "DVAZ", TANGENT_AT),
    (derivatives.tangent_rational, DERIVATIVES, 3, "DVBA", TANGENT_AT),
    (derivatives.tangent_exponential_level, DERIVATIVES, 3, "DVBB", TANGENT_FIND),
    (derivatives.tangent_arctan_quotient, DERIVATIVES, 3, "DVBC", TANGENT_AT),
    (derivatives.tangent_exponential_cubic, DERIVATIVES, 3, "DVBD", TANGENT_FIND),
    (derivatives.tangent_parallel_quartic, DERIVATIVES, 3, "DVBE", TANGENT_FULL),
    (derivatives.tangent_angle_root, DERIVATIVES, 3, "DVBF", TANGENT_FULL),
    (derivatives.tangent_perpendicular_xlogx, DERIVATIVES, 4, "DVBG", TANGENT_FULL),
    (derivatives.tangent_line_intersection, DERIVATIVES, 4, "DVBH", TANGENT_FULL),
    (derivatives.tangent_axis_intersection, DERIVATIVES, 2, "DVBI", TANGENT_FULL),
    (derivatives.tangent_horizontal, DERIVATIVES, 4, "DVBJ", TANGENT_FULL),
    (derivatives.tangent_pair_perpendicular, DERIVATIVES, 5, "DVBK", TWO_TANGENTS),
    # #261
    (lhopital.error_triangle_area, DERIVATIVES, 3, "DVBL", CONSTANT),
    (lhopital.error_sphere_volume, DERIVATIVES, 2, "DVBM", CONSTANT),
    (lhopital.error_fall_depth, DERIVATIVES, 2, "DVBN", CONSTANT),
    (lhopital.error_average_speed, DERIVATIVES, 3, "DVBO", CONSTANT),
    (lhopital.log_exponential_growth, DERIVATIVES, 2, "DVBP", LIMIT),
    (lhopital.log_sine_ratio, DERIVATIVES, 3, "DVBQ", LIMIT),
    (lhopital.arctan_difference, DERIVATIVES, 3, "DVBR", LIMIT),
    (lhopital.double_root_quotient, DERIVATIVES, 4, "DVBS", LIMIT),
    (lhopital.log_cosine_ratio, DERIVATIVES, 3, "DVBT", LIMIT),
    (lhopital.root_arccot, DERIVATIVES, 3, "DVBU", LIMIT),
    (lhopital.power_log_zero, DERIVATIVES, 2, "DVBV", LIMIT),
    (lhopital.tangent_half_angle, DERIVATIVES, 3, "DVBW", LIMIT),
    (lhopital.cosine_difference, DERIVATIVES, 4, "DVBX", LIMIT),
    (lhopital.cotangent_difference, DERIVATIVES, 4, "DVBY", LIMIT),
    (lhopital.log_reciprocal_sum, DERIVATIVES, 4, "DVBZ", LIMIT),
    (lhopital.log_power_zero, DERIVATIVES, 4, "DVCA", LIMIT),
    (lhopital.arctan_power, DERIVATIVES, 5, "DVCB", LIMIT),
    (lhopital.log_exponent_power, DERIVATIVES, 4, "DVCC", LIMIT),
    (lhopital.tangent_cosine_power, DERIVATIVES, 4, "DVCD", LIMIT),
    (lhopital.exponential_cosh, DERIVATIVES, 2, "DVCE", LIMIT),
    (lhopital.one_minus_power, DERIVATIVES, 5, "DVCF", LIMIT),
    (lhopital.tangent_log, DERIVATIVES, 3, "DVCG", LIMIT),
    (lhopital.log_tangent_product, DERIVATIVES, 3, "DVCH", LIMIT),
    (lhopital.differentiable_join, DERIVATIVES, 3, "DVCI", JOINS),
    # #262
    (extrema.monotone_cubic, DERIVATIVES, 2, "DVCJ", MONOTONIC),
    (extrema.monotone_trig_difference, DERIVATIVES, 3, "DVCK", MONOTONIC),
    (extrema.monotone_linear_reciprocal, DERIVATIVES, 2, "DVCL", MONOTONIC),
    (extrema.monotone_cubic_over_quadratic, DERIVATIVES, 4, "DVCM", MONOTONIC),
    (extrema.monotone_root_quotient, DERIVATIVES, 3, "DVCN", MONOTONIC),
    (extrema.monotone_exponential_product, DERIVATIVES, 2, "DVCO", MONOTONIC),
    (extrema.monotone_log_square, DERIVATIVES, 4, "DVCP", MONOTONIC),
    (extrema.monotone_log_quotient, DERIVATIVES, 3, "DVCQ", MONOTONIC),
    (extrema.monotone_exponential_difference, DERIVATIVES, 4, "DVCR", MONOTONIC),
    (extrema.monotone_reciprocal_log, DERIVATIVES, 2, "DVCS", MONOTONIC),
    (extrema.monotone_power_log, DERIVATIVES, 3, "DVCT", MONOTONIC),
    (extrema.extrema_cubic, DERIVATIVES, 2, "DVCU", EXTREMA),
    (extrema.extrema_linear_reciprocal, DERIVATIVES, 2, "DVCV", EXTREMA),
    (extrema.extrema_exponential_quotient, DERIVATIVES, 3, "DVCW", EXTREMA),
    (extrema.extrema_shifted_exponential, DERIVATIVES, 2, "DVCX", EXTREMA),
    (extrema.extrema_rational, DERIVATIVES, 4, "DVCY", EXTREMA),
    (extrema.extrema_absolute_quadratic, DERIVATIVES, 4, "DVCZ", EXTREMA),
    (extrema.extrema_x_log, DERIVATIVES, 2, "DVDA", EXTREMA),
    (extrema.extrema_root_cubic, DERIVATIVES, 5, "DVDB", EXTREMA),
    (extrema.extrema_arctan_log, DERIVATIVES, 3, "DVDC", EXTREMA),
    (extrema.extrema_none, DERIVATIVES, 3, "DVDD", EXTREMA),
    (extrema.extrema_exponential_shift, DERIVATIVES, 2, "DVDE", EXTREMA),
    (extrema.global_cubic, DERIVATIVES, 2, "DVDF", GLOBAL),
    (extrema.global_reciprocal_quadratic, DERIVATIVES, 2, "DVDG", GLOBAL),
    (extrema.global_root_difference, DERIVATIVES, 2, "DVDH", GLOBAL),
    (extrema.global_absolute_exponential, DERIVATIVES, 5, "DVDI", GLOBAL),
    (extrema.global_absolute_parabola, DERIVATIVES, 4, "DVDJ", GLOBAL),
    (extrema.global_sine_cubic, DERIVATIVES, 3, "DVDK", GLOBAL),
    (extrema.global_semicircle_root, DERIVATIVES, 2, "DVDL", GLOBAL),
    (extrema.global_cosine_quotient, DERIVATIVES, 4, "DVDM", GLOBAL),
    (extrema.global_rational_interval, DERIVATIVES, 3, "DVDN", GLOBAL),
    (extrema.global_root_product, DERIVATIVES, 3, "DVDO", GLOBAL),
    (extrema.fenced_plots, DERIVATIVES, 4, "DVDP", DIMENSIONS),
    (extrema.pipeline, DERIVATIVES, 4, "DVDQ", CONSTANT),
    (extrema.container, DERIVATIVES, 4, "DVDR", BOX),
    (extrema.incircle_triangle, DERIVATIVES, 5, "DVDS", ANGLE_RADIUS),
    (extrema.parabola_rectangle, DERIVATIVES, 3, "DVDT", DIMENSIONS),
    (extrema.semicircle_rectangle, DERIVATIVES, 3, "DVDU", DIMENSIONS),
    (extrema.semicircle_waste, DERIVATIVES, 3, "DVDV", CONSTANT),
    (extrema.circle_square, DERIVATIVES, 3, "DVDW", DIMENSIONS),
    # #263
    (convexity.convex_cubic, DERIVATIVES, 2, "DVDX", CONVEXITY),
    (convexity.convex_exponential_product, DERIVATIVES, 3, "DVDY", CONVEXITY),
    (convexity.convex_cubic_quotient, DERIVATIVES, 4, "DVDZ", CONVEXITY),
    (convexity.convex_log_quadratic, DERIVATIVES, 3, "DVEA", CONVEXITY),
    (convexity.convex_reciprocal, DERIVATIVES, 3, "DVEB", CONVEXITY),
    (convexity.convex_log_absolute, DERIVATIVES, 4, "DVEC", CONVEXITY),
    (convexity.convex_trig, DERIVATIVES, 4, "DVED", CONVEXITY),
    (convexity.convex_exponential_arctan, DERIVATIVES, 3, "DVEE", CONVEXITY),
    (convexity.convex_log_root, DERIVATIVES, 4, "DVEF", CONVEXITY),
    (convexity.convex_reversed_exponential, DERIVATIVES, 3, "DVEG", CONVEXITY),
    (convexity.increasing_convex_quadratic_exponential, DERIVATIVES, 5, "DVEH", REAL_SET),
    (convexity.increasing_convex_root_log, DERIVATIVES, 4, "DVEI", REAL_SET),
    (convexity.decreasing_concave_quadratic_exponential, DERIVATIVES, 5, "DVEJ", REAL_SET),
    (convexity.increasing_concave_arccot, DERIVATIVES, 5, "DVEK", REAL_SET),
    (convexity.polynomial_extrema, DERIVATIVES, 3, "DVEL", LINE),
    (convexity.polynomial_inflection, DERIVATIVES, 3, "DVEM", LINE),
    # #264
    (taylor.taylor_cubic, DERIVATIVES, 3, "DVEN", TAYLOR),
    (taylor.taylor_reciprocal_power, DERIVATIVES, 3, "DVEO", TAYLOR),
    (taylor.taylor_sine_at_pi, DERIVATIVES, 4, "DVEP", TAYLOR),
    (taylor.taylor_exponential, DERIVATIVES, 3, "DVEQ", TAYLOR),
    (taylor.maclaurin_sine, DERIVATIVES, 3, "DVER", TAYLOR),
    (taylor.maclaurin_cosh, DERIVATIVES, 3, "DVES", TAYLOR),
    (taylor.maclaurin_cosine, DERIVATIVES, 3, "DVET", TAYLOR),
    (taylor.maclaurin_exponential_product, DERIVATIVES, 4, "DVEU", TAYLOR),
    (taylor.error_tangent, DERIVATIVES, 5, "DVEV", CONSTANT),
    (taylor.error_cosine_square, DERIVATIVES, 4, "DVEW", CONSTANT),
    (taylor.error_square_root, DERIVATIVES, 4, "DVEX", CONSTANT),
    (taylor.error_logarithm, DERIVATIVES, 4, "DVEY", CONSTANT),
    (taylor.error_inverse_root, DERIVATIVES, 4, "DVEZ", CONSTANT),
    (taylor.approximate_reciprocal_e, DERIVATIVES, 4, "DVFA", APPROXIMATION),
    (taylor.approximate_cube_root, DERIVATIVES, 5, "DVFB", APPROXIMATION),
    (taylor.approximate_logarithm, DERIVATIVES, 4, "DVFC", APPROXIMATION),
    (taylor.approximate_sine, DERIVATIVES, 4, "DVFD", APPROXIMATION),
    # #265
    (antiderivatives.sum_of_powers, BASIC, 1, "INAA", PRIMITIVE),
    (antiderivatives.conjugate_quotient, BASIC, 2, "INAB", PRIMITIVE),
    (antiderivatives.polynomial_division, BASIC, 2, "INAC", PRIMITIVE),
    (antiderivatives.double_angle_quotient, BASIC, 3, "INAD", LINE),
    (antiderivatives.root_powers, BASIC, 2, "INAE", PRIMITIVE),
    (antiderivatives.exponential_product, BASIC, 2, "INAF", PRIMITIVE),
    (antiderivatives.linear_exponential, PARTS, 1, "INAG", PRIMITIVE),
    (antiderivatives.square_exponential, PARTS, 2, "INAH", PRIMITIVE),
    (antiderivatives.root_arctan, PARTS, 3, "INAI", PRIMITIVE),
    (antiderivatives.secant_square, PARTS, 2, "INAJ", LINE),
    (antiderivatives.square_sine, PARTS, 2, "INAK", PRIMITIVE),
    (antiderivatives.arccos_over_root, PARTS, 3, "INAL", PRIMITIVE),
    (antiderivatives.logarithm, PARTS, 1, "INAM", PRIMITIVE),
    (antiderivatives.arccos_scaled, PARTS, 2, "INAN", PRIMITIVE),
    (antiderivatives.exponential_sine, PARTS, 3, "INAO", PRIMITIVE),
    (antiderivatives.sine_sine, PARTS, 2, "INAP", PRIMITIVE),
    (antiderivatives.sine_cosine, PARTS, 2, "INAQ", PRIMITIVE),
    (antiderivatives.cosine_cosine, PARTS, 2, "INAR", PRIMITIVE),
    (antiderivatives.sine_square, PARTS, 1, "INAS", PRIMITIVE),
    (antiderivatives.cosine_fourth, PARTS, 3, "INAT", PRIMITIVE),
    (antiderivatives.logarithm_quadratic, PARTS, 3, "INAU", PRIMITIVE),
    (antiderivatives.linear_sine_exponential, PARTS, 3, "INAV", PRIMITIVE),
    (antiderivatives.arccot_linear, PARTS, 2, "INAW", PRIMITIVE),
    (antiderivatives.cosine_root, BASIC, 3, "INAX", PRIMITIVE),
    (antiderivatives.root_over_x, BASIC, 4, "INAY", PRIMITIVE),
    (antiderivatives.cosine_over_root_sine, BASIC, 3, "INAZ", PRIMITIVE),
    (antiderivatives.sine_of_quadratic, BASIC, 2, "INBA", PRIMITIVE),
    (antiderivatives.reciprocal_cosh, BASIC, 4, "INBB", PRIMITIVE),
    (antiderivatives.linear_power, BASIC, 2, "INBC", PRIMITIVE),
    (antiderivatives.fifth_root, BASIC, 3, "INBD", PRIMITIVE),
    (antiderivatives.reciprocal_root_sum, BASIC, 3, "INBE", PRIMITIVE),
    (antiderivatives.logarithm_power, BASIC, 2, "INBF", PRIMITIVE),
    (antiderivatives.exponential_arctan, BASIC, 3, "INBG", PRIMITIVE),
    (antiderivatives.sine_over_cosine, BASIC, 3, "INBH", PRIMITIVE),
    (antiderivatives.cubic_exponential, BASIC, 4, "INBI", PRIMITIVE),
    (antiderivatives.root_over_linear, BASIC, 3, "INBJ", PRIMITIVE),
    (antiderivatives.logarithm_arctan, BASIC, 4, "INBK", PRIMITIVE),
    (antiderivatives.sine_cosine_arctan, BASIC, 5, "INBL", PRIMITIVE),
    (antiderivatives.root_quotient_value, BASIC, 4, "INBM", LINE),
)


class LimitParams(Drawn):
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=1, le=5)
    c: int = Field(ge=1, le=5)


@lru_cache(maxsize=8192)
def build_form(evaluate: Callable[[int, int, int], Built], a: int, b: int, c: int) -> Built:
    return evaluate(a, b, c)


@dataclass(frozen=True, slots=True)
class AnalysisLimits:
    evaluate: Callable[[int, int, int], Built]
    topic: str
    difficulty: int
    prefix: str
    contract: InputContract | None
    code_version = 1
    params = LimitParams
    requires: tuple[str, ...] = ()

    @property
    def family(self) -> str:
        if self.evaluate.__module__.endswith("_antiderivatives"):
            stem = "analysis1-integrals-"
        elif self.topic == DERIVATIVES:
            stem = "analysis1-derivatives-"
        else:
            stem = "analysis1-limits-"
        return stem + self.evaluate.__name__.replace("_", "-")

    @property
    def version(self) -> str:
        return self.family + "-v1"

    @property
    def answer(self) -> type[Answer]:
        if self.contract is None:
            return AntiderivativeAnswer
        return ANSWERS[self.contract.kind]

    @property
    def step_text(self) -> dict[str, str]:
        return {
            "method": "Identify the applicable definition or method.",
            "calculation": "Work with the given parameters.",
            "result": "Read off the exact result.",
        }

    def draw(self, seed: int) -> LimitParams:
        rng = DeterministicRNG(seed)
        return LimitParams(
            seed=seed, a=1 + rng.randbelow(5), b=1 + rng.randbelow(5), c=1 + rng.randbelow(5)
        )

    def input_contract(self, params: LimitParams) -> InputContract:
        return self.contract

    def build(self, params: LimitParams) -> Task:
        built = build_form(self.evaluate, params.a, params.b, params.c)
        return Task(
            built.statement,
            built.steps,
            built.answer,
            {"difficulty": self.difficulty},
            encode(self.prefix, self.code_version, params.seed),
            self.version,
        )

    def solution_visual(self, params: LimitParams) -> dict[str, Any] | None:
        from app.engine.generators._limit_visuals import diagrams

        diagram = diagrams.get(self.evaluate)
        if diagram is None:
            return None
        return diagram(params.a, params.b, params.c)


def generators() -> tuple[AnalysisLimits, ...]:
    return tuple(AnalysisLimits(*spec) for spec in SPECS)
