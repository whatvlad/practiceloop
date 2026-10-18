"""Human-run PostgREST checks on disposable hosted fixtures; never logs credentials.

No service-role key is needed. Supply two short-lived real Auth access tokens via
hidden prompts, never shell arguments or chat. See supabase/README.md.
"""

import argparse
import getpass
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

TABLES = ("profiles", "topics", "problems", "attempts")
PROBLEMS = tuple(f"31000000-0000-0000-0000-{slot:012d}" for slot in (1, 2))
ATTEMPTS = tuple(f"32000000-0000-0000-0000-{slot:012d}" for slot in (1, 2))


class CheckFailure(Exception):
    """A safe, credential-free verification failure."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward a token to a different location."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


class Client:
    def __init__(self, url: str, key: str, token: str = "") -> None:
        self.url = url
        self.key = key
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(
        self,
        path: str,
        method: str = "GET",
        body: dict[str, Any] | None = None,
        schema: str = "public",
    ) -> tuple[int, Any]:
        headers = {"apikey": self.key, "Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        # Both headers ensure read and mutation requests select the same schema.
        headers["Accept-Profile"] = schema
        headers["Content-Profile"] = schema
        req = urllib.request.Request(  # noqa: S310 -- validated HTTPS origin in main
            self.url + path,
            method=method,
            headers=headers,
            data=None if body is None else json.dumps(body).encode(),
        )
        try:
            response = self.opener.open(req, timeout=20)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            status = response.code
            if status == 204:
                return status, None
            try:
                data = json.loads(response.read(1_000_000))
            except (ValueError, UnicodeError):
                raise CheckFailure("Response is not JSON; check project/API availability") from None
        return status, data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def rows(client: Client, table: str, query: str) -> list[dict[str, Any]]:
    status, data = client.request(f"/rest/v1/{table}?{query}")
    require(status == 200 and isinstance(data, list), f"{table}: expected successful read")
    return data  # type: ignore[no-any-return]


def denied(client: Client, table: str, method: str, body: dict[str, Any] | None) -> None:
    status, data = client.request(f"/rest/v1/{table}?id=eq.{PROBLEMS[0]}", method, body)
    require(
        status in (401, 403) and isinstance(data, dict) and data.get("code") == "42501",
        f"{table} {method}: expected PostgreSQL permission denial (42501)",
    )


def check_private(client: Client) -> None:
    for method in ("GET", "POST", "PATCH", "DELETE"):
        status, data = client.request(
            "/rest/v1/problem_solutions",
            method,
            {} if method in ("POST", "PATCH") else None,
            schema="private",
        )
        require(
            status == 406 and isinstance(data, dict) and data.get("code") == "PGRST106",
            f"private {method}: schema must be unexposed (PGRST106), not merely filtered",
        )


def verify(clients: list[Client]) -> int:
    user_ids: list[str] = []
    for client in clients:
        status, user = client.request("/auth/v1/user")
        require(status == 200 and isinstance(user, dict), "Real authenticated session required")
        require(user.get("role") == "authenticated", "Expected authenticated user role")
        require(user.get("is_anonymous") is False, "Anonymous Auth users are not test users")
        user_ids.append(user["id"])
    require(user_ids[0] != user_ids[1], "Use two different real Auth users")

    for slot, client in enumerate(clients):
        own = user_ids[slot]
        other = user_ids[1 - slot]
        profile = rows(client, "profiles", f"select=id&id=eq.{own}")
        require(profile == [{"id": own}], "Own profile fixture missing")
        require(not rows(client, "profiles", f"select=id&id=eq.{other}"), "Cross-user profile leak")
        for table, ids, owner_col in (
            ("problems", PROBLEMS, "user_id"),
            ("attempts", ATTEMPTS, "user_id"),
        ):
            own_rows = rows(client, table, f"select=id,user_id&id=eq.{ids[slot]}")
            require(
                own_rows == [{"id": ids[slot], owner_col: own}],
                f"{table}: own fixture missing or users supplied in wrong order",
            )
            require(
                not rows(client, table, f"select=id&id=eq.{ids[1 - slot]}"),
                f"{table}: cross-user fixture leaked",
            )
            # Exercise unfiltered RLS too; fixture project must contain <1000 rows.
            all_rows = rows(client, table, "select=id,user_id&limit=1000")
            require(all(row[owner_col] == own for row in all_rows), f"{table}: owner filter failed")
        topics = rows(client, "topics", "select=id,slug")
        require(len(topics) == 5, "Expected five seeded MVP topics")
        bodies = {
            "profiles": {"id": own},
            "topics": {"name": "forged", "slug": "forged"},
            "problems": {
                "user_id": own,
                "topic_id": topics[0]["id"],
                "difficulty": 1,
                "problem_latex": "forged",
            },
            "attempts": {
                "problem_id": PROBLEMS[slot],
                "user_id": own,
                "user_answer": "forged",
                "is_correct": True,
            },
        }
        for table in TABLES:
            for method in ("POST", "PATCH", "DELETE"):
                denied(client, table, method, None if method == "DELETE" else bodies[table])
        check_private(client)
        print(f"PASS: user {slot + 1} own/cross-user reads, browser write denial, private schema")

    anonymous = Client(clients[0].url, clients[0].key)
    for table in TABLES:
        status, data = anonymous.request(f"/rest/v1/{table}?select=id")
        require(
            status in (401, 403) and isinstance(data, dict) and data.get("code") == "42501",
            f"anon {table}: expected permission denial",
        )
        for method in ("POST", "PATCH", "DELETE"):
            denied(anonymous, table, method, None if method == "DELETE" else bodies[table])
    check_private(anonymous)
    print("PASS: anonymous reads/writes denied; private schema unexposed")
    print(
        "Hosted PostgREST checks passed. SQL catalogue/FK checks and API ownership remain separate."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--google-login",
        action="store_true",
        help="Open two real Google logins on localhost:5173, keeping tokens in memory",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = root / ".local/hosted-test-result.json"
    if args.google_login:
        # A failed new run must not leave an older success report looking current.
        report.unlink(missing_ok=True)
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    if args.google_login and not url:
        url = input("Supabase project URL (public HTTPS origin): ").strip().rstrip("/")
    parsed = urllib.parse.urlsplit(url)
    require(
        parsed.scheme == "https"
        and parsed.hostname is not None
        and parsed.hostname.endswith(".supabase.co")
        and parsed.path == ""
        and parsed.username is None
        and parsed.password is None
        and parsed.port is None
        and not parsed.query
        and not parsed.fragment,
        "Set SUPABASE_URL to the hosted HTTPS project origin",
    )
    key = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    if args.google_login and not key:
        key = input("Public sb_publishable_ key (never a secret/service-role key): ").strip()
    require(key.startswith("sb_publishable_"), "Supply only the public sb_publishable_ key")
    require(sys.stdin.isatty(), "Run interactively; access tokens use hidden prompts")
    if args.google_login:
        from supabase_google_test_login import collect_google_tokens

        tokens = collect_google_tokens(url)
    else:
        tokens = [
            getpass.getpass(f"User {slot} short-lived access token (hidden): ") for slot in (1, 2)
        ]
    require(all(tokens), "Both user tokens are required")
    clients = [Client(url, key, token) for token in tokens]
    if args.google_login:
        ids = []
        for client in clients:
            status, user = client.request("/auth/v1/user")
            require(status == 200 and isinstance(user, dict), "Google session verification failed")
            require(user.get("app_metadata", {}).get("provider") == "google", "Google required")
            ids.append(str(UUID(user["id"])))
        require(ids[0] != ids[1], "Use two different Google accounts; rerun the command")
        fixture = (root / "supabase/tests/hosted_fixture.sql").read_text(encoding="utf-8")
        fixture = fixture.replace("REPLACE_WITH_USER_A_UUID", ids[0])
        fixture = fixture.replace("REPLACE_WITH_USER_B_UUID", ids[1])
        output = root / ".local/hosted_fixture.sql"
        output.parent.mkdir(exist_ok=True)
        output.write_text(fixture, encoding="utf-8")
        print(f"Run this generated SQL in the project's SQL Editor: {output}")
        print(f"Then run: {root / 'supabase/tests/hosted_schema.sql'}")
        require(
            input("Type SQL PASSED after both SQL scripts succeed: ").strip() == "SQL PASSED",
            "Hosted SQL checks were not confirmed; no success reported",
        )
    result = verify(clients)
    if args.google_login:
        print(f"Finish by running: {root / 'supabase/tests/hosted_cleanup.sql'}")
        for client in clients:
            status, _ = client.request("/auth/v1/logout?scope=local", "POST", {})
            require(status == 204, "Test-session logout failed; revoke it in Supabase Auth")
        print("Test Supabase sessions signed out; close the callback tabs.")
        report.write_text(
            json.dumps(
                {
                    "timestamp_utc": datetime.now(UTC).isoformat(),
                    "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    "postgrest": "passed",
                    "sql": "human-confirmed passed",
                }
            )
            + "\n",
            encoding="utf-8",
        )
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CheckFailure as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from None
    except (OSError, ValueError, KeyError):
        # Do not dump exception objects, HTTP bodies, headers, URLs or user data.
        print("FAIL: network/configuration/response error; no credentials logged", file=sys.stderr)
        raise SystemExit(1) from None
