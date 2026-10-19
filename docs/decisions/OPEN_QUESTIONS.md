# Open decisions — resolve before dependent features

| ID | Question | Blocked task |
|---|---|---|
| OQ-06 | Oracle availability/region, resource-limited math worker mechanism, backups and CORS origins? | PL-014 |

Do not silently treat these as resolved. Proposals belong in the owning Issue/ADR.

OQ-06 is outside PL-002 because production host selection, capacity, backups and
CORS are deployment decisions; ADR-003 defines only the application worker's
required safety limits.

Resolved on 2026-10-19 with accountable-human approval: OQ-01, OQ-02 and OQ-03
in ADR-003; OQ-04, OQ-05 and OQ-08 in ADR-004.
