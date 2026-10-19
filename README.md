# PracticeLoop

A mathematics practice platform with rule-based problem generation, symbolic
answer verification and personal practice history. The MVP covers Integration,
five topics and five difficulty levels, Google login, attempts, answer/solution
reveal and a basic profile. [Original specification](docs/PRACTICELOOP_MVP.md).

**Current code: Google account login with saved server-generated practice.**
Supabase handles sign-in, restore and logout. Signed-in generation, attempts and
reveals use the saved API. History reloads saved problems with paginated older
entries, latest attempts and reveal flags; profile counts cover the whole account.
[Auth setup](docs/auth/GOOGLE_AUTH.md), [practice UI](docs/architecture/SAVED_PRACTICE_UI.md).
Private repository:
[whatvlad/practiceloop](https://github.com/whatvlad/practiceloop). Tasks live in
[GitHub Issues](https://github.com/whatvlad/practiceloop/issues). Initial schema is
applied to the hosted test database; #3's two-user isolation verification passed.
Cloudflare Pages serves the preview; the API runs on Oracle.
The backend also provides the bounded math-input parser and isolated Linux
construction worker from #7 and the shared answer checker from #8. Untracked
preview integration is implemented in #34; #10/#11/#12 connect saved practice,
durable history, reopen and profile counts.
See [math-input implementation](docs/architecture/MATH_INPUT.md).
The basic-integral generator now covers levels 1–5 with versioned private
parameters and checked solution steps ([generator details](docs/architecture/BASIC_GENERATOR.md)).
The preview connects basic integrals and substitution at levels 1–2 to a separate
non-persistent API, with 186 verified records and no repeats within a pool cycle.
Other cells are disabled. [Preview boundaries](docs/architecture/PREVIEW_PRACTICE.md).

## Stack and structure

React, TypeScript, Vite and KaTeX (Cloudflare Pages); Python, FastAPI and SymPy
(Oracle Free Tier); Supabase PostgreSQL and Auth. Browser -> authenticated
FastAPI -> rule engine/private solutions and Supabase. Only backend can write
trusted outcomes; owner-filtered browser reads use RLS. [Architecture](docs/architecture/OVERVIEW.md).

```text
frontend/src/          React app: components/, pages/, styles/, data/ (api.ts + temporary mock/)
backend/app/           main.py, api/, core/, models/, services/, generators/, schemas/
backend/tests/         liveness, mathematical invariants and public-data boundary
supabase/migrations/   hosted test schema and verified two-user RLS isolation
supabase/tests/        disposable SQL fixture and isolation tests
docs/                 MVP, architecture, decisions, agents, api
.github/              CI, issue/PR templates, owners, Dependabot, protection payload
scripts/              repository checks, disposable database tests
```

## Local setup

Use Node 24 LTS and Python 3.12–3.14. CI targets Node 24/Python 3.12/Linux;
use these supported versions for local work as well.
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
Frontend sign-in needs the public Supabase settings in frontend/.env.local;
copy only the VITE_* public values there. Saved practice needs backend database
and auth configuration (docs/production/ORACLE_DEPLOY.md).
Never copy the entire backend .env into the frontend. On Unix use
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
powershell -File scripts/test-db.ps1
```
Database test needs Docker and pulls a disposable PostgreSQL image. Never point
auth_fixture.sql at Supabase/shared data. Git history secret scan is also in CI;
run Gitleaks locally with `gitleaks git . --config .gitleaks.toml --redact` if needed.
No command should report success on skipped/missing tests. CI jobs are Frontend,
Backend, Database isolation and Security; hosted outcomes are unverified until run.

## Collaboration

Two developers, each with an AI agent, as equal collaborators. Rules:
[AGENTS.md](AGENTS.md) and [docs/agents](docs/agents/WORKFLOW.md).
[Architecture](docs/architecture/OVERVIEW.md), [API status](docs/api/README.md),
[decisions](docs/decisions/DECISIONS.md), [open questions](docs/decisions/OPEN_QUESTIONS.md),
[security](SECURITY.md), [changelog](CHANGELOG.md). No license is granted yet;
the owner must select one.

## Product direction

The original [MVP specification](docs/PRACTICELOOP_MVP.md) remains the product
source of truth. Approved planning documents refine the path to production
without silently changing that specification:

- [production-readiness plan](docs/production/PRODUCTION_READINESS_PLAN.md);
- [problem-generation intent](docs/intent/PROBLEM_GENERATION.md);
- [educational content-style intent](docs/intent/CONTENT_STYLE.md);
- [staged production roadmap](docs/agents/NEXT_CHAT_GITHUB_ROADMAP.md).

The roadmap is tracked in
[GitHub Issue #30](https://github.com/whatvlad/practiceloop/issues/30).
