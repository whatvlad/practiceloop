"""Run the same development content checks through the existing backend CI job."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_educational_catalogue_and_checker() -> None:
    for arguments in (
        ("scripts/check_content.py",),
        ("-m", "unittest", "discover", "-s", "scripts", "-p", "test_content_unit.py"),
    ):
        # Fixed trusted commands, no learner input or shell.
        subprocess.run(  # noqa: S603
            (sys.executable, *arguments),
            cwd=ROOT,
            check=True,
            timeout=15,
            capture_output=True,
            text=True,
        )
