# ADR-002: private solutions and backend-owned writes

Date: 2026-10-15. Status: proposed; migration prepared for review, not hosted.

The MVP forbids direct browser access to correct answers or generator internals.
Use private.problem_solutions; expose only the four public MVP tables, grant
authenticated read with owner RLS, deny browser writes, let backend persist
trusted generation/check results and reveal events atomically.

Tradeoff: service_role bypasses RLS; JWT verification and query-level ownership
must be tested in the API. Keep private outside exposed PostgREST schemas.
Composite attempts(problem_id,user_id) FK prevents cross-owner attachment.
Nullable attempts.is_correct distinguishes invalid input from a wrong answer
without expanding the source specification; confirm before applying migration.

Alternative: user-scoped write policies and privileged RPCs. Deferred because
allowing arbitrary client writes risks fabricated scores/history/reveal flags.
