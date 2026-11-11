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
from app.engine.answers.logic import LogicAnswer
from app.engine.codes import encode
from app.engine.generators import _alternating_power_series as alternating_power_series
from app.engine.generators import _antiderivatives as antiderivatives
from app.engine.generators import _applied_optimization as applied_optimization
from app.engine.generators import _convexity as convexity
from app.engine.generators import _definite_integrals as definite_integrals
from app.engine.generators import _derivatives as derivatives
from app.engine.generators import _double_integrals as double_integrals
from app.engine.generators import _extrema as extrema
from app.engine.generators import _function_limits as functions
from app.engine.generators import _global_extrema as global_extrema
from app.engine.generators import _gradient_directional as gradient_directional
from app.engine.generators import _improper_integrals as improper_integrals
from app.engine.generators import _integral_applications as integral_applications
from app.engine.generators import _inverse_laplace as inverse_laplace
from app.engine.generators import _laplace_transforms as laplace_transforms
from app.engine.generators import _lhopital as lhopital
from app.engine.generators import _linear_odes as linear_odes
from app.engine.generators import _maclaurin_expansions as maclaurin_expansions
from app.engine.generators import _multivariable_domains as multivariable_domains
from app.engine.generators import _multivariable_extrema as multivariable_extrema
from app.engine.generators import _multivariable_partials as multivariable_partials
from app.engine.generators import _polar_integrals as polar_integrals
from app.engine.generators import _rational_antiderivatives as rational_antiderivatives
from app.engine.generators import _revolution_applications as revolution_applications
from app.engine.generators import _second_partials as second_partials
from app.engine.generators import _separable_odes as separable_odes
from app.engine.generators import _sequence_limits as sequences
from app.engine.generators import _series_comparisons as series_comparisons
from app.engine.generators import _series_identities as series_identities
from app.engine.generators import _series_ratio_root as series_ratio_root
from app.engine.generators import _surface_centroid_inertia as surface_centroid_inertia
from app.engine.generators import _tangent_linear as tangent_linear
from app.engine.generators import _taylor as taylor
from app.engine.generators import _trig_antiderivatives as trig_antiderivatives
from app.engine.generators._elementary_common import Built
from app.engine.models import Answer, Drawn, Task
from app.engine.prng import DeterministicRNG
from app.math_input.contracts import InputContract

LIMIT = InputContract("limit_result")
CONSTANT = InputContract("formula")
VOLUME_SURFACE = InputContract(
    "tuple", components=(CONSTANT, CONSTANT), labels=("Volume", "Lateral surface area")
)
IMPROPER_CONVERGENCE = InputContract("category", choices=improper_integrals.CONVERGENCE)
SURFACE_FINITUDE = InputContract("category", choices=improper_integrals.FINITUDE)
IMPROPER_VALUE = InputContract(
    "tuple", components=(IMPROPER_CONVERGENCE, LIMIT), labels=improper_integrals.VALUE_LABELS
)
IMPROPER_TAILS = InputContract(
    "tuple",
    components=(IMPROPER_CONVERGENCE, LIMIT, LIMIT, LIMIT),
    labels=improper_integrals.TAIL_LABELS,
)
PARTIAL_ONE = InputContract(
    "tuple",
    components=(CONSTANT, IMPROPER_CONVERGENCE, LIMIT),
    labels=series_comparisons.PARTIAL_ONE_LABELS,
)
PARTIAL_TWO = InputContract(
    "tuple",
    components=(CONSTANT, CONSTANT, IMPROPER_CONVERGENCE, LIMIT),
    labels=series_comparisons.PARTIAL_TWO_LABELS,
)
SERIES_TEST = InputContract(
    "tuple", components=(LIMIT, IMPROPER_CONVERGENCE), labels=series_ratio_root.TEST_LABELS
)
ABSOLUTE_CLASSIFICATION = InputContract(
    "category", choices=alternating_power_series.ABSOLUTE_CHOICES
)
SERIES_COEFFICIENTS = InputContract(
    "tuple",
    components=(CONSTANT, CONSTANT, InputContract("real_set")),
    labels=maclaurin_expansions.COEFFICIENT_LABELS,
)
PARTIAL_XY = InputContract("formula", symbols=multivariable_partials.XY)
PARTIAL_XYZ = InputContract("formula", symbols=multivariable_partials.XYZ)
PARTIAL_VALUES = InputContract(
    "tuple", components=(CONSTANT, CONSTANT), labels=multivariable_partials.PARTIALS
)
FIRST_PARTIALS = InputContract(
    "tuple", components=(PARTIAL_XY, PARTIAL_XY), labels=multivariable_partials.PARTIALS
)
THREE_PARTIALS = InputContract(
    "tuple",
    components=(PARTIAL_XYZ, PARTIAL_XYZ, PARTIAL_XYZ),
    labels=multivariable_partials.TRIPLE_PARTIALS,
)
EULER_PARTIALS = InputContract(
    "tuple", components=(PARTIAL_XY, PARTIAL_XY, CONSTANT), labels=multivariable_partials.EULER
)
TANGENT_PLANE = InputContract(
    "tuple", components=(CONSTANT, CONSTANT, CONSTANT), labels=tangent_linear.PLANE
)
TANGENT_CONTACT = InputContract(
    "tuple", components=(CONSTANT, CONSTANT, CONSTANT), labels=tangent_linear.CONTACT
)
LINEAR_ESTIMATE = InputContract(
    "tuple", components=(CONSTANT, CONSTANT), labels=tangent_linear.LINEAR
)
DIRECTIONAL_QUOTIENTS = InputContract(
    "tuple", components=(LIMIT, LIMIT, LIMIT), labels=gradient_directional.QUOTIENTS
)
GRADIENT_XY = InputContract(
    "tuple", components=(CONSTANT, CONSTANT), labels=gradient_directional.GRADIENT_XY
)
GRADIENT_XYZ = InputContract(
    "tuple", components=(CONSTANT,) * 3, labels=gradient_directional.GRADIENT_XYZ
)
ZERO_DIRECTION = InputContract(
    "tuple", components=(CONSTANT, CONSTANT), labels=gradient_directional.ZERO_DIRECTION
)
EXTREME_DIRECTIONS = InputContract(
    "tuple", components=(CONSTANT,) * 5, labels=gradient_directional.EXTREME_DIRECTIONS
)
HESSIAN_2D = InputContract("tuple", components=(PARTIAL_XY,) * 3, labels=second_partials.HESSIAN_2D)
HESSIAN_3D = InputContract(
    "tuple", components=(PARTIAL_XYZ,) * 6, labels=second_partials.HESSIAN_3D
)
HESSIAN_X = InputContract("tuple", components=(PARTIAL_XYZ,) * 2, labels=second_partials.HESSIAN_X)
HESSIAN_Y = InputContract("tuple", components=(PARTIAL_XYZ,) * 2, labels=second_partials.HESSIAN_Y)
HESSIAN_Z = InputContract("tuple", components=(PARTIAL_XYZ,) * 2, labels=second_partials.HESSIAN_Z)
LAPLACIAN = InputContract(
    "tuple", components=(PARTIAL_XY, PARTIAL_XY, CONSTANT), labels=second_partials.LAPLACE
)
MV_MINIMUM = InputContract(
    "tuple", components=(CONSTANT,) * 3, labels=multivariable_extrema.MINIMUM
)
MV_MAXIMUM = InputContract(
    "tuple", components=(CONSTANT,) * 3, labels=multivariable_extrema.MAXIMUM
)
MV_EXTREMA = InputContract(
    "tuple", components=(CONSTANT,) * 6, labels=multivariable_extrema.EXTREMA
)
MV_STATIONARY = InputContract(
    "tuple",
    components=(CONSTANT, CONSTANT, InputContract("category", choices=multivariable_extrema.TYPES)),
    labels=multivariable_extrema.STATIONARY,
)
MV_PARABOLA = InputContract(
    "tuple", components=(CONSTANT,) * 8, labels=multivariable_extrema.PARABOLA_EXTREMA
)
MV_TWO_MINIMA = InputContract("tuple", components=(CONSTANT,) * 8, labels=global_extrema.TWO_MINIMA)
MV_TWO_MAXIMA = InputContract("tuple", components=(CONSTANT,) * 8, labels=global_extrema.TWO_MAXIMA)
OPTIMUM_DIMENSIONS = InputContract(
    "tuple", components=(CONSTANT,) * 4, labels=applied_optimization.DIMENSIONS
)
OPTIMUM_PROFIT = InputContract(
    "tuple", components=(CONSTANT,) * 3, labels=applied_optimization.PROFIT
)
CLOSEST_POINT = InputContract(
    "tuple", components=(CONSTANT,) * 3, labels=applied_optimization.CLOSEST
)
X_BOUND = InputContract("formula", symbols=(("x", "real"),))
Y_BOUND = InputContract("formula", symbols=(("y", "real"),))
X_BOUNDS = InputContract(
    "tuple",
    components=(CONSTANT, CONSTANT, X_BOUND, X_BOUND),
    labels=double_integrals.BOUND_LABELS,
)
Y_BOUNDS = InputContract(
    "tuple",
    components=(CONSTANT, CONSTANT, Y_BOUND, Y_BOUND),
    labels=double_integrals.BOUND_LABELS,
)
Y_BOUNDS_TWO = InputContract(
    "tuple", components=(Y_BOUNDS,) * 2, labels=double_integrals.PIECES[:2]
)
Y_BOUNDS_THREE = InputContract("tuple", components=(Y_BOUNDS,) * 3, labels=double_integrals.PIECES)
X_BOUNDS_THREE = InputContract("tuple", components=(X_BOUNDS,) * 3, labels=double_integrals.PIECES)
CENTROID = InputContract(
    "tuple", components=(CONSTANT, CONSTANT), labels=surface_centroid_inertia.CENTROID
)
INERTIA = InputContract("formula", symbols=surface_centroid_inertia.MASS)
ELLIPSE_INERTIA = InputContract(
    "tuple", components=(INERTIA, INERTIA), labels=surface_centroid_inertia.INERTIA
)
TIME_FORMULA = InputContract("formula", symbols=(("t", "real"),))
DEPENDENT_FORMULA = InputContract("formula", symbols=(("y", "real"),))
SET_VALUE = InputContract("real_set")
DECAY_FIT = InputContract("tuple", components=(CONSTANT,) * 2, labels=separable_odes.DECAY_FIT)
HALF_LIFE = InputContract("tuple", components=(CONSTANT,) * 2, labels=separable_odes.HALF_LIFE)
DECAY_PERCENT = InputContract(
    "tuple", components=(CONSTANT,) * 3, labels=separable_odes.DECAY_PERCENT
)
ODE_GENERAL = InputContract(
    "tuple", components=(TIME_FORMULA, SET_VALUE, SET_VALUE), labels=separable_odes.GENERAL
)
ODE_JUNCTION = InputContract(
    "tuple", components=(*ODE_GENERAL.components, SET_VALUE), labels=separable_odes.JUNCTION
)
ODE_IVP = InputContract("tuple", components=(TIME_FORMULA, SET_VALUE), labels=separable_odes.IVP)
ODE_IMPLICIT_IVP = InputContract(
    "tuple",
    components=(DEPENDENT_FORMULA, TIME_FORMULA, CONSTANT, SET_VALUE),
    labels=separable_odes.IMPLICIT_IVP,
)
ODE_WAITING = InputContract(
    "tuple", components=(TIME_FORMULA, X_BOUND, SET_VALUE, SET_VALUE), labels=separable_odes.WAITING
)
ODE_LINEAR = InputContract(
    "tuple",
    components=(TIME_FORMULA, TIME_FORMULA, SET_VALUE, SET_VALUE),
    labels=linear_odes.LINEAR_FAMILY,
)
ODE_TANGENT = InputContract(
    "tuple",
    components=(TIME_FORMULA, TIME_FORMULA, SET_VALUE, TIME_FORMULA, TIME_FORMULA),
    labels=linear_odes.TANGENT_FAMILY,
)
LAPLACE_FORMULA = InputContract("formula", symbols=(("s", "real"),))
LAPLACE_TRANSFORM = InputContract(
    "tuple", components=(LAPLACE_FORMULA, SET_VALUE), labels=laplace_transforms.TRANSFORM
)
LAPLACE_COMPACT = InputContract(
    "tuple", components=(LAPLACE_FORMULA, CONSTANT, SET_VALUE), labels=laplace_transforms.COMPACT
)
LAPLACE_RESPONSE = InputContract(
    "tuple", components=(TIME_FORMULA, SET_VALUE), labels=inverse_laplace.RESPONSE
)
NATURAL_REGION = InputContract("logic", choices=multivariable_domains.ATOMS)
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
    "logic": LogicAnswer,
}

SEQUENCES = "functions-and-sequences"
FUNCTIONS = "limits-and-continuity"
DERIVATIVES = "differential-calculus"
BASIC = "basic-integrals"
PARTS = "integration-by-parts"
SUBSTITUTION = "substitution"
RATIONAL = "rational-functions"
TRIGONOMETRIC = "trigonometric-integrals"
DEFINITE = "definite-integrals"
IMPROPER = "improper-integrals"
SERIES = "series"
MULTIVARIABLE = "multivariable-functions"
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
    (antiderivatives.double_angle_quotient, BASIC, 3, "INAD", PRIMITIVE),
    (antiderivatives.root_powers, BASIC, 2, "INAE", PRIMITIVE),
    (antiderivatives.exponential_product, BASIC, 2, "INAF", PRIMITIVE),
    (antiderivatives.linear_exponential, PARTS, 1, "INAG", PRIMITIVE),
    (antiderivatives.square_exponential, PARTS, 2, "INAH", PRIMITIVE),
    (antiderivatives.root_arctan, PARTS, 3, "INAI", PRIMITIVE),
    (antiderivatives.secant_square, PARTS, 2, "INAJ", PRIMITIVE),
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
    (antiderivatives.cosine_root, SUBSTITUTION, 3, "INAX", PRIMITIVE),
    (antiderivatives.root_over_x, SUBSTITUTION, 4, "INAY", PRIMITIVE),
    (antiderivatives.cosine_over_root_sine, SUBSTITUTION, 3, "INAZ", PRIMITIVE),
    (antiderivatives.sine_of_quadratic, SUBSTITUTION, 2, "INBA", PRIMITIVE),
    (antiderivatives.reciprocal_cosh, SUBSTITUTION, 4, "INBB", PRIMITIVE),
    (antiderivatives.linear_power, SUBSTITUTION, 2, "INBC", PRIMITIVE),
    (antiderivatives.fifth_root, SUBSTITUTION, 3, "INBD", PRIMITIVE),
    (antiderivatives.reciprocal_root_sum, SUBSTITUTION, 3, "INBE", PRIMITIVE),
    (antiderivatives.logarithm_power, SUBSTITUTION, 2, "INBF", PRIMITIVE),
    (antiderivatives.exponential_arctan, SUBSTITUTION, 3, "INBG", PRIMITIVE),
    (antiderivatives.sine_over_cosine, SUBSTITUTION, 3, "INBH", PRIMITIVE),
    (antiderivatives.cubic_exponential, SUBSTITUTION, 4, "INBI", PRIMITIVE),
    (antiderivatives.root_over_linear, SUBSTITUTION, 3, "INBJ", PRIMITIVE),
    (antiderivatives.logarithm_arctan, SUBSTITUTION, 4, "INBK", PRIMITIVE),
    (antiderivatives.sine_cosine_arctan, SUBSTITUTION, 5, "INBL", PRIMITIVE),
    (antiderivatives.root_quotient_value, SUBSTITUTION, 4, "INBM", LINE),
    # #266
    (rational_antiderivatives.linear_high_power, RATIONAL, 2, "INBN", PRIMITIVE),
    (rational_antiderivatives.shifted_log, RATIONAL, 1, "INBO", PRIMITIVE),
    (rational_antiderivatives.decreasing_linear_power, RATIONAL, 2, "INBP", PRIMITIVE),
    (rational_antiderivatives.scaled_linear_log, RATIONAL, 1, "INBQ", PRIMITIVE),
    (rational_antiderivatives.quadratic_arctangent, RATIONAL, 2, "INBR", PRIMITIVE),
    (rational_antiderivatives.quadratic_logarithm, RATIONAL, 2, "INBS", PRIMITIVE),
    (rational_antiderivatives.quadratic_log_and_arctangent, RATIONAL, 3, "INBT", PRIMITIVE),
    (rational_antiderivatives.nonmonic_quadratic, RATIONAL, 3, "INBU", PRIMITIVE),
    (rational_antiderivatives.distinct_linear_factors, RATIONAL, 3, "INBV", PRIMITIVE),
    (rational_antiderivatives.divide_by_linear, RATIONAL, 3, "INBW", PRIMITIVE),
    (rational_antiderivatives.repeated_linear_factor, RATIONAL, 4, "INBX", PRIMITIVE),
    (rational_antiderivatives.divide_by_difference_of_squares, RATIONAL, 5, "INBY", PRIMITIVE),
    (rational_antiderivatives.distinct_quadratic_factors, RATIONAL, 4, "INBZ", PRIMITIVE),
    (rational_antiderivatives.nonmonic_logarithm, RATIONAL, 2, "INCA", PRIMITIVE),
    (rational_antiderivatives.positive_quadratic_reciprocal, RATIONAL, 2, "INCB", PRIMITIVE),
    (rational_antiderivatives.three_linear_factors, RATIONAL, 4, "INCC", PRIMITIVE),
    (rational_antiderivatives.decreasing_quadratic_numerator, RATIONAL, 3, "INCD", PRIMITIVE),
    (rational_antiderivatives.divide_by_irreducible_quadratic, RATIONAL, 5, "INCE", PRIMITIVE),
    (rational_antiderivatives.linear_times_irreducible_quadratic, RATIONAL, 4, "INCF", PRIMITIVE),
    (rational_antiderivatives.quartic_via_square, RATIONAL, 5, "INCG", PRIMITIVE),
    (rational_antiderivatives.mixed_cubic_exam, RATIONAL, 5, "INCH", PRIMITIVE),
    (rational_antiderivatives.difference_of_squares_log_exam, RATIONAL, 3, "INCI", PRIMITIVE),
    # #267
    (trig_antiderivatives.odd_sine_cube, TRIGONOMETRIC, 2, "INCJ", PRIMITIVE),
    (trig_antiderivatives.even_sine_odd_cosine, TRIGONOMETRIC, 3, "INCK", PRIMITIVE),
    (trig_antiderivatives.shifted_cosine_fourth, TRIGONOMETRIC, 3, "INCL", PRIMITIVE),
    (trig_antiderivatives.odd_sine_even_cosine, TRIGONOMETRIC, 3, "INCM", PRIMITIVE),
    (trig_antiderivatives.cosine_square_double_angle, TRIGONOMETRIC, 4, "INCN", PRIMITIVE),
    (trig_antiderivatives.product_of_sine_squares, TRIGONOMETRIC, 5, "INCO", PRIMITIVE),
    (trig_antiderivatives.reciprocal_sine, TRIGONOMETRIC, 3, "INCP", PRIMITIVE),
    (trig_antiderivatives.secant_plus_secant_tangent, TRIGONOMETRIC, 4, "INCQ", PRIMITIVE),
    (trig_antiderivatives.cancel_sine_square, TRIGONOMETRIC, 2, "INCR", PRIMITIVE),
    (trig_antiderivatives.reciprocal_cosine_quadratic, TRIGONOMETRIC, 4, "INCS", PRIMITIVE),
    (trig_antiderivatives.reciprocal_one_minus_tangent, TRIGONOMETRIC, 4, "INCT", PRIMITIVE),
    (trig_antiderivatives.odd_sine_over_cosine_cube, TRIGONOMETRIC, 4, "INCU", PRIMITIVE),
    (trig_antiderivatives.reciprocal_sine_plus_tangent, TRIGONOMETRIC, 5, "INCV", PRIMITIVE),
    (trig_antiderivatives.reciprocal_sine_plus_cosine, TRIGONOMETRIC, 4, "INCW", PRIMITIVE),
    (trig_antiderivatives.pythagorean_trig_denominator, TRIGONOMETRIC, 5, "INCX", PRIMITIVE),
    (trig_antiderivatives.sine_fourth_exam, TRIGONOMETRIC, 3, "INCY", PRIMITIVE),
    # #268
    (definite_integrals.root_and_reciprocal_root, DEFINITE, 2, "INCZ", CONSTANT),
    (definite_integrals.linear_quotient_value, DEFINITE, 3, "INDA", CONSTANT),
    (definite_integrals.arctangent_value, DEFINITE, 2, "INDB", CONSTANT),
    (definite_integrals.polynomial_product_value, DEFINITE, 1, "INDC", CONSTANT),
    (definite_integrals.reciprocal_powers_value, DEFINITE, 2, "INDD", CONSTANT),
    (definite_integrals.tangent_square_value, DEFINITE, 3, "INDE", CONSTANT),
    (definite_integrals.riemann_power, DEFINITE, 2, "INDF", CONSTANT),
    (definite_integrals.riemann_cosine, DEFINITE, 3, "INDG", CONSTANT),
    (definite_integrals.riemann_shifted_root, DEFINITE, 3, "INDH", CONSTANT),
    (definite_integrals.parts_linear_exponential_value, DEFINITE, 2, "INDI", CONSTANT),
    (definite_integrals.parts_square_exponential_value, DEFINITE, 3, "INDJ", CONSTANT),
    (definite_integrals.parts_logarithm_reciprocal_square, DEFINITE, 3, "INDK", CONSTANT),
    (definite_integrals.parts_linear_sine_value, DEFINITE, 3, "INDL", CONSTANT),
    (definite_integrals.parts_linear_one_plus_cosine, DEFINITE, 3, "INDM", CONSTANT),
    (definite_integrals.parts_arcsine_value, DEFINITE, 4, "INDN", CONSTANT),
    (definite_integrals.substitute_cosine_value, DEFINITE, 3, "INDO", CONSTANT),
    (definite_integrals.substitute_shifted_root_denominator, DEFINITE, 3, "INDP", CONSTANT),
    (definite_integrals.substitute_shifted_root_product, DEFINITE, 3, "INDQ", CONSTANT),
    (definite_integrals.substitute_logarithm_value, DEFINITE, 4, "INDR", CONSTANT),
    (definite_integrals.substitute_square_at_endpoint, DEFINITE, 5, "INDS", CONSTANT),
    (definite_integrals.substitute_quarter_circle, DEFINITE, 4, "INDT", CONSTANT),
    (definite_integrals.substitute_exponential_value, DEFINITE, 3, "INDU", CONSTANT),
    (definite_integrals.parts_linear_cosine_exam, DEFINITE, 3, "INDV", CONSTANT),
    # #269
    (integral_applications.parabola_and_line, DEFINITE, 3, "INDW", CONSTANT),
    (integral_applications.two_parabolas_and_ray, DEFINITE, 4, "INDX", CONSTANT),
    (integral_applications.inverse_square_and_line, DEFINITE, 4, "INDY", CONSTANT),
    (integral_applications.rational_cap_and_horizontal, DEFINITE, 3, "INDZ", CONSTANT),
    (integral_applications.exponential_and_horizontal, DEFINITE, 3, "INEA", CONSTANT),
    (integral_applications.sine_lobe_area, DEFINITE, 4, "INEB", CONSTANT),
    (integral_applications.meeting_root_arcs, DEFINITE, 4, "INEC", CONSTANT),
    (integral_applications.inverse_fourth_between_levels, DEFINITE, 4, "INED", CONSTANT),
    (integral_applications.logarithmic_arch, DEFINITE, 4, "INEE", CONSTANT),
    (integral_applications.root_sum_with_axes, DEFINITE, 4, "INEF", CONSTANT),
    (integral_applications.parabola_and_rational_cap, DEFINITE, 4, "INEG", CONSTANT),
    (integral_applications.logarithm_and_two_lines, DEFINITE, 3, "INEH", CONSTANT),
    (integral_applications.circle_between_horizontal_lines, DEFINITE, 4, "INEI", CONSTANT),
    (integral_applications.two_exponentials_and_level, DEFINITE, 4, "INEJ", CONSTANT),
    (integral_applications.unbounded_tangent_cotangent, DEFINITE, 5, "INEK", LIMIT),
    (integral_applications.logarithmic_exponential_arc, DEFINITE, 5, "INEL", CONSTANT),
    (integral_applications.parabola_arc, DEFINITE, 4, "INEM", CONSTANT),
    (integral_applications.three_halves_power_arc, DEFINITE, 3, "INEN", CONSTANT),
    (integral_applications.exponential_arc, DEFINITE, 5, "INEO", CONSTANT),
    (integral_applications.reciprocal_power_arc, DEFINITE, 4, "INEP", CONSTANT),
    (integral_applications.logarithm_cosine_arc, DEFINITE, 4, "INEQ", CONSTANT),
    (integral_applications.spring_work, DEFINITE, 2, "INER", CONSTANT),
    (integral_applications.horizontal_tank_work, DEFINITE, 5, "INES", CONSTANT),
    (integral_applications.two_phase_motion, DEFINITE, 3, "INET", CONSTANT),
    (integral_applications.approaching_particles, DEFINITE, 4, "INEU", CONSTANT),
    (integral_applications.root_line_axis_exam, DEFINITE, 4, "INEV", CONSTANT),
    (integral_applications.sideways_parabola_line_exam, DEFINITE, 3, "INEW", CONSTANT),
    (integral_applications.two_parabolas_exam, DEFINITE, 3, "INEX", CONSTANT),
    (integral_applications.parabola_tangent_axes_exam, DEFINITE, 5, "INEY", CONSTANT),
    (integral_applications.cubic_tangent_axis_exam, DEFINITE, 4, "INEZ", CONSTANT),
    (integral_applications.logarithm_and_square_exam, DEFINITE, 4, "INFA", CONSTANT),
    # #270
    (revolution_applications.parabolic_disc_volume, DEFINITE, 3, "INFB", CONSTANT),
    (revolution_applications.reciprocal_root_shell_volume, DEFINITE, 3, "INFC", CONSTANT),
    (revolution_applications.tangent_disc_volume, DEFINITE, 3, "INFD", CONSTANT),
    (revolution_applications.power_root_shell_volume, DEFINITE, 4, "INFE", CONSTANT),
    (revolution_applications.cubic_shell_volume, DEFINITE, 3, "INFF", CONSTANT),
    (revolution_applications.reciprocal_shell_volume, DEFINITE, 3, "INFG", CONSTANT),
    (revolution_applications.line_reciprocal_washers, DEFINITE, 4, "INFH", CONSTANT),
    (revolution_applications.sine_cosine_disc_volume, DEFINITE, 4, "INFI", CONSTANT),
    (revolution_applications.sine_shifted_horizontal_volume, DEFINITE, 4, "INFJ", CONSTANT),
    (revolution_applications.parabola_shifted_vertical_volume, DEFINITE, 4, "INFK", CONSTANT),
    (revolution_applications.cosine_surface, DEFINITE, 4, "INFL", CONSTANT),
    (revolution_applications.square_root_surface, DEFINITE, 4, "INFM", CONSTANT),
    (revolution_applications.logarithm_vertical_surface, DEFINITE, 4, "INFN", CONSTANT),
    (revolution_applications.corner_vertical_surface, DEFINITE, 3, "INFO", CONSTANT),
    (revolution_applications.sphere_belt_surface, DEFINITE, 3, "INFP", CONSTANT),
    (revolution_applications.root_cubic_surface, DEFINITE, 5, "INFQ", CONSTANT),
    (revolution_applications.line_vertical_surface, DEFINITE, 3, "INFR", CONSTANT),
    (revolution_applications.parabola_vertical_surface, DEFINITE, 4, "INFS", CONSTANT),
    (revolution_applications.sine_line_volume_exam, DEFINITE, 4, "INFT", CONSTANT),
    (revolution_applications.sine_volume_and_surface_exam, DEFINITE, 5, "INFU", VOLUME_SURFACE),
    (revolution_applications.torus_shell_volume, DEFINITE, 5, "INFV", CONSTANT),
    # #271
    (improper_integrals.rational_tail_definition, IMPROPER, 2, "IPAA", IMPROPER_VALUE),
    (improper_integrals.root_quotient_divergence, IMPROPER, 2, "IPAB", IMPROPER_VALUE),
    (improper_integrals.oscillatory_linear_tail, IMPROPER, 4, "IPAC", IMPROPER_VALUE),
    (improper_integrals.exponential_root_tail, IMPROPER, 3, "IPAD", IMPROPER_VALUE),
    (improper_integrals.two_sided_quadratic_tail, IMPROPER, 3, "IPAE", IMPROPER_TAILS),
    (improper_integrals.two_sided_exponential_linear, IMPROPER, 4, "IPAF", IMPROPER_TAILS),
    (improper_integrals.root_product_comparison, IMPROPER, 3, "IPAG", IMPROPER_CONVERGENCE),
    (
        improper_integrals.squared_root_denominator_comparison,
        IMPROPER,
        3,
        "IPAH",
        IMPROPER_CONVERGENCE,
    ),
    (improper_integrals.polynomial_quotient_comparison, IMPROPER, 3, "IPAI", IMPROPER_CONVERGENCE),
    (improper_integrals.exponential_ratio_comparison, IMPROPER, 3, "IPAJ", IMPROPER_CONVERGENCE),
    (
        improper_integrals.oscillatory_numerator_comparison,
        IMPROPER,
        3,
        "IPAK",
        IMPROPER_CONVERGENCE,
    ),
    (
        improper_integrals.bounded_numerator_root_comparison,
        IMPROPER,
        3,
        "IPAL",
        IMPROPER_CONVERGENCE,
    ),
    (improper_integrals.root_linear_limit_comparison, IMPROPER, 4, "IPAM", IMPROPER_CONVERGENCE),
    (
        improper_integrals.quintic_square_root_limit_comparison,
        IMPROPER,
        4,
        "IPAN",
        IMPROPER_CONVERGENCE,
    ),
    (
        improper_integrals.exponential_reciprocal_limit_comparison,
        IMPROPER,
        4,
        "IPAO",
        IMPROPER_CONVERGENCE,
    ),
    (improper_integrals.squared_sine_limit_comparison, IMPROPER, 4, "IPAP", IMPROPER_CONVERGENCE),
    (
        improper_integrals.cubic_oscillatory_limit_comparison,
        IMPROPER,
        4,
        "IPAQ",
        IMPROPER_CONVERGENCE,
    ),
    (improper_integrals.unbounded_quadratic_area, IMPROPER, 4, "IPAR", CONSTANT),
    (improper_integrals.unbounded_exponential_volume, IMPROPER, 4, "IPAS", CONSTANT),
    (improper_integrals.surface_finitude_comparison, IMPROPER, 5, "IPAT", SURFACE_FINITUDE),
    # #272
    (series_comparisons.geometric_partial_sums, SERIES, 2, "SRAA", PARTIAL_ONE),
    (series_comparisons.rational_telescoping_partial_sums, SERIES, 3, "SRAB", PARTIAL_TWO),
    (series_comparisons.factorial_telescoping_partial_sums, SERIES, 3, "SRAC", PARTIAL_TWO),
    (series_comparisons.root_telescoping_partial_sums, SERIES, 3, "SRAD", PARTIAL_TWO),
    (series_comparisons.quadratic_integral_test, SERIES, 3, "SRAE", IMPROPER_CONVERGENCE),
    (series_comparisons.harmonic_quotient_integral_test, SERIES, 3, "SRAF", IMPROPER_CONVERGENCE),
    (series_comparisons.logarithmic_integral_test, SERIES, 3, "SRAG", IMPROPER_CONVERGENCE),
    (series_comparisons.root_integral_test, SERIES, 3, "SRAH", IMPROPER_CONVERGENCE),
    (series_comparisons.exponential_integral_test, SERIES, 3, "SRAI", IMPROPER_CONVERGENCE),
    (series_comparisons.polynomial_direct_comparison, SERIES, 3, "SRAJ", IMPROPER_CONVERGENCE),
    (series_comparisons.root_direct_comparison, SERIES, 3, "SRAK", IMPROPER_CONVERGENCE),
    (series_comparisons.sine_direct_comparison, SERIES, 3, "SRAL", IMPROPER_CONVERGENCE),
    (series_comparisons.exponential_direct_comparison, SERIES, 3, "SRAM", IMPROPER_CONVERGENCE),
    (
        series_comparisons.harmonic_exponential_direct_comparison,
        SERIES,
        3,
        "SRAN",
        IMPROPER_CONVERGENCE,
    ),
    (series_comparisons.root_cubic_limit_comparison, SERIES, 4, "SRAO", IMPROPER_CONVERGENCE),
    (series_comparisons.rational_square_limit_comparison, SERIES, 4, "SRAP", IMPROPER_CONVERGENCE),
    (series_comparisons.exponential_limit_comparison, SERIES, 4, "SRAQ", IMPROPER_CONVERGENCE),
    (
        series_comparisons.growing_geometric_limit_comparison,
        SERIES,
        4,
        "SRAR",
        IMPROPER_CONVERGENCE,
    ),
    (series_comparisons.sine_quotient_limit_comparison, SERIES, 4, "SRAS", IMPROPER_CONVERGENCE),
    (series_comparisons.factorial_limit_comparison, SERIES, 4, "SRAT", IMPROPER_CONVERGENCE),
    # #273
    (series_ratio_root.exponential_over_multiple_factorial, SERIES, 4, "SRAU", SERIES_TEST),
    (series_ratio_root.exponential_over_polynomial, SERIES, 4, "SRAV", SERIES_TEST),
    (series_ratio_root.factorial_over_self_power, SERIES, 4, "SRAW", SERIES_TEST),
    (series_ratio_root.self_power_over_factorial, SERIES, 4, "SRAX", SERIES_TEST),
    (series_ratio_root.central_binomial_ratio, SERIES, 5, "SRAY", SERIES_TEST),
    (series_ratio_root.quadratic_self_power_root, SERIES, 5, "SRAZ", SERIES_TEST),
    (series_ratio_root.exponential_quotient_root, SERIES, 4, "SRBA", SERIES_TEST),
    (series_ratio_root.power_quotient_root, SERIES, 4, "SRBB", SERIES_TEST),
    (series_ratio_root.arctangent_power_root, SERIES, 4, "SRBC", SERIES_TEST),
    (series_ratio_root.polynomial_exponential_sequence_limit, SERIES, 5, "SRBD", LIMIT),
    (series_ratio_root.self_power_squared_factorial_limit, SERIES, 5, "SRBE", LIMIT),
    (series_ratio_root.self_power_factorial_infinite_limit, SERIES, 5, "SRBF", LIMIT),
    (series_ratio_root.balanced_factorial_sequence_limit, SERIES, 5, "SRBG", LIMIT),
    # #274
    (alternating_power_series.root_difference_leibniz, SERIES, 3, "SRBH", IMPROPER_CONVERGENCE),
    (
        alternating_power_series.exponential_quotient_leibniz,
        SERIES,
        3,
        "SRBI",
        IMPROPER_CONVERGENCE,
    ),
    (alternating_power_series.sine_reciprocal_leibniz, SERIES, 3, "SRBJ", IMPROPER_CONVERGENCE),
    (alternating_power_series.factorial_leibniz, SERIES, 3, "SRBK", IMPROPER_CONVERGENCE),
    (
        alternating_power_series.alternating_geometric_absolute,
        SERIES,
        4,
        "SRBL",
        ABSOLUTE_CLASSIFICATION,
    ),
    (
        alternating_power_series.alternating_harmonic_conditional,
        SERIES,
        4,
        "SRBM",
        ABSOLUTE_CLASSIFICATION,
    ),
    (
        alternating_power_series.negative_rational_power_classification,
        SERIES,
        4,
        "SRBN",
        ABSOLUTE_CLASSIFICATION,
    ),
    (
        alternating_power_series.alternating_exponential_conditional,
        SERIES,
        4,
        "SRBO",
        ABSOLUTE_CLASSIFICATION,
    ),
    (alternating_power_series.damped_sine_absolute, SERIES, 4, "SRBP", ABSOLUTE_CLASSIFICATION),
    (alternating_power_series.logarithmic_power_domain, SERIES, 5, "SRBQ", REAL_SET),
    (alternating_power_series.geometric_power_domain, SERIES, 5, "SRBR", REAL_SET),
    (alternating_power_series.factorial_power_domain, SERIES, 5, "SRBS", REAL_SET),
    (alternating_power_series.exponential_difference_power_domain, SERIES, 5, "SRBT", REAL_SET),
    (alternating_power_series.even_power_domain, SERIES, 5, "SRBU", REAL_SET),
    # #275
    (maclaurin_expansions.geometric_maclaurin, SERIES, 3, "SRBV", SERIES_COEFFICIENTS),
    (maclaurin_expansions.sine_maclaurin, SERIES, 3, "SRBW", SERIES_COEFFICIENTS),
    (maclaurin_expansions.polynomial_exponential_maclaurin, SERIES, 3, "SRBX", SERIES_COEFFICIENTS),
    (maclaurin_expansions.odd_rational_maclaurin, SERIES, 3, "SRBY", SERIES_COEFFICIENTS),
    (maclaurin_expansions.hyperbolic_cosine_maclaurin, SERIES, 3, "SRBZ", SERIES_COEFFICIENTS),
    (maclaurin_expansions.sine_square_maclaurin, SERIES, 4, "SRCA", SERIES_COEFFICIENTS),
    (maclaurin_expansions.cosine_high_derivative, SERIES, 4, "SRCB", CONSTANT),
    (maclaurin_expansions.exponential_high_derivative, SERIES, 4, "SRCC", CONSTANT),
    (maclaurin_expansions.rational_high_derivative, SERIES, 4, "SRCD", CONSTANT),
    (maclaurin_expansions.sine_square_high_derivative, SERIES, 4, "SRCE", CONSTANT),
    (
        maclaurin_expansions.differentiated_geometric_maclaurin,
        SERIES,
        4,
        "SRCF",
        SERIES_COEFFICIENTS,
    ),
    (
        maclaurin_expansions.differentiated_exponential_maclaurin,
        SERIES,
        4,
        "SRCG",
        SERIES_COEFFICIENTS,
    ),
    (maclaurin_expansions.integrated_logarithm_maclaurin, SERIES, 4, "SRCH", SERIES_COEFFICIENTS),
    (maclaurin_expansions.integrated_arctangent_maclaurin, SERIES, 4, "SRCI", SERIES_COEFFICIENTS),
    # #276
    (series_identities.weighted_geometric_identity, SERIES, 4, "SRCJ", LINE),
    (series_identities.quadratic_geometric_identity, SERIES, 4, "SRCK", LINE),
    (series_identities.corrected_factorial_identity, SERIES, 4, "SRCL", LINE),
    (series_identities.logarithmic_shift_sum, SERIES, 4, "SRCM", CONSTANT),
    (series_identities.linear_weighted_sum, SERIES, 4, "SRCN", CONSTANT),
    (series_identities.quadratic_weighted_sum, SERIES, 4, "SRCO", CONSTANT),
    (series_identities.weighted_logarithmic_sum, SERIES, 4, "SRCP", CONSTANT),
    # #277
    (multivariable_domains.logarithmic_sine_region, MULTIVARIABLE, 1, "MVAA", NATURAL_REGION),
    (multivariable_domains.quotient_square_root_region, MULTIVARIABLE, 2, "MVAB", NATURAL_REGION),
    (multivariable_domains.denominator_root_region, MULTIVARIABLE, 1, "MVAC", NATURAL_REGION),
    (multivariable_domains.logarithmic_annulus_region, MULTIVARIABLE, 2, "MVAD", NATURAL_REGION),
    (multivariable_domains.independent_root_region, MULTIVARIABLE, 2, "MVAE", NATURAL_REGION),
    (multivariable_domains.arccosine_shell_region, MULTIVARIABLE, 3, "MVAF", NATURAL_REGION),
    (multivariable_domains.quartic_sine_limit, MULTIVARIABLE, 3, "MVAG", LIMIT),
    (multivariable_domains.quadratic_cosine_limit, MULTIVARIABLE, 4, "MVAH", LIMIT),
    (multivariable_domains.cubic_over_quadratic_limit, MULTIVARIABLE, 3, "MVAI", LIMIT),
    (multivariable_domains.bounded_oscillation_limit, MULTIVARIABLE, 3, "MVAJ", LIMIT),
    (multivariable_partials.quotient_at_point, "partial-derivatives", 1, "MVAK", PARTIAL_VALUES),
    (multivariable_partials.radical_at_origin, "partial-derivatives", 2, "MVAL", PARTIAL_VALUES),
    (multivariable_partials.rational_partials, "partial-derivatives", 1, "MVAM", FIRST_PARTIALS),
    (
        multivariable_partials.arctangent_quotient_partials,
        "partial-derivatives",
        2,
        "MVAN",
        FIRST_PARTIALS,
    ),
    (
        multivariable_partials.exponential_cosine_partials,
        "partial-derivatives",
        2,
        "MVAO",
        FIRST_PARTIALS,
    ),
    (
        multivariable_partials.radial_product_partials,
        "partial-derivatives",
        2,
        "MVAP",
        FIRST_PARTIALS,
    ),
    (
        multivariable_partials.logarithmic_radial_partials,
        "partial-derivatives",
        3,
        "MVAQ",
        FIRST_PARTIALS,
    ),
    (
        multivariable_partials.three_variable_polynomial_quotient,
        "partial-derivatives",
        2,
        "MVAR",
        THREE_PARTIALS,
    ),
    (
        multivariable_partials.three_variable_radial_quotient,
        "partial-derivatives",
        2,
        "MVAS",
        THREE_PARTIALS,
    ),
    (
        multivariable_partials.nested_trigonometric_x,
        "partial-derivatives",
        3,
        "MVAT",
        PARTIAL_XYZ,
    ),
    (
        multivariable_partials.nested_radical_x,
        "partial-derivatives",
        4,
        "MVAU",
        PARTIAL_XYZ,
    ),
    (
        multivariable_partials.logarithmic_euler_partials,
        "partial-derivatives",
        3,
        "MVAV",
        EULER_PARTIALS,
    ),
    (
        multivariable_partials.homogeneous_euler_partials,
        "partial-derivatives",
        3,
        "MVAW",
        EULER_PARTIALS,
    ),
    (multivariable_partials.nested_trigonometric_y, "partial-derivatives", 3, "MVAX", PARTIAL_XYZ),
    (multivariable_partials.nested_trigonometric_z, "partial-derivatives", 4, "MVAY", PARTIAL_XYZ),
    (multivariable_partials.nested_radical_y, "partial-derivatives", 4, "MVAZ", PARTIAL_XYZ),
    (multivariable_partials.nested_radical_z, "partial-derivatives", 4, "MVBA", PARTIAL_XYZ),
    (tangent_linear.radical_plane, MULTIVARIABLE, 2, "MVBB", TANGENT_PLANE),
    (tangent_linear.exponential_plane, MULTIVARIABLE, 2, "MVBC", TANGENT_PLANE),
    (tangent_linear.inverse_trig_plane, MULTIVARIABLE, 3, "MVBD", TANGENT_PLANE),
    (tangent_linear.vertical_axis_plane, MULTIVARIABLE, 3, "MVBE", TANGENT_PLANE),
    (tangent_linear.horizontal_axis_plane, MULTIVARIABLE, 3, "MVBF", TANGENT_PLANE),
    (tangent_linear.parallel_plane_contact, MULTIVARIABLE, 4, "MVBG", TANGENT_CONTACT),
    (tangent_linear.perpendicular_line_plane, MULTIVARIABLE, 4, "MVBH", TANGENT_PLANE),
    (tangent_linear.power_product_approximation, MULTIVARIABLE, 2, "MVBI", LINEAR_ESTIMATE),
    (tangent_linear.cube_norm_approximation, MULTIVARIABLE, 3, "MVBJ", LINEAR_ESTIMATE),
    (tangent_linear.exponential_product_approximation, MULTIVARIABLE, 2, "MVBK", LINEAR_ESTIMATE),
    (tangent_linear.cosine_quotient_approximation, MULTIVARIABLE, 2, "MVBL", LINEAR_ESTIMATE),
    (tangent_linear.cylinder_measurement_error, MULTIVARIABLE, 3, "MVBM", CONSTANT),
    (tangent_linear.diagonal_measurement_change, MULTIVARIABLE, 3, "MVBN", CONSTANT),
    (tangent_linear.box_relative_error, MULTIVARIABLE, 3, "MVBO", CONSTANT),
    (gradient_directional.norm_at_origin, MULTIVARIABLE, 3, "MVBP", DIRECTIONAL_QUOTIENTS),
    (gradient_directional.cube_root_at_boundary, MULTIVARIABLE, 4, "MVBQ", DIRECTIONAL_QUOTIENTS),
    (gradient_directional.cubic_polynomial_gradient, MULTIVARIABLE, 1, "MVBR", GRADIENT_XY),
    (gradient_directional.nested_log_gradient, MULTIVARIABLE, 2, "MVBS", GRADIENT_XY),
    (gradient_directional.variable_power_gradient, MULTIVARIABLE, 2, "MVBT", GRADIENT_XY),
    (gradient_directional.radical_log_gradient, MULTIVARIABLE, 2, "MVBU", GRADIENT_XYZ),
    (gradient_directional.sinusoidal_quotient_gradient, MULTIVARIABLE, 2, "MVBV", GRADIENT_XYZ),
    (gradient_directional.nested_root_gradient, MULTIVARIABLE, 3, "MVBW", GRADIENT_XYZ),
    (gradient_directional.quadratic_directional, MULTIVARIABLE, 2, "MVBX", CONSTANT),
    (gradient_directional.rational_directional, MULTIVARIABLE, 2, "MVBY", CONSTANT),
    (gradient_directional.exponential_directional, MULTIVARIABLE, 3, "MVBZ", CONSTANT),
    (
        gradient_directional.logarithmic_extreme_directions,
        MULTIVARIABLE,
        4,
        "MVCA",
        EXTREME_DIRECTIONS,
    ),
    (gradient_directional.exponential_zero_directions, MULTIVARIABLE, 3, "MVCB", ZERO_DIRECTION),
    (second_partials.radial_cosine_hessian, "partial-derivatives", 3, "MVCC", HESSIAN_2D),
    (second_partials.exponential_hessian, "partial-derivatives", 3, "MVCD", HESSIAN_2D),
    (second_partials.rational_hessian, "partial-derivatives", 2, "MVCE", HESSIAN_2D),
    (second_partials.logarithmic_hessian, "partial-derivatives", 2, "MVCF", HESSIAN_2D),
    (second_partials.polynomial_hessian, "partial-derivatives", 2, "MVCG", HESSIAN_3D),
    (second_partials.nested_log_hessian_x, "partial-derivatives", 3, "MVCH", HESSIAN_X),
    (second_partials.nested_log_hessian_y, "partial-derivatives", 4, "MVCI", HESSIAN_Y),
    (second_partials.nested_log_hessian_z, "partial-derivatives", 4, "MVCJ", HESSIAN_Z),
    (second_partials.arctangent_laplacian, "partial-derivatives", 4, "MVCK", LAPLACIAN),
    (second_partials.radial_log_laplacian, "partial-derivatives", 3, "MVCL", LAPLACIAN),
    (second_partials.trigonometric_laplacian, "partial-derivatives", 3, "MVCM", LAPLACIAN),
    (multivariable_extrema.symmetric_cubic_extrema, MULTIVARIABLE, 5, "MVCN", MV_EXTREMA),
    (multivariable_extrema.reciprocal_exponential_extremum, MULTIVARIABLE, 4, "MVCO", MV_MINIMUM),
    (multivariable_extrema.positive_cubic_product_extremum, MULTIVARIABLE, 4, "MVCP", MV_MAXIMUM),
    (multivariable_extrema.square_root_extremum, MULTIVARIABLE, 4, "MVCQ", MV_MAXIMUM),
    (multivariable_extrema.coupled_cubic_extremum, MULTIVARIABLE, 4, "MVCR", MV_MINIMUM),
    (multivariable_extrema.positive_rational_extremum, MULTIVARIABLE, 4, "MVCS", MV_MINIMUM),
    (multivariable_extrema.logarithmic_saddle, MULTIVARIABLE, 4, "MVCT", MV_STATIONARY),
    (multivariable_extrema.exponential_sum_extremum, MULTIVARIABLE, 4, "MVCU", MV_MINIMUM),
    (multivariable_extrema.exponential_product_saddle, MULTIVARIABLE, 4, "MVCV", MV_STATIONARY),
    (multivariable_extrema.linear_constraint_minimum, MULTIVARIABLE, 3, "MVCW", MV_MINIMUM),
    (multivariable_extrema.parabolic_constraint_extrema, MULTIVARIABLE, 4, "MVCX", MV_PARABOLA),
    (multivariable_extrema.logarithmic_constraint_maximum, MULTIVARIABLE, 4, "MVCY", MV_MAXIMUM),
    (multivariable_extrema.circular_constraint_extrema, MULTIVARIABLE, 4, "MVCZ", MV_EXTREMA),
    (global_extrema.parabolic_cap_extrema, MULTIVARIABLE, 4, "MVDA", MV_TWO_MAXIMA),
    (global_extrema.radical_lens_extrema, MULTIVARIABLE, 4, "MVDB", MV_TWO_MINIMA),
    (global_extrema.radical_strip_extrema, MULTIVARIABLE, 3, "MVDC", MV_EXTREMA),
    (global_extrema.triangular_region_extrema, MULTIVARIABLE, 3, "MVDD", MV_EXTREMA),
    (global_extrema.quartic_disk_extrema, MULTIVARIABLE, 3, "MVDE", MV_EXTREMA),
    (global_extrema.quadrant_decay_extrema, MULTIVARIABLE, 3, "MVDF", MV_EXTREMA),
    (global_extrema.triangle_least_squares, MULTIVARIABLE, 2, "MVDG", MV_MINIMUM),
    (global_extrema.skew_line_distance, MULTIVARIABLE, 3, "MVDH", CONSTANT),
    (applied_optimization.open_tank, MULTIVARIABLE, 3, "MVDI", OPTIMUM_DIMENSIONS),
    (applied_optimization.weighted_warehouse, MULTIVARIABLE, 4, "MVDJ", OPTIMUM_DIMENSIONS),
    (applied_optimization.discrete_profit, MULTIVARIABLE, 3, "MVDK", OPTIMUM_PROFIT),
    (applied_optimization.closest_parabola, MULTIVARIABLE, 4, "MVDL", CLOSEST_POINT),
    (double_integrals.polynomial_rectangle, "double-integrals", 1, "DIAA", CONSTANT),
    (double_integrals.reciprocal_rectangle, "double-integrals", 1, "DIAB", CONSTANT),
    (double_integrals.cubic_denominator_rectangle, "double-integrals", 2, "DIAC", CONSTANT),
    (double_integrals.sine_rectangle, "double-integrals", 3, "DIAD", CONSTANT),
    (double_integrals.separable_exponential_rectangle, "double-integrals", 2, "DIAE", CONSTANT),
    (double_integrals.linear_exponential_rectangle, "double-integrals", 2, "DIAF", CONSTANT),
    (double_integrals.power_strip_integral, "double-integrals", 2, "DIAG", CONSTANT),
    (double_integrals.radical_wedge_integral, "double-integrals", 3, "DIAH", CONSTANT),
    (double_integrals.semicircle_integral, "double-integrals", 3, "DIAI", CONSTANT),
    (double_integrals.radical_triangle_integral, "double-integrals", 2, "DIAJ", CONSTANT),
    (double_integrals.absolute_value_reversal, "double-integrals", 4, "DIAK", Y_BOUNDS_THREE),
    (double_integrals.circular_strip_reversal, "double-integrals", 4, "DIAL", Y_BOUNDS_TWO),
    (double_integrals.semicircle_split_reversal, "double-integrals", 5, "DIAM", Y_BOUNDS_THREE),
    (double_integrals.two_parabola_reversal, "double-integrals", 5, "DIAN", X_BOUNDS_THREE),
    (double_integrals.trigonometric_reversal, "double-integrals", 4, "DIAO", Y_BOUNDS_TWO),
    (double_integrals.logarithmic_reversal, "double-integrals", 3, "DIAP", Y_BOUNDS),
    (double_integrals.parabola_line_integral, "double-integrals", 3, "DIAQ", CONSTANT),
    (double_integrals.negative_curves_integral, "double-integrals", 3, "DIAR", CONSTANT),
    (double_integrals.exponential_radical_integral, "double-integrals", 3, "DIAS", CONSTANT),
    (double_integrals.shifted_parabola_integral, "double-integrals", 3, "DIAT", CONSTANT),
    (double_integrals.exponential_triangle_integral, "double-integrals", 4, "DIAU", CONSTANT),
    (double_integrals.angular_strip_integral, "double-integrals", 3, "DIAV", CONSTANT),
    (double_integrals.gaussian_wedge_integral, "double-integrals", 3, "DIAW", CONSTANT),
    (double_integrals.sinusoidal_strip_integral, "double-integrals", 4, "DIAX", CONSTANT),
    (polar_integrals.sector_xy, "double-integrals", 3, "DIAY", CONSTANT),
    (polar_integrals.half_annulus_xy_squared, "double-integrals", 3, "DIAZ", CONSTANT),
    (polar_integrals.quadrant_radial_exponential, "double-integrals", 4, "DIBA", CONSTANT),
    (polar_integrals.shifted_disk_x_squared, "double-integrals", 4, "DIBB", CONSTANT),
    (polar_integrals.radial_between_disks, "double-integrals", 4, "DIBC", CONSTANT),
    (polar_integrals.lower_shifted_disk_y, "double-integrals", 3, "DIBD", CONSTANT),
    (polar_integrals.radial_sine_disk, "double-integrals", 3, "DIBE", CONSTANT),
    (polar_integrals.radial_log_annulus, "double-integrals", 3, "DIBF", CONSTANT),
    (polar_integrals.parabola_triangle_area, "double-integrals", 2, "DIBG", CONSTANT),
    (polar_integrals.nested_tangent_circles_area, "double-integrals", 3, "DIBH", CONSTANT),
    (polar_integrals.affine_parallelogram_area, "double-integrals", 3, "DIBI", CONSTANT),
    (polar_integrals.disk_wedge_area, "double-integrals", 3, "DIBJ", CONSTANT),
    (polar_integrals.sphere_paraboloid_volume, "double-integrals", 4, "DIBK", CONSTANT),
    (polar_integrals.spherical_cap_volume, "double-integrals", 3, "DIBL", CONSTANT),
    (polar_integrals.shifted_disk_paraboloid_volume, "double-integrals", 3, "DIBM", CONSTANT),
    (polar_integrals.paraboloid_slab_volume, "double-integrals", 3, "DIBN", CONSTANT),
    (polar_integrals.disk_product_volume, "double-integrals", 4, "DIBO", CONSTANT),
    (polar_integrals.plane_paraboloid_volume, "double-integrals", 4, "DIBP", CONSTANT),
    (surface_centroid_inertia.paraboloid_patch, "double-integrals", 3, "DIBQ", CONSTANT),
    (
        surface_centroid_inertia.tangent_disk_spherical_patch,
        "double-integrals",
        4,
        "DIBR",
        CONSTANT,
    ),
    (surface_centroid_inertia.conical_patch, "double-integrals", 3, "DIBS", CONSTANT),
    (surface_centroid_inertia.spherical_paraboloid_patch, "double-integrals", 4, "DIBT", CONSTANT),
    (surface_centroid_inertia.parabolic_segment_centroid, "double-integrals", 3, "DIBU", CENTROID),
    (surface_centroid_inertia.sine_square_centroid, "double-integrals", 3, "DIBV", CENTROID),
    (
        surface_centroid_inertia.exponential_bound_centroid,
        "double-integrals",
        1,
        "DIBW",
        CENTROID,
    ),
    (surface_centroid_inertia.isosceles_triangle_centroid, "double-integrals", 2, "DIBX", CENTROID),
    (
        surface_centroid_inertia.semicircle_triangle_centroid,
        "double-integrals",
        4,
        "DIBY",
        CENTROID,
    ),
    (surface_centroid_inertia.semicircle_cutout_centroid, "double-integrals", 4, "DIBZ", CENTROID),
    (surface_centroid_inertia.triangle_base_inertia, "double-integrals", 3, "DICA", INERTIA),
    (surface_centroid_inertia.parabolic_segment_inertia, "double-integrals", 3, "DICB", INERTIA),
    (surface_centroid_inertia.square_diagonal_inertia, "double-integrals", 3, "DICC", INERTIA),
    (surface_centroid_inertia.quadrant_symmetry_inertia, "double-integrals", 4, "DICD", INERTIA),
    (surface_centroid_inertia.disk_center_inertia, "double-integrals", 2, "DICE", INERTIA),
    (surface_centroid_inertia.ellipse_axes_inertia, "double-integrals", 4, "DICF", ELLIPSE_INERTIA),
    (separable_odes.two_measurements_decay, "differential-equations", 2, "ODAA", DECAY_FIT),
    (separable_odes.half_life_mass, "differential-equations", 2, "ODAB", HALF_LIFE),
    (separable_odes.half_life_percentages, "differential-equations", 2, "ODAC", DECAY_PERCENT),
    (separable_odes.circle_separable_family, "differential-equations", 3, "ODAD", ODE_GENERAL),
    (separable_odes.vanishing_factor_family, "differential-equations", 5, "ODAE", ODE_JUNCTION),
    (separable_odes.product_invariant_family, "differential-equations", 4, "ODAF", ODE_GENERAL),
    (separable_odes.arcsine_plateau_family, "differential-equations", 5, "ODAG", ODE_GENERAL),
    (separable_odes.euler_separable_family, "differential-equations", 3, "ODAH", ODE_GENERAL),
    (separable_odes.exponential_separable_family, "differential-equations", 3, "ODAI", ODE_GENERAL),
    (separable_odes.logarithm_sine_ivp, "differential-equations", 4, "ODAJ", ODE_IVP),
    (separable_odes.square_root_waiting_ivp, "differential-equations", 5, "ODAK", ODE_WAITING),
    (separable_odes.logarithm_implicit_ivp, "differential-equations", 4, "ODAL", ODE_IMPLICIT_IVP),
    (separable_odes.cosine_implicit_ivp, "differential-equations", 4, "ODAM", ODE_IMPLICIT_IVP),
    (separable_odes.reciprocal_pole_ivp, "differential-equations", 4, "ODAN", ODE_IVP),
    (separable_odes.exponential_log_ivp, "differential-equations", 3, "ODAO", ODE_IVP),
    (linear_odes.sinusoidal_forcing_family, "differential-equations", 3, "ODAP", ODE_LINEAR),
    (linear_odes.gaussian_forcing_family, "differential-equations", 3, "ODAQ", ODE_LINEAR),
    (linear_odes.cosine_euler_family, "differential-equations", 4, "ODAR", ODE_LINEAR),
    (linear_odes.power_euler_family, "differential-equations", 4, "ODAS", ODE_LINEAR),
    (linear_odes.exponential_singular_family, "differential-equations", 4, "ODAT", ODE_LINEAR),
    (linear_odes.shifted_singular_family, "differential-equations", 5, "ODAU", ODE_LINEAR),
    (linear_odes.constant_forcing_ivp, "differential-equations", 2, "ODAV", ODE_IVP),
    (linear_odes.sinusoidal_coefficient_ivp, "differential-equations", 3, "ODAW", ODE_IVP),
    (linear_odes.rational_forcing_ivp, "differential-equations", 4, "ODAX", ODE_IVP),
    (linear_odes.trigonometric_singular_ivp, "differential-equations", 4, "ODAY", ODE_IVP),
    (linear_odes.tangent_area_family, "differential-equations", 5, "ODAZ", ODE_TANGENT),
    (laplace_transforms.affine_definition, "differential-equations", 1, "LTAA", LAPLACE_TRANSFORM),
    (laplace_transforms.sine_definition, "differential-equations", 2, "LTAB", LAPLACE_TRANSFORM),
    (laplace_transforms.power_definition, "differential-equations", 2, "LTAC", LAPLACE_TRANSFORM),
    (
        laplace_transforms.decaying_linear_definition,
        "differential-equations",
        2,
        "LTAD",
        LAPLACE_TRANSFORM,
    ),
    (
        laplace_transforms.growing_cosine_definition,
        "differential-equations",
        3,
        "LTAE",
        LAPLACE_TRANSFORM,
    ),
    (
        laplace_transforms.hyperbolic_sine_definition,
        "differential-equations",
        3,
        "LTAF",
        LAPLACE_TRANSFORM,
    ),
    (
        laplace_transforms.rectangular_pulse_transform,
        "differential-equations",
        3,
        "LTAG",
        LAPLACE_COMPACT,
    ),
    (
        laplace_transforms.triangular_pulse_transform,
        "differential-equations",
        4,
        "LTAH",
        LAPLACE_COMPACT,
    ),
    (
        laplace_transforms.ramp_to_constant_transform,
        "differential-equations",
        4,
        "LTAI",
        LAPLACE_TRANSFORM,
    ),
    (
        laplace_transforms.linear_cosine_table,
        "differential-equations",
        2,
        "LTAJ",
        LAPLACE_TRANSFORM,
    ),
    (laplace_transforms.polynomial_table, "differential-equations", 2, "LTAK", LAPLACE_TRANSFORM),
    (
        laplace_transforms.shifted_affine_table,
        "differential-equations",
        3,
        "LTAL",
        LAPLACE_TRANSFORM,
    ),
    (laplace_transforms.sine_cosine_table, "differential-equations", 3, "LTAM", LAPLACE_TRANSFORM),
    (
        laplace_transforms.shifted_sine_constant_table,
        "differential-equations",
        3,
        "LTAN",
        LAPLACE_TRANSFORM,
    ),
    (
        laplace_transforms.shifted_trigonometric_table,
        "differential-equations",
        4,
        "LTAO",
        LAPLACE_TRANSFORM,
    ),
    (inverse_laplace.inverse_simple_pole, "differential-equations", 2, "LTAP", LAPLACE_RESPONSE),
    (
        inverse_laplace.inverse_shifted_numerator,
        "differential-equations",
        3,
        "LTAQ",
        LAPLACE_RESPONSE,
    ),
    (inverse_laplace.inverse_distinct_real, "differential-equations", 3, "LTAR", LAPLACE_RESPONSE),
    (
        inverse_laplace.inverse_real_and_complex,
        "differential-equations",
        4,
        "LTAS",
        LAPLACE_RESPONSE,
    ),
    (
        inverse_laplace.inverse_repeated_symmetric_poles,
        "differential-equations",
        5,
        "LTAT",
        LAPLACE_RESPONSE,
    ),
    (
        inverse_laplace.inverse_completed_square,
        "differential-equations",
        3,
        "LTAU",
        LAPLACE_RESPONSE,
    ),
    (
        inverse_laplace.laplace_constant_forcing,
        "differential-equations",
        3,
        "LTAV",
        LAPLACE_RESPONSE,
    ),
    (inverse_laplace.laplace_sine_forcing, "differential-equations", 3, "LTAW", LAPLACE_RESPONSE),
    (inverse_laplace.laplace_velocity_decay, "differential-equations", 3, "LTAX", LAPLACE_RESPONSE),
    (inverse_laplace.laplace_resonant_decay, "differential-equations", 4, "LTAY", LAPLACE_RESPONSE),
    (
        inverse_laplace.laplace_growing_oscillator,
        "differential-equations",
        5,
        "LTAZ",
        LAPLACE_RESPONSE,
    ),
    (
        inverse_laplace.laplace_affine_acceleration,
        "differential-equations",
        4,
        "LTBA",
        LAPLACE_RESPONSE,
    ),
    (inverse_laplace.laplace_repeated_root, "differential-equations", 5, "LTBB", LAPLACE_RESPONSE),
    (
        inverse_laplace.laplace_damped_exponential_forcing,
        "differential-equations",
        5,
        "LTBC",
        LAPLACE_RESPONSE,
    ),
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
        if self.evaluate.__module__.endswith(("_laplace_transforms", "_inverse_laplace")):
            stem = "analysis2-laplace-"
        elif self.evaluate.__module__.endswith(("_separable_odes", "_linear_odes")):
            stem = "analysis2-ode-"
        elif self.evaluate.__module__.endswith(
            ("_double_integrals", "_polar_integrals", "_surface_centroid_inertia")
        ):
            stem = "analysis2-double-integral-"
        elif self.evaluate.__module__.endswith(
            (
                "_multivariable_domains",
                "_multivariable_partials",
                "_tangent_linear",
                "_gradient_directional",
                "_second_partials",
                "_multivariable_extrema",
                "_global_extrema",
                "_applied_optimization",
            )
        ):
            stem = "analysis2-multivariable-"
        elif self.evaluate.__module__.endswith("_improper_integrals"):
            stem = "analysis2-improper-"
        elif self.evaluate.__module__.endswith(
            (
                "_series_comparisons",
                "_series_ratio_root",
                "_alternating_power_series",
                "_maclaurin_expansions",
                "_series_identities",
            )
        ):
            stem = "analysis2-series-"
        elif self.evaluate.__module__.endswith(
            (
                "_antiderivatives",
                "_definite_integrals",
                "_integral_applications",
                "_revolution_applications",
            )
        ):
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

    def input_contract(self, params: LimitParams) -> InputContract | None:
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

    def prompt_visual(self, params: LimitParams) -> dict[str, Any] | None:
        graph = laplace_transforms.PROMPT_GRAPHS.get(self.evaluate)
        return None if graph is None else graph(params.a, params.b, params.c)

    def solution_visual(self, params: LimitParams) -> dict[str, Any] | None:
        from app.engine.generators._limit_visuals import diagrams

        built = build_form(self.evaluate, params.a, params.b, params.c)
        if built.visual is not None:
            return built.visual
        diagram = diagrams.get(self.evaluate)
        if diagram is None:
            return None
        return diagram(params.a, params.b, params.c)


def generators() -> tuple[AnalysisLimits, ...]:
    return tuple(AnalysisLimits(*spec) for spec in SPECS)
