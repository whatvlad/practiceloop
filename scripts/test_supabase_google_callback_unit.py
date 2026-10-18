"""The test callback accepts only a bounded, same-origin request with its nonce."""

import http.client
import json
import threading
import unittest
from http.server import HTTPServer
from typing import Any

from supabase_google_test_login import handler_for


class CallbackChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.tokens: list[str] = []
        self.server = HTTPServer(("127.0.0.1", 0), handler_for("test-nonce", self.tokens))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def request(
        self,
        path: str = "/callback/test-nonce/token",
        origin: str = "http://localhost:5173",
        host: str = "localhost:5173",
        body: Any = None,
        method: str = "POST",
    ) -> tuple[int, bytes, dict[str, str]]:
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            conn.request(
                method,
                path,
                body=None if body is None else json.dumps(body),
                headers={"Host": host, "Origin": origin, "Content-Type": "application/json"},
            )
            response = conn.getresponse()
            return response.status, response.read(), dict(response.getheaders())
        finally:
            conn.close()

    def test_rejects_wrong_origin_host_and_nonce(self) -> None:
        for overrides in (
            {"origin": "https://example.invalid"},
            {"host": "127.0.0.1:5173"},
            {"path": "/callback/wrong-nonce/token"},
        ):
            with self.subTest(overrides=overrides):
                self.assertEqual(self.request(**overrides)[0], 403)
        self.assertEqual(self.tokens, [])

    def test_rejects_empty_malformed_and_oversized_token(self) -> None:
        bodies: list[Any] = [{}, [], {"access_token": 3}, {"access_token": "x" * 16_384}]
        for body in bodies:
            with self.subTest(body_type=type(body).__name__):
                self.assertEqual(self.request(body=body)[0], 400)
        self.assertEqual(self.tokens, [])

    def test_accepts_once_without_echoing_token(self) -> None:
        token = "fixture-token-is-not-real"  # noqa: S105 -- synthetic, never accepted by Supabase
        status, body, _ = self.request(body={"access_token": token})
        self.assertEqual(status, 204)
        self.assertEqual(body, b"")
        self.assertEqual(self.tokens, [token])
        self.assertEqual(self.request(body={"access_token": token})[0], 409)

    def test_callback_disables_cache_external_requests_and_framing(self) -> None:
        status, page, headers = self.request(path="/callback/test-nonce", method="GET")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertIn("connect-src 'self'", headers["Content-Security-Policy"])
        self.assertIn(b"history.replaceState", page)


if __name__ == "__main__":
    unittest.main()
