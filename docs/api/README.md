# API contract status

Implemented: `GET /health` -> 200 `{"status":"ok"}`. Liveness only. Runtime
OpenAPI at `/openapi.json` and `/docs`. No auth/persistence readiness claim.

Proposed routes below are NOT implemented. Agree contracts in PL-002/004/010.
Every route requires a verified Supabase Bearer access token except health.

| Route | Intended behavior |
|---|---|
| GET /api/topics | Allowed topics and available levels |
| POST /api/problems | Validate topic/level; atomically save public + private problem before returning public DTO |
| POST /api/problems/{id}/attempts | Bounded input; persist attempt; return Correct / Incorrect / Invalid expression |
| POST /api/problems/{id}/reveal-answer | Owner check; save reveal flag; return only final result |
| POST /api/problems/{id}/reveal-solution | Owner check; save solution flag; return checked steps |
| GET /api/problems | Paginated own history, no solution/internal fields |
| GET /api/problems/{id} | Reopen own public problem and authorized saved reveal state |
| GET /api/profile | Account and agreed aggregate counts |

Public response includes id, topic, difficulty, statement/LaTeX and creation time
once persistence exists. The current internal fixture DTO is not this final API.
404 for another user's ID, 401 missing/invalid token, 422 invalid request fields,
429 resource/rate limit and 503 worker unavailability are proposed transport
semantics. Invalid expression is a domain result, not a server exception.
Timeouts must not be mislabeled Incorrect; finalize retry/error behavior first.
Accept no client user_id or is_correct. Do not return expected answers in checks,
logs, OpenAPI examples or errors. Endpoint tests must cover cross-user IDs and
concurrent generation/check persistence. Generation, reveal and login should be
rate limited before public exposure.
