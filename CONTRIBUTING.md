# Contributing

Read AGENTS.md (humans and AI share the same boundaries), the MVP, relevant ADRs,
and docs/agents/WORKFLOW.md. Claim one Issue and an accountable human. Keep PRs
small and single-purpose; separate concurrent work into clones/worktrees.

Use branch names and Conventional Commits from AGENTS.md. Before a PR, fetch,
inspect divergence, resolve conflicts deliberately, rerun checks from README,
inspect the diff, scan for secrets and update relevant docs. Do not force push.

Codex and Claude Code cross-review diffs; humans approve independently. Do not
rubber-stamp or self-approve. Only an authorized human merges after required CI,
review and all acceptance criteria. See REVIEW_PROTOCOL for finding format and
WORKFLOW for Definition of Done. Bootstrap remains In Review until these gates
are actually satisfied on GitHub; local tests alone are not completion.
