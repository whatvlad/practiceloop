# Security policy

Do not open public Issues containing credentials, private user data or exploitable
details. Use GitHub private vulnerability reporting when the owner enables it;
otherwise contact the repository owner through a previously agreed private channel.
No reporting mailbox or response SLA is invented at bootstrap.

Never commit .env, service_role credentials, tokens, passwords or private keys.
Only public Supabase URL/publishable key may enter frontend configuration.
If exposed, revoke/rotate immediately with the owner, then plan history cleanup
explicitly; never rewrite shared history without permission.

PR CI has read-only repository permissions, no deployment credentials and no
pull_request_target execution. Do not approve untrusted Actions runs casually;
dependency installation and test execution run PR code. Keep external Actions
pinned and reviewed. No production deploy automation is configured.

RLS tests verify SQL isolation in a disposable DB. Hosted JWT, API ownership,
service-role usage and resource-limited expression workers require additional
integration tests before launch. A timeout must terminate the math process;
thread/request timeouts alone do not bound CPU/memory. Reject unsupported grammar,
giant expressions, deep nesting and attribute/import/call escapes before SymPy.
Never log raw credentials or user answers by default.

Dependency checks fail on configured severity; scanner/network errors fail CI.
Hosted secret scanning and push protection depend on repository plan/availability;
local Gitleaks is a separate check and does not imply those features are enabled.
