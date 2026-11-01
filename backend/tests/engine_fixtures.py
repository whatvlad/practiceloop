"""Frozen curriculum contracts and native-code fixtures; no legacy runtime adapters."""

import json
from pathlib import Path
from types import SimpleNamespace

from app.engine import practice as engine
from app.engine.blocks.integral_forms.form import IntegralForm
from app.engine.codes import encode
from app.engine.generators.integrals import integral_generators

FIXTURES = Path(__file__).parent / "fixtures"
CURRICULUM = json.loads((FIXTURES / "engine_curriculum_v1.json").read_text(encoding="utf-8"))
PUBLISHED_TOPICS = {
    x["slug"]: SimpleNamespace(**{**x, "levels": tuple(x["levels"])})
    for x in json.loads((FIXTURES / "published_topic_contract.json").read_text(encoding="utf-8"))
}
_indexes = {}
_positions = {}


def native_record(family, template, coefficient=1, secondary=1, power=2):
    form = IntegralForm(
        family=family, template=template, coefficient=coefficient, secondary=secondary, power=power
    )
    generator = next(g for g in integral_generators() if g.form_family == family and not g.bounded)
    index = _indexes.setdefault(family, {})
    for seed in range(_positions.get(family, 0), 50000):
        if form in index:
            break
        drawn = generator.draw(seed)
        index.setdefault(
            drawn.form,
            {
                "generator_version": generator.version,
                "code": encode(generator.prefix, generator.code_version, seed),
            },
        )
        _positions[family] = seed + 1
    if form not in index:
        raise AssertionError(f"Native test form not drawn: {form}")
    return dict(index[form])


def answer_for(record):
    return engine.replay(record).answer


def check(tree, answer):
    return answer.check(tree)


def catalogue(topic, level):
    return tuple(p.issued() for p in engine.pool(topic, level))


def native_params(record):
    from app.engine.codes import parse_code

    r = engine._registry()
    c = parse_code(record["code"], r)
    return r.get_code(c.prefix, c.version).draw(c.seed)


def native_data(record):
    from app.engine.codes import parse_code

    r = engine._registry()
    c = parse_code(record["code"], r)
    g = r.get_code(c.prefix, c.version)
    return g.data(g.draw(c.seed))


def multiple_record(dimension, template, variant=0, coefficient=1):
    from app.engine.blocks.multiple.form import MultipleForm
    from app.engine.generators.multiple import DoubleIntegrals, TripleIntegrals

    g = DoubleIntegrals() if dimension == 2 else TripleIntegrals()
    form = MultipleForm(
        dimension=dimension, template=template, variant=variant, coefficient=coefficient
    )
    family = g.version
    index = _indexes.setdefault(family, {})
    for seed in range(_positions.get(family, 0), 50000):
        if form in index:
            break
        drawn = g.draw(seed)
        index.setdefault(
            drawn.form,
            {"generator_version": g.version, "code": encode(g.prefix, g.code_version, seed)},
        )
        _positions[family] = seed + 1
    if form not in index:
        raise AssertionError(f"Native multiple form not drawn: {form}")
    return dict(index[form])
