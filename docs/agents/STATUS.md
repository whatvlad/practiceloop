# Project status

Account completion (#35, branch implementation): one fixed anonymous demo;
private constant-omission count/rate/topic+difficulty breakdown/eight-week UTC
trend; editable/removable optional display name; attempt elapsed time; explicit
Auth hard deletion and deleted-identity guard. Migration, backend credential,
backup/retention and live deletion verification remain deployment gates. See
docs/architecture/ACCOUNT_COMPLETION.md and the live Issue/PR for actual status.

The MVP features are not implemented yet. Tasks are the open GitHub Issues in
the Implementation Queue project (https://github.com/users/whatvlad/projects/1),
worked in `Order`. Live state is always GitHub Issues, pull requests, merged
commits and that project.

History/profile (#12): saved practice now has owner-scoped paginated reads,
persisted reopen with latest attempt/count and previously authorized reveal
payloads, and account-wide ADR-004 profile counts. The frontend restores those
after reload, supports loading older history and retries failures. No schema,
auth-policy or mathematical changes. See docs/architecture/SAVED_PRACTICE_UI.md;
the Issue/PR remains authoritative for delivery/deployment verification.

Connected preview (#34): `data/api.ts` now uses the untracked `/preview` backend
for basic integrals and substitution, levels 1–2. There are 186 verified records,
shuffled without replacement per session/cell; unsupported options are disabled.
Checking uses the isolated worker; private answers/steps are explicit reveals.
History/counts are temporary page memory, not account data. The shared educational
catalogue is checked in CI. See docs/architecture/PREVIEW_PRACTICE.md. This describes
the branch implementation; the Issue/PR remains authoritative for review, merge
and actual deployment. The earlier mock-practice notes below describe prior stages.

Frontend design (#26): the design system in docs/design/system is implemented
with mock data behind `frontend/src/data/api.ts`; the temporary stub in
`frontend/src/data/mock/` is replaced when the API (PL-010/011/012) lands.

Preview hosting (#28, #33): `.github/workflows/preview.yml` deploys `frontend/`
and the Graphify graph (`/graph/`) to https://practiceloop.pages.dev on push to
main (noindex). GitHub Pages stopped when the repo became private. The app reaches
the API same-origin at `/api`, forwarded by a Pages Function (`frontend/functions/`).
The backend deploys to an Oracle VM over SSH on push to main
(`.github/workflows/backend-deploy.yml`, docs/production/ORACLE_DEPLOY.md).

Google client authentication (#5): implementation replaces mock identity with
Supabase Google OAuth, persistent sessions, refresh/logout and protected routes.
See docs/auth/GOOGLE_AUTH.md for configuration and verification. Practice/history
and counters remain an explicitly labeled browser-session demo until #10/#12.
#3's hosted two-user isolation check passed on 2026-10-19 (supabase/README.md).
Use the Issue and PR for current delivery/merge/preview verification state.

Mathematical input (#7): a bounded allowlisted parser produces an internal syntax
tree, and a fresh Linux worker constructs SymPy expressions under CPU, memory,
wall-clock and combined-output limits. See docs/architecture/MATH_INPUT.md.
The API remains separate work; the browser demo does not use this parser yet.

Basic-integral generation (#6): 11 bounded templates cover all five ADR-003
basic-integral levels. Private `basic-v1` records reproduce the integrand,
domain, answer and structured solution steps; all 126 parameter combinations
are checked in tests. See docs/architecture/BASIC_GENERATOR.md. This is an
internal library; API/persistence, other topics and frontend integration remain
separate work.

Answer input (#57): the practice card has a math keypad and a live preview.
`frontend/src/answerSyntax.ts` mirrors the backend parser's grammar and limits
to render how an answer will be read and to explain syntax mistakes while
typing; it never decides correctness. Keep it in step with
`backend/app/services/math_parser.py` (shared test corpus in
`frontend/src/answerSyntax.test.ts`).

Formula editor (#61): on the practice card the answer box is a MathLive 2D
editor, loaded lazily. `frontend/src/mathEditor.ts` turns its LaTeX into
ADR-003 text before checking, so the backend is unchanged; it also corrects
slips such as `x(x+1)`, `sin x` and `arctan`. Phones get MathLive's on-screen
keyboard with the same keys instead of the inline keypad.

API identity and ownership (#4): `app.core.auth.current_user` verifies Supabase
access tokens against the project's public JWKS (asymmetric keys only) and is
the only source of a user ID. `app.services.owned_records` holds the owner-scoped
SQL for problems, attempts and reveals; CI's Database isolation job runs it as
the RLS-bypassing service role (`pytest -m db`).

Saved practice (#10): `app.api.practice` serves `/topics`, `/problems`, attempts
and both reveals (browser path `/api/...`), persisted through `app.core.database`
with ADR-004 idempotency keys and the shared #8 checker. It needs `DATABASE_URL`
on the VM; without it those routes return 503. The #11 frontend switches
signed-in practice to these saved routes, fetches available cells from `/topics`,
and keeps guest preview isolated. #12 adds history, reopen and profile reads
after a reload; account pages use persisted data rather than browser-only counts.
See docs/architecture/SAVED_PRACTICE_UI.md.

Answer checking (#8): `app.services.math_worker.check_answer(answer, record)`
applies ADR-003 inside the limited worker and returns correct, incorrect (with a
missing-constant flag) or invalid, or raises a retryable/inconclusive error. See
docs/architecture/ANSWER_CHECK.md. The preview (#34) and saved-practice (#10)
routes call it through one shared worker slot.
