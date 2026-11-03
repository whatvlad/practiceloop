"""Strict bounded distributions and exact mathematical results; no product copy."""

from __future__ import annotations

from collections.abc import Collection
from fractions import Fraction as F
from math import comb, factorial
from typing import Any, Literal, Self

import sympy as sp
from pydantic import Field, model_validator

from app.engine.models import Parameters

type StandardKind = Literal["bernoulli", "binomial", "geometric", "hypergeometric", "poisson"]


class FiniteDistribution(Parameters):
    values: tuple[F, ...]
    masses: tuple[F, ...]

    @model_validator(mode="after")
    def validate_distribution(self) -> Self:
        if not 1 <= len(self.values) <= 8 or len(self.values) != len(self.masses):
            raise ValueError("Finite distributions have one to eight outcomes")
        if len(set(self.values)) != len(self.values) or any(abs(x) > 12 for x in self.values):
            raise ValueError("Outcomes must be distinct and bounded")
        if any(p < 0 for p in self.masses) or sum(self.masses) != 1:
            raise ValueError("Masses must be nonnegative and sum to one")
        return self

    @classmethod
    def from_weights(cls, values: tuple[int | F, ...], weights: tuple[int, ...]) -> Self:
        if any(type(w) is not int or not 0 <= w <= 25 for w in weights) or not sum(weights):
            raise ValueError("Invalid bounded weights")
        if any(isinstance(x, bool) or not isinstance(x, (int, F)) for x in values):
            raise ValueError("Outcomes must be exact")
        return cls(values=tuple(map(F, values)), masses=tuple(F(w, sum(weights)) for w in weights))

    @property
    def support(self) -> tuple[F, ...]:
        return tuple(x for x, p in zip(self.values, self.masses, strict=True) if p)

    def probability(self, event: Collection[int | F]) -> F:
        return sum((p for x, p in zip(self.values, self.masses, strict=True) if x in event), F())

    def cdf(self, point: F) -> F:
        return self.probability(tuple(x for x in self.values if x <= point))

    def moment(self, order: int) -> F:
        if type(order) is not int or order not in (0, 1, 2):
            raise ValueError("Only bounded moments are supported")
        return sum((x**order * p for x, p in zip(self.values, self.masses, strict=True)), F())

    @property
    def variance(self) -> F:
        return self.moment(2) - self.moment(1) ** 2

    def pushforward(self, values: tuple[F, ...]) -> FiniteDistribution:
        if len(values) != len(self.values):
            raise ValueError("One image per original outcome is required")
        masses: dict[F, F] = {}
        for x, p in zip(values, self.masses, strict=True):
            masses[x] = masses.get(x, F()) + p
        support = tuple(sorted(masses))
        return FiniteDistribution(values=support, masses=tuple(masses[x] for x in support))


class JointDistribution(Parameters):
    x: tuple[F, ...]
    y: tuple[F, ...]
    masses: tuple[tuple[F, ...], ...]

    @model_validator(mode="after")
    def validate_joint(self) -> Self:
        if not 1 <= len(self.x) <= 4 or not 1 <= len(self.y) <= 4:
            raise ValueError("Joint tables are at most four by four")
        if len(self.masses) != len(self.x) or any(len(row) != len(self.y) for row in self.masses):
            raise ValueError("Table dimensions differ")
        self.marginal_x()
        self.marginal_y()
        if any(p < 0 for row in self.masses for p in row):
            raise ValueError("Joint masses must be nonnegative")
        return self

    def marginal_x(self) -> FiniteDistribution:
        return FiniteDistribution(values=self.x, masses=tuple(sum(row, F()) for row in self.masses))

    def marginal_y(self) -> FiniteDistribution:
        return FiniteDistribution(
            values=self.y,
            masses=tuple(sum((row[j] for row in self.masses), F()) for j in range(len(self.y))),
        )

    def conditional(self, row: int, column: int) -> F:
        denominator = self.marginal_y().masses[column]
        if not denominator:
            raise ValueError("Conditioning event has zero probability")
        return self.masses[row][column] / denominator

    @property
    def covariance(self) -> F:
        product = sum(
            (x * y * self.masses[i][j] for i, x in enumerate(self.x) for j, y in enumerate(self.y)),
            F(),
        )
        return product - self.marginal_x().moment(1) * self.marginal_y().moment(1)

    @property
    def independent(self) -> bool:
        px, py = self.marginal_x().masses, self.marginal_y().masses
        return all(
            p == px[i] * py[j] for i, row in enumerate(self.masses) for j, p in enumerate(row)
        )


class StandardDistribution(Parameters):
    kind: StandardKind
    n: int = Field(default=1, ge=1, le=12)
    numerator: int = Field(default=1, ge=1, le=5)
    denominator: int = Field(default=2, ge=2, le=10)
    population: int = Field(default=10, ge=2, le=20)
    successes: int = Field(default=5, ge=0, le=20)
    draws: int = Field(default=2, ge=1, le=12)
    rate: int = Field(default=1, ge=1, le=5)

    @model_validator(mode="after")
    def validate_parameters(self) -> Self:
        if self.numerator >= self.denominator:
            raise ValueError("Probability must be strictly between zero and one")
        if self.successes > self.population or self.draws > self.population:
            raise ValueError("Invalid finite population")
        return self

    @property
    def p(self) -> F:
        return F(self.numerator, self.denominator)

    def pmf(self, k: int) -> Any:
        if type(k) is not int or not -1 <= k <= 12:
            raise ValueError("Query is outside the bounded integer table")
        p = self.p
        if self.kind == "bernoulli":
            return p**k * (1 - p) ** (1 - k) if k in (0, 1) else F()
        if self.kind == "binomial":
            return F(comb(self.n, k)) * p**k * (1 - p) ** (self.n - k) if 0 <= k <= self.n else F()
        if self.kind == "geometric":
            return p * (1 - p) ** (k - 1) if k >= 1 else F()
        if self.kind == "hypergeometric":
            lo = max(0, self.draws - (self.population - self.successes))
            hi = min(self.draws, self.successes)
            return (
                F(
                    comb(self.successes, k)
                    * comb(self.population - self.successes, self.draws - k),
                    comb(self.population, self.draws),
                )
                if lo <= k <= hi
                else F()
            )
        return sp.exp(-self.rate) * sp.Rational(self.rate**k, factorial(k)) if k >= 0 else sp.S.Zero

    def cdf(self, k: int) -> Any:
        if type(k) is not int or not -1 <= k <= 12:
            raise ValueError("Query is outside the bounded integer table")
        return sum((self.pmf(j) for j in range(k + 1)), F())

    @property
    def mean(self) -> F:
        return {
            "bernoulli": self.p,
            "binomial": self.n * self.p,
            "geometric": 1 / self.p,
            "hypergeometric": F(self.draws * self.successes, self.population),
            "poisson": F(self.rate),
        }[self.kind]

    @property
    def variance(self) -> F:
        p = self.p
        return {
            "bernoulli": p * (1 - p),
            "binomial": self.n * p * (1 - p),
            "geometric": (1 - p) / p**2,
            "hypergeometric": F(self.draws * self.successes, self.population)
            * (1 - F(self.successes, self.population))
            * F(self.population - self.draws, self.population - 1),
            "poisson": F(self.rate),
        }[self.kind]


class DensitySegment(Parameters):
    lower: int = Field(ge=-12, le=11)
    upper: int = Field(ge=-11, le=12)
    # Polynomial in (x-lower), nonnegative over this segment.
    coefficients: tuple[int, ...]

    @model_validator(mode="after")
    def validate_segment(self) -> Self:
        if self.lower >= self.upper or not 1 <= len(self.coefficients) <= 4:
            raise ValueError("Invalid bounded segment")
        if any(type(c) is not int or not 0 <= c <= 5 for c in self.coefficients) or not any(
            self.coefficients
        ):
            raise ValueError("A positive polynomial shape is required")
        return self

    def integral(self, lower: F, upper: F, order: int = 0) -> F:
        if type(order) is not int or order not in (0, 1, 2):
            raise ValueError("Only bounded moments are supported")
        lo, hi = max(lower, F(self.lower)), min(upper, F(self.upper))
        if lo >= hi:
            return F()
        # x^order = ((x-lower_endpoint)+lower_endpoint)^order.
        return sum(
            (
                F(c * comb(order, j) * self.lower ** (order - j), i + j + 1)
                * ((hi - self.lower) ** (i + j + 1) - (lo - self.lower) ** (i + j + 1))
                for i, c in enumerate(self.coefficients)
                for j in range(order + 1)
            ),
            F(),
        )

    def expression(self, x: Any) -> Any:
        return sum(c * (x - self.lower) ** i for i, c in enumerate(self.coefficients))


class PolynomialDensity(Parameters):
    segments: tuple[DensitySegment, ...]

    @model_validator(mode="after")
    def validate_segments(self) -> Self:
        if not 1 <= len(self.segments) <= 2:
            raise ValueError("At most two density segments")
        if any(
            left.upper != right.lower
            for left, right in zip(self.segments, self.segments[1:], strict=False)
        ):
            raise ValueError("Density segments must form one ordered interval")
        return self

    @property
    def normalizer(self) -> F:
        return sum((s.integral(F(-12), F(12)) for s in self.segments), F())

    def probability(self, lower: F, upper: F) -> F:
        return sum((s.integral(lower, upper) for s in self.segments), F()) / self.normalizer

    def moment(self, order: int) -> F:
        return sum((s.integral(F(-12), F(12), order) for s in self.segments), F()) / self.normalizer


class UniformDistribution(Parameters):
    lower: int = Field(ge=-12, le=11)
    upper: int = Field(ge=-11, le=12)

    @model_validator(mode="after")
    def validate_bounds(self) -> Self:
        if self.lower >= self.upper:
            raise ValueError("Uniform endpoints must increase")
        return self

    def probability(self, lower: F, upper: F) -> F:
        return max(F(), min(upper, F(self.upper)) - max(lower, F(self.lower))) / (
            self.upper - self.lower
        )


class ExponentialDistribution(Parameters):
    rate: F

    @model_validator(mode="after")
    def validate_rate(self) -> Self:
        if not 0 < self.rate <= 5:
            raise ValueError("Positive bounded rate required")
        return self

    def survival(self, x: F) -> Any:
        return (
            sp.exp(-sp.Rational(self.rate.numerator, self.rate.denominator) * sp.Rational(x))
            if x >= 0
            else sp.S.One
        )

    def quantile(self, p: F) -> Any:
        if not 0 < p < 1:
            raise ValueError("Quantile probability must be in (0,1)")
        return -sp.log(sp.Rational(1 - p)) / sp.Rational(self.rate)


class NormalDistribution(Parameters):
    mean: int = Field(ge=-12, le=12)
    sigma: int = Field(ge=1, le=5)

    def standardize(self, x: F) -> F:
        return (x - self.mean) / self.sigma
