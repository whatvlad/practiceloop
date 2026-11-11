"""#269: original boundary integrals, numerical arc lengths, units and diagrams."""

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

APPLICATIONS = [
    g for g in generators() if g.evaluate.__module__.endswith("._integral_applications")
]
AREA_PREFIXES = {
    "INDW",
    "INDX",
    "INDY",
    "INDZ",
    "INEA",
    "INEB",
    "INEC",
    "INED",
    "INEE",
    "INEF",
    "INEG",
    "INEH",
    "INEI",
    "INEJ",
    "INEV",
    "INEW",
    "INEX",
    "INEY",
    "INEZ",
    "INFA",
}


def boundary_integrals(prefix, a, b, c):
    angle = mp.pi / (c + 3)
    meet = mp.mpf(b * b * (c + 1)) / (a * a + b * b)
    span = a + b + 2
    tangent_contact = a + c
    tangent_intercept = mp.mpf(tangent_contact**2 - c * c) / (2 * tangent_contact)
    cap = mp.mpf(b * b * (b * b + c * c)) / (a + 1)
    cases = {
        "INDW": [(lambda x: (a + c) * x - b * x * x, 0, mp.mpf(a + c) / b)],
        "INDX": [
            (lambda x: b * x * x, 0, mp.mpf(c) / (a + b)),
            (lambda x: c * x - a * x * x, mp.mpf(c) / (a + b), mp.mpf(c) / a),
        ],
        "INDY": [(lambda y: a * y - a / mp.sqrt(y), 1, a + b + 1)],
        "INDZ": [
            (
                lambda x: c * (a + b) ** 2 / (x * x + a * a) - c,
                -mp.sqrt((a + b) ** 2 - a * a),
                mp.sqrt((a + b) ** 2 - a * a),
            )
        ],
        "INEA": [(lambda x: (b + 1) ** a - mp.power(b + 1, x), 0, a)],
        "INEB": [(lambda x: a * (mp.sin(b * x) - mp.sin(angle)), angle / b, (mp.pi - angle) / b)],
        "INEC": [
            (lambda x: a * mp.sqrt(x), 0, meet),
            (lambda x: b * mp.sqrt(c + 1 - x), meet, c + 1),
        ],
        "INED": [(lambda y: 2 * a / mp.root(y, 4), 1, (b + 1) ** 4)],
        "INEE": [(lambda x: 2 * c * mp.log(x), 1, mp.mpf(span) / 2)],
        "INEF": [(lambda x: b * (c - mp.sqrt(x / a)) ** 2, 0, a * c * c)],
        "INEG": [(lambda x: cap / (x * x + c * c) - x * x / (a + 1), -b, b)],
        "INEH": [(lambda x: mp.log(x) + a, mp.exp(-a), mp.exp(b))],
        "INEI": [(lambda y: 2 * mp.sqrt((a + b + c) ** 2 - y * y), a, a + b)],
        "INEJ": [(lambda y: mp.log(y) / (2 * mp.log(b + 1)), 1, (b + 1) ** (2 * (1 + a % 2)))],
        "INEV": [(lambda x: a + b * a * a - b * x - mp.sqrt(x), 0, a * a)],
        "INEW": [(lambda y: a * (a + 1) - y - y * y, -a - 1, a)],
        "INEX": [(lambda x: (b + c) * (x + a) * (c - x), -a, c)],
        "INEY": [
            (lambda x: b * (x * x + c * c), 0, tangent_contact),
            (
                lambda x: -(2 * b * tangent_contact * x + b * (c * c - tangent_contact**2)),
                tangent_intercept,
                tangent_contact,
            ),
        ],
        "INEZ": [(lambda x: a * x**3 - 3 * a * b * b * x + 2 * a * b**3, 0, b)],
        "INFA": [(lambda x: a * mp.log(x) - b * mp.log(x) ** 2, 1, mp.exp(mp.mpf(a) / b))],
    }
    return cases[prefix]


def original_arc(prefix, a, b, c):
    curves = {
        "INEL": (lambda x: mp.log((mp.exp(a * x) + 1) / (mp.exp(a * x) - 1)) / a, b, b + c),
        "INEM": (lambda x: a * x * x + c, 0, b),
        "INEN": (lambda x: a * x ** mp.mpf("1.5"), 0, b + c),
        "INEO": (lambda x: mp.exp(c * x) / c, mp.log(a) / c, mp.log(a + b) / c),
        "INEP": (
            lambda x: x ** (3 + a % 3) / (2 * (3 + a % 3)) + x ** (-1 - a % 3) / (2 * (1 + a % 3)),
            1 + b % 2,
            2 + b % 2 + c % 2,
        ),
        "INEQ": (lambda x: (c - mp.log(mp.cos(a * x))) / a, 0, mp.pi / ((b + 3) * a)),
    }
    return curves[prefix]


def original_slope(prefix, a, b, c, x):
    slopes = {
        "INEL": lambda: -1 / mp.sinh(a * x),
        "INEM": lambda: 2 * a * x,
        "INEN": lambda: mp.mpf("1.5") * a * mp.sqrt(x),
        "INEO": lambda: mp.exp(c * x),
        "INEP": lambda: (x ** (2 + a % 3) - x ** (-2 - a % 3)) / 2,
        "INEQ": lambda: mp.tan(a * x),
    }
    return slopes[prefix]()


def numerical_value(prefix, a, b, c, expected):
    if prefix in AREA_PREFIXES:
        return sum(mp.quad(f, [lo, hi]) for f, lo, hi in boundary_integrals(prefix, a, b, c))
    if prefix in {"INEL", "INEM", "INEN", "INEO", "INEP", "INEQ"}:
        curve, lo, hi = original_arc(prefix, a, b, c)
        for fraction in (mp.mpf("0.2"), mp.mpf("0.7")):
            x = lo + (hi - lo) * fraction
            assert abs(mp.diff(curve, x) - original_slope(prefix, a, b, c, x)) < mp.mpf("1e-25")
        return mp.quad(lambda x: mp.sqrt(1 + original_slope(prefix, a, b, c, x) ** 2), [lo, hi])
    if prefix == "INER":
        return mp.quad(lambda s: 10 * a * s, [0, mp.mpf(c) / 10])
    if prefix == "INES":
        return mp.quad(
            lambda y: 1000 * mp.mpf("9.81") * (b + c) * 2 * mp.sqrt(a * a - y * y) * (a - y),
            [-a, a],
        )
    if prefix == "INET":
        initial = a + b * c
        return mp.quad(lambda t: initial + a * t, [0, b]) + mp.quad(
            lambda s: initial + a * b - b * s, [0, c]
        )
    if prefix == "INEU":
        distance = (a + b) * (a + 1) ** 2 + c * (a + 1) ** 4
        covered = mp.quad(lambda t: (2 * a + 2 * b) * t + 4 * c * t**3, [0, expected])
        assert abs(covered - distance) < mp.mpf("1e-28")
        assert expected > 0
        return expected
    raise AssertionError(prefix)


def polygon_area(points):
    pairs = zip(points, points[1:] + points[:1], strict=True)
    return abs(sum(x1 * y2 - y1 * x2 for (x1, y1), (x2, y2) in pairs)) / 2


@pytest.mark.parametrize("generator", APPLICATIONS, ids=lambda g: g.prefix)
def test_full_seed_sweep_matches_original_geometry_and_physics(generator):
    seen = set()
    checked_answers = set()
    with mp.workdps(40):
        for seed in sweep(1000):
            params = generator.draw(seed)
            coefficients = params.a, params.b, params.c
            if coefficients in seen:
                continue
            seen.add(coefficients)
            task = generator.build(params)
            answer = task.answer
            visual = validate_plot(generator.solution_visual(params))
            if generator.prefix == "INEK":
                assert answer.expected == sp.oo
                a, b, c = coefficients
                crossing = mp.atan(mp.sqrt(mp.mpf(c) / a)) / b

                def gap(x, a=a, b=b, c=c):
                    return c / mp.tan(b * x) - a * mp.tan(b * x)

                first = mp.quad(gap, [mp.mpf("1e-4") / b, crossing])
                second = mp.quad(gap, [mp.mpf("1e-8") / b, crossing])
                assert second > first + mp.mpf(c) / b * 9
            else:
                expected = mp.mpf(str(sp.N(answer.expected, 40)))
                actual = numerical_value(generator.prefix, *coefficients, expected)
                assert abs(expected - actual) < mp.mpf("1e-25") * max(1, abs(actual))
                if generator.prefix in AREA_PREFIXES:
                    assert actual > 0
                    drawn = sum(polygon_area(p["points"]) for p in visual["paths"])
                    assert drawn == pytest.approx(float(actual), rel=0.08)
            if answer not in checked_answers:
                text = source(answer)
                tree = parse_answer_input(
                    text, answer.kind, contract=getattr(answer, "contract", None)
                )
                assert answer.check(tree) == "correct"
                checked_answers.add(answer)
            if seed < 5:
                assert "pdfliteral" in graph(visual)
