# API contract

Implemented: `GET /health` returns `200 {"status":"ok"}` (liveness only), the
separate [untracked preview API](../architecture/PREVIEW_PRACTICE.md) under
`/preview`, and (#10, `backend/app/api/practice.py`) the saved-practice routes
`GET /api/topics`, `POST /api/problems`, `POST /api/problems/{id}/attempts`,
`/reveal-answer` and `/reveal-solution`. `GET /api/problems`,
`GET /api/problems/{id}` and `GET /api/profile` belong to #12 and are not
implemented yet. The browser calls `/api/...` on the Pages origin; the proxy
strips `/api`, so FastAPI serves these at `/topics`, `/problems`, ... like
`/preview`. The proxy forwards `Idempotency-Key`. Saved practice needs
`DATABASE_URL` on the host (docs/production/ORACLE_DEPLOY.md); without it these
routes return `503 database_unavailable`.

Generation picks a random record from the cell's verified catalogue, skipping the
records behind the user's latest half-catalogue in that cell, so a learner sees
no repeat within that window. Only the cells the generators support are offered
(basic integrals and substitution, levels 1 and 2); other cells return 422.
Idempotency keys live in `private.idempotency_keys` (migration
`202610190001_practice_persistence.sql`) and expire after 24 hours. Rate limits
are per user and per process: 30 generations, 30 attempts and 60 reveals a minute.

All routes documented here require `Authorization: Bearer <Supabase access token>`.
The backend verifies the token and takes the user ID only from its `sub` claim.
Verification (#4, `backend/app/core/auth.py`, dependency `current_user`) accepts
only tokens signed with the project's asymmetric Supabase keys (ES256 or RS256)
from `<SUPABASE_URL>/auth/v1/.well-known/jwks.json`; shared-secret (HS256) and
unsigned tokens are always rejected. It requires `exp`, `iat`, `iss` (the
project's `SUPABASE_JWT_ISSUER`), `aud = authenticated`, `role = authenticated`,
a UUID `sub`, and not `is_anonymous`. Keys are cached and refetched when a token
names an unknown `kid` (rotation), at most once per 30 seconds. Owner-scoped SQL
for problems, attempts and reveals is in `backend/app/services/owned_records.py`;
route handlers use those functions rather than writing their own queries.
Request and response bodies use JSON, UUIDs are lowercase strings and timestamps
are UTC RFC 3339 strings. Unknown request fields are rejected.

The untracked preview slice in #34 and the one anonymous demo in #35 use a
separate non-persistent boundary. They must not write anonymous problems or
attempts through these authenticated routes.

## Shared shapes

```json
{
  "problem": {
    "id": "uuid",
    "topic": "basic-integrals",
    "difficulty": 1,
    "problemLatex": "\\int 3x^2\\,dx",
    "createdAt": "2026-10-19T12:00:00Z",
    "answerRevealed": false,
    "solutionRevealed": false,
    "lastAttempt": null
  }
}
```

`topic` is one of `basic-integrals`, `substitution`, `integration-by-parts`,
`rational-functions`, or `trigonometric-integrals`; `difficulty` is `1..5`.
`lastAttempt`, when present, contains `answer`, `result` and `feedbackCode`.
`result` is exactly `correct`, `incorrect` or `invalid`.
`feedbackCode` is `missing_constant` or `null`; it is never an expected answer.

Errors have one envelope:

```json
{"error":{"code":"problem_not_found","message":"Problem not found.","retryable":false}}
```

Messages are safe learner-facing text. Logs, errors, OpenAPI examples and check
responses never include expected answers, solution steps or generator data.

## Routes

### `GET /api/topics`

Returns only implemented template cells:

```json
{"items":[{"slug":"basic-integrals","name":"Basic integrals","availableDifficulties":[1,2]}]}
```

### `POST /api/problems`

Requires `Idempotency-Key: <UUIDv4>`.

```json
{"topic":"basic-integrals","difficulty":1}
```

Returns `201` and the shared problem shape after the public problem, private
solution and idempotency record commit atomically. An exact replay returns the
same status/body with `Idempotency-Replayed: true` and creates no second problem.

### `POST /api/problems/{id}/attempts`

Requires `Idempotency-Key: <UUIDv4>`.

```json
{"answer":"x^3 + C"}
```

Returns `201` after the result and idempotency record commit:

```json
{"attempt":{"id":"uuid","answer":"x^3 + C","result":"correct","feedbackCode":null,"createdAt":"2026-10-19T12:01:00Z"}}
```

An invalid expression is a persisted domain result with `result: "invalid"`, not
an HTTP validation error. A missing integration constant returns
`result: "incorrect"` and `feedbackCode: "missing_constant"`. Empty input or an
answer longer than the ADR-003 limit is rejected before an attempt is created.

### `POST /api/problems/{id}/reveal-answer`

Returns `200` and sets the answer flag in the same transaction:

```json
{"answerLatex":"x^3 + C"}
```

### `POST /api/problems/{id}/reveal-solution`

Returns `200` and sets both reveal flags in the same transaction:

```json
{"steps":[{"say":"Use the power rule.","latex":"\\int x^n\\,dx=\\frac{x^{n+1}}{n+1}+C"}]}
```

Both reveal routes are naturally idempotent. They return the already authorized
payload when repeated.

### `GET /api/problems`

Accepts `limit` (`1..50`, default `20`) and opaque `cursor`. Returns newest first
by `(created_at, id)`:

```json
{"items":[{"id":"uuid","topic":"basic-integrals","difficulty":1,"problemLatex":"\\int 3x^2\\,dx","createdAt":"2026-10-19T12:00:00Z","answerRevealed":false,"solutionRevealed":false,"lastAttempt":null}],"nextCursor":null}
```

The cursor is stable for rows already seen. Newly generated problems appear only
when pagination restarts without a cursor.

### `GET /api/problems/{id}`

Returns `200` and the shared problem shape. If a reveal flag is true, the response
also includes the corresponding previously authorized `answer` or `solution`.

### `GET /api/profile`

```json
{"account":{"id":"uuid","name":"Ada","email":"ada@example.test","provider":"Google"},"counts":{"generated":4,"attempted":3,"correct":2}}
```

Counts use ADR-004 distinct-problem semantics. `name` is nullable. Account data
comes from the verified session/profile, never client-supplied identity fields.

## HTTP failures and retry behavior

| Status | Code | Meaning / retry |
|---|---|---|
| `401` | `authentication_required`, `invalid_token` | Missing or failed token; refresh/re-authenticate, do not blindly retry |
| `404` | `problem_not_found` | Missing and other-user IDs are intentionally indistinguishable |
| `409` | `idempotency_conflict` | Same key with different input; create a new key only for a deliberate new action |
| `422` | `invalid_request` | Malformed JSON, unknown field, empty answer, unsupported topic/level or normalized input over 256 bytes |
| `429` | `rate_limited` | Retry only after the `Retry-After` delay |
| `503` | `authentication_unavailable`, `math_worker_unavailable`, `math_check_inconclusive`, `database_unavailable` | No mutation committed; retry with the same idempotency key only when `retryable` is true |

Unexpected failures return a generic `500 internal_error` with a correlation ID,
not exception text. Client disconnects do not cancel a database commit already in
progress; the client repeats the request with the same idempotency key to learn
the committed outcome.

## Ownership and atomicity

Every problem, attempt, reveal, history and profile query is scoped to the
verified user in SQL even though the backend service role bypasses RLS. All
access to another user's problem returns the same `404` as a missing UUID.
Transaction and retry boundaries are defined in ADR-004; mathematical input and
equivalence rules are defined in ADR-003.
