# Shared development rules

Scope: all PracticeLoop files, for both developers and both AI agents (Codex and
Claude Code). Read this before every task. The product source of truth is the
original specification `docs/PRACTICELOOP_MVP.md` (UTF-16; read it with
`iconv -f UTF-16 -t UTF-8` if your tools show it as binary). Do not edit it
without the owner's permission.

## Team

Two developers with equal rights: @whatvlad and @Feijhoaaaaa. Each works with
their own AI agent. There are no permanent roles: anyone (human or agent) can
build frontend, backend, Supabase, tests, docs or refactors, create Issues and
PRs, and review the other developer's PRs. Nobody is review-only and nobody
needs the other's permission to start an ordinary task.

## Workflow

1. **Pick a task.** Take an open Issue or create one. Assign yourself and move it
   to *In Progress* so nobody duplicates it. Statuses: *Todo*, *In Progress*,
   *Done*; add the `blocked` label when waiting on something. Assignment is for
   coordination, not permission.
2. **Branch.** From the latest `main`: `feature/google-auth`,
   `fix/answer-validation`, `docs/...`, `refactor/...`, `test/...`. Never commit
   directly to `main`. When agents run at the same time on one machine, use
   separate clones or `git worktree`.
3. **Build.** Implement, write tests, run the checks from README, commit with
   Conventional Commits, push your branch.
4. **Open a PR** into `main`: what changed, why, what you tested, risks. Keep PRs
   reasonably small.
5. **Review and merge.** The other developer reviews (an AI agent may help).
   Ordinary changes get a light review; security, auth, database migrations and
   mathematical logic get a careful one. Authors don't approve their own PR.
   When CI is green and the review is done, merge into `main` (squash).

Coordinate with the other developer (an Issue or PR comment is enough) before
changing shared contracts: API routes/DTOs, database schema or RLS, auth
behaviour, or major architecture. Record a significant decision once, as an ADR
in `docs/decisions/`.

## Synchronization

GitHub (Issues, PRs, `main`) is the shared source of truth.
- Before starting: check `git status`, `git fetch origin --prune`, and look at
  open PRs touching the same area.
- Before merging: bring your branch up to date with `main`, resolve conflicts
  by reading both sides, rerun affected tests.
- Never overwrite someone's uncommitted work, never force-push a shared branch,
  never run destructive Git commands (reset --hard, history rewrites) on your own
  initiative.

## Project rules

- Stack: React/TypeScript/KaTeX (Cloudflare Pages) -> FastAPI/Python/SymPy
  (Oracle Cloud) -> Supabase PostgreSQL/Auth.
- MVP only: Google login, Integration topics, five difficulties, rule-based
  generation, answer checking, show answer, step-by-step solution, history,
  basic profile. No tutor, chat, subscriptions, rankings or LLM problem generation.
- Pay attention to mathematical correctness (derivative check, domains,
  integration constants), database security and API compatibility.

## Security

- Never commit secrets or `.env`. Never send service-role keys to the browser.
- Correct answers and generator internals stay in private storage; return them
  only through explicit reveal responses.
- Verify JWT signature, issuer, audience and expiry; take `user_id` from the
  verified token, never the request body. RLS plus API ownership checks always.
- Never `eval`/`sympify`/`parse_expr` user strings; use a bounded allowlisted
  parser and resource-limited workers for math input.
- Every new table needs explicit grants/revokes and RLS (Supabase grants new
  public tables to browser roles by default).

## Checks

Run the relevant commands from README before pushing. CI (Frontend, Backend,
Database isolation, Security) must be green before merge.
