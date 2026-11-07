"""Geometry derived from the local complex-number exercise after solution reveal."""

import sympy as sp

from app.engine.generators.complex_numbers import (
    ComplexArgument,
    ComplexRoot,
    DeMoivre,
    _angle,
    _base,
    _rectangular,
)
from local_complex_generator import LocalComplexGenerator
from local_conversion_generator import LocalConversionGenerator, LocalConversionToPolarGenerator
from local_modulus_generator import LocalModulusCircle, LocalModulusGenerator, LocalModulusPractice


def complex_visual(generator, params, task):
    version = generator.version
    if version == LocalModulusCircle.version:
        return {
            "kind": "complex-plane",
            "version": 1,
            "mode": "circle",
            "first": [float(params.center_x), float(params.center_y)],
            "second": None,
            "result": None,
            "power": None,
            "radius": float(params.radius),
        }
    if version == LocalComplexGenerator.version:
        first = params.first[0] + params.first[1] * sp.I
        second = params.second[0] + params.second[1] * sp.I
        mode = params.operation
    elif version in {LocalConversionGenerator.version, LocalConversionToPolarGenerator.version}:
        first = _rectangular(params.modulus, _angle(params.angle))
        second, mode = None, "argument"
    elif version == LocalModulusGenerator.version:
        first, second, mode = params.real + params.imaginary * sp.I, None, "modulus"
    elif version == LocalModulusPractice.version:
        first, second, mode = generator.value(params), None, "modulus"
    elif version == DeMoivre.version:
        first, second, mode = _base(params.base), None, "power"
    elif version == ComplexArgument.version:
        angle = _angle(params.angle)
        sixth = (angle / (sp.pi / 6)).is_integer
        first = _rectangular(params.scale * (2 if sixth else sp.sqrt(2)), angle)
        second, mode = None, "argument"
    elif version == ComplexRoot.version:
        first = _rectangular(params.scale**params.order, params.order * _angle(params.angle))
        second, mode = None, "root"
    else:
        return None

    def point(value):
        return [float(sp.re(value).evalf()), float(sp.im(value).evalf())]

    # A modulus or argument is real; only show a result vector for complex-valued answers.
    result = None if mode in {"modulus", "argument"} else point(task.answer.expected)
    return {
        "kind": "complex-plane",
        "version": 1,
        "mode": mode,
        "first": point(first),
        "second": point(second) if second is not None else None,
        "result": result,
        "power": params.power if mode == "power" else None,
        **({"firstLabel": "value"} if version == LocalModulusPractice.version else {}),
    }
