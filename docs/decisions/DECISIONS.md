# Decision index

| Date | Decision | State / evidence |
|---|---|---|
| 2026-10-15 | Preserve source MVP exactly | docs/PRACTICELOOP_MVP.md hash verified |
| 2026-10-15 | React/TypeScript/Vite static frontend | ADR-001; within permitted React option |
| 2026-10-15 | Private answers, backend-only writes, nullable correctness | ADR-002 proposed; no hosted migration |
| 2026-10-15 | Dependency versions pinned after actual audit | Lockfiles and setup report |
| 2026-10-15 | Owner approved private whatvlad/practiceloop; infrastructure through PR #16 | Repository/Issues created; four hosted CI jobs passed; no merge |
| 2026-10-15 | Preserve Private visibility despite plan-limited branch protection | GitHub protection HTTP 403 requires Pro; main is not protected; main is not protected |
| 2026-10-15 | No approval required: authors merge their own PR after green CI; review optional | Owner decision in project chat |
| 2026-10-15 | Equal agent roles; collaboration rules reduced to AGENTS.md + docs/agents | Bootstrap setup reports, backlog snapshot and onboarding docs removed (kept in Git history) |

Open questions are in docs/decisions/OPEN_QUESTIONS.md. Record substantial choices
in a new ADR rather than changing accepted history or the source specification.
