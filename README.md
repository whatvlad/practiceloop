# PracticeLoop

A mathematics practice platform with rule-based problem generation, symbolic
answer verification and personal practice history. The MVP covers Integration,
five topics and five difficulty levels, Google login, attempts, answer/solution
reveal and a basic profile. [Original specification](docs/PRACTICELOOP_MVP.md).

**Current state: collaboration infrastructure and a development scaffold.** The
authenticated practice flow is not implemented. Private repository:
[whatvlad/practiceloop](https://github.com/whatvlad/practiceloop).
Infrastructure is submitted on `chore/bootstrap-collaboration` for human review;
no hosted database has been migrated and no deployment is configured. See
[publication status](docs/development/GITHUB_STATUS.md),
[setup report](docs/development/SETUP_REPORT.md) and
[second-agent connection guide](docs/agents/CONNECT_AGENT.md).

## Stack and structure

React, TypeScript, Vite and KaTeX (Cloudflare Pages); Python, FastAPI and SymPy
(proposed Oracle Free Tier); Supabase PostgreSQL and Auth. Browser -> authenticated
FastAPI -> rule engine/private solutions and Supabase. Only backend can write
trusted outcomes; owner-filtered browser reads use RLS. [Architecture](docs/architecture/OVERVIEW.md).

```text
frontend/src/          React entry, safe KaTeX utility and tests
backend/app/           main.py, api/, core/, models/, services/, generators/, schemas/
backend/tests/         liveness, mathematical invariants and public-data boundary
supabase/migrations/   prepared schema and RLS (not hosted)
supabase/tests/        disposable SQL fixture and isolation tests
docs/                 MVP, architecture, decisions, agents, api, development
.github/              CI, issue/PR templates, owners, Dependabot, protection payload
scripts/              repository checks, disposable database tests, issue publishing
```

## Local setup

Use Node 24 LTS and Python 3.12–3.14. CI targets Node 24/Python 3.12/Linux;
local setup machine uses different runtime versions noted in the report.
PowerShell examples, from repository root:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e backend
cd frontend
npm ci --ignore-scripts
cd ..
```
Do not commit .env. Copy the example only when configuring real services:
```powershell
Copy-Item .env.example .env
```
Scaffold needs no credentials. Real services are not wired yet. Vite reads
frontend/.env.local when integration is implemented; copy only the VITE_* public
values there. Never copy the entire backend .env into the frontend. On Unix use
`.venv/bin/python` instead of `.venv\Scripts\python.exe`.

## Run

In two terminals:
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
```powershell
cd frontend
npm run dev
```
Frontend: http://localhost:5173. Backend health: http://localhost:8000/health.
OpenAPI: http://localhost:8000/docs. Health is liveness, not database readiness.

## Verify

```powershell
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
npm audit --audit-level=moderate
cd ..
.\.venv\Scripts\python.exe -m ruff check backend scripts
.\.venv\Scripts\python.exe -m ruff format --check backend scripts
cd backend
..\.venv\Scripts\python.exe -m mypy
..\.venv\Scripts\python.exe -m pytest
cd ..
.\.venv\Scripts\python.exe -m pip_audit --no-deps --disable-pip --timeout 10 --progress-spinner off -r backend/requirements.txt
.\.venv\Scripts\python.exe scripts/check_repository.py
powershell -File scripts/test-db.ps1
```
Database test needs Docker and pulls a disposable PostgreSQL image. Never point
auth_fixture.sql at Supabase/shared data. Git history secret scan is also in CI;
see GITHUB_SETUP.md for the local command after the first commit exists.
No command should report success on skipped/missing tests. CI jobs are Frontend,
Backend, Database isolation and Security; hosted outcomes are unverified until run.

## Collaboration

Read [CONTRIBUTING](CONTRIBUTING.md), [shared agent rules](AGENTS.md),
[workflow and Done criteria](docs/agents/WORKFLOW.md),
[task protocol](docs/agents/TASK_PROTOCOL.md),
[review protocol](docs/agents/REVIEW_PROTOCOL.md) and [handoff](docs/agents/HANDOFF.md).
One Issue/owner/branch, isolated worktrees, cross-agent review and independent
human approval. [Connect developer 2, Codex and Claude](docs/development/ONBOARDING.md).

Owner approval is required before GitHub creation/publication/access changes or
merge. [Exact GitHub completion steps](docs/development/GITHUB_SETUP.md).
[Backlog](docs/development/BACKLOG.md), [open decisions](docs/decisions/OPEN_QUESTIONS.md),
[API status](docs/api/README.md), [security](SECURITY.md),
[current status](docs/agents/STATUS.md), [decision log](docs/agents/DECISIONS.md),
[changelog](CHANGELOG.md). No license is granted yet; owner must select one.
