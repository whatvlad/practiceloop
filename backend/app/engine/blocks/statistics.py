"""Exact small-sample statistics and inference from explicitly supplied constants."""

from collections import Counter
from fractions import Fraction as F
from typing import Any, Self

import sympy as sp
from pydantic import model_validator

from app.engine.models import Parameters

# NIST e-Handbook mpc3652.htm: two-sided 5% Student critical values, 3 decimals.
T95 = {
    3: F(3182, 1000),
    4: F(2776, 1000),
    5: F(2571, 1000),
    6: F(2447, 1000),
    7: F(2365, 1000),
    8: F(2306, 1000),
    9: F(2262, 1000),
    11: F(2201, 1000),
    15: F(2131, 1000),
    24: F(2064, 1000),
}
# Finite normal reference table (NIST eda3671.htm); these rounded values are
# explicitly supplied in prompts, never treated as exact distribution identities.
NORMAL_CDF = {
    F(0): F(1, 2),
    F(1, 2): F(69146, 100000),
    F(1): F(84134, 100000),
    F(3, 2): F(93319, 100000),
    F(2): F(97725, 100000),
}
Z_TWO_SIDED = ((90, F(1645, 1000)), (95, F(196, 100)), (99, F(2576, 1000)))


def median(values: tuple[F, ...]) -> F:
    if not values:
        raise ValueError("Median requires data")
    data = sorted(values)
    n = len(data)
    return data[n // 2] if n % 2 else (data[n // 2 - 1] + data[n // 2]) / 2


class Sample(Parameters):
    values: tuple[int, ...]

    @model_validator(mode="after")
    def validate_values(self) -> Self:
        if not 3 <= len(self.values) <= 12 or any(
            type(v) is not int or abs(v) > 12 for v in self.values
        ):
            raise ValueError("A bounded sample has 3..12 integer observations")
        return self

    @property
    def mean(self) -> F:
        return F(sum(self.values), len(self.values))

    @property
    def median(self) -> F:
        return median(tuple(map(F, self.values)))

    @property
    def modes(self) -> tuple[int, ...]:
        counts = Counter(self.values)
        return tuple(sorted(x for x, count in counts.items() if count == max(counts.values())))

    @property
    def quartiles(self) -> tuple[F, F]:
        data = tuple(map(F, sorted(self.values)))
        half = len(data) // 2
        return median(data[:half]), median(data[-half:])

    def variance(self, sample: bool = True) -> F:
        return sum(((F(x) - self.mean) ** 2 for x in self.values), F()) / (
            len(self.values) - int(sample)
        )


class PairedSample(Parameters):
    x: Sample
    y: Sample

    @model_validator(mode="after")
    def validate_pair(self) -> Self:
        if len(self.x.values) != len(self.y.values):
            raise ValueError("Paired samples need equal lengths")
        if not self.x.variance() or not self.y.variance():
            raise ValueError("Nonzero variances required")
        return self

    @property
    def centered_product(self) -> F:
        return sum(
            (
                (F(x) - self.x.mean) * (F(y) - self.y.mean)
                for x, y in zip(self.x.values, self.y.values, strict=True)
            ),
            F(),
        )

    @property
    def slope(self) -> F:
        return self.centered_product / sum(((F(x) - self.x.mean) ** 2 for x in self.x.values), F())

    @property
    def intercept(self) -> F:
        return self.y.mean - self.slope * self.x.mean

    @property
    def correlation(self) -> Any:
        n = len(self.x.values)
        return (
            sp.Rational(self.centered_product)
            / sp.sqrt(sp.Rational(self.x.variance() * self.y.variance()))
            / (n - 1)
        )


def mean_interval(mean: Any, scale: Any, n: int, critical: F) -> tuple[Any, Any]:
    if type(n) is not int or not 4 <= n <= 100 or scale <= 0 or critical <= 0:
        raise ValueError("Invalid bounded inference inputs")
    margin = sp.Rational(critical) * sp.sympify(scale) / sp.sqrt(n)
    return sp.simplify(mean - margin), sp.simplify(mean + margin)


def mean_statistic(mean: Any, null: Any, scale: Any, n: int) -> Any:
    mean_interval(mean, scale, n, F(1))
    return sp.simplify((mean - null) * sp.sqrt(n) / scale)


def reject(statistic: Any, critical: F, tail: str) -> bool:
    if tail not in {"two", "upper", "lower"} or critical <= 0:
        raise ValueError("Invalid critical region")
    value = abs(statistic) if tail == "two" else statistic if tail == "upper" else -statistic
    decision = sp.simplify(value - sp.Rational(critical))
    if decision.is_positive is None:
        raise ValueError("Critical comparison is not exactly decidable")
    return bool(decision.is_positive)
