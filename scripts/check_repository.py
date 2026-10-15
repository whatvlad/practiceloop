"""Fail on unsafe repository files and drift in the protected specification.

Gitleaks performs token detection separately. Never print a matched secret value.
Includes untracked files for local bootstrap; ignored artifacts are excluded by Git.
"""

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_SHA = "f8605364ce622bec262ae61aa6c3d1971ad99cf67be97200fe00e691a4701944"


def main() -> int:
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("Git executable is required for repository policy checks")
    # Executable resolved from PATH, flags fixed; no user input or shell execution.
    result = subprocess.run(  # noqa: S603
        [git, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    failures: list[str] = []
    for name in set(result.stdout.decode().split("\0")) - {""}:
        path = Path(name)
        if (path.name == ".env" or path.name.startswith(".env.")) and path.name != ".env.example":
            failures.append(f"Forbidden environment file: {name}")
        if path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
            failures.append(f"Forbidden key file: {name}")
        if path.name.startswith(("id_rsa", "id_ed25519")):
            failures.append(f"Forbidden SSH key file: {name}")
    if hashlib.sha256((ROOT / "docs/PRACTICELOOP_MVP.md").read_bytes()).hexdigest() != SPEC_SHA:
        failures.append(
            "Original MVP specification bytes changed; explicit owner approval required"
        )
    for problem in failures:
        print(problem, file=sys.stderr)
    if failures:
        return 1
    print("Repository file policy and original specification hash passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
