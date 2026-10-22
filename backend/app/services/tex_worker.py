"""Child entry point for one pdflatex run (ADR-007): set limits, then become pdflatex.

Kept free of app imports so the child starts fast. The parent passes a fixed
argv and environment; this process only lowers its own limits and execs.
"""

from __future__ import annotations

import os
import resource
import sys

CPU_SECONDS = 10
ADDRESS_SPACE_BYTES = 512 * 1024 * 1024
MAX_FILE_BYTES = 5 * 1024 * 1024


def main(argv: list[str]) -> int:
    if not argv or not os.path.isabs(argv[0]):
        return 2
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
    resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE_BYTES, ADDRESS_SPACE_BYTES))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_FILE_BYTES, MAX_FILE_BYTES))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.execv(argv[0], argv)  # noqa: S606 - fixed argv built by the parent, no shell
    return 1  # pragma: no cover - execv does not return


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
