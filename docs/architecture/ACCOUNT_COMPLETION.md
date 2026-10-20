# Account completion (#35)

This finishes the approved account stage on top of Google authentication (#5),
JWT/ownership (#4), saved practice (#10/#11), and durable history/profile (#12).
The original MVP specification is unchanged. Delivery state is in the Issue/PR.

## Anonymous demo and privacy

`/practice` is public. Without a session it opens one fixed basic-integral demo.
Each bounded one-hour in-memory preview session admits one problem; further
generation returns 403. Every fresh anonymous session receives the same statement,
so resetting admission cannot unlock more distinct exercises. The next action
leads to login. This is a demo restriction, not a claim to identify visitors.
No cookies, persistent anonymous identifiers or anonymous learning records are
created. The backend holds only the exercise/token until expiry, never an answer
or verdict. The browser holds the current card in memory; reload starts it blank.
Existing global preview admission/request limits remain in place.

Authenticated generation remains random, owner-scoped and persisted. History,
statistics and profile routes require authentication. Anonymous demo data is
discarded on identity changes and is never imported into an account.

## Learning records and metrics

Problems store topic, difficulty, statement, generation time, answer/solution use;
the private solution stores generator version/data. Attempts store submitted
answer, nullable correctness, omission flag and timestamp. The additive migration
adds optional `elapsed_ms` (0..86,400,000), measured from opening the active card
to submission. It includes idle time, restarts after reload/reopen, and is
client-reported rather than a trustworthy performance score. Historical attempts
remain NULL; no invented durations are backfilled. This UI has no problem-hint
action; answer and full-solution use are stored as the existing reveal flags.

`GET /api/statistics` returns lifetime `checkedAttempts`, `omitted`, `rate`, a
`byTopicDifficulty` array and eight `weekly` buckets. Each checked attempt counts,
including retries with a new idempotency key. Invalid expressions and definite
integrals (#36, which never take a constant) are excluded;
idempotent replays count once. Rate is omitted/checked, NULL when there is no
denominator. Breakdown is by topic AND difficulty. Trend weeks start Monday UTC;
the current week is incomplete and zero weeks remain present. A lower rate means
fewer omissions; no improvement claim is inferred from sparse data. SQL is
owner-filtered and both queries share a read-only repeatable-read snapshot.

`POST /api/profile {"name": string|null}` stores a private, optional 80-character
display name. Whitespace-only/NULL removes it. It does not rewrite Google metadata.
The profile header uses Learner when unset. Browser writes remain revoked and RLS
continues to permit only owner reads. Email comes from the verified token.

## Hard deletion and expired identity

`POST /api/account/delete {"confirmation":"DELETE"}` requires a verified JWT
and exact confirmation. Unknown fields (including a caller-supplied user ID)
are rejected. The server calls the Supabase Auth admin hard-delete endpoint using
only verified `sub`, HTTPS and `SUPABASE_SERVICE_ROLE_KEY`. Redirects are never
followed; credentials/upstream bodies never reach the browser or logs. Missing
configuration/network/upstream errors return a safe 503 and do not pre-delete
learning data. A retry treats Auth 404 as success. After an uncertain network
failure the UI asks to retry; it does not claim success prematurely.

Auth deletion cascades profiles, problems, attempts, private solutions and
idempotency responses in the database transaction. No per-user aggregates or
deletion tombstones are retained by this implementation. Google itself is
unaffected. The client clears practice and locally signs out on success.

Supabase JWTs can remain cryptographically valid until expiry after deletion.
Every learning-data transaction therefore checks the narrow service-only
`private.account_exists(uuid)` function before access; old identities receive
401 and cannot provision a new profile/problem. `/topics` contains only public
catalogue metadata. The function has a fixed empty search path and no browser
execution grants. Its existence check discloses no Auth row contents.

## Deployment and retention gates

Apply `202610190002_account_completion.sql` before activating this backend.
Follow the populated-project backup and restore rehearsal requirement in
`supabase/README.md` first. The migration is additive and does not delete users.
Never run disposable CI fixtures against the hosted project.

The backend-only service-role key is needed for Auth deletion; without it the
endpoint safely returns 503. Configure it directly in `/etc/practiceloop/api.env`
(root-owned mode 600), restart the API, and never put it in VITE variables, GitHub
frontend build inputs, git, command arguments or chat. Test successful deletion
with a disposable account; do not delete an owner's real account for verification.

Policy: active account data is deleted immediately; recovery copies containing
it must expire within 30 days of deletion. Do not create indefinite dumps,
Actions artifacts or VM snapshots containing learning data. Inventory provider
backups/PITR and manual exports; verify their actual maximum retention and remove
expired copies. Restore only to an isolated environment, reconcile deletions
before serving traffic, and never silently restore a deleted account to service.
This release retains no learning aggregates after account deletion (only truly
irreversible aggregates would be permitted in future).

Supabase retention depends on the project's plan and settings; application code
cannot shorten provider backups. Current hosted backup/restore coverage and
retention require owner verification, as does server credential provisioning.
Do not mark #35 Done until the actual configuration and disposable-account live
deletion are verified. See the [Supabase backup guide](https://supabase.com/docs/guides/platform/backups)
and [Auth deletion behavior](https://supabase.com/docs/guides/auth/managing-user-data).
