"""#281: independent second differentiation and constrained profile checks."""

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

FAMILIES = [
    g
    for g in generators()
    if g.evaluate.__module__.endswith(("._second_partials", "._multivariable_extrema"))
]


def hessian_function(prefix, a, b, c):
    if prefix == "MVCC":
        return lambda x, y: c * mp.cos(a * x * x + b * y * y)
    if prefix == "MVCD":
        return lambda x, y: a * y * mp.exp(b * x * y + c)
    if prefix == "MVCE":
        return lambda x, y: a * x * x + b * y**3 / (c * x)
    if prefix == "MVCF":
        return lambda x, y: a * y * mp.log(b * x / (c * y))
    if prefix == "MVCG":
        return lambda x, y, z: y * (a + b * x * x + c * z * z)
    if prefix in ("MVCH", "MVCI", "MVCJ"):
        return lambda x, y, z: mp.log(a * x + b * y * y + c * z**3 + 1)
    if prefix == "MVCK":
        return lambda x, y: a * mp.atan((x + b) / (y + c))
    if prefix == "MVCL":
        return lambda x, y: a * mp.log((x + b) ** 2 + (y + c) ** 2)
    if prefix == "MVCM":
        return lambda x, y: a * mp.cos(b * x) * mp.cosh(b * y + c)
    raise AssertionError(prefix)


def local_function(prefix, a, b, c):
    if prefix == "MVCN":
        return lambda x, y: (
            a * ((x - b) ** 3 + 3 * (x - b) * (y - c) ** 2 - 51 * (x - b) - 24 * (y - c))
        )
    if prefix == "MVCO":
        return lambda x, y: a * (x / b * mp.exp(c - y) + b / x + mp.exp(y - c))
    if prefix == "MVCP":
        return lambda x, y: a * x * y * y * (4 * (b + c) - x - y)
    if prefix == "MVCQ":
        return lambda x, y: a * (y * mp.sqrt(x) - y * y - x + 3 * (b + c) * y)
    if prefix == "MVCR":
        return lambda x, y: a * ((x - b) ** 3 + (y - c) ** 3 - 3 * a * (x - b) * (y - c))
    if prefix == "MVCS":
        return lambda x, y: a * ((b + c) ** 3 / x + x / y + y)
    if prefix == "MVCT":
        return lambda x, y: b * (x * y + mp.log(y) + a * x * x) + c
    if prefix == "MVCU":
        return lambda x, y: mp.exp(x - b - 2 * (y - c)) + mp.exp(y - c - x + b) + mp.exp(a + y - c)
    if prefix == "MVCV":
        return lambda x, y: a * mp.exp(x * x - y) * (b + c - x - y)
    raise AssertionError(prefix)


def close(actual, expected):
    assert abs(actual - expected) <= mp.mpf("1e-34") * max(1, abs(expected))


def at(part, coordinates=()):
    expression = part.expected
    values = dict(zip("xyz"[: len(coordinates)], map(sp.Rational, coordinates), strict=True))
    return mp.mpf(
        str(expression.subs({s: values[s.name] for s in expression.free_symbols}).evalf(46))
    )


def verify_hessian(prefix, answer, coefficients):
    function = hessian_function(prefix, *coefficients)
    dimension = 3 if prefix in ("MVCG", "MVCH", "MVCI", "MVCJ") else 2
    coordinates = ("1.3", "0.7", "1.1")[:dimension]
    point = tuple(map(mp.mpf, coordinates))
    variables = "xyz"[:dimension]
    derivatives = []
    for label, component in zip(answer.labels, answer.components, strict=True):
        if label == "Laplacian":
            close(sum(derivatives), 0)
            close(at(component), 0)
        else:
            counts = tuple(label.count(v) for v in variables)
            expected = mp.diff(function, point, counts)
            derivatives.append(expected)
            close(at(component, coordinates), expected)


def verify_local(prefix, answer, coefficients):
    function = local_function(prefix, *coefficients)
    if prefix in ("MVCT", "MVCV"):
        x, y, kind = answer.components
        points = [(at(x), at(y), None, kind.expected)]
    else:
        parts = answer.components
        points = [
            (at(parts[i]), at(parts[i + 1]), at(parts[i + 2]), answer.labels[i].split()[0].lower())
            for i in range(0, len(parts), 3)
        ]
    for x, y, value, kind in points:
        close(mp.diff(function, (x, y), (1, 0)), 0)
        close(mp.diff(function, (x, y), (0, 1)), 0)
        if value is not None:
            close(function(x, y), value)
        xx = mp.diff(function, (x, y), (2, 0))
        xy = mp.diff(function, (x, y), (1, 1))
        yy = mp.diff(function, (x, y), (0, 2))
        det = xx * yy - xy * xy
        if kind == "minimum":
            assert det > 0 and xx > 0
        elif kind == "maximum":
            assert det > 0 and xx < 0
        else:
            assert kind == "saddle" and det < 0


def verify_constrained(prefix, answer, coefficients):
    a, b, c = coefficients
    values = tuple(map(at, answer.components))
    if prefix == "MVCW":
        x, y, z = values
        close(a * x + b * y, c)

        def profile(t):
            return t * t + ((c - a * t) / b) ** 2

        candidates = ((x, z, 1),)
    elif prefix == "MVCX":
        x, y, z, xx, yy, xm, ym, zm = values
        for u, v in ((x, y), (xx, yy), (xm, ym)):
            close(u, v * v + a)
        assert y > 0 and yy < 0

        def profile(t):
            return (t * t + a - (a + (b + c) ** 2 + 1)) ** 2 + 2 * t * t

        candidates = ((y, z, 1), (yy, z, 1), (ym, zm, -1))
    elif prefix == "MVCY":
        x, y, z = values
        k = mp.mpf(b) / (3 * a**3)
        close(y, -k * x)

        def profile(t):
            return -k * t**3 + b * mp.log(t) + c

        candidates = ((x, z, -1),)
    else:
        x, y, z, xx, yy, zz = values
        close(x * x + y * y, c * c)
        close(xx * xx + yy * yy, c * c)
        angle = mp.atan2(yy, xx)

        def profile(t):
            return c * (a * mp.cos(t) + b * mp.sin(t))

        candidates = ((angle + mp.pi, z, 1), (angle, zz, -1))
    for t, height, curvature_sign in candidates:
        close(profile(t), height)
        close(mp.diff(profile, t), 0)
        assert curvature_sign * mp.diff(profile, t, 2) > 0


@pytest.mark.parametrize("generator", FAMILIES, ids=lambda item: item.prefix)
def test_second_partial_or_extremum_independently(generator):
    seen = set()
    prefix = generator.prefix
    with mp.workdps(52):
        for seed in sweep(1000):
            params = generator.draw(seed)
            coefficients = params.a, params.b, params.c
            if coefficients in seen:
                continue
            seen.add(coefficients)
            answer = generator.build(params).answer
            tree = parse_answer_input(
                source(answer), generator.contract.kind, contract=generator.contract
            )
            assert answer.check(tree) == "correct"
            visual = generator.solution_visual(params)
            if prefix <= "MVCM":
                verify_hessian(prefix, answer, coefficients)
                assert visual is None
            else:
                assert graph(validate_plot(visual))
                if prefix <= "MVCV":
                    verify_local(prefix, answer, coefficients)
                else:
                    verify_constrained(prefix, answer, coefficients)
