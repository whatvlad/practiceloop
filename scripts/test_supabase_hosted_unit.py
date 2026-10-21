"""Regression checks: permission-test failures must never become false success."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from typing import Any
from unittest.mock import patch

from test_supabase_hosted import (
    CheckFailure,
    Client,
    check_private,
    denied,
    verify,
    verify_single_user,
)


class StubClient(Client):
    def __init__(self, status: int, data: Any) -> None:
        self.status = status
        self.data = data

    def request(
        self,
        path: str,
        method: str = "GET",
        body: dict[str, Any] | None = None,
        schema: str = "public",
    ) -> tuple[int, Any]:
        return self.status, self.data


class DenialChecks(unittest.TestCase):
    def test_full_isolation_rejects_single_client(self) -> None:
        with self.assertRaises(CheckFailure):
            verify([StubClient(200, {})])

    def test_mutation_requires_database_permission_denial(self) -> None:
        for status, code in (
            (401, "PGRST301"),
            (400, "23503"),
            (404, "PGRST205"),
            (200, "42501"),
            (403, "unknown"),
            (503, "42501"),
        ):
            with self.subTest(status=status, code=code), self.assertRaises(CheckFailure):
                denied(StubClient(status, {"code": code}), "attempts", "POST", {})
        for status in (401, 403):
            denied(StubClient(status, {"code": "42501"}), "attempts", "POST", {})

    def test_private_must_be_unexposed_not_only_denied(self) -> None:
        for status, data in (
            (403, {"code": "42501"}),
            (200, []),
            (404, {"code": "PGRST205"}),
            (406, {"code": "other"}),
        ):
            with self.subTest(status=status), self.assertRaises(CheckFailure):
                check_private(StubClient(status, data))
        check_private(StubClient(406, {"code": "PGRST106"}))

    def test_expired_token_does_not_prove_isolation(self) -> None:
        with self.assertRaises(CheckFailure):
            verify([StubClient(401, {"code": "bad_jwt"})] * 2)

    def test_same_or_anonymous_users_do_not_prove_isolation(self) -> None:
        for anonymous in (False, True):
            user = {"id": "same-user", "role": "authenticated", "is_anonymous": anonymous}
            with self.subTest(anonymous=anonymous), self.assertRaises(CheckFailure):
                verify([StubClient(200, user)] * 2)

    def test_missing_fixture_fails_before_mutation_probes(self) -> None:
        a = StubClient(200, {"id": "a", "role": "authenticated", "is_anonymous": False})
        b = StubClient(200, {"id": "b", "role": "authenticated", "is_anonymous": False})
        with patch("test_supabase_hosted.rows", return_value=[]), self.assertRaises(CheckFailure):
            verify([a, b])


class SingleUserClient(StubClient):
    def __init__(self, leak: bool = False) -> None:
        super().__init__(403, {"code": "42501"})
        self.url = "https://example.supabase.co"
        self.key = "sb_publishable_fixture"
        self.leak = leak

    def request(
        self,
        path: str,
        method: str = "GET",
        body: dict[str, Any] | None = None,
        schema: str = "public",
    ) -> tuple[int, Any]:
        if path == "/auth/v1/user":
            return 200, {
                "id": "00000000-0000-0000-0000-000000000001",
                "role": "authenticated",
                "is_anonymous": False,
            }
        if schema == "private":
            return 406, {"code": "PGRST106"}
        if method != "GET":
            return super().request(path, method, body, schema)
        if path.startswith("/rest/v1/topics?"):
            return 200, [{"id": f"topic-{slot}", "slug": str(slot)} for slot in range(9)]
        if self.leak:
            return 200, [{"id": "someone-else", "user_id": "someone-else"}]
        return 200, []


class SingleUserChecks(unittest.TestCase):
    def test_empty_owner_reads_stay_explicitly_partial(self) -> None:
        anonymous = StubClient(403, {"code": "42501"})
        original = anonymous.request

        def respond(*args: Any, **kwargs: Any) -> tuple[int, Any]:
            if kwargs.get("schema") == "private":
                return 406, {"code": "PGRST106"}
            return original(*args, **kwargs)

        output = StringIO()
        with (
            patch("test_supabase_hosted.Client", return_value=anonymous),
            patch.object(anonymous, "request", side_effect=respond),
            redirect_stdout(output),
        ):
            counts = verify_single_user(SingleUserClient())
        self.assertEqual(counts, {"profiles": 0, "problems": 0, "attempts": 0})
        self.assertIn("PARTIAL", output.getvalue())
        self.assertIn("cross-user isolation", output.getvalue())
        self.assertIn("NOT tested", output.getvalue())

    def test_visible_foreign_owner_fails_single_user_smoke_check(self) -> None:
        with self.assertRaises(CheckFailure):
            verify_single_user(SingleUserClient(leak=True))


if __name__ == "__main__":
    unittest.main()
