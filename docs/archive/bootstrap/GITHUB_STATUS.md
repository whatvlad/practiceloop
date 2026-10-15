# GitHub publication status — 2026-10-15

Owner approved creation/publication/configuration in this chat.
Repository: [whatvlad/practiceloop](https://github.com/whatvlad/practiceloop).
Visibility: **Private**, verified through authenticated GitHub API.
Default branch: **main**. Original MVP is the seed commit; infrastructure is
published on **chore/bootstrap-collaboration** and requires human PR review.
Draft PR: [#16](https://github.com/whatvlad/practiceloop/pull/16), **not merged**.
Infrastructure Issue [#1](https://github.com/whatvlad/practiceloop/issues/1) is
assigned to whatvlad and In Review; the remaining 14 Issues are Backlog/unassigned.

## Applied and verified

- Repository created under verified owner whatvlad, without replacing any history.
- Issues and repository Projects capability enabled. No Projects v2 board created.
- Squash merges enabled; merge/rebase merge methods disabled; automatic deletion
  of merged feature branches enabled.
- 15 MVP Issues published, one per prepared PL ID, with type/priority/status labels
  and acceptance criteria. No second human or assignee was invented.
- Dependabot vulnerability alerts read-back returned HTTP 204 (enabled);
  automated-security-fixes read-back returned `enabled: true, paused: false`.
- No collaborator invitations, visibility change, paid upgrade, hosted migration,
  deployment or PR merge performed.

## GitHub plan limitation: main is NOT protected

Applying `.github/branch-protection.json` returned HTTP 403:
"Upgrade to GitHub Pro or make this repository public to enable this feature."
The repository remains Private. Required human review/CI, no force push/deletion
remain project policy, but GitHub does **not** enforce this prepared protection.
Owner can separately choose a suitable plan. Do not claim main is protected,
and do not bypass the human review policy because enforcement is unavailable.

Hosted secret scanning/push protection are not confirmed: repository API did not
return security_and_analysis state. Gitleaks CI is an independent repository check.

## Published task mapping

| Local ID | GitHub Issue |
|---|---|
| PL-001 | [#1 Repository and collaboration gates](https://github.com/whatvlad/practiceloop/issues/1) |
| PL-002 | [#2 API and mathematical policies](https://github.com/whatvlad/practiceloop/issues/2) |
| PL-003 | [#3 Supabase schema](https://github.com/whatvlad/practiceloop/issues/3) |
| PL-004 | [#4 JWT and ownership](https://github.com/whatvlad/practiceloop/issues/4) |
| PL-005 | [#5 Google authentication](https://github.com/whatvlad/practiceloop/issues/5) |
| PL-006 | [#6 Basic generator](https://github.com/whatvlad/practiceloop/issues/6) |
| PL-007 | [#7 Safe parser](https://github.com/whatvlad/practiceloop/issues/7) |
| PL-008 | [#8 Equivalence checking](https://github.com/whatvlad/practiceloop/issues/8) |
| PL-009 | [#9 Remaining topics](https://github.com/whatvlad/practiceloop/issues/9) |
| PL-010 | [#10 Persistence and reveals](https://github.com/whatvlad/practiceloop/issues/10) |
| PL-011 | [#11 Practice frontend](https://github.com/whatvlad/practiceloop/issues/11) |
| PL-012 | [#12 History and profile](https://github.com/whatvlad/practiceloop/issues/12) |
| PL-013 | [#13 End-to-end verification](https://github.com/whatvlad/practiceloop/issues/13) |
| PL-014 | [#14 Hosting](https://github.com/whatvlad/practiceloop/issues/14) |
| PL-015 | [#15 Operations/release docs](https://github.com/whatvlad/practiceloop/issues/15) |

## CI and review

Hosted CI **passed all four jobs** (Frontend, Backend, Database isolation and
Security) on infrastructure commit `a201ebd92cebd8e5e962c0679896ae95fdd722f3`:
[PR run](https://github.com/whatvlad/practiceloop/actions/runs/38814546491) and
[push run](https://github.com/whatvlad/practiceloop/actions/runs/38814518255).
This includes full Git-history Gitleaks scan and actual Linux frontend/backend/
database tests. Subsequent documentation commits trigger their own checks; inspect
the latest PR head before merging. Local results are in SETUP_REPORT.md.
No merge or independent human approval exists.
Private-branch enforcement unavailability means PL-001 must not be marked Done.

## Connect another agent

Use [CONNECT_AGENT.md](../agents/CONNECT_AGENT.md) for exact clone commands and
a ready-to-send Russian prompt. Before infrastructure merge, clone the review
branch and start with independent PR review. After authorized human merge, fetch
main and claim one free Issue. Separate humans need separately approved repository
access; an agent does not receive account permissions merely from this link.
