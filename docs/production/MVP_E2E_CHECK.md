# MVP end-to-end check (#13)

Two parts: an automated run of the real API against disposable Postgres, and a
short manual pass on the deployed site for what only a person with a Google
account can do.

## Automated: `scripts/e2e_local.py`

Starts the real FastAPI app under uvicorn, with the real math worker and a real
database, and drives it over HTTP. Only the Supabase JWKS is swapped for a
local ES256 key. CI runs it in the Database isolation job; locally:

```sh
cd backend
pip install --no-deps -e .
PRACTICELOOP_TEST_DATABASE_URL=postgresql://... python ../scripts/e2e_local.py \
  --stop-db "<command that stops Postgres>" --start-db "<command that starts it>"
```

It covers:

- **Practice flow**, for every offered cell (23 topic/level cells and 5 mixed
  levels): generate, the response hides the answer, a wrong attempt is
  `incorrect`, the exact answer is `correct`, reveal answer, reveal solution,
  reopen shows both attempts and both reveals, history lists every problem,
  profile counts and statistics load.
- **Cross-user denial**: a second user gets 404 for the first user's problem,
  attempts and reveals, and sees an empty history. No token, an HS256 token,
  an expired token, a wrong issuer, the `anon` role and an anonymous user are
  all 401.
- **Malicious input**: code injection, SQL, LaTeX `\input`, HTML, deep nesting,
  huge powers, oversized input and a NUL byte are each `invalid`/`incorrect`
  or 422, within 10 s, with no traceback.
- **Worker saturation**: 12 concurrent checks give only 201 or a retryable 503
  `math_worker_unavailable` with `Retry-After`, and the slot is free afterwards.
- **Database failure** (only with `--stop-db`/`--start-db`; CI skips it):
  requests get a retryable 503 `database_unavailable` that names no database
  internals, and the API recovers when Postgres is back.

Run on 2026-10-20: 175 checks passed. The first run found that an answer or
profile name containing a NUL byte gave a 500 (PostgreSQL text cannot hold
NUL); both are now a 422.

The math corpus itself (every generated record's answer accepted, wrong
answers and adversarial inputs classified within the worker limits) is in
`backend/tests/test_answer_check.py`, `test_families.py`, `test_definite.py`
and `test_math_worker.py`.

## Manual: deployed site

On https://mathloop.pages.dev, ideally in a private window:

1. Sign in with Google. You land back on the site, signed in.
2. Choose a topic and level, generate a problem.
3. Submit a wrong answer: it says incorrect. Submit the right one: correct.
4. Reveal the answer, then the full solution.
5. Open History, reopen that problem: both attempts and both reveals are there.
6. Reload the page and open the problem again: still there.
7. Open Profile: the counts include this problem.
8. Sign out, sign in with a second Google account: the first account's problem
   is not in its history.
