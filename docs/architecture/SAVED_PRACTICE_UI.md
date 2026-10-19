# Saved practice UI (#11/#12)

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
returned by reveal calls (or an authorized reopen) and held separately in the active card. They are never
prefetched for an unrevealed problem or stored in the shared problem cache.
Reopening an already revealed problem restores its authorized payload through
the read-only GET route, without additional reveal writes. KaTeX retains `trust: false`, bounded
expansion/size and MathML output; rendering failures fall back to escaped text.

## Durable history and profile

The #12 read routes load history after a reload, reopen owned problems and return
account-wide profile counts. History uses 20-row pages with stable cursors and a
Load more control; the dashboard requests only three recent records. Filters
apply to loaded records and say when older pages remain. Failed next-page reads
retain existing rows and retry the same cursor; pending requests are guarded.
Each row shows topic, difficulty, creation time, latest user answer/result,
attempt count and reveal flags. Full attempt timelines are outside this contract.

Reopen always reads the server and restores latest input/feedback plus previously
authorized answers/solutions in an `OpenedProblem`. The shared `PublicProblem`
cache receives only public fields. Unsigned preview keeps its in-memory history.

Profile counts come from the server, not the loaded history subset. A single SQL
statement computes generated, distinct attempted (including invalid-only), and
distinct ever-correct problems. Repeated attempts do not inflate counts; a later
incorrect attempt cannot erase an earlier success. Loading/errors have explicit
states and retries, with no invented zero counts on service failure.

## Verification

`practice.test.ts` covers saved/preview routing, DTO projection, key reuse,
duplicate requests, token refresh, Retry-After, invalid/missing-constant results
and identity races. `savedPracticeFlow.test.tsx` runs the real React controls,
answer syntax/Enter handler and data boundary against controlled HTTP responses:
selection, generation, invalid/correct checking, explicit reveals and next.
It also checks topic-specific availability, catalogue retry, stale verdicts and
reopen after clearing the browser cache. History page tests cover pagination
retry/duplicate clicks, empty state and discarding the previous account's read.
Database tests run as the RLS-bypassing service role and check ownership, stable
timestamp ties/new insertions, the 50-row boundary, reveal gating and ADR-004
invalid/repeated/correct-then-incorrect semantics. Unit/component tests do not
claim live Google OAuth/database verification; delivery evidence is in the PR.
