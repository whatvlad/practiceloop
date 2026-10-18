"""Human-run, loopback-only Google sessions for the hosted isolation test.

This is test tooling, not application authentication (#5). Session tokens stay in
process memory. No service-role key, external scripts or token logging are used.
"""

import json
import secrets
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

ORIGIN = "http://localhost:5173"
PAGE = b"""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="referrer" content="no-referrer"><title>PracticeLoop isolation check</title>
<h1>PracticeLoop test session</h1><p id="status">Receiving Google session...</p>
<script>
const fragment = new URLSearchParams(location.hash.slice(1));
history.replaceState(null, '', location.pathname);
const token = fragment.get('access_token');
fragment.delete('access_token'); fragment.delete('refresh_token');
if (!token) {
  document.getElementById('status').textContent =
    'No session received. Return to the terminal and check Google configuration.';
} else {
  fetch(location.pathname + '/token', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({access_token: token})
  }).then(response => {
    document.getElementById('status').textContent = response.ok
      ? 'Session received. Close this tab and return to the terminal.'
      : 'Session rejected. Return to the terminal.';
  }).catch(() => {
    document.getElementById('status').textContent = 'Local connection failed.';
  });
}
</script></html>"""


def handler_for(nonce: str, captured: list[str]) -> type[BaseHTTPRequestHandler]:
    callback = f"/callback/{nonce}"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args: Any) -> None:
            # Never log callback URLs, bodies, tokens or authorization errors.
            pass

        def do_GET(self) -> None:  # noqa: N802 -- stdlib handler method name
            if self.headers.get("Host") != "localhost:5173" or self.path != callback:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; script-src 'unsafe-inline'; connect-src 'self'; "
                "frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
            )
            self.end_headers()
            self.wfile.write(PAGE)

        def do_POST(self) -> None:  # noqa: N802 -- stdlib handler method name
            if (
                self.headers.get("Host") != "localhost:5173"
                or self.headers.get("Origin") != ORIGIN
                or self.path != callback + "/token"
                or self.headers.get("Content-Type") != "application/json"
            ):
                self.send_error(403)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size < 20_000:
                    raise ValueError
                data = json.loads(self.rfile.read(size))
                token = data.get("access_token")
                if not isinstance(token, str) or not 16 < len(token) < 16_384:
                    raise ValueError
            except (ValueError, AttributeError):
                self.send_error(400)
                return
            if captured:
                self.send_error(409)
                return
            captured.append(token)
            self.send_response(204)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

    return Handler


def collect_google_tokens(project_url: str) -> list[str]:
    tokens: list[str] = []
    for slot in (1, 2):
        nonce = secrets.token_urlsafe(32)
        captured: list[str] = []
        handler = handler_for(nonce, captured)
        # Fixed registered localhost callback, bound only to IPv4 loopback.
        with HTTPServer(("127.0.0.1", 5173), handler) as server:
            server.timeout = 1
            params = urllib.parse.urlencode(
                {
                    "provider": "google",
                    "redirect_to": f"{ORIGIN}/callback/{nonce}",
                    "prompt": "select_account",
                }
            )
            login_url = f"{project_url}/auth/v1/authorize?{params}"
            print(f"Sign in with Google test account {slot} in your browser.")
            if slot == 2:
                print("Select a DIFFERENT Google account from the first one.")
            print(f"If no tab opens, open this public login URL: {login_url}")
            webbrowser.open(login_url)
            deadline = time.monotonic() + 300
            while not captured and time.monotonic() < deadline:
                server.handle_request()
            if not captured:
                raise TimeoutError("Google test login did not complete in five minutes")
            tokens.append(captured[0])
    return tokens
