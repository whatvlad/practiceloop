"""Run CI's Database isolation job locally against a disposable PostgreSQL container.

Mirrors the `database` job in .github/workflows/ci.yml: auth fixture, every
migration in order, RLS isolation, hosted-check SQL, API ownership queries
(`pytest -m db`) and the end-to-end API flow, including its database outage.
Needs Docker and the backend installed in this Python (README "Local setup").
Never point any of these files at Supabase or shared data.

    python scripts/test-db.py            # from the repository root
    python scripts/test-db.py --sql-only # skip pytest and the end-to-end flow
"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASSWORD = "local-ci-only"  # noqa: S105 - throwaway container, same as CI
USER_A = "00000000-0000-0000-0000-000000000001"
USER_B = "00000000-0000-0000-0000-000000000002"
HOSTED_USERS = f"insert into auth.users(id) values ('{USER_A}'), ('{USER_B}')"  # noqa: S608
EMPTY_AFTER_CLEANUP = (
    "do $$ begin assert (select count(*) from public.problems) = 0; "
    "assert (select count(*) from public.attempts) = 0; "
    "assert (select count(*) from private.problem_solutions) = 0; end $$"
)


def run(command: list[str], **kwargs: object) -> None:
    # Fixed argument lists built here; no shell and no user-supplied commands.
    subprocess.run(command, check=True, **kwargs)  # noqa: S603


def psql(docker: str, container: str, sql: str) -> None:
    run(
        [docker, "exec", "-i", container, "psql", "-U", "postgres", "-v", "ON_ERROR_STOP=1", "-q"],
        input=sql.encode(),
    )


def wait_ready(docker: str, container: str) -> None:
    for _ in range(60):
        probe = subprocess.run(  # noqa: S603
            [docker, "exec", container, "pg_isready", "-U", "postgres"], capture_output=True
        )
        if probe.returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("PostgreSQL did not become ready")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sql-only", action="store_true", help="skip pytest -m db and e2e")
    args = parser.parse_args()
    docker = shutil.which("docker")
    if docker is None:
        raise RuntimeError("Docker is required for the disposable database")
    container = f"practiceloop-test-{uuid.uuid4().hex[:10]}"
    port = free_port()
    run(
        [
            docker,
            "run",
            "--detach",
            "--name",
            container,
            "--env",
            f"POSTGRES_PASSWORD={PASSWORD}",
            "--publish",
            f"127.0.0.1:{port}:5432",
            "postgres:17",
        ],
        stdout=subprocess.DEVNULL,
    )
    try:
        wait_ready(docker, container)
        read = lambda name: (ROOT / name).read_text(encoding="utf-8")  # noqa: E731
        psql(docker, container, read("supabase/tests/auth_fixture.sql"))
        for migration in sorted((ROOT / "supabase/migrations").glob("*.sql")):
            psql(docker, container, migration.read_text(encoding="utf-8"))
        psql(docker, container, read("supabase/tests/isolation.sql"))
        psql(docker, container, HOSTED_USERS)
        fixture = read("supabase/tests/hosted_fixture.sql")
        fixture = fixture.replace("REPLACE_WITH_USER_A_UUID", USER_A)
        psql(docker, container, fixture.replace("REPLACE_WITH_USER_B_UUID", USER_B))
        psql(docker, container, read("supabase/tests/hosted_schema.sql"))
        psql(docker, container, read("supabase/tests/hosted_cleanup.sql"))
        psql(docker, container, EMPTY_AFTER_CLEANUP)
        print("Migrations, RLS isolation and hosted-check SQL passed")
        if args.sql_only:
            return 0
        env = os.environ | {
            "PRACTICELOOP_TEST_DATABASE_URL": f"postgresql://postgres:{PASSWORD}@127.0.0.1:{port}/postgres"
        }
        backend = ROOT / "backend"
        run([sys.executable, "-m", "app.engine.catalogue"], cwd=backend, env=env)
        run([sys.executable, "-m", "pytest", "-m", "db"], cwd=backend, env=env)
        run(
            [
                sys.executable,
                str(ROOT / "scripts/e2e_local.py"),
                "--stop-db",
                f"docker stop {container}",
                "--start-db",
                f"docker start {container}",
            ],
            cwd=backend,
            env=env,
        )
    finally:
        subprocess.run([docker, "rm", "--force", container], capture_output=True)  # noqa: S603
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
