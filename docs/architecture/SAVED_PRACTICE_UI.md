# Saved practice UI (#11)

The signed-in dashboard and practice card use #10's saved routes through
`frontend/src/data/api.ts` and `practice.ts`. Before every request, the data
boundary reads the current Supabase session token. Backend JWT verification and
ownership checks remain authoritative. No identity is sent in the request body.
A missing/failed account session produces a sign-in message, never a silent
fallback to anonymous practice. The guest data boundary still uses `/preview/*`;
this change does not expand guest route access or implement #35's demo policy.

`GET /topics` determines the enabled topic/difficulty cells. All five levels and
five MVP topics remain visible; unsupported cells are disabled and explained as
not available yet. Failed catalogue requests can be retried. The UI does not
substitute easier exercises for unavailable cells.

## Writes, retries and stale responses

Generation and attempts use UUIDv4 idempotency keys. The same action retains its
key after a timeout, lost response, server failure or malformed response; a
completed action releases its key so the next deliberate action gets a fresh
one. Keys are private module memory scoped to the current identity and page
lifetime. Refreshing the page does not resume an unfinished operation.
There are no automatic mutation retries. `Retry-After` blocks early retries.
Rate limits, authentication failures and server errors appear as service errors,
not mathematical verdicts. Duplicate clicks/Enter are guarded in the UI;
concurrent identical data operations share a promise.

Identity changes clear public problems, selections, keys and pending-request
references. Epoch checks reject old credentials and responses. The app remounts
practice state when the problem ID changes, and ignores results after navigation
or after the answer is edited. The input remains editable while checking, but an
old verdict cannot overwrite the newly edited answer.

Invalid expressions are saved attempts for signed-in practice, as in ADR-004.
Missing-constant feedback remains distinct from a general incorrect result.
Revealing the solution sets both local reveal flags, matching the backend.

## Public/private boundary

Generation explicitly projects only the public problem fields into the cache.
Checks accept only verdict/feedback fields. Answers and solution steps are
returned by reveal calls and held separately in the active card. They are never
prefetched for an unrevealed problem or stored in the shared problem cache.
Reopening an already revealed problem in this browser session can request its
previously authorized reveal payload again. KaTeX retains `trust: false`, bounded
expansion/size and MathML output; rendering failures fall back to escaped text.

## History limitation and verification

All generated problems, attempts and reveals are persisted by #10, but the #12
read routes do not exist yet. History/reopen/counters currently use this browser
session's public cache. Reload clears that cache, not the saved database rows.
The app labels this explicitly. Durable history restoration and account-wide
profile statistics are excluded from #11.

`practice.test.ts` covers saved/preview routing, DTO projection, key reuse,
duplicate requests, token refresh, Retry-After, invalid/missing-constant results
and identity races. `savedPracticeFlow.test.tsx` runs the real React controls,
answer syntax/Enter handler and data boundary against controlled HTTP responses:
selection, generation, invalid/correct checking, explicit reveals and next.
It also checks topic-specific availability, catalogue retry and stale verdicts.
These tests do not claim a live Google OAuth/database end-to-end run.
