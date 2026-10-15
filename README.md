# PracticeLoop

A mathematics practice platform with rule-based problem generation, symbolic
answer verification and personal practice history. The MVP covers Integration,
five topics and five difficulty levels, Google login, attempts, answer/solution
reveal and a basic profile. [Original specification](docs/PRACTICELOOP_MVP.md).

**Current state: development scaffold.** The authenticated practice flow is not
implemented yet. Private repository:
[whatvlad/practiceloop](https://github.com/whatvlad/practiceloop). Tasks live in
[GitHub Issues](https://github.com/whatvlad/practiceloop/issues). No hosted
database has been migrated and no deployment is configured.

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
run Gitleaks locally with `gitleaks git . --config .gitleaks.toml --redact` if needed.
No command should report success on skipped/missing tests. CI jobs are Frontend,
Backend, Database isolation and Security; hosted outcomes are unverified until run.

## Collaboration

Two developers, two AI agents, equal rights. Rules for everyone (humans, Codex,
Claude Code): [AGENTS.md](AGENTS.md). In short: pick or create an Issue, branch
from `main`, push, open a PR, the other developer reviews, merge when CI is green.
[Getting started](docs/development/ONBOARDING.md), [contributing](CONTRIBUTING.md),
[architecture](docs/architecture/OVERVIEW.md), [API status](docs/api/README.md),
[decisions](docs/decisions/DECISIONS.md), [open questions](docs/decisions/OPEN_QUESTIONS.md),
[security](SECURITY.md), [changelog](CHANGELOG.md). Bootstrap-era process documents
are kept in [docs/archive/bootstrap](docs/archive/bootstrap/README.md) for history only.
No license is granted yet; the owner must select one.
