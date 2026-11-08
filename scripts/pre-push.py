"""Run the Backend and Database CI checks that most often fail a first push.

ruff check, ruff format --check and mypy (as in the Backend job), then the
Database isolation job: `pytest -m db` against PRACTICELOOP_TEST_DATABASE_URL
when it is set, otherwise scripts/test-db.py with a disposable PostgreSQL 17
(Docker or native binaries) when one is available. Prints one line per step and
only the tail of a failing step. Run once before the first push of a PR.

    python scripts/pre-push.py           # from the repository root
    python scripts/pre-push.py --no-db   # lint and types only
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
TAIL = 40


def database_available() -> bool:
    spec = importlib.util.spec_from_file_location("test_db", ROOT / "scripts/test-db.py")
    if spec is None or spec.loader is None:
        return False
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return shutil.which("docker") is not None or module.find_pg_bin(None) is not None


def step(name: str, command: list[str], cwd: Path) -> bool:
    started = time.monotonic()
    # Fixed argument lists built here; no shell.
    result = subprocess.run(  # noqa: S603
        command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    seconds = time.monotonic() - started
    if result.returncode == 0:
        print(f"ok    {name} ({seconds:.0f}s)")
        return True
    print(f"FAIL  {name} ({seconds:.0f}s)")
    lines = (result.stdout + result.stderr).strip().splitlines()
    print("\n".join("      " + line for line in lines[-TAIL:]))
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--no-db", action="store_true", help="skip the database tests")
    args = parser.parse_args()
    python = sys.executable
    checks = [
        ("ruff check", [python, "-m", "ruff", "check", ".", "../scripts"], BACKEND),
        ("ruff format", [python, "-m", "ruff", "format", "--check", ".", "../scripts"], BACKEND),
        ("mypy", [python, "-m", "mypy"], BACKEND),
    ]
    skipped = ""
    if not args.no_db:
        if os.environ.get("PRACTICELOOP_TEST_DATABASE_URL"):
            db = [python, "-m", "pytest", "-m", "db", "-q", "-x", "--tb=short"]
            checks.append(("pytest -m db", db, BACKEND))
        elif database_available():
            checks.append(("test-db.py", [python, "scripts/test-db.py"], ROOT))
        else:
            skipped = "skip  database tests: no Docker, PostgreSQL 17 or URL (README)"
    failed = [name for name, command, cwd in checks if not step(name, command, cwd)]
    if skipped:
        print(skipped)
    if failed:
        print(f"{len(failed)} failed: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
