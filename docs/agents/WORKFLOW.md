# Shared workflow

GitHub owns accepted code, Issues, PRs and discussions. Local docs are useful
snapshots only. Git does not automatically sync computers; each developer fetches,
reviews and pushes deliberately. Agents use their human owner's credentials with
minimum scope, never a shared token pasted into chat or tracked configuration.

1. **Backlog**: Issue specifies scope, acceptance, priority, dependencies and owner.
2. **Ready**: decisions/dependencies resolved; owner claims Issue. Check other open
   PRs for overlapping work. Prefer serial work on migrations, lockfiles and API contracts.
3. **In Progress**: agent identifies itself, fetches remote, checks a clean tree,
   branches from current main in an isolated clone/worktree and implements only scope.
4. **In Review**: implementation agent runs checks and reviews diff; creates PR
   with Issue, agent and human owner. Other AI reviews the actual diff when available.
5. **Blocked**: state exact dependency/error, impact, evidence and next action;
   unaffected independent tasks may continue. Never hide failures as success.
6. **Done**: acceptance met, architecture respected, meaningful tests pass, required
   hosted CI passes, docs current, no blocking findings, independent review complete,
   independent human approval obtained, authorized human merges PR, Issue closed,
   relevant release/decision/status records updated. No partial state counts as Done.

GitHub only natively prevents author self-approval; account types do not reliably
prove a reviewer is human. An accountable human checks this policy. Bots/AI review
never count as the required human approval, even if GitHub counts their account.
Do not claim CODEOWNERS alone enforces independent review or branch protection.

## Roles (proposal; names need confirmation)
- Developer 1 + Codex: frontend, user flows, KaTeX, frontend tests.
- Developer 2 + Claude Code: FastAPI, SymPy, Supabase, API and database tests.
- Cross review: Claude reviews Codex; Codex reviews Claude.
- Any participant may work across boundaries after ownership coordination.
- Owner approves publication, permissions and invitations; human other than PR
  author reviews and approves; authorized human performs merge.

## Safe synchronization
```powershell
git status --short --branch
git fetch origin --prune
git switch main
git pull --ff-only
git switch -c feature/issue-123-description
```
Only switch when the worktree is clean. For an existing feature, merge current
origin/main after inspecting it; do not rewrite shared commits. Analyze both sides
of conflicts; coordinate overlapping ownership, test again, push without force.
When offline, record freshness and remote ownership as unverified; do not claim
to have checked live Issues. No automatic cross-agent messaging is configured.
