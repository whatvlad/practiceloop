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


PARTIAL = "partial-derivatives"


def correct_answer(url: str, problem_id: str) -> str:

    with psycopg.connect(url) as conn:
        row = conn.execute(
            "select generator_data from private.problem_solutions where problem_id = %s",
            (problem_id,),
        ).fetchone()
    if row is None:
        raise SystemExit(f"no private record for {problem_id}")
    # Use the answer kind's trusted expression, not its display LaTeX.
    import sympy as sp

    from app.engine import practice as engine
    from app.engine.answers.antiderivative import AntiderivativeAnswer

    answer = engine.replay(row[0]).answer
    if isinstance(answer, AntiderivativeAnswer):
        value, constant = answer.primitive, " + C"
    else:
        value, constant = answer.expected, ""  # type: ignore[attr-defined]
    return sp.sstr(value).replace("**", "^").replace("Abs", "abs").replace("E", "e") + constant


def private_record(url: str, problem_id: str) -> dict[str, object]:
    with psycopg.connect(url) as conn:
        row = conn.execute(
            "select generator_data from private.problem_solutions where problem_id = %s",
            (problem_id,),
        ).fetchone()
    if row is None:
        raise SystemExit(f"no private record for {problem_id}")
    return dict(row[0])


def key() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid4())}


def full_flow(api: httpx.Client, url: str) -> list[str]:
    topics = api.get("/topics").json()
    # ADR-005: every topic names a listed area, and mixed practice is per area.
    areas = {area["slug"]: area for area in topics["areas"]}
    check(
        all(t["area"] in areas for t in topics["items"]) and "mathematical-analysis" in areas,
        "topics are grouped by listed areas",
        topics["areas"],
    )
    # Keep PR feedback fast: one representative cell per published topic/area.
    # The full level matrix remains covered by catalogue and worksheet tests.
    cells: list[tuple[str, int, dict[str, str]]] = [(t["slug"], 1, {}) for t in topics["items"]]
    cells += [
        ("mixed", d, {"area": slug})
        for slug, area in areas.items()
        if area["mixed"]
        for d in area["mixed"]["availableDifficulties"][:1]
    ]
    check(len(cells) == 23, "one cell for 21 topics plus two mixed levels", len(cells))
    created: list[str] = []
    for topic, level, extra in cells:
        reset_limits()
        label = f"{topic} L{level}" + (f" ({extra['area']})" if extra else "")
        body = {"topic": topic, "difficulty": level, **extra}
        response = api.post("/problems", json=body, headers=key())
        if response.status_code != 201:
            check(False, f"generate {label}", response.text)
            continue
        problem = response.json()["problem"]
        pid = problem["id"]
        created.append(pid)
        leaked = {"answerLatex", "solution", "generator_data", "steps"} & set(problem)
        check(not leaked and not problem["answerRevealed"], f"generate {label} hides the answer")
        answer = correct_answer(url, pid)
        # A numeric wrong answer is valid input for both numeric and symbolic cells.
        # A partial answer keeps its declared variables and adds a nonzero offset.
        wrong_answer = f"({answer}) + 7" if problem["topic"] == PARTIAL else "999999"
        wrong = api.post(f"/problems/{pid}/attempts", json={"answer": wrong_answer}, headers=key())
        check(
            wrong.status_code == 201 and wrong.json()["attempt"]["result"] == "incorrect",
            f"wrong answer {label} is incorrect",
            wrong.text,
        )
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
    # More cells than one 50-item page: follow the cursor.
    listed: set[str] = set()
    params: dict[str, object] = {"limit": 50}
    while True:
        history = api.get("/problems", params=params).json()
        listed |= {p["id"] for p in history["items"]}
        if not history["nextCursor"]:
            break
        params = {"limit": 50, "cursor": history["nextCursor"]}
    check(
        listed == set(created),
        "history lists every generated problem",
        len(listed),
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


def derivatives(api: httpx.Client, base: str, url: str) -> None:
    """#98: a derivative renders, checks, reveals, and reaches history, stats, shares, reports."""
    reset_limits()
    before = api.get("/statistics").json()["checkedAttempts"]
    response = api.post("/problems", json={"topic": "derivatives", "difficulty": 3}, headers=key())
    check(response.status_code == 201, "generate a derivative", response.text)
    if response.status_code != 201:
        return
    problem = response.json()["problem"]
    pid = problem["id"]
    check(
        problem["topic"] == "derivatives" and r"\frac{d}{dx}" in problem["problemLatex"],
        "a derivative statement asks for d/dx",
        problem["problemLatex"],
    )
    answer = correct_answer(url, pid)
    plus_c = api.post(f"/problems/{pid}/attempts", json={"answer": answer + " + C"}, headers=key())
    attempt = plus_c.json().get("attempt", {})
    check(
        (attempt.get("result"), attempt.get("feedbackCode")) == ("incorrect", None),
        "a native derivative with + C is incorrect",
        plus_c.text,
    )
    right = api.post(f"/problems/{pid}/attempts", json={"answer": answer}, headers=key())
    check(right.json().get("attempt", {}).get("result") == "correct", "a derivative checks", answer)
    revealed = api.post(f"/problems/{pid}/reveal-answer").json()["answerLatex"]
    check("+ C" not in revealed, "a revealed derivative has no constant", revealed)
    history = api.get("/problems", params={"limit": 50}).json()["items"]
    listed = any(p["id"] == pid and p["topic"] == "derivatives" for p in history)
    check(listed, "a derivative appears in history")
    after = api.get("/statistics").json()["checkedAttempts"]
    check(after == before, "+ C statistics leave derivatives out", (before, after))
    shared = api.post(f"/problems/{pid}/share").json()["share"]
    lookup = httpx.get(f"{base}/shares/{shared['token']}").json()["problem"]
    check(lookup["topic"] == "derivatives", "a derivative can be shared", lookup)
    reported = api.post(f"/problems/{pid}/report", json={"category": "statement"})
    check(reported.status_code == 201, "a derivative can be reported", reported.text)
    mixed = api.post(
        "/problems", json={"topic": "mixed", "area": "derivatives", "difficulty": 1}, headers=key()
    )
    drawn = mixed.json().get("problem", {}).get("topic") if mixed.status_code == 201 else None
    check(
        drawn in {"derivatives", PARTIAL},
        "mixed derivatives practice draws within its area",
        mixed.text,
    )


def combinations(api: httpx.Client, url: str) -> None:
    """#169: the new-engine topic stores only its problem code, which replays the problem."""
    from app.engine import practice as engine

    reset_limits()
    catalogue = api.get("/topics").json()
    listed = {t["slug"]: t for t in catalogue["items"]}
    check(
        listed.get("combinations", {}).get("area") == "algebra",
        "combinations is listed under Algebra",
        listed.get("combinations"),
    )
    algebra = next((a for a in catalogue["areas"] if a["slug"] == "algebra"), {})
    weights = (algebra.get("mixed") or {}).get("weights", {})
    # #191 publishes the mixed weight; #192 supplies worksheet pools.
    check(weights.get("combinations") == 1, "combinations is in Algebra mixed practice", weights)
    response = api.post("/problems", json={"topic": "combinations", "difficulty": 1}, headers=key())
    check(response.status_code == 201, "generate a combinations problem", response.text)
    if response.status_code != 201:
        return
    problem = response.json()["problem"]
    pid = problem["id"]
    record = private_record(url, pid)
    check(
        set(record) == {"generator_version", "code"}
        and record["generator_version"] == "combinations-v1"
        and str(record["code"]).startswith("CMB-1-"),
        "a combinations problem stores its problem code",
        record,
    )
    replayed = engine.public_replay(record)
    check(
        replayed.statement == problem["problemLatex"] and r"\binom" in problem["problemLatex"],
        "replaying the code gives the same statement",
        (replayed.statement, problem["problemLatex"]),
    )
    check(
        str(record["code"]) not in response.text and "code" not in problem,
        "the problem code stays private",
        response.text,
    )
    shared = api.get(f"/problems/{pid}").text
    check(str(record["code"]) not in shared, "a reopened problem hides its code")
    fraction = api.post(f"/problems/{pid}/attempts", json={"answer": "1/2"}, headers=key())
    check(
        fraction.json().get("attempt", {}).get("result") == "incorrect",
        "a non-integer count is incorrect",
        fraction.text,
    )
    answer = replayed.answer_latex
    right = api.post(f"/problems/{pid}/attempts", json={"answer": f"{answer}/1"}, headers=key())
    check(right.json().get("attempt", {}).get("result") == "correct", "an equal fraction checks")
    steps = api.post(f"/problems/{pid}/reveal-solution").json()
    check(
        steps.get("steps") == list(replayed.steps) and "visual" not in steps,
        "the solution is the replayed steps, with no visual",
        steps,
    )
    sheet = api.post(
        "/worksheets",
        json={
            "source": "generate",
            "groups": [{"topic": "combinations", "difficulty": 1, "count": 3}],
            "solutions": True,
        },
        headers=key(),
    )
    check(sheet.status_code == 201, "generate a combinations worksheet from the pool", sheet.text)
    if sheet.status_code == 201:
        ids = sheet.json()["worksheet"]["problemIds"]
        check(len(ids) == 3, "the worksheet has three problems", ids)
        records = [private_record(url, pid) for pid in ids]
        check(len({r["code"] for r in records}) == 3, "worksheet codes do not repeat", records)
        for pid, record in zip(ids, records, strict=True):
            opened = api.get(f"/problems/{pid}").json()
            pooled = engine.pooled(record)
            check(
                opened["problem"]["problemLatex"] == pooled.statement
                and opened["answer"]["answerLatex"] == pooled.answer_latex
                and opened["solution"]["steps"] == list(pooled.steps),
                "worksheet stores the pooled statement, answer and steps",
                opened,
            )


def partials(api: httpx.Client, url: str) -> None:
    """#101: declared variables, θ, coordinate changes and mistake feedback."""
    from app.engine import practice as engine

    reset_limits()
    response = api.post("/problems", json={"topic": PARTIAL, "difficulty": 4}, headers=key())
    check(response.status_code == 201, "generate a coordinate change", response.text)
    if response.status_code != 201:
        return
    problem = response.json()["problem"]
    pid = problem["id"]
    check(r"\theta" in problem["problemLatex"], "a coordinate change names θ", problem)
    record = private_record(url, pid)
    issued = engine.public_replay(record)
    answer = correct_answer(url, pid).replace("theta", "θ")
    xy = api.post(f"/problems/{pid}/attempts", json={"answer": "x*y"}, headers=key())
    check(
        xy.json().get("attempt", {}).get("result") == "invalid",
        "an answer in x, y is invalid where r, θ is asked",
        xy.text,
    )
    text = f"({correct_answer(url, pid)}) + 1"
    mistake = api.post(f"/problems/{pid}/attempts", json={"answer": text}, headers=key())
    attempt = mistake.json().get("attempt", {})
    check(
        (attempt.get("result"), attempt.get("feedbackCode")) == ("incorrect", None),
        f"a shifted native partial answer is incorrect ({text})",
        mistake.text,
    )
    right = api.post(f"/problems/{pid}/attempts", json={"answer": answer}, headers=key())
    check(right.json().get("attempt", {}).get("result") == "correct", "θ answer checks", answer)
    revealed = api.post(f"/problems/{pid}/reveal-solution").json()["steps"]
    check(
        revealed == list(issued.steps) and len(revealed) == 4,
        "the solution shows each chain-rule step",
        revealed,
    )


def multiple_integral(api: httpx.Client, url: str, topic: str, starts: tuple[str, ...]) -> None:
    """#99, #100: a multiple integral is one exact number, outside the + C statistics."""
    name = topic.replace("-", " ")[:-1]
    reset_limits()
    before = api.get("/statistics").json()["checkedAttempts"]
    response = api.post("/problems", json={"topic": topic, "difficulty": 3}, headers=key())
    check(response.status_code == 201, f"generate a {name}", response.text)
    if response.status_code != 201:
        return
    problem = response.json()["problem"]
    pid = problem["id"]
    check(
        any(start in problem["problemLatex"] for start in starts),
        f"a {name} shows a region or iterated bounds",
        problem["problemLatex"],
    )
    answer = correct_answer(url, pid)
    flipped = api.post(f"/problems/{pid}/attempts", json={"answer": f"-({answer})"}, headers=key())
    attempt = flipped.json().get("attempt", {})
    check(
        (attempt.get("result"), attempt.get("feedbackCode")) == ("incorrect", None),
        f"a negated native {name} is incorrect with general feedback",
        flipped.text,
    )
    right = api.post(f"/problems/{pid}/attempts", json={"answer": answer}, headers=key())
    check(right.json().get("attempt", {}).get("result") == "correct", f"a {name} checks")
    after = api.get("/statistics").json()["checkedAttempts"]
    check(after == before, f"+ C statistics leave {name}s out", (before, after))


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


def permanent_code_flow(api: httpx.Client, base: str, url: str) -> None:
    from app.engine.codes import encode

    reset_limits()
    code = encode("CMB", 1, 198)
    with httpx.Client(base_url=base, timeout=10) as guest:
        found = guest.get("/codes", params={"code": code.lower().replace("-", " ")})
        check(
            found.status_code == 200
            and set(found.json()["problem"]) == {"topic", "difficulty", "problemLatex"},
            "permanent code opens publicly without private data",
            found.text,
        )
        invalid = guest.get("/codes", params={"code": code[:-2] + "99"})
        unknown = guest.get("/codes", params={"code": encode("ZZZ", 1, 0)})
        check(
            invalid.status_code == unknown.status_code == 400,
            "wrong checksum and unknown prefix are clear errors",
        )
    headers = key()
    created = api.post("/codes/practice", json={"code": code}, headers=headers)
    replayed = api.post("/codes/practice", json={"code": code.lower()}, headers=headers)
    check(
        created.status_code == 201 and replayed.json() == created.json(),
        "permanent code practice is saved once on retry",
        created.text,
    )
    if created.status_code != 201:
        return
    problem = created.json()["problem"]
    pid = problem["id"]
    check(
        not problem["answerRevealed"] and not problem["solutionRevealed"],
        "code practice starts with both reveals hidden",
    )
    checked = api.post(
        f"/problems/{pid}/attempts", json={"answer": correct_answer(url, pid)}, headers=key()
    )
    check(
        checked.status_code == 201 and checked.json()["attempt"]["result"] == "correct",
        "code practice uses normal answer checking",
        checked.text,
    )
    answer = api.post(f"/problems/{pid}/reveal-answer")
    solution = api.post(f"/problems/{pid}/reveal-solution")
    check(
        answer.status_code == solution.status_code == 200 and bool(solution.json()["steps"]),
        "code practice reveals only on request",
    )


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
            derivatives(api_a, base, url)
            multiple_integral(api_a, url, "double-integrals", (r"\iint_D", r"\int_"))
            multiple_integral(api_a, url, "triple-integrals", (r"\iiint_E", r"\int_"))
            partials(api_a, url)
            combinations(api_a, url)
            permanent_code_flow(api_a, base, url)
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
