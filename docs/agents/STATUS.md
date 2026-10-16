# Project status

Infrastructure and a development scaffold are in review (PR #16); the MVP
features are not implemented yet. Tasks: GitHub Issues #1–#15. Live state is
always GitHub Issues, pull requests and merged commits.

Frontend design (#26): the design system in docs/design/system is implemented
with mock data behind `frontend/src/data/api.ts`; the temporary stub in
`frontend/src/data/mock/` is replaced when the API (PL-010/011/012) lands.

Preview hosting (#28): `.github/workflows/pages.yml` deploys `frontend/` to
GitHub Pages on push to main; temporary until PL-014.
