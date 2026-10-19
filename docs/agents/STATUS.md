# Project status

The MVP features are not implemented yet. Tasks are the open GitHub Issues in
the Implementation Queue project (https://github.com/users/whatvlad/projects/1),
worked in `Order`. Live state is always GitHub Issues, pull requests, merged
commits and that project.

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
#3's two-user database checks are still pending.
Use the Issue and PR for current delivery/merge/preview verification state.

Mathematical input (#7): a bounded allowlisted parser produces an internal syntax
tree, and a fresh Linux worker constructs SymPy expressions under CPU, memory,
wall-clock and combined-output limits. See docs/architecture/MATH_INPUT.md.
Equivalence/domain checks (#8) and the API remain separate work;
the browser demo does not use this parser yet.

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
the RLS-bypassing service role (`pytest -m db`). No `/api` route uses them yet;
the routes arrive with #34/#10, which also call `install_error_handlers`.
