# Untracked generated practice (#34)

This slice replaces the repeating browser mock behind `data/api.ts`. The existing
Google login is unchanged. It does **not** implement account-backed practice,
persisted history, or the authenticated `/api/problems` contract.

## Supported generation

| Topic | Level | Distinct records per cycle | Method |
|---|---|---|---|
| Basic integrals | 1 | 42 | Direct constant, power, exponential, sine or cosine |
| Basic integrals | 2 | 36 | Separate two direct terms |
| Substitution | 1 | 36 | Visible derivative pair with inner `x²+b` |
| Substitution | 2 | 72 | Affine inner expression and constant-factor adjustment |

These cells follow ADR-003. Other topics and levels are disabled, not mislabeled
copies of easy problems. All 186 records start with a known primitive and derive
the displayed integrand. Coefficients are bounded small integers. All domains are
the real line; every answer is indefinite and needs an arbitrary constant.
Basic records retain `basic-v1`; substitution uses `substitution-v1` with a
validated family, coefficient, offset, scale and level. No serialized expressions
or browser-chosen parameters enter reconstruction.

Each session gets a shuffled bag per topic/level. Every distinct record is used
once before reshuffling, and the cycle boundary cannot repeat the last exercise.
The finite pool is intentional: this does not promise infinitely unique problems.
Canonical substitution steps explicitly verify the chain-rule identity, integrate
the outer expression, and substitute back. All records and replay are tested.

## Separate preview boundary

Browser requests go to `/api/preview/*` through the existing Pages proxy; FastAPI
receives `/preview/*`. Vite proxies local `/api` to `127.0.0.1:8000`.

- `POST /preview/sessions`: returns a random 256-bit opaque capability token.
- `GET /preview/topics`: advertises only the four supported cells.
- `POST /preview/problems`: `{topic, difficulty}`, returns the existing public
  frontend problem shape, never a record, answer or solution.
- `POST /preview/problems/{id}/attempts`: `{answer}`, returns `result` and
  `feedbackCode`. Missing constant is `incorrect` + `missing_constant`, rendered
  as a dedicated reminder. No expected answer is returned.
- `POST /preview/problems/{id}/reveal-answer` and `/reveal-solution`: explicit
  reveals scoped to the same capability session.

All problem operations require `Authorization: Bearer <preview token>`. This
token is **not** a Supabase JWT and conveys no account or database permissions.
No account IDs, answers, results or history are persisted by these endpoints.
Tokens and public browser history stay only in page memory. Identity changes,
reloads and deployments discard the relevant temporary state. Server sessions
expire after one hour. Missing and other-session IDs both return 404.

The single-process Oracle preview has at most 256 sessions and 200 problem
references per session. Global admission is 120 session/problem operations per
minute (429 + Retry-After); session capacity yields 503. This deliberately simple
global limit can throttle all preview users; multi-process/account-backed scaling
belongs to the authenticated workflow, not this temporary store.
Body size is capped at 4096 bytes before JSON validation. Errors do not echo input.
Responses are `no-store`; there is no demo fallback when the server is down.

## Mathematical checking and safety

The shared #8 checker, allowlisted parser and killable Linux child are reused.
`preview_check.py` only limits concurrency and translates the shared result.
For all-real cells a child checks every original syntax subtree's real domain before simplification so
`x/x` and cancelled logarithms cannot conceal holes. Symbolic differentiation
proves equality; the shared checker uses bounded high-precision counterexamples
to reject differences. Numeric sampling never
proves correctness. Constants must reduce to an affine `aK+b` with nonzero real
numeric `a`, as in ADR-003. Syntax/domain errors are `invalid`; unproved cases,
worker failure and saturation return retryable 503, not a guessed verdict.
This additional pre-evaluation guard covers the all-real preview cells; other
domains retain #8's component-aware checks. The known cancelled-log domain-hole
case now returns invalid instead of inconclusive through the worker.

One check runs at a time under 2 CPU seconds, 3 wall seconds, 256 MiB address
space and 64 KiB combined output. One slot leaves parent headroom in Oracle's
512 MiB service limit. All children are killed/reaped on failure. #8 still owns
general equivalence across other domains and definite integrals.

## Educational content

`backend/app/content/en.json` is shared with TypeScript and packaged with Python.
Python `TextKey` and TypeScript's inferred JSON keys type the catalogue. Text and
formulae remain separate. No template currently needs placeholders: braces and
markup are critical errors, so missing/unused/untyped placeholders cannot ship.
When dynamic placeholders are needed, add explicit typed schemas first.

Run `npm run lint:content` in `frontend` (Python 3.12+) or
`python scripts/check_content.py` at the root. CI uses the same checker and tests
its failures. Missing/unknown keys, empty/non-string text, unsupported placeholders,
inconsistent terminology and instruction text without an approved action verb
are critical. Sentences over 20 words and missing terminal periods each subtract
25 points from 100; scores below 80 fail. Reports name file, key, rule and remedy.
These deterministic house rules are STE-inspired, not ASD certification or a
complete assessment of clarity. There is no runtime rewriting or external service.

## Verification and release

The regression suite exhausts all records and bag cycles, checks private/public
boundaries, cross-session denial, invalid cells, request bounds, expiry, rate
limits, equivalent expressions and domain traps. Client tests cover duplicate
clicks, stale identity responses, unavailable cells, failures and explicit reveals.
Before release, verify the actual generate/check/reveal flow through Pages, not
only `/health`. #34 explicitly requires independent review and human approval
before merge. A local/PR implementation is not a verified deployed preview.
