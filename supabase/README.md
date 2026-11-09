# Database preparation

Migration preserves the MVP's four public tables and adds private storage for
answers, versioned generator data and solution steps. Every migration in
`migrations/` is applied to the hosted project by `supabase-deploy.yml`, and the
two-user hosted isolation check passed on 2026-10-19 (#3). Nullable
`attempts.is_correct` semantics are confirmed; ADR-002 is accepted through ADR-004.

Only authenticated reads are granted, filtered to each owner. All writes use the
backend. A backend service-role client bypasses RLS: validate the JWT and verify
ownership in every query, including reveal/check/history. Persist public problem
and private solution atomically. Provision profiles after verified login.

`private` must never be added to PostgREST exposed schemas. No public view/RPC may
return internal answers before explicit authorized reveal. Do not store secrets
in generator_data. Use bounded, versioned primitive JSON parameters, never pickle
or executable SymPy strings. Add migrations rather than editing applied SQL.

Local/CI isolation tests use a fresh PostgreSQL 17 container and the minimal
`tests/auth_fixture.sql`. See `scripts/test-db.py`. This tests the actual
migration, role grants, RLS and composite ownership FK. It does **not** verify
hosted Supabase Auth, JWT claims, Google OAuth or PostgREST configuration.
PL-003/004/005 track those integration checks against a disposable Supabase project.

## Issue #3 delivery and first-project procedure

Implementation branch: `codex/issue-3-supabase-schema`, base
`fc839a9fbeb2c01a0b525c2f3443021128bd7158`. Vlad confirmed starting #3 while
#2 remains open on 2026-10-18 and confirmed the `NULL` / `false` / `true`
invalid/incorrect/correct representation for the disposable hosted project.
This is not approval of the other outstanding #2 policies or production release.
The initial migration remains byte-for-byte unchanged.

`config.toml` was initialized with CLI **2.121.0**, then reduced to the local
settings used here. It exposes only `public`, disables seeding and email signup,
and uses Postgres 17. It does not change hosted Auth or exposed-schema settings.
Before local Supabase startup, check the hosted `SHOW server_version` result and
match `db.major_version` if needed. Never expose `private`, locally or hosted.

The pinned CLI source accepts filenames matching `^([0-9]+)_(.*)\.sql$`, so
`202610150001_initial_schema.sql` is accepted without renaming its 12-digit
version. Source: [CLI v2.121.0 migration listing](https://github.com/supabase/cli/blob/v2.121.0/apps/cli/src/command-internal/migration-list.ts).
The first real-project dry-run must still list **202610150001** before applying.

### Human provisioning, without sharing credentials

1. Create a **disposable** Supabase project; Frankfurt was suggested, but Vlad's
   created project shows West EU (Ireland). Confirm no existing application data
   before first migration. Save its database password in a password manager.
2. In Supabase account settings → Access Tokens, create a scoped token limited to
   this project: **Project Settings**, **API Keys**, **API Key Secrets**, and
   **Connection Pooling**, all **Read**. The pooler permission
   (`database_pooling_config_read`) is required for IPv4 fallback on GitHub runners;
   link otherwise silently skips caching its connection URL. See the
   [pooler endpoint permissions](https://supabase.com/docs/reference/api/v1-get-pooler-config).
   Record its
   expiry and rotate the GitHub secret before it expires. A seven-day setup token
   requires replacement for continuing automatic delivery.
3. In GitHub → repository Settings → Secrets and variables → Actions → Secrets,
   add `SUPABASE_ACCESS_TOKEN`, `SUPABASE_PROJECT_REF`, `SUPABASE_DB_PASSWORD`.
   Do not add a service-role key. Do not share any values in chat or logs.
4. Keep Actions variable `SUPABASE_MIGRATIONS_READY` absent until the first hosted
   dry-run, policy decision and backup/recovery plan have been checked.

Reference: [official migration delivery guide](https://supabase.com/docs/guides/deployment/managing-environments).

### Migration workflow

`.github/workflows/supabase-deploy.yml` runs on relevant pushes to main and by
manual dispatch. It first applies migrations and the existing isolation test to
disposable Postgres 17, never the hosted database. The existing CI **Database
isolation** job is retained. Actions are pinned by commit; CLI is pinned by version.
Missing any of the three secrets produces an explicit hosted-skip notice.

With secrets present, it links the project and runs `supabase db push --linked
--dry-run`. No Auth fixtures or test data are sent to the hosted database.
Dry-run can initialize CLI migration bookkeeping; it does not apply application
migrations or validate every SQL statement. Application remains blocked until
`SUPABASE_MIGRATIONS_READY=true` is set by the human. Dispatch mode defaults to
`dry-run`; choose `apply` only after the first-project checks. Automatic relevant
main pushes apply pending migrations once the readiness variable is true.

First deployment (after the preparation workflow is on main):

```powershell
gh workflow run supabase-deploy.yml --repo whatvlad/practiceloop --ref main -f mode=dry-run
gh run list --repo whatvlad/practiceloop --workflow supabase-deploy.yml --limit 5
gh run view <RUN_ID> --repo whatvlad/practiceloop --log
```

Confirm the expected project and pending `202610150001` migration with no skipped
file warning. If the project has existing tables or migration-history differences,
stop and reconcile the actual schema; do not use `--include-all`, `migration repair`,
or `db reset --linked` to hide a mismatch. After verification and recovery planning,
the human sets Actions → Variables → `SUPABASE_MIGRATIONS_READY` to `true`, then:

```powershell
gh workflow run supabase-deploy.yml --repo whatvlad/practiceloop --ref main -f mode=apply
```

### Hosted Auth and PostgREST verification (human only)

This test is deliberately separate from the ordinary CI fixture. Never execute
`tests/auth_fixture.sql` or `tests/isolation.sql` in a real Supabase project.

1. Dashboard → Integrations / Data API settings: inspect **Exposed schemas** and
   verify `private` is absent. Check the setting directly; `config.toml` is local.
2. Configure Google in Google Cloud Console → APIs & Services → Credentials →
   Create credentials → OAuth client ID → Web application. Set authorized redirect
   URI to `https://<project-ref>.supabase.co/auth/v1/callback`. Put the client ID and
   secret directly into Supabase → Authentication → Sign In / Providers → Google.
   Enable Google only; disable email/password, phone and anonymous Auth sign-in.
3. Authentication → URL Configuration: Site URL `https://mathloop.net` after
   attachment; allow `https://mathloop.net/**` and `http://localhost:5173/**`.
   Keep `https://mathloop.pages.dev/**` during the domain rollout.
   Google consent/testing configuration must allow both real test Google accounts.
4. Obtain two real Google-authenticated user sessions. You can use the human-only
   helper below, which avoids copying tokens and does not depend on the #5 client.
   Auth sessions must belong to this hosted project and be short lived. Never send
   JWTs to the agent or put them in shell arguments. This PR does not implement #5
   or claim the application's login is functional.
5. SQL Editor as `postgres`: replace only the two UUID placeholders in
   `tests/hosted_fixture.sql` with those real Auth user IDs, then run it. It creates
   two profiles if absent, two public problems, attempts and private answers. Fixed
   IDs deliberately fail on collision. Run `tests/hosted_schema.sql`: it checks
   tables, RLS, indexes, all browser mutation/TRUNCATE grants, private permissions,
   service-role bypass and a rejected cross-owner composite FK insert.
6. Run this locally yourself (only public values in environment):

   ```powershell
   $env:SUPABASE_URL = 'https://<project-ref>.supabase.co'
   $env:SUPABASE_PUBLISHABLE_KEY = '<public-sb_publishable_key>'
   python scripts/test_supabase_hosted.py
   ```

   Paste user A and B access tokens, in fixture order, into the two hidden prompts.
   The script contacts Auth `/user` to establish two distinct real identities,
   verifies own reads and cross-user invisibility, rejects POST/PATCH/DELETE on
   every public table for both users and anonymous clients, and requires PGRST106
   for every tested private-schema operation. An expired JWT, missing fixture,
   network failure, wrong error, or empty own read cannot count as isolation success.
   Do not run this mutation-denial probe on a project with real user data: unsafe
   privileges could allow a test insert or update before the script detects failure.
7. Record only test summaries, date, CLI version, commit, SQL success and workflow
   run links. Never record raw tokens, users' personal details or private answers.
   Run `tests/hosted_cleanup.sql` in the same disposable project's SQL Editor;
   fixture problems cascade to attempts/solutions. Profiles and Auth users remain.
   Remove test Auth users manually when no longer needed; sign out test sessions.

PostgREST denial does not prove API ownership: `service_role` bypasses RLS. #4
must verify JWT claims and scope **every** service-role query by verified user ID.

#### Human-only Google test helper (no token copying)

Stop any local frontend server using port 5173. In the implementation worktree:

```powershell
python scripts/test_supabase_hosted.py --google-login
```

The script asks for the public Project URL and `sb_publishable_` API key (from
Project Settings → API Keys), unless already set in public environment variables.
It opens Google's sign-in twice: choose the two different allowed test accounts.
The helper listens only on IPv4 loopback port 5173. The nonce callback accepts only
same-origin POSTs, clears the URL fragment immediately and never persists/logs
tokens. It loads no third-party script. Sessions remain in memory in this human-run
process and expire; do not run the command through the agent's tools.

Once both sessions have been verified with Supabase, it generates the ignored
`.local/hosted_fixture.sql` with their UUIDs (no tokens). Run that generated file,
then `supabase/tests/hosted_schema.sql`, in the hosted SQL Editor as `postgres`.
Type `SQL PASSED` in the terminal only if both completed successfully. The helper
then runs the two-user/anonymous PostgREST checks and signs out its test Supabase
sessions on success. Run `supabase/tests/hosted_cleanup.sql` to remove fixtures.
Only a successful check writes `.local/hosted-test-result.json`; it contains
status fields, timestamp and verifier hash, with no credentials. SQL success is a human confirmation, distinct
from the script's directly observed PostgREST results. On failure, retain the safe
terminal message and inspect configuration; do not share tokens or callback URLs
containing fragments. Revoke test sessions in Supabase if interrupted.

For a partial check without fixture setup or a second login, run:

```powershell
python scripts/test_supabase_hosted.py --google-login --single-user
```

This checks authenticated reads, browser mutation denial, anonymous denial and
unexposed private schema. It observes existing owned-row counts and explicitly
reports empty-table coverage limits. It creates no fixtures. The output/report is
marked `partial`, with cross-user and SQL checks `not run`; it cannot replace the
two-real-user check. The default two-account verifier rejects duplicate identities.

### Profile provisioning and transaction boundary

The schema creates no automatic Auth trigger and the browser cannot insert a
profile. #4/#10 must upsert `profiles(id)` server-side **after** verified login,
using only the verified `sub`, with conflict-on-id retry safety. Use the database
default timestamp, not arbitrary metadata. Test fixtures provision explicitly as
admin. Auth-user deletion cascades to profiles/problems/attempts/private solutions.
The backend must persist public problem and private solution in one transaction;
separate HTTP calls are not atomic. No new RPC or persistence API is added here.

### Backup and rollback

- Before first application, confirm this is the intended empty disposable project.
  Existing populated projects require a verified backup and a restore rehearsal
  before any migration; never treat a dashboard backup label as proof of recovery.
- For an empty test project, record Auth/provider and Data API settings without
  secrets. Recovery is a new disposable project, the same migration, recreated
  test Google users and repeat hosted checks. Keep the old project until verified.
- For later populated projects, the human takes an encrypted, access-controlled
  pre-change backup (roles, schema, data and private schema) using the plan-supported
  Supabase backup/export tools, checks retention, and rehearses restore into a
  separate project. Confirm Auth/Storage/managed-schema coverage separately.
  Never commit database dumps or store them in Actions artifacts/logs.
- On failure, leave readiness disabled to stop application, retain the failed run,
  inspect the real schema and migration history, and prefer a corrective **new**
  migration. Do not edit an applied migration. The initial SQL uses a transaction;
  still verify history and objects after CLI failure rather than assuming rollback.
- Reverting app code does not undo a database migration. Never drop hosted tables
  or reset a hosted database as an automatic rollback. Destructive recovery requires
  the human's explicit project-specific decision and verified recoverable backup.

### Current verification status

The initial migration was applied successfully in hosted preflight run
[39173170854, attempt 3](https://github.com/whatvlad/practiceloop/actions/runs/39173170854/attempts/3)
after a successful real-project dry-run and Vlad's explicit approval. Both commands
recognized the unchanged 12-digit version. On 2026-10-19 Vlad ran the full
two-account check against the hosted project with two different real Google users:
`hosted_fixture.sql` and `hosted_schema.sql` succeeded in the SQL Editor, and the
PostgREST checks passed for user 1, user 2 and anonymous clients (own reads,
cross-user isolation, browser write denial, anonymous denial, private schema
unexposed). Fixtures were then removed with `hosted_cleanup.sql`. This closes #3.
Populated-project backup/restore is still unrehearsed; do it before the first
migration on a project with real data. #4/#5/#10/#12 own later API/frontend integration; #35 reuses
their results and covers residual demo/statistics/deletion requirements after #34.

The fixture reproduces Supabase's automatic public-table grants to anon,
authenticated and service_role. Isolation tests enumerate every public/private
table (including partitioned and foreign tables) and reject INSERT, UPDATE,
DELETE or TRUNCATE privileges for either browser role, including inherited/PUBLIC
grants. This catches newly introduced tables without explicit revokes and checks
TRUNCATE separately because RLS does not constrain it. The fixture is a focused
table-privilege model, not a full Supabase installation.
