# Decision index

| Date | Decision | State / evidence |
|---|---|---|
| 2026-10-15 | Preserve source MVP exactly | docs/PRACTICELOOP_MVP.md hash verified |
| 2026-10-15 | React/TypeScript/Vite static frontend | ADR-001; deployed to Cloudflare Pages |
| 2026-10-15 | Private answers, backend-only writes, nullable correctness | ADR-002, accepted through ADR-004; hosted, isolation verified (#3) |
| 2026-10-15 | Dependency versions pinned after actual audit | Lockfiles and setup report |
| 2026-10-15 | Owner approved private whatvlad/practiceloop; infrastructure through PR #16 | Repository/Issues created; four hosted CI jobs passed; PR #16 merged |
| 2026-10-15 | Preserve Private visibility despite plan-limited branch protection | GitHub protection HTTP 403 requires Pro; main is not protected (README Merge gates) |
| 2026-10-15 | No approval required: authors merge their own PR after green CI; review optional | Owner decision in project chat |
| 2026-10-15 | Equal agent roles; collaboration rules reduced to AGENTS.md + docs/agents | Bootstrap setup reports, backlog snapshot and onboarding docs removed (kept in Git history) |
| 2026-10-19 | Bounded answer language, real-domain equivalence and five-by-five template matrix | ADR-003 accepted by accountable human |
| 2026-10-19 | Backend-owned attempts/reveals, distinct-problem counters and idempotent writes | ADR-004 accepted by accountable human |
| 2026-10-20 | Oracle region, worker isolation, backups and CORS (OQ-06) | Live VM audit, #14; docs/production/ORACLE_DEPLOY.md |
| 2026-10-20 | License: proprietary, all rights reserved | Owner decision (#15); LICENSE |
| 2026-10-21 | Add multiple integrals and derivatives as a second calculus area; scope amendment to the MVP | ADR-005 (#95); specification file unchanged |
| 2026-10-22 | Interactive visualizations in worked solutions (declarative spec, own SVG 2D, lazy three.js 3D); replaces ADR-005's plot exclusion | ADR-006 (#111), accepted by accountable human (PR #119) |
| 2026-10-22 | Printable LaTeX PDF worksheets from Practice and History; amends ADR-004's `generated` counter | ADR-007 (#115), accepted by accountable human (PR #119); product decisions by Vlad |
| 2026-10-22 | Worked solutions and static graphs in worksheet PDFs (`solutions` option, a solution reveal; graphs via `\pdfliteral`, no new TeX package) | ADR-007 amendment (#130), requested by Vlad |

Practice areas: ADR-005 amendment of 2026-10-26 (#144) supersedes the old
Integrals/Derivatives grouping with Algebra/Mathematical Analysis. Launch #39
and roadmap tracker #30 are deferred outside the active curriculum queue by
the product owner.

Open questions are in docs/decisions/OPEN_QUESTIONS.md. Record substantial choices
in a new ADR rather than changing accepted history or the source specification.
