# Review protocol

Implementation owner checks diff, requirements, real test outcomes, formatting,
types, dependency/secret checks, migration/API compatibility and docs. Provide
exact commands and failures, not a generic "tested" claim.

Independent reviewer reads the actual base/head diff and affected context.
Check math correctness (derivative, domains, constants, steps), malicious input,
resource exhaustion, ownership/JWT/RLS boundaries, leaked answers, failure paths,
concurrent writes and regressions. Run meaningful targeted checks when possible.
If the other AI is unavailable, record that limitation and request human review;
do not invent a Claude review or replace it with a second Codex identity.

Each finding must include:
```text
Severity: critical | high | medium | low
File: repository-relative path
Line/area: exact current location
Problem: concrete condition and behavior
Impact: consequence
Recommendation: actionable correction
Status: open | fixed (commit) | accepted by human (reason)
```
If no significant findings: say so with the reviewed scope, commands and limits;
never guarantee absence of all bugs. Fix critical/high and other blockers, rerun
relevant tests and rereview the new diff. AI review is advisory. Require at least
one independent human approval and successful hosted checks before an authorized
human merges. PR authors never approve/merge their own work.
