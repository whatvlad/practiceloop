"""Local end-to-end check of the MVP API against disposable Postgres (#13).

Runs the real FastAPI app under uvicorn on 127.0.0.1, with the real math worker
and a real database, and drives it over HTTP like the frontend does. Only the
Supabase JWKS is replaced by a local ES256 key, so Google sign-in itself is not
covered here: that part is checked by hand on the deployed site.

Never point it at Supabase or shared data: it inserts and deletes auth.users rows.

    cd backend
    PRACTICELOOP_TEST_DATABASE_URL=postgresql://... \
    python ../scripts/e2e_local.py --stop-db "<cmd>" --start-db "<cmd>"

The database must already have supabase/tests/auth_fixture.sql and every
migration applied, as in CI, and the backend installed (pip install --no-deps -e .).
--stop-db/--start-db are optional commands (split like a shell, not run by one)
used for the database-failure check; it is skipped (and reported) without them.
"""

from __future__ import annotations

import argparse
import os
import shlex
import socket
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from uuid import UUID, uuid4

import httpx
import jwt
import psycopg
import uvicorn
from cryptography.hazmat.primitives.asymmetric import ec

ISSUER = "https://e2e.invalid/auth/v1"
KID = "e2e-key"
FAILURES: list[str] = []


def check(condition: bool, label: str, detail: object = "") -> None:
    print(("PASS " if condition else "FAIL ") + label + ("" if condition else f": {detail}"))
    if not condition:
        FAILURES.append(label)


class LocalKeys:
    """Stands in for PyJWKClient: one local ES256 key."""

    def __init__(self) -> None:
        self.private = ec.generate_private_key(ec.SECP256R1())

    def get_signing_key(self, kid: str) -> Any:
        if kid != KID:
            raise jwt.PyJWKClientError("unknown kid")
        return jwt.PyJWK.from_dict(
            {
                **jwt.algorithms.ECAlgorithm.to_jwk(self.private.public_key(), as_dict=True),
                "kid": KID,
                "alg": "ES256",
            }
        )

    def token(self, user: UUID, **overrides: Any) -> str:
        now = int(time.time())
        claims = {
            "sub": str(user),
            "aud": "authenticated",
            "iss": ISSUER,
            "iat": now,
            "exp": now + 3600,
            "role": "authenticated",
            "email": f"{user}@e2e.invalid",
        }
        claims.update(overrides)
        return jwt.encode(claims, self.private, algorithm="ES256", headers={"kid": KID})


def start_server(keys: LocalKeys) -> tuple[uvicorn.Server, str]:
    from app.core.auth import TokenVerifier, token_verifier
    from app.main import app

    app.dependency_overrides[token_verifier] = lambda: TokenVerifier(ISSUER, keys)  # type: ignore[arg-type]
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    base = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            if httpx.get(f"{base}/health", timeout=1).status_code == 200:
                return server, base
        except httpx.HTTPError:
            pass
        time.sleep(0.1)
    raise SystemExit("API did not start")


def reset_limits() -> None:
    from app.api import practice, shares

    for limiter in (
        practice.generation_limit,
        practice.attempt_limit,
        practice.reveal_limit,
        shares.share_limit,
        shares.lookup_limit,
    ):
        limiter.reset()


def correct_answer(url: str, problem_id: str) -> str:
    from app.generators.core import replay

    with psycopg.connect(url) as conn:
        row = conn.execute(
            "select generator_data from private.problem_solutions where problem_id = %s",
            (problem_id,),
        ).fetchone()
    if row is None:
        raise SystemExit(f"no private record for {problem_id}")
    exercise = replay(row[0])
    if exercise.value is not None:
        return str(exercise.value).replace("**", "^").replace("E", "e")
    return str(exercise.primitive).replace("**", "^").replace("Abs", "abs") + " + C"


def key() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid4())}


def full_flow(api: httpx.Client, url: str) -> list[str]:
    topics = api.get("/topics").json()
    cells = [(t["slug"], d) for t in topics["items"] for d in t["availableDifficulties"]]
    cells += [("mixed", d) for d in topics["mixed"]["availableDifficulties"]]
    check(len(cells) == 28, "topics list 23 cells plus 5 mixed levels", len(cells))
    created: list[str] = []
    for topic, level in cells:
        reset_limits()
        label = f"{topic} L{level}"
        response = api.post("/problems", json={"topic": topic, "difficulty": level}, headers=key())
        if response.status_code != 201:
            check(False, f"generate {label}", response.text)
            continue
        problem = response.json()["problem"]
        pid = problem["id"]
        created.append(pid)
        leaked = {"answerLatex", "solution", "generator_data", "steps"} & set(problem)
        check(not leaked and not problem["answerRevealed"], f"generate {label} hides the answer")
        wrong = api.post(f"/problems/{pid}/attempts", json={"answer": "x^9 + 7"}, headers=key())
        check(
            wrong.status_code == 201 and wrong.json()["attempt"]["result"] == "incorrect",
            f"wrong answer {label} is incorrect",
            wrong.text,
        )
        answer = correct_answer(url, pid)
        right = api.post(f"/problems/{pid}/attempts", json={"answer": answer}, headers=key())
        check(
            right.status_code == 201 and right.json()["attempt"]["result"] == "correct",
            f"correct answer {label} ({answer}) is correct",
            right.text,
        )
        revealed = api.post(f"/problems/{pid}/reveal-answer")
        steps = api.post(f"/problems/{pid}/reveal-solution")
        check(
            revealed.status_code == 200
            and revealed.json()["answerLatex"]
            and steps.status_code == 200
            and steps.json()["steps"],
            f"reveal answer and solution {label}",
            (revealed.text, steps.text),
        )
        reopened = api.get(f"/problems/{pid}").json()
        reopened = reopened.get("problem", reopened)
        check(
            reopened.get("answerRevealed")
            and reopened.get("solutionRevealed")
            and reopened.get("attemptCount") == 2
            and reopened["lastAttempt"]["result"] == "correct",
            f"reopen {label} keeps attempts and reveals",
            reopened,
        )
    history = api.get("/problems", params={"limit": 50}).json()
    check(
        {p["id"] for p in history["items"]} == set(created),
        "history lists every generated problem",
        len(history["items"]),
    )
    counts = api.get("/profile").json()["counts"]
    check(str(len(created)) in str(counts), "profile counts the generated problems", counts)
    stats = api.get("/statistics")
    check(stats.status_code == 200, "statistics load", stats.text)
    return created


def cross_user(api_b: httpx.Client, base: str, keys: LocalKeys, alice: UUID, pid: str) -> None:
    for method, path, body in (
        ("GET", f"/problems/{pid}", None),
        ("POST", f"/problems/{pid}/attempts", {"answer": "x + C"}),
        ("POST", f"/problems/{pid}/reveal-answer", None),
        ("POST", f"/problems/{pid}/reveal-solution", None),
    ):
        response = api_b.request(method, path, json=body, headers=key())
        check(
            response.status_code == 404,
            f"other user {method} {path.split('/')[-1]} is 404",
            response.status_code,
        )
    check(api_b.get("/problems").json()["items"] == [], "other user's history is empty")
    bad_tokens = {
        "no token": None,
        "HS256 token": jwt.encode(
            {
                "sub": str(alice),
                "aud": "authenticated",
                "iss": ISSUER,
                "role": "authenticated",
                "iat": int(time.time()),
                "exp": int(time.time()) + 60,
            },
            "secret" * 8,
            "HS256",
            headers={"kid": KID},
        ),
        "expired token": keys.token(alice, exp=int(time.time()) - 60, iat=int(time.time()) - 120),
        "wrong issuer": keys.token(alice, iss="https://evil.invalid/auth/v1"),
        "anon role": keys.token(alice, role="anon"),
        "anonymous user": keys.token(alice, is_anonymous=True),
    }
    for label, token in bad_tokens.items():
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = httpx.get(f"{base}/problems/{pid}", headers=headers)
        check(response.status_code == 401, f"{label} is rejected", response.status_code)


def sharing(api_a: httpx.Client, api_b: httpx.Client, base: str, pid: str) -> None:
    """#37: anyone with the link or code sees the statement, topic and difficulty only."""
    created = api_a.post(f"/problems/{pid}/share")
    check(created.status_code == 201, "owner shares a problem", created.text)
    share = created.json()["share"]
    check(api_b.post(f"/problems/{pid}/share/revoke").status_code == 404, "others cannot revoke")
    for label, path in (("link", share["token"]), ("code", f"code/{share['code']}")):
        response = httpx.get(f"{base}/shares/{path}")  # no Authorization header at all
        body = response.json()
        check(
            response.status_code == 200
            and set(body) == {"problem"}
            and set(body["problem"]) == {"topic", "difficulty", "problemLatex"},
            f"anonymous {label} lookup returns only the public statement",
            response.text,
        )
    check(api_a.post(f"/problems/{pid}/share/revoke").status_code == 200, "owner revokes")
    gone = httpx.get(f"{base}/shares/{share['token']}")
    check(
        gone.status_code == 410 and gone.json()["error"]["code"] == "share_revoked",
        "a revoked link says so",
        gone.text,
    )


MALICIOUS = [
    "__import__('os').system('id')",
    "exec('print(1)')",
    "x.__class__.__bases__",
    "lambda: 1",
    "'; drop table public.attempts; --",
    "x" * 300,
    "9" * 200,
    "x^(x^(x^(x^(x^x))))",
    "(" * 120 + "x" + ")" * 120,
    "factorial(10^9)",
    "\\input{/etc/passwd}",
    "<script>alert(1)</script>",
    "x\x00+C",
    "e^(10^10)",
]


def malicious(api: httpx.Client, pid: str) -> None:
    for answer in MALICIOUS:
        reset_limits()
        started = time.monotonic()
        response = api.post(f"/problems/{pid}/attempts", json={"answer": answer}, headers=key())
        elapsed = time.monotonic() - started
        ok = response.status_code in (201, 422) or (
            response.status_code == 503 and response.json()["error"]["retryable"]
        )
        if response.status_code == 201:
            ok = ok and response.json()["attempt"]["result"] in ("invalid", "incorrect")
        check(
            ok and elapsed < 10 and "Traceback" not in response.text,
            f"malicious answer {answer[:30]!r} -> {response.status_code} in {elapsed:.1f}s",
            response.text[:200],
        )


def saturation(api: httpx.Client, url: str, pid: str) -> None:
    reset_limits()
    answer = correct_answer(url, pid)

    def one(_: int) -> httpx.Response:
        return api.post(f"/problems/{pid}/attempts", json={"answer": answer}, headers=key())

    with ThreadPoolExecutor(12) as pool:
        responses = list(pool.map(one, range(12)))
    codes = [r.status_code for r in responses]
    busy = [r for r in responses if r.status_code == 503]
    check(
        set(codes) <= {201, 503} and 201 in codes and bool(busy),
        "12 concurrent checks: some succeed, the rest are busy, none fail",
        codes,
    )
    retryable = all(
        r.json()["error"]["code"] == "math_worker_unavailable" and r.headers.get("retry-after")
        for r in busy
    )
    check(retryable, "busy responses are retryable with Retry-After")
    after = one(0)
    check(after.status_code == 201, "worker slot is released after saturation", after.text)


def database_failure(api: httpx.Client, stop: str, start: str) -> None:
    subprocess.run(shlex.split(stop), check=True)  # noqa: S603 - operator-supplied
    try:
        response = api.get("/problems", timeout=30)
        body = response.json()
        check(
            response.status_code == 503
            and body["error"]["code"] == "database_unavailable"
            and body["error"]["retryable"],
            "database down -> retryable 503",
            response.text,
        )
        check(
            "psycopg" not in response.text and "postgres" not in response.text.lower(),
            "database error does not leak details",
        )
    finally:
        subprocess.run(shlex.split(start), check=True)  # noqa: S603 - operator-supplied
    for _ in range(30):
        response = api.get("/problems")
        if response.status_code == 200:
            break
        time.sleep(1)
    check(response.status_code == 200, "API recovers once the database is back", response.text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stop-db")
    parser.add_argument("--start-db")
    args = parser.parse_args()
    url = os.environ.get("PRACTICELOOP_TEST_DATABASE_URL", "")
    if not url:
        raise SystemExit("PRACTICELOOP_TEST_DATABASE_URL must name a disposable database")
    os.environ["DATABASE_URL"] = url
    alice, bob = uuid4(), uuid4()
    with psycopg.connect(url) as conn:
        conn.execute("insert into auth.users(id) values (%s), (%s)", (alice, bob))
    keys = LocalKeys()
    server, base = start_server(keys)
    try:
        api_a = httpx.Client(
            base_url=base, timeout=60, headers={"Authorization": f"Bearer {keys.token(alice)}"}
        )
        api_b = httpx.Client(
            base_url=base, timeout=60, headers={"Authorization": f"Bearer {keys.token(bob)}"}
        )
        created = full_flow(api_a, url)
        if created:
            cross_user(api_b, base, keys, alice, created[0])
            sharing(api_a, api_b, base, created[0])
            malicious(api_a, created[0])
            saturation(api_a, url, created[0])
        if args.stop_db and args.start_db:
            database_failure(api_a, args.stop_db, args.start_db)
        else:
            print("SKIP database failure: pass --stop-db and --start-db")
    finally:
        server.should_exit = True
        with psycopg.connect(url) as conn:
            conn.execute("delete from auth.users where id in (%s, %s)", (alice, bob))
    print(f"\n{len(FAILURES)} failed" if FAILURES else "\nAll end-to-end checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
