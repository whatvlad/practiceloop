"""#162: a new generator file and topic entry need no central registry/checker edit."""

import sys
from pathlib import Path

import pytest

from app.engine import generators as package
from app.engine.generators.catalogue import registry
from app.engine.topics.catalogue import Choice, Topic
from app.math_input import parse_math_input


def test_new_generator_module_registers_without_a_catalogue_edit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = tmp_path / "extension_example.py"
    module.write_text(
        "from app.engine.generators.combinations import Combinations\n"
        "class Example(Combinations):\n"
        "    version = 'extension-example-v1'\n"
        "    prefix = 'EXT'\n"
        "    family = 'extension-example'\n"
        "def generators():\n"
        "    return (Example(),)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(package, "__path__", [*package.__path__, str(tmp_path)])
    try:
        registered = registry()
        topic = Topic(
            "example",
            "algebra",
            {1: (Choice("extension-example-v1"),)},
            1,
            title="Example",
            space_cm=4,
        )
        task = topic.generate(1, 162, registered)
        assert task.generator_version == "extension-example-v1"
        assert task.code.startswith("EXT-1-")
        assert task.answer.check(parse_math_input(task.answer.latex())) == "correct"
    finally:
        sys.modules.pop("app.engine.generators.extension_example", None)
