"""Reference inverse geometry is the same sampled function, reflected point for point."""

import math

import pytest
from seed_sweep import sweep

from app.engine.generators.elementary import generators
from app.visuals.plot2d import validate_plot


@pytest.mark.parametrize(
    "generator",
    [
        g
        for g in generators()
        if g.template.startswith("inverse-") and not g.template.startswith("inverse-trig-")
    ],
    ids=lambda g: g.template,
)
def test_thousand_inverse_diagrams_preserve_function_branch_and_exact_reflection(generator):
    for seed in sweep(1000):
        params = generator.draw(seed)
        a, b, c, variant = params.a, params.b, params.c, params.variant
        diagram = validate_plot(generator.solution_visual(params))
        assert diagram["x"] == diagram["y"]
        paths = diagram["paths"]
        for original, reflected in zip(paths[1::2], paths[2::2], strict=True):
            assert reflected["points"] == [[y, x] for x, y in original["points"]]
            for x, y in original["points"]:
                assert diagram["x"][0] - 1e-12 <= x <= diagram["x"][1] + 1e-12
                assert diagram["y"][0] - 1e-12 <= y <= diagram["y"][1] + 1e-12
                if generator.template == "inverse-mobius":
                    assert abs(x - b) > 1e-12
                    expected = (x + a) / (x - b)
                elif generator.template == "inverse-quadratic-branch":
                    assert (x >= a - 1e-12) if variant % 2 else (x <= a + 1e-12)
                    expected = (x - a) ** 2 - b
                elif generator.template == "inverse-negative-fourth":
                    assert x <= 0
                    expected = -a * x**4
                elif generator.template == "inverse-semicircle-branch":
                    assert -a - 1e-12 <= x <= 0
                    expected = b - math.sqrt(max(0.0, a * a - x * x))
                elif generator.template == "inverse-exponential":
                    expected = (c + 1) ** (a * x - b) if variant % 2 else math.exp(a * x - b)
                else:
                    assert x + a > 0
                    expected = math.log(x + a) / math.log(b + 1)
                # Display coordinates are floats; exact mathematical inverse identities
                # and complete domains/ranges are proved in the separate solver tests.
                assert y == pytest.approx(expected, rel=1e-7, abs=1e-7)
        for original, reflected in zip(
            diagram["points"][::2], diagram["points"][1::2], strict=True
        ):
            assert original["included"] and reflected["included"]
            assert (original["x"], original["y"]) == (reflected["y"], reflected["x"])
