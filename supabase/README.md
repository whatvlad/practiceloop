# Database preparation

Migration preserves the MVP's four public tables and adds private storage for
answers, versioned generator data and solution steps. It is **not applied to a
hosted Supabase project**. Schema additions and nullable `attempts.is_correct`
are proposals in ADR-002; human review is required before production application.

Only authenticated reads are granted, filtered to each owner. All writes use the
backend. A backend service-role client bypasses RLS: validate the JWT and verify
ownership in every query, including reveal/check/history. Persist public problem
and private solution atomically. Provision profiles after verified login.

`private` must never be added to PostgREST exposed schemas. No public view/RPC may
return internal answers before explicit authorized reveal. Do not store secrets
in generator_data. Use bounded, versioned primitive JSON parameters, never pickle
or executable SymPy strings. Add migrations rather than editing applied SQL.

Local/CI isolation tests use a fresh PostgreSQL 17 container and the minimal
`tests/auth_fixture.sql`. See `scripts/test-db.ps1`. This tests the actual
migration, role grants, RLS and composite ownership FK. It does **not** verify
hosted Supabase Auth, JWT claims, Google OAuth or PostgREST configuration.
PL-003/004/005 track those integration checks against a disposable Supabase project.
