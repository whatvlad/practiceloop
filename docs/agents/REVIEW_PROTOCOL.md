# Receiving a HANDOFF and reviewing

When receiving a HANDOFF from the other agent:

1. Verify the referenced branch and exact commits.
2. Fetch current remote state.
3. Inspect the real GitHub diff instead of trusting the summary alone.
4. Check whether the work overlaps your Issue, files, API contract, database schema, migration, lockfile, or architectural decision.
5. If there is no overlap, acknowledge it and continue.
6. If there is overlap, stop the conflicting part of your work and ask the accountable human to assign ownership or sequence the changes.
7. Do not modify the other agent’s branch unless explicitly authorized.
8. For review findings, provide severity, file, exact line or area, concrete impact, and an actionable recommendation.
9. Do not describe self-review as independent review.
10. Review is advisory; it is not required for merging.

Use this review finding format:

```text
Severity: critical | high | medium | low
File:
Line/area:
Problem:
Impact:
Recommendation:
Status: open | fixed in commit | accepted by human with reason
```
