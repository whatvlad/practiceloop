# Project status

**MVP complete (2026-10-20).** Every MVP Issue (#1–#15) is closed; the release is
recorded as 0.1.0 in CHANGELOG.md. What works and its known limitations are in
README.md. Live state is always GitHub Issues, pull requests, merged commits and
the Implementation Queue project (https://github.com/users/whatvlad/projects/1),
worked in `Order`. Post-MVP work is the open queue (#30 roadmap and its stages).

Where each part is documented:

| Area | Issues | Document |
|---|---|---|
| Schema, RLS, two-user hosted isolation | #2, #3 | supabase/README.md, ADR-002 |
| Token verification and owner-scoped queries | #4 | docs/api/README.md |
| Google sign-in | #5 | docs/auth/GOOGLE_AUTH.md |
| Generators (basic, substitution, parts, rational, trigonometric, definite) | #6, #9, #36, #77–#80 | docs/architecture/BASIC_GENERATOR.md, TOPIC_GENERATORS.md |
| Answer input, parser, worker, checking | #7, #8, #57, #59, #61, #69 | docs/architecture/MATH_INPUT.md, ANSWER_CHECK.md, ADR-003 |
| Saved practice, history, profile | #10, #11, #12 | docs/architecture/SAVED_PRACTICE_UI.md, ADR-004 |
| Anonymous demo, statistics, name, deletion | #34, #35 | docs/architecture/PREVIEW_PRACTICE.md, ACCOUNT_COMPLETION.md |
| Mixed practice and mistake feedback | #36 | docs/api/README.md, TOPIC_GENERATORS.md |
| Practice areas: Integrals and Derivatives | #98 | docs/api/README.md "GET /api/topics", ADR-005 |
| Partial derivatives, coordinate changes, Jacobians (`partial-v1`) | #101 | TOPIC_GENERATORS.md, ADR-005 |
| Problem sharing by link and code; recipient-owned solving | #37, #109 | docs/api/README.md "Sharing" |
| Production readiness on preview (metadata, headers, reports, privacy draft) | #38 | docs/production/PRODUCTION_CHECKLIST.md |
| End-to-end check | #13 | docs/production/MVP_E2E_CHECK.md |
| Hosting, deploy, audit, backups | #14, #28, #33 | docs/production/ORACLE_DEPLOY.md |
| Operations docs, gates, license, release | #15 | README.md, CHANGELOG.md, LICENSE |

Keep these in sync when behaviour changes: `frontend/src/answerSyntax.ts` mirrors
the backend parser grammar (`backend/app/services/math_parser.py`, shared corpus
in `frontend/src/answerSyntax.test.ts`); `frontend/src/mathEditor.ts` turns the
MathLive editor's LaTeX into ADR-003 text before checking.
