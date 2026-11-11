import pytest
from seed_sweep import sweep

from app.api.practice import _check
from app.core.errors import ApiError
from app.engine import practice
from app.engine.generators.self_review import generators
from app.engine.rendering import render
from app.services.worksheet_graphs import graph


@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.prefix)
def test_self_review_reference_and_public_projection(generator):
    seen = set()
    for seed in sweep(1000):
        p = generator.draw(seed)
        params = (p.a, p.b, p.c)
        if params in seen:
            continue
        seen.add(params)
        issued = render(generator.build(p), practice._registry())
        public = practice.problem_projection(issued.record)
        assert public["selfReview"] is True
        with pytest.raises(ApiError) as rejected:
            _check("draft", issued.record)
        assert rejected.value.status_code == 409
        assert issued.steps
        if generator.prefix in ("RVA", "RVB"):
            assert public == {"selfReview": True}
            for x1, x2 in ((-2, 0), (0, p.b), (p.b - 1, p.b)):
                if generator.prefix == "RVA":
                    assert p.a * x1 - p.b < p.a * x2 - p.b
                else:
                    assert p.a * (x1 - p.b) ** 2 + p.c > p.a * (x2 - p.b) ** 2 + p.c
            continue
        if generator.prefix in ("RVK", "RVL"):
            assert public == {"selfReview": True}
            for u, v in ((-4, -2), (-2, 1), (1, 3)):
                if generator.prefix == "RVK":
                    assert p.a * u**3 + p.b * u - p.c < p.a * v**3 + p.b * v - p.c
                else:
                    assert p.a / (u + 5) + p.c > p.a / (v + 5) + p.c
            continue
        assert set(public) == {"selfReview", "promptVisual"}
        assert graph(public["promptVisual"])
        assert graph(issued.visual)

        def base(x, p=p):
            if x <= -p.a:
                return p.b
            return -p.c + (p.b + p.c) * abs(x) / p.a

        reference = {
            "RVC": lambda x, c=p.c: base(x) + c,
            "RVD": lambda x, a=p.a: base(x + a),
            "RVE": lambda x: -base(x),
            "RVF": lambda x: base(-x),
            "RVG": lambda x, b=p.b: base(x) / b,
            "RVH": lambda x, a=p.a: base(a * x),
            "RVI": lambda x: abs(base(x)),
            "RVJ": lambda x: base(abs(x)),
        }[generator.prefix]
        for path in issued.visual["paths"]:
            for (x, y), (xx, yy) in zip(path["points"], path["points"][1:], strict=False):
                assert y == pytest.approx(reference(x))
                assert (y + yy) / 2 == pytest.approx(reference((x + xx) / 2))
