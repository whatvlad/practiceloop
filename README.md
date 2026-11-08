# PracticeLoop

A mathematics practice platform with rule-based problem generation, symbolic
answer verification and personal practice history. The MVP covers Integration:
five topics, difficulty levels 1–5, Google login, saved attempts, answer and
solution reveal, history and a profile. [Original specification](docs/PRACTICELOOP_MVP.md).

**Status: MVP complete (0.1.0, see [CHANGELOG](CHANGELOG.md)).** Live at
https://practiceloop.pages.dev (noindex). Signed-in learners can:

- practise the current 49 Algebra, Mathematical Analysis, and Probability and Statistics topics, with their
  available levels and mixed practice supplied by the API, including the
  [Analysis I](docs/architecture/ANALYSIS_I.md) and
  [Analysis II](docs/architecture/ANALYSIS_II.md) and
  [Probability and Statistics](docs/architecture/PROBABILITY_STATISTICS.md) curricula;
- solve [elementary functions and logic](docs/architecture/ELEMENTARY_FUNCTIONS.md),
  including complete real sets, branch-aware inverses and periodic solutions;
- type answers in a formula editor; typed engine answers check them symbolically
  (Correct, Incorrect or Invalid expression, with explicit missing-constant feedback);
- open a permanent problem code at `/p/<code>` and sign in to solve that exact
  exercise in their own history;
- reveal the answer or the full step-by-step solution;
- reopen every generated problem from history after a reload;
- share a problem's statement by link or short code for 90 days, and stop
  sharing it at any time; recipients can view it without an account and sign
  in to solve the exact exercise in their own saved history;
- see profile counts, constant-omission statistics, an optional display name,
  and delete their account.

A signed-out visitor gets one fixed, untracked demo problem. Details:
[saved practice](docs/architecture/SAVED_PRACTICE_UI.md),
[account completion](docs/architecture/ACCOUNT_COMPLETION.md),
[topic generators](docs/architecture/TOPIC_GENERATORS.md),
[answer checking](docs/architecture/ANSWER_CHECK.md),
[API](docs/api/README.md), [operations](docs/production/ORACLE_DEPLOY.md).

Private repository [whatvlad/practiceloop](https://github.com/whatvlad/practiceloop);
tasks are [GitHub Issues](https://github.com/whatvlad/practiceloop/issues) worked in
the order of the [Implementation Queue](https://github.com/users/whatvlad/projects/1).

## Known limitations

- **Hosting is a single free-tier VM.** The API runs on one Oracle A1.Flex VM
  (1 OCPU, 6 GB) with one math-worker slot; a busy worker returns a retryable
  `503`. A complex answer can hit the 2 s CPU cap and returns
  `math_check_inconclusive`. Rate limits are per process and reset on restart.
  Shared-problem lookups have one global limit, since the client address is
  not passed through.
  The VM runs Ubuntu 20.04 on ESM security updates and also hosts an unrelated
  app ([ORACLE_DEPLOY.md](docs/production/ORACLE_DEPLOY.md)).
- **Backups are manual.** Supabase is on the Free plan: no scheduled backups or
  PITR. Recovery copies are made by hand and must expire within 30 days of an
  account deletion ([ACCOUNT_COMPLETION.md](docs/architecture/ACCOUNT_COMPLETION.md)).
- **Preview, not a launch.** The privacy page is a draft without the
  operator's legal details; launch blockers are listed in
  [PRODUCTION_CHECKLIST.md](docs/production/PRODUCTION_CHECKLIST.md).
  The site is public but `noindex`, has no custom
  domain, and Cloudflare Access is off. Until the Google OAuth consent screen is
  published, only Google accounts listed as test users can sign in. Google is the
  only sign-in provider.
- **Content is fixed.** Problems come from a verified catalogue (no repeats
  within half a cell's catalogue per learner), not open-ended generation. Only
  the current Algebra, Mathematical Analysis and Probability and Statistics syllabus is covered. Mistake
  native wrong answers get general feedback; historical named feedback remains readable.
- **Answer language is bounded** (ADR-003): real domain only, a 256-byte limit,
  and an allowlisted grammar. The formula editor's phone keyboard was checked
  on iOS in an emulator only.
- **Process gates are conventions.** `main` has no branch protection; see
  [Merge gates](#merge-gates).
- `/health` is liveness only, not a database readiness check.

## Stack and structure

React, TypeScript, Vite and KaTeX (Cloudflare Pages); Python, FastAPI and SymPy
(Oracle Free Tier); Supabase PostgreSQL and Auth. Browser -> authenticated
FastAPI -> rule engine/private solutions and Supabase. Only backend can write
trusted outcomes; owner-filtered browser reads use RLS. [Architecture](docs/architecture/OVERVIEW.md).

```text
frontend/src/          React app: components/, pages/, styles/, data/api.ts (the only API boundary)
backend/app/           main.py, api/, core/, models/, services/, engine/, math_input/, schemas/
backend/tests/         API, auth, generators, answer checking and public-data boundary
supabase/migrations/   applied schema migrations (deployed by supabase-deploy.yml)
supabase/tests/        disposable SQL fixture and isolation tests
docs/                 MVP, architecture, decisions, agents, api
.github/              CI, issue/PR templates, owners, protection payload
scripts/              repository checks, disposable database and end-to-end tests
deploy/oracle/        VM bootstrap, release, rollback and audit scripts
```

## Local setup

Use Node 24 LTS and Python 3.12–3.14. CI targets Node 24/Python 3.12/Linux;
use these supported versions for local work as well.
PowerShell examples, from repository root:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e backend
.\.venv\Scripts\python.exe -m app.engine.catalogue
cd frontend
npm ci --ignore-scripts
cd ..
```
Do not commit .env. Copy the example only when configuring real services:
```powershell
Copy-Item .env.example .env
```
Build the private engine catalogue after changing an engine generator or topic:
`.\.venv\Scripts\python.exe -m app.engine.catalogue`. It writes the ignored
`backend/.engine-catalogue.json` (64 verified codes per engine topic x level,
including rendered answers and steps). Startup refuses a missing or incomplete
catalogue; never copy this private artifact into frontend assets. The Oracle
release script builds it before switching releases; rollback keeps the prior
release's own catalogue. See [ADR-008](docs/decisions/0008-generator-engine.md).

Frontend sign-in needs the public Supabase settings in frontend/.env.local;
copy only the VITE_* public values there. Saved practice needs backend database
and auth configuration (docs/production/ORACLE_DEPLOY.md).
Never copy the entire backend .env into the frontend. On Unix use
`.venv/bin/python` instead of `.venv\Scripts\python.exe`.

## Run

For the local matrix generator preview, complete the setup above, then run
`..\.venv\Scripts\python.exe -m uvicorn local_matrix_preview:app --host 127.0.0.1 --port 8011`
from `backend/`. Run Vite from `frontend/` and open `/local-preview.html`.
To view it on another Tailscale device, start Vite with
`npm run dev -- --host <tailscale-ip> --port 5177` and use that IP and port.
The preview uses real generators without login or saved history; it is local
development tooling, not a production API.

In two terminals:
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
```powershell
cd frontend
npm run dev
```
A preview of `main` (saved practice, plus the Graphify code graph at `/graph/`)
deploys to Cloudflare Pages via `.github/workflows/preview.yml` at
https://practiceloop.pages.dev (noindex, Google login; practice is persisted).
Frontend: http://localhost:5173. Backend health: http://localhost:8000/health.
OpenAPI: http://localhost:8000/docs. Health is liveness, not database readiness.

## Verify

```powershell
cd frontend
npm run lint
npm run lint:content
npm run typecheck
npm test
npm run build
npm audit --audit-level=moderate
cd ..
.\.venv\Scripts\python.exe -m ruff check backend scripts
.\.venv\Scripts\python.exe -m ruff format --check backend scripts
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_supabase_*_unit.py'
cd backend
..\.venv\Scripts\python.exe -m mypy
..\.venv\Scripts\python.exe -m pytest
cd ..
.\.venv\Scripts\python.exe -m pip_audit --no-deps --disable-pip --timeout 10 --progress-spinner off -r backend/requirements.txt
.\.venv\Scripts\python.exe scripts/check_repository.py
.\.venv\Scripts\python.exe scripts/test-db.py
```
Before the first push of a pull request, run `python scripts/pre-push.py`: ruff,
`ruff format --check`, mypy and the database tests below, one line per step
(`--no-db` skips the database). mypy checks as Linux (`platform = "linux"`), so a
clean run on Windows means a clean Backend CI run.

### Local database

`scripts/test-db.py` runs CI's Database isolation job locally: it starts a
disposable PostgreSQL 17, applies every migration, runs the RLS and hosted-check
SQL, `pytest -m db` and the [end-to-end check](docs/production/MVP_E2E_CHECK.md),
then removes the database (`--sql-only` skips the Python parts). It uses Docker
(`postgres:17`, as in CI) when installed, otherwise native PostgreSQL 17 binaries.

On Windows, most API tests check answers through the math worker, which only runs
on Linux, so run the job in WSL (Ubuntu 24.04). One-time setup, no sudo: it
installs `uv`, a Python 3.12 venv with `backend/requirements.txt` and PostgreSQL
17 from apt.postgresql.org (unpacked, not installed) into
`~/.local/share/practiceloop` inside WSL:

```powershell
wsl bash scripts/setup-wsl-tests.sh
.\.venv\Scripts\python.exe scripts/test-db.py --wsl                  # whole CI job
.\.venv\Scripts\python.exe scripts/test-db.py --wsl -- -q tests/test_practice_api.py
```

`scripts/pre-push.py` uses `--wsl` on Windows when this setup exists. To check
only the SQL part on Windows itself (migrations, RLS, hosted checks), without
Docker:

1. Download the PostgreSQL 17 "Windows x86-64" binaries zip (not the installer)
   from https://www.enterprisedb.com/download-postgresql-binaries.
2. Extract it so `C:\PracticeLoop\.local\postgres\bin\initdb.exe` exists (the zip
   holds a `pgsql` folder; rename it to `postgres`). `.local/` is git-ignored and
   worktrees use the main checkout's copy. No admin rights or service needed.
   An installed PostgreSQL 17 in `C:\Program Files\PostgreSQL\17\bin`, a folder in
   `PRACTICELOOP_PG_BIN` or `--pg-bin`, or `initdb` on `PATH` also work.

3. Run `.\.venv\Scripts\python.exe scripts/test-db.py --sql-only`.

On Linux or macOS, `python scripts/test-db.py` runs the whole job directly.
Arguments after `--` are added to `pytest -m db` (and skip the end-to-end flow). `--serve`
prints `PRACTICELOOP_TEST_DATABASE_URL` for running `pytest -m db` from another
terminal until Ctrl+C. Never point these files at Supabase or shared data. Git history secret scan is also in CI;
run Gitleaks locally with `gitleaks git . --config .gitleaks.toml --redact` if needed.
No command should report success on skipped/missing tests. CI jobs are Frontend,
Backend, Database isolation and Security; hosted outcomes are unverified until run.

Normal Backend CI runs the critical test files listed in `.github/workflows/ci.yml`:
authentication, account, health, math input and worker limits, answer checking,
preview, sharing, topic areas and `test_engine*.py`. Put new engine tests under that
name and update the list when other critical tests are added. The broader generator
and visualization tests are not part of this fast check. Run the full backend suite
locally with the `pytest` command above, or run the CI workflow manually with
`full_backend` enabled. Database isolation and Security keep their separate checks.
Local runs cap randomised generator seed sweeps at 50 seeds per test to keep
iterations short; hosted CI (where `CI` is set) always runs the full counts. Set
`$env:PRACTICELOOP_SEEDS = "1000"` (PowerShell) or `PRACTICELOOP_SEEDS=1000` to
run the full sweep locally (`backend/tests/seed_sweep.py`).
Worksheet TeX is temporarily disabled in CI until the worksheet is reworked
([#181](https://github.com/whatvlad/practiceloop/issues/181)).

## Collaboration

Two developers, each with an AI agent, as equal collaborators. Rules:
[AGENTS.md](AGENTS.md) and [docs/agents](docs/agents/WORKFLOW.md).
[Architecture](docs/architecture/OVERVIEW.md), [API](docs/api/README.md),
[decisions](docs/decisions/DECISIONS.md), [open questions](docs/decisions/OPEN_QUESTIONS.md),
[security](SECURITY.md), [changelog](CHANGELOG.md).

### Second developer setup

1. Get collaborator access to the repository and the
   [Implementation Queue](https://github.com/users/whatvlad/projects/1), and sign in
   `gh` with the `project` scope: `gh auth login`, then `gh auth refresh -s project`.
2. Clone once and follow [Local setup](#local-setup) and [Verify](#verify). Docker or
   PostgreSQL 17 binaries are only needed for `scripts/test-db.py`
   ([Local database](#local-database)).
3. Give each agent (Codex, Claude Code) its own worktree and branch from the
   latest `main`, so agents never share a working directory:
   ```powershell
   git fetch origin --prune
   git worktree add ..\practiceloop-issue-15 -b claude/issue-15 origin/main
   ```
   Each worktree needs its own `.venv` and `frontend/node_modules`. Remove it
   after the merge with `git worktree remove ..\practiceloop-issue-15`.
4. Point the agent at the worktree. Codex reads [AGENTS.md](AGENTS.md); Claude Code
   reads [CLAUDE.md](CLAUDE.md), which points to AGENTS.md. Graphify is optional:
   `bash scripts/setup-graphify.sh` (Git Bash on Windows).
5. Secrets (`api.env` on the VM, GitHub Actions secrets, Supabase dashboard) are
   managed by the owner and never shared through chat. Local work needs only the
   public `VITE_*` values; the tests above need no secrets.

### Merge gates

These are the gates that actually exist; none is enforced by GitHub.

| Gate | State |
|---|---|
| Hosted CI (Frontend, Backend, Database isolation, Security) | Runs on every PR and push to `main`; the author merges only when it is green (convention). Backend and Database isolation skip draft PRs and changes outside `backend/`, `scripts/`, `deploy/`, `supabase/`. Worksheet TeX is temporarily disabled until the worksheet is reworked. |
| Review | Optional; recommended for database, auth and mathematical changes (AGENTS.md) |
| Approval | Not required; authors merge their own PRs (owner decision, 2026-10-15) |
| Branch protection / rulesets | **Not applied.** The private repo's plan returns HTTP 403; `.github/branch-protection.json` is an unapplied payload |
| Deploy | A push to `main` deploys the frontend (`preview.yml`), backend (`backend-deploy.yml`) and migrations (`supabase-deploy.yml`) when their files change. Deploys run alongside CI, not after it, so a red `main` can still deploy; `backend-deploy.yml` runs no tests of its own |

## License

Proprietary, all rights reserved. See [LICENSE](LICENSE).

## Product direction

Current topics use the native engine in Algebra and Mathematical Analysis.
Analysis I (#145) and Analysis II (#146) extend the retained integral and partial
derivative families; #200 adds the approved Probability and Statistics matrix.
Curriculum expansion follows
the [ADR-005 amendment](docs/decisions/0005-multiple-integrals-and-derivatives.md#amendment-practice-areas-144-2026-10-26).

The original [MVP specification](docs/PRACTICELOOP_MVP.md) remains the product
source of truth. Approved planning documents refine the path to production
without silently changing that specification:

- [production-readiness plan](docs/production/PRODUCTION_READINESS_PLAN.md);
- [problem-generation intent](docs/intent/PROBLEM_GENERATION.md);
- [educational content-style intent](docs/intent/CONTENT_STYLE.md);
- [staged production roadmap](docs/agents/NEXT_CHAT_GITHUB_ROADMAP.md).

The roadmap is tracked in
[GitHub Issue #30](https://github.com/whatvlad/practiceloop/issues/30).
