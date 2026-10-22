# API contract

Account completion (#35): `GET /api/statistics` (private omission metrics),
`POST /api/profile {name: string|null}` (private optional name) and
`POST /api/account/delete {confirmation: "DELETE"}` (hard deletion).
Attempts additionally accept optional `elapsedMs` from 0 to 86,400,000.
See [account completion](../architecture/ACCOUNT_COMPLETION.md) for exact
denominators, UTC trend, deleted-token guard, deployment and retention gates.

Implemented: `GET /health` returns `200 {"status":"ok"}` (liveness only), the
separate [untracked preview API](../architecture/PREVIEW_PRACTICE.md) under
`/preview`, and (#10, `backend/app/api/practice.py`) the saved-practice routes
`GET /api/topics`, `POST /api/problems`, `POST /api/problems/{id}/attempts`,
`/reveal-answer` and `/reveal-solution`, plus (#12) `GET /api/problems`,
`GET /api/problems/{id}` and `GET /api/profile`.
The browser calls `/api/...` on the Pages origin; the proxy
strips `/api`, so FastAPI serves these at `/topics`, `/problems`, ... like
`/preview`. The proxy forwards `Idempotency-Key`. Saved practice needs
`DATABASE_URL` on the host (docs/production/ORACLE_DEPLOY.md); without it these
routes return `503 database_unavailable`.

The #11 frontend uses these saved write routes for signed-in accounts, taking a
current Supabase access token before each request. Guests keep the separate
preview boundary. See [saved-practice UI](../architecture/SAVED_PRACTICE_UI.md)
for retry behavior, durable history and previously authorized reveal restoration.

Generation picks a random record from the cell's verified catalogue, skipping the
records behind the user's latest half-catalogue in that cell, so a learner sees
no repeat within that window. Only the cells the generators support are offered:
every topic at levels 1–5 except integration by parts, which has levels 1–3
(ADR-003). Other cells return 422. `GET /topics` lists them as
`availableDifficulties`. Substitution levels 1–2 keep `substitution-v1`; levels
3–5 use `substitution-v2`. Most cells also contain `definite-v1` records (#36):
their `problemLatex` starts with `\int_{a}^{b}` and their answer is one exact
number with no constant. See [topic generators](../architecture/TOPIC_GENERATORS.md#definite-integrals).
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
`feedbackCode` is `missing_constant`, one declared mistake code (#36) on an
`incorrect` result, or `null`. The mistake codes are `power_rule`, `trig_sign`,
`chain_factor`, `log_absolute`, `split_product`, `parts_sign`, `cycle_factor`,
`partial_fraction_sign`, `definite_not_evaluated`, `bounds_reversed`,
`definite_constant`, `missing_jacobian` (#99), `z_bounds` (#100), the derivative codes `derivative_power`,
`derivative_trig_sign`, `derivative_chain`, `derivative_factors`,
`quotient_sign` and `derivative_constant` (#97), and the partial-derivative codes
`partial_held_constant`, `partial_chain_term`, `jacobian_missing_r` and
`jacobian_sign` (#101). A code is sent only when the answer unambiguously matches
that mistake; `null` on an incorrect answer means the UI shows a general hint.
Clients treat an unknown code as `null`. A code is never an expected answer.
Read responses add `attemptCount`, the total number of persisted attempts for
that problem, including invalid expressions. `lastAttempt` is the latest by
`(created_at, id)`, not an aggregate result or all previous submissions.

Errors have one envelope:

```json
{"error":{"code":"problem_not_found","message":"Problem not found.","retryable":false}}
```

Messages are safe learner-facing text. Logs, errors, OpenAPI examples and check
responses never include expected answers, solution steps or generator data.

## Routes

### `GET /api/topics`

Returns the practice areas (ADR-005, #98), only implemented template cells, and
each area's fixed mixed-practice weights (#36):

```json
{"areas":[
  {"slug":"integrals","name":"Integrals","mixed":{"availableDifficulties":[1,2,3,4,5],"weights":{"basic-integrals":1,"substitution":2,"integration-by-parts":2,"rational-functions":2,"trigonometric-integrals":2},"worksheetCapacity":{"1":168,"2":186}}},
  {"slug":"derivatives","name":"Derivatives","mixed":{"availableDifficulties":[1,2,3,4,5],"weights":{"derivatives":1,"partial-derivatives":1},"worksheetCapacity":{"1":42}}}],
 "items":[{"slug":"basic-integrals","name":"Basic integrals","area":"integrals","availableDifficulties":[1,2,3,4,5],"worksheetCapacity":{"1":54,"2":42}}]}
```

Every topic belongs to exactly one area, and `areas` lists only areas with at
least one topic, in display order. The topic slugs are seeded in `public.topics`
(migration `202610210003_topic_areas.sql`, which also stores each topic's
`area`); a seeded topic appears in `items` only once its generator ships.
`mixed` is `null` while an area has fewer than two topics.

Mixed practice draws a topic of one area for each problem with these weights,
over that area's topics offered at the chosen level; at levels 1–2 integration
by parts is not offered, so the others share its part. Weights are constants in
`TOPICS` in `backend/app/api/practice.py`, never adapted to a learner's history.

`worksheetCapacity` maps each offered level to the number of distinct records a
worksheet group can take from that cell (ADR-007 decision 4); for `mixed` it is
the sum over the area's topics offered at that level.

### `POST /api/problems`

Requires `Idempotency-Key: <UUIDv4>`.

```json
{"topic":"basic-integrals","difficulty":1}
```

`topic` may also be `"mixed"` (levels 1–5) with an optional `"area"` (default
`"integrals"`): the server draws a topic of that area with the published
weights, and the saved problem and the response carry the drawn topic. `area`
with any other `topic`, an unknown area, or an area without mixed practice is
`422 invalid_request`.

```json
{"topic":"mixed","area":"integrals","difficulty":3}
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
`result: "incorrect"` and `feedbackCode: "missing_constant"`; a definite answer
never needs one, and one that contains `x` or a constant is incorrect. Empty input or an
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

The response may also carry `visual`, the declarative picture of ADR-006, built
on the server from the stored record (`backend/app/visuals/`). It holds plotting
data only: expression trees, windows, bounds, marked points and the exact value
the steps already show, never the record. The key is absent for versions that
declare no visual (derivatives). Double
integrals (`double-v1`) carry `region2d`: the solution's system, bounds and
integrand, a window and the region as LaTeX inequalities (#113). Triple
integrals (`triple-v1`) carry `solid3d`: the solution's system (Cartesian or
cylindrical), its bounds with `z` innermost, an x/y/z window and the solid as
LaTeX inequalities, without the integrand (#114). The
same `solution` object, with `visual`, comes back from `GET /api/problems/{id}`
once the solution is revealed, and from the demo's `reveal-solution`.

Both reveal routes are naturally idempotent. They return the already authorized
payload when repeated.

### `GET /api/problems`

Accepts `limit` (`1..50`, default `20`), opaque `cursor` and `worksheet=true`,
which keeps only problems a generated worksheet created (ADR-007). Returns newest
first by `(created_at, id)`:

```json
{"items":[{"id":"uuid","topic":"basic-integrals","difficulty":1,"problemLatex":"\\int 3x^2\\,dx","createdAt":"2026-10-19T12:00:00Z","answerRevealed":false,"solutionRevealed":false,"worksheetId":null,"lastAttempt":null}],"nextCursor":null}
```

The cursor encodes the last visible `(created_at, id)` tuple; it is bounded and
validated, and never supplies an owner ID. Each page reads problem metadata and
latest-attempt/count summaries from one read-only repeatable-read transaction.
One extra row detects whether another page exists, including at the 50-row limit.
The cursor is stable for rows already seen. Newly generated problems appear only
when pagination restarts without a cursor. History never includes reveal payloads.

### `GET /api/problems/{id}`

Returns `200` and the shared problem shape. If a reveal flag is true, the response
also includes the corresponding previously authorized `answer` or `solution`.
These are top-level siblings of `problem`, with the same shapes as the reveal
responses, e.g. `{"problem":{...},"answer":{"answerLatex":"..."}}`.
This is a read-only transaction: reopening never creates attempts or changes
reveal flags. Unrevealed content and generator records are not returned.
It also carries `share`: the owner's live share of this problem (see Sharing)
or `null`.

### `GET /api/profile`

```json
{"account":{"id":"uuid","name":"Ada","email":"ada@example.test","provider":"Google"},"counts":{"generated":4,"attempted":3,"correct":2}}
```

Counts use one SQL aggregate snapshot and ADR-004 distinct-problem semantics
(ADR-007: a worksheet problem counts as `generated` only once it has an attempt):
invalid-only attempts count as attempted, repeated attempts do not inflate
counts, and any previous correct attempt keeps the problem counted as correct.
`name` is the optional display name saved with `POST /api/profile` (#35), or
null; the UI then shows the Google-session name. Account data
comes from the verified session/profile, never client-supplied identity fields.

## Sharing (#37, #109)

An owner shares a saved problem's statement, topic and difficulty, nothing more.
A share has two independent random keys: a link token (32 bytes from
`secrets`, base64url, 43 characters) and an 8-symbol Crockford base32 code
(40 bits, shown as `K7M2-QX9P`). Neither is derived from the problem. Shares
live in `private.problem_shares`, which only the backend reads; they last 90
days, and deleting the problem or the account deletes them.

### `POST /api/problems/{id}/share`

Owner only. Returns `201` with a new share, or `200` with the problem's live
share, so a second click never makes a second link:

```json
{"share":{"token":"43 base64url chars","code":"K7M2QX9P","expiresAt":"2027-01-18T12:00:00Z"}}
```

### `POST /api/problems/{id}/share/revoke`

Owner only. Ends the link and the code at once and returns `{"share":null}`.
Idempotent; a later share gets a new token and code. Another user's or a
missing problem is the usual `404 problem_not_found` for both routes.

### `GET /api/shares/{token}` and `GET /api/shares/code/{code}`

No account needed and no `Authorization` header read. A code is accepted in any
case, with spaces or hyphens, and with `O`, `I` and `L` read as `0`, `1` and
`1`. Returns only:

```json
{"problem":{"topic":"substitution","difficulty":3,"problemLatex":"\\int ..."}}
```

Never the problem ID, owner, answers, results, statistics, reveals or
solutions. An unavailable share is one of four states, each with no problem
data: `400 share_invalid` (not a well-formed token or code), `404
share_not_found`, `410 share_expired` and `410 share_revoked` (revocation wins
when both apply).

Rate limits: 20 creates and revokes a minute per user, and 120 lookups a minute
in total. The Pages proxy does not pass the client address, so lookups share
one window; guessing a code or token stays infeasible at that rate. The
frontend serves shares at `/s/{token}`, `/shared/{token}` and `/shared?code=...`,
all with a `noindex, nofollow` robots meta tag on top of the site's `X-Robots-Tag`.

### `POST /api/shares/practice`

Requires a verified account and a UUID v4 `Idempotency-Key`. The strict body
contains exactly one reference: `{"token":"43 base64url chars"}` or
`{"code":"K7M2-QX9P"}`. Code normalization matches public lookup. Unknown
fields are rejected. This shares the generation limit of 30 requests per
minute per user.

Returns `201 {"problem": ...}` in the normal saved-problem shape, with a new
recipient-owned ID, zero attempts and both reveal flags false. The server
copies the exact trusted statement, topic, difficulty and private solution
record. It does not regenerate a similar exercise or copy the sender's attempts,
answers or reveal state. The private record remains server-only; answer checks,
explicit reveals and history use the recipient's normal saved-practice routes.

Missing, expired, revoked and malformed references use the public lookup error
states. Copying locks the source problem and share through commit so revocation
cannot race a new copy. The copy and idempotency outcome commit atomically.
Repeating the same key and normalized body within 24 hours replays the original
response, including after the share ends, without creating another problem.
An ended share cannot create a new copy with a fresh key. Existing recipient
copies survive revocation, expiry and deletion of the sender's account.

The shared page offers **Solve this problem** for an account, or **Sign in to
solve this problem** for a visitor. A validated shared route is kept in this
tab's session storage across Google sign-in and consumed on return. It contains
only the existing link token or code. Arbitrary return URLs are rejected. The
recipient then explicitly starts solving; there is no automatic copy on lookup.

## Reports (#38)

### `POST /api/problems/{id}/report`

Owner only: a learner reports one of their own saved problems. Body:

```json
{"category":"answer_check","comment":"optional, at most 500 characters"}
```

`category` is one of `answer_check` (my answer was checked wrongly),
`solution` (the answer or solution is wrong), `statement` (the problem is
unclear or broken), `display` and `other`. The comment is trimmed; an empty one
is stored as null. Unknown fields, other categories, a longer comment or a NUL
character are `422 invalid_request`, and the error never echoes the input.
Returns `201`:

```json
{"report":{"id":"...","category":"answer_check","createdAt":"2026-10-21T08:00:00Z"}}
```

Reports live in `private.problem_reports` (problem, category, comment, time and
the owner key), which only the backend reads. Deleting the problem or the
account deletes its reports. Another user's or a missing problem is `404
problem_not_found`. Rate limits: 5 reports a minute and 30 an hour per user.
The anonymous demo has no report button, since its problem is not stored.

## Worksheets (#116, ADR-007)

### `POST /api/worksheets`

Requires `Idempotency-Key: <UUIDv4>`; an exact retry returns the same worksheet.

```json
{"source":"generate",
 "groups":[{"topic":"substitution","difficulty":2,"count":5},{"topic":"mixed:integrals","difficulty":3,"count":4}],
 "paper":"a4","columns":1,"answerKey":true}
```

or `{"source":"history","problemIds":["uuid", ...],"paper":"letter","columns":2,"answerKey":false}`.
`paper` (`a4`, `letter`) defaults to `a4`, `columns` (`1`, `2`) to `1`,
`answerKey` to `true`, `solutions` (#130) to `false`. Limits: 1-8 groups, `count` 1-20, 40 problems in total,
1-40 distinct `problemIds`. Returns `201`:

```json
{"worksheet":{"id":"uuid","source":"generate","createdAt":"2026-10-22T14:00:00Z","paper":"a4","columns":1,"answerKey":true,"solutions":false,
 "groups":[{"label":"Substitution, level 2","topic":"substitution","difficulty":2,"requested":5,"count":5},
           {"label":"Mixed integrals, level 3","topic":"mixed:integrals","difficulty":3,"requested":4,"count":4}],
 "problemIds":["uuid", "..."]}}
```

- `generate` picks new problems: no record twice in one worksheet (across
  groups too), distinct base problems before coefficient variants. A group whose
  cell runs out is capped: `count < requested`, possibly `0`. The problems are
  saved as normal problems with `worksheetId`, so they appear in History.
- `history` uses the user's own problems, in catalogue area and topic order, then
  level, then oldest first; each topic and level is one group. Any missing or
  foreign id fails the whole request with `404 problem_not_found`.
- With `answerKey` every included problem gets `answerRevealed: true` in the same
  transaction. With `solutions` every included problem gets both
  `answerRevealed` and `solutionRevealed`, with or without the key. With
  neither no flag changes.
- `problemIds` are in print order. Rate limit: 5 a minute and 30 an hour per user.

### `GET /api/worksheets/{id}/pdf`

Returns `200 application/pdf` with
`Content-Disposition: attachment; filename="practiceloop-worksheet-YYYY-MM-DD.pdf"`
(the creation date). It is read-only: no flag changes, so it can be retried or
repeated. One section per group, problems numbered through the whole sheet with
writing space, and with the key an "Answers" section on a new page (final
answers only). With `solutions` a "Solutions" section follows on a new page:
each problem's statement, its worked steps and, where its version has an ADR-006
visual, a static graph (no graph for derivatives). Graphs stop after 12 s of
building in one render, and the remaining problems print their steps without
one. Rate limit: 20 a minute per user. One compile runs at a time;
waiting over 10 s gives `503 worksheet_busy`, a failed compile
`503 worksheet_render_failed` (both retryable). Another user's or a missing
worksheet is `404 problem_not_found`.

## Response headers

Every API response carries `X-Content-Type-Options: nosniff`,
`X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`,
`Cross-Origin-Resource-Policy: same-site` and
`Content-Security-Policy: default-src 'none'; frame-ancestors 'none'; ...`
(the local `/docs` and `/redoc` pages keep only `frame-ancestors 'none'`).
CORS answers only exact origins from `ALLOWED_ORIGINS`; wildcards and plain
`http://` origins other than the local Vite server are dropped. Caddy adds HSTS
and redirects HTTP to HTTPS.

## HTTP failures and retry behavior

| Status | Code | Meaning / retry |
|---|---|---|
| `401` | `authentication_required`, `invalid_token` | Missing or failed token; refresh/re-authenticate, do not blindly retry |
| `400` | `share_invalid` | Malformed share token or code; ask for a new one |
| `404` | `problem_not_found` | Missing and other-user IDs are intentionally indistinguishable |
| `404` | `share_not_found` | No share has this token or code |
| `410` | `share_expired`, `share_revoked` | The share existed but no longer works; do not retry |
| `409` | `idempotency_conflict` | Same key with different input; create a new key only for a deliberate new action |
| `422` | `invalid_request` | Malformed JSON, unknown field, empty answer, unsupported topic/level or normalized input over 256 bytes |
| `429` | `rate_limited` | Retry only after the `Retry-After` delay |
| `503` | `authentication_unavailable`, `math_worker_unavailable`, `math_check_inconclusive`, `database_unavailable`, `worksheet_busy`, `worksheet_render_failed` | No mutation committed; retry with the same idempotency key only when `retryable` is true |

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
