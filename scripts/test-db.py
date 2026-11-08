"""Run CI's Database isolation job locally against a disposable PostgreSQL 17.

Mirrors the `database` job in .github/workflows/ci.yml: auth fixture, every
migration in order, RLS isolation, hosted-check SQL, API ownership queries
(`pytest -m db`) and the end-to-end API flow, including its database outage.
Uses Docker (`postgres:17`, as in CI) when it is installed, otherwise native
PostgreSQL 17 binaries (`initdb`, `pg_ctl`, `psql`) found in --pg-bin,
PRACTICELOOP_PG_BIN, .local/postgres/bin (here or in the main checkout),
C:/Program Files/PostgreSQL/17/bin, the WSL setup or PATH. The database lives in a
temporary folder and is removed afterwards.
Needs the backend installed in this Python (README "Local setup"). On Windows,
--wsl reruns this script in WSL after `wsl bash scripts/setup-wsl-tests.sh`,
because the math worker behind most API tests only runs on Linux.
Never point any of these files at Supabase or shared data.

    python scripts/test-db.py            # from the repository root
    python scripts/test-db.py --sql-only # skip pytest and the end-to-end flow
    python scripts/test-db.py --serve    # apply the SQL, print the URL, wait
    python scripts/test-db.py --wsl      # Windows: run it all in WSL (Linux)
"""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol

ROOT = Path(__file__).resolve().parents[1]
PASSWORD = "local-ci-only"  # noqa: S105 - throwaway database, same as CI
USER_A = "00000000-0000-0000-0000-000000000001"
USER_B = "00000000-0000-0000-0000-000000000002"
HOSTED_USERS = f"insert into auth.users(id) values ('{USER_A}'), ('{USER_B}')"  # noqa: S608
EMPTY_AFTER_CLEANUP = (
    "do $$ begin assert (select count(*) from public.problems) = 0; "
    "assert (select count(*) from public.attempts) = 0; "
    "assert (select count(*) from private.problem_solutions) = 0; end $$"
)
WSL_HOME = "~/.local/share/practiceloop"  # scripts/setup-wsl-tests.sh
PG_BIN_DIRS = (
    ROOT / ".local/postgres/bin",
    Path("C:/Program Files/PostgreSQL/17/bin"),
    Path(WSL_HOME).expanduser() / "postgres/usr/lib/postgresql/17/bin",
)


def main_checkout() -> Path:
    # Worktrees share one .local/ in the main checkout.
    try:
        result = subprocess.run(  # noqa: S603
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],  # noqa: S607
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
    except OSError:
        return ROOT
    return Path(result.stdout.strip()).parent if result.returncode == 0 else ROOT


def run(command: list[str], **kwargs: object) -> None:
    # Fixed argument lists built here; no shell and no user-supplied commands.
    subprocess.run(command, check=True, **kwargs)  # noqa: S603


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def command_line(*parts: str | Path) -> str:
    # e2e_local.py splits these like a POSIX shell, so use forward slashes.
    return " ".join(shlex.quote(Path(p).as_posix() if isinstance(p, Path) else p) for p in parts)


class Database(Protocol):
    port: int
    stop_command: str
    start_command: str

    def psql(self, sql: str) -> None: ...


class DockerDatabase:
    def __init__(self, docker: str, port: int) -> None:
        self.docker = docker
        self.port = port
        self.container = f"practiceloop-test-{uuid.uuid4().hex[:10]}"
        self.stop_command = command_line(docker, "stop", self.container)
        self.start_command = command_line(docker, "start", self.container)

    def start(self) -> None:
        run(
            [
                self.docker,
                "run",
                "--detach",
                "--name",
                self.container,
                "--env",
                f"POSTGRES_PASSWORD={PASSWORD}",
                "--publish",
                f"127.0.0.1:{self.port}:5432",
                "postgres:17",
            ],
            stdout=subprocess.DEVNULL,
        )
        for _ in range(60):
            probe = subprocess.run(  # noqa: S603
                [self.docker, "exec", self.container, "pg_isready", "-U", "postgres"],
                capture_output=True,
            )
            if probe.returncode == 0:
                return
            time.sleep(1)
        raise RuntimeError("PostgreSQL did not become ready")

    def remove(self) -> None:
        subprocess.run([self.docker, "rm", "--force", self.container], capture_output=True)  # noqa: S603

    def psql(self, sql: str) -> None:
        run(
            [self.docker, "exec", "-i", self.container]
            + ["psql", "-U", "postgres", "-v", "ON_ERROR_STOP=1", "-q"],
            input=sql.encode(),
        )


class NativeDatabase:
    def __init__(self, bin_dir: Path, data: Path, port: int) -> None:
        self.bin = bin_dir
        self.data = data / "data"
        self.log = data / "postgres.log"
        self.port = port
        pg_ctl = self.tool("pg_ctl")
        options = f"-p {port} -c listen_addresses=127.0.0.1"
        if os.name != "nt":
            options += f" -k {shlex.quote(str(data))}"
        # Unpacked Debian packages keep libpq in usr/lib/x86_64-linux-gnu.
        libs = bin_dir.parent.parent.parent / "x86_64-linux-gnu"
        if os.name != "nt" and libs.is_dir():
            old = os.environ.get("LD_LIBRARY_PATH")
            os.environ["LD_LIBRARY_PATH"] = f"{libs}:{old}" if old else str(libs)
        self.stop_command = command_line(pg_ctl, "stop", "-D", self.data, "-m", "fast", "-w")
        self.start_command = command_line(
            pg_ctl, "start", "-D", self.data, "-l", self.log, "-o", options, "-w"
        )

    def tool(self, name: str) -> Path:
        suffix = ".exe" if os.name == "nt" else ""
        return self.bin / f"{name}{suffix}"

    def start(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".pw") as pwfile:
            pwfile.write(PASSWORD)
        try:
            run(
                [str(self.tool("initdb")), "-D", str(self.data), "-U", "postgres"]
                + ["--pwfile", pwfile.name, "--auth=scram-sha-256", "--encoding=UTF8"]
                + ["--locale=C", "--locale-provider=icu", "--icu-locale=en-US"],
                stdout=subprocess.DEVNULL,
            )
        finally:
            os.unlink(pwfile.name)
        run(shlex.split(self.start_command), stdout=subprocess.DEVNULL)

    def remove(self) -> None:
        subprocess.run(shlex.split(self.stop_command), capture_output=True)  # noqa: S603

    def psql(self, sql: str) -> None:
        run(
            [str(self.tool("psql")), "-h", "127.0.0.1", "-p", str(self.port), "-U", "postgres"]
            + ["-v", "ON_ERROR_STOP=1", "-q"],
            input=sql.encode(),
            env=os.environ | {"PGPASSWORD": PASSWORD, "PGCLIENTENCODING": "UTF8"},
        )


def find_pg_bin(explicit: str | None) -> Path | None:
    candidates = [Path(p) for p in (explicit, os.environ.get("PRACTICELOOP_PG_BIN")) if p]
    candidates += [*PG_BIN_DIRS, main_checkout() / ".local/postgres/bin"]
    initdb = shutil.which("initdb")
    if initdb:
        candidates.append(Path(initdb).parent)
    suffix = ".exe" if os.name == "nt" else ""
    return next((p for p in candidates if (p / f"initdb{suffix}").is_file()), None)


@contextmanager
def disposable_database(pg_bin: str | None, native: bool) -> Iterator[Database]:
    port = free_port()
    docker = None if native else shutil.which("docker")
    if docker is not None:
        database = DockerDatabase(docker, port)
        try:
            database.start()
            yield database
        finally:
            database.remove()
        return
    bin_dir = find_pg_bin(pg_bin)
    if bin_dir is None:
        raise SystemExit(
            "Neither Docker nor PostgreSQL 17 binaries found; see README 'Local database'"
        )
    with tempfile.TemporaryDirectory(prefix="practiceloop-pg-") as folder:
        native_db = NativeDatabase(bin_dir, Path(folder), port)
        try:
            native_db.start()
            yield native_db
        finally:
            native_db.remove()


def apply_ci_sql(database: Database) -> None:
    read = lambda name: (ROOT / name).read_text(encoding="utf-8")  # noqa: E731
    database.psql(read("supabase/tests/auth_fixture.sql"))
    for migration in sorted((ROOT / "supabase/migrations").glob("*.sql")):
        database.psql(migration.read_text(encoding="utf-8"))
    database.psql(read("supabase/tests/isolation.sql"))
    database.psql(HOSTED_USERS)
    fixture = read("supabase/tests/hosted_fixture.sql")
    fixture = fixture.replace("REPLACE_WITH_USER_A_UUID", USER_A)
    database.psql(fixture.replace("REPLACE_WITH_USER_B_UUID", USER_B))
    database.psql(read("supabase/tests/hosted_schema.sql"))
    database.psql(read("supabase/tests/hosted_cleanup.sql"))
    database.psql(EMPTY_AFTER_CLEANUP)
    print("Migrations, RLS isolation and hosted-check SQL passed")


def wsl_ready() -> bool:
    """Whether scripts/setup-wsl-tests.sh has prepared WSL on this Windows PC."""
    if os.name != "nt" or shutil.which("wsl") is None:
        return False
    home = WSL_HOME.replace("~", "$HOME")
    initdb = f"{home}/postgres/usr/lib/postgresql/17/bin/initdb"
    check = f'test -x "{home}/venv/bin/python" && test -x "{initdb}"'
    result = subprocess.run(["wsl", "-e", "bash", "-c", check], capture_output=True)  # noqa: S603,S607
    return result.returncode == 0


def in_wsl(arguments: list[str]) -> int:
    if not wsl_ready():
        raise SystemExit("WSL is not set up; run: wsl bash scripts/setup-wsl-tests.sh")
    script = subprocess.run(  # noqa: S603
        ["wsl", "-e", "wslpath", "-u", str(Path(__file__).resolve())],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    python = WSL_HOME.replace("~", "$HOME") + "/venv/bin/python"
    # $HOME expands inside WSL; the script path and arguments pass through as-is.
    launcher = f'exec "{python}" "$@"'
    command = ["wsl", "-e", "bash", "-c", launcher, "test-db", script, "--native", *arguments]
    return subprocess.run(command).returncode  # noqa: S603,S607


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sql-only", action="store_true", help="skip pytest -m db and e2e")
    parser.add_argument("--serve", action="store_true", help="keep the database until Ctrl+C")
    parser.add_argument("--native", action="store_true", help="use PostgreSQL binaries, not Docker")
    parser.add_argument("--pg-bin", help="folder with initdb, pg_ctl and psql")
    parser.add_argument("--wsl", action="store_true", help="Windows: rerun everything in WSL")
    parser.add_argument("pytest_args", nargs="*", help="extra pytest arguments; skips e2e")
    args = parser.parse_args()
    if args.wsl:
        return in_wsl([a for a in sys.argv[1:] if a != "--wsl"])
    with disposable_database(args.pg_bin, args.native) as database:
        apply_ci_sql(database)
        url = f"postgresql://postgres:{PASSWORD}@127.0.0.1:{database.port}/postgres"
        if args.serve:
            print(f"PRACTICELOOP_TEST_DATABASE_URL={url}\nCtrl+C stops and removes it")
            try:
                while True:
                    time.sleep(3600)
            except KeyboardInterrupt:
                return 0
        if args.sql_only:
            return 0
        backend = ROOT / "backend"
        # PYTHONPATH stands in for CI's `pip install -e .` (a WSL venv has no install).
        path = os.pathsep.join(p for p in (str(backend), os.environ.get("PYTHONPATH")) if p)
        env = os.environ | {"PRACTICELOOP_TEST_DATABASE_URL": url, "PYTHONPATH": path}
        run([sys.executable, "-m", "app.engine.catalogue"], cwd=backend, env=env)
        # addopts deselects db tests; a later -m in pytest_args still wins.
        run([sys.executable, "-m", "pytest", "-m", "db", *args.pytest_args], cwd=backend, env=env)
        if args.pytest_args:
            return 0
        run(
            [sys.executable, str(ROOT / "scripts/e2e_local.py")]
            + ["--stop-db", database.stop_command, "--start-db", database.start_command],
            cwd=backend,
            env=env,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
