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
main (noindex). GitHub Pages stopped when the repo became private.
The backend deploys to an Oracle VM over SSH on push to main
(`.github/workflows/backend-deploy.yml`, docs/production/ORACLE_DEPLOY.md).

Google client authentication (#5): implementation replaces mock identity with
Supabase Google OAuth, persistent sessions, refresh/logout and protected routes.
See docs/auth/GOOGLE_AUTH.md for configuration and verification. Practice/history
and counters remain an explicitly labeled browser-session demo until #10/#12.
Backend JWT enforcement (#4) and #3's two-user database checks are still pending.
Use the Issue and PR for current delivery/merge/preview verification state.
