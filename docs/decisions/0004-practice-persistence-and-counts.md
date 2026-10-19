# ADR-004: backend-owned practice records and distinct-problem counts

Date: 2026-10-19. Status: proposed for PL-002 owner review.

The backend owns all practice writes, stores solutions privately and makes every
client retry safe. Profile counters describe distinct problems rather than the
number of submissions. This proposes accepting ADR-002's storage boundary and
resolving OQ-04, OQ-05 and OQ-08.

## Attempts and counters

Every non-empty submission that passes request-size validation is persisted as
one attempt after ownership is verified. The existing nullable correctness field
means:

- `true`: correct;
- `false`: incorrect, including an otherwise valid primitive with no arbitrary
  constant;
- `null`: invalid expression.

A later migration owned by the persistence feature adds
`constant_omitted boolean not null default false` with a constraint that it can
be true only when `is_correct = false`. Empty or whitespace-only answers fail
request validation and are not attempts. Worker timeout, worker crash, database
failure and rate limiting create no attempt because no trustworthy result exists.

Profile counters are:

- `generated`: number of the user's persisted problems;
- `attempted`: number of distinct problems with at least one persisted attempt,
  including a problem whose only attempts are invalid;
- `correct`: number of distinct problems with at least one correct attempt.

Once solved, a problem remains counted as correct. Repeated attempts do not
increase any of the three counters. Total attempts and constant-omission metrics
are separate reporting values, not MVP profile counters.

## Private data and profile provisioning

`private.problem_solutions` remains outside exposed PostgREST schemas. Browser
roles cannot write trusted rows. The API verifies the Supabase JWT and derives
the user ID from its `sub` claim before every data access; service-role database
access never replaces query-level ownership checks.

After the first verified request, the API idempotently inserts
`profiles(id) values (<verified sub>) on conflict (id) do nothing`. It never
accepts a profile owner ID from the request body. Deleting the Auth user cascades
to the profile and learning records.

## Reveal semantics

The two MVP booleans are sufficient. Reveal calls are idempotent:

- revealing the answer sets `answer_revealed = true`;
- revealing the solution atomically sets both `solution_revealed = true` and
  `answer_revealed = true`, because the solution contains the final answer.

Flags never return to false. Timestamps and a reveal audit log are deferred until
a concrete product or compliance need exists.

## Transaction and retry boundaries

- Generation inserts the public problem, private solution and idempotency record
  in one transaction. Nothing is returned unless all three commit.
- Checking verifies ownership before reading the private solution. A completed
  result and its idempotency record are inserted in one transaction. A worker
  failure commits neither.
- A reveal verifies ownership, updates flags and reads the authorized private
  payload in one transaction.
- A profile read computes all three counters from one database snapshot.

Generation and attempt creation require a client-generated UUIDv4
`Idempotency-Key`. Keys are scoped to verified user, HTTP method and route and
are retained for 24 hours. An exact retry returns the stored status and body;
reuse with a different request body returns `409 idempotency_conflict`.
Concurrent requests with the same key produce one mutation. Reveal requests are
naturally idempotent and need no key.

Transient `429` and retryable `503` responses include `Retry-After` and are safe
to retry. Validation failures, an inconclusive deterministic math check and the
domain result `invalid` are not retried automatically.

## Consequences

The already-applied initial migration is not rewritten. PL-010 or its successor
adds only the idempotency storage and constant-omission field through a new
migration. The temporary browser mock may keep simpler behavior, but its counters
and invalid-attempt handling are not the final persistence contract.
