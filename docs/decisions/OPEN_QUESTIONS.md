# Open decisions — resolve before dependent features

| ID | Question | Blocked task |
|---|---|---|
| OQ-01 | Require explicit +C, accept any additive constant, or both? Define real domains and absolute values such as log(abs(x)). Proposed resolution: ADR-003. | PL-008 |
| OQ-02 | Exact template matrix and meaning of five difficulties for each of five topics? Proposed resolution: ADR-003. | PL-006/009 |
| OQ-03 | Safe grammar, Unicode normalization, maximum AST size/depth, power bounds and CPU/memory wall timeout? Proposed resolution: ADR-003. | PL-007/008 |
| OQ-04 | Count distinct attempted/correct problems or all attempts in profile? Proposed resolution: ADR-004. | PL-012 |
| OQ-05 | Confirm private solution storage, nullable correctness and profile provisioning strategy (ADR-002). Proposed resolution: ADR-004. | PL-003 |
| OQ-06 | Oracle availability/region, resource-limited math worker mechanism, backups and CORS origins? | PL-014 |
| OQ-08 | Reveal stores mutable flags only or additional audit timestamps? Proposed resolution: ADR-004. | PL-010 |

Do not silently treat these as resolved. Proposals belong in the owning Issue/ADR.

OQ-06 is outside PL-002 because production host selection, capacity, backups and
CORS are deployment decisions; ADR-003 defines only the application worker's
required safety limits.
