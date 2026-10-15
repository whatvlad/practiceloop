# MVP backlog — published Issues

The 15 tasks below have been published as GitHub Issues #1–#15. See the verified
[mapping and live links](GITHUB_STATUS.md). The criteria below are a preparation
snapshot; actual ownership/status/PRs are maintained on GitHub. Machine-readable
source: [backlog.json](backlog.json). Suggested pairings are proposals, not actual
assignments. Done follows WORKFLOW.md; PL-001 remains open during bootstrap review.

## PL-001: Publish repository and enforce collaboration gates

Type: Infrastructure. Priority: P0. Status: Backlog. Owner: Unassigned.
Suggested pairing: Owner + both developers. Dependencies: none.
Related PRs: none.

Apply prepared GitHub configuration after explicit approval.

- [ ] Confirm owner/private target and absence or reconcile existing history
- [ ] Publish bootstrap PR; all four hosted jobs pass
- [ ] Verify protection, independent human review, CODEOWNERS, security availability, labels and optional board
- [ ] Connect actual second developer with approved least-privilege role

## PL-002: Finalize API and unresolved mathematical policies

Type: Architecture. Priority: P0. Status: Backlog. Owner: Unassigned.
Suggested pairing: Both developers + both agents. Dependencies: none.
Related PRs: none.

Resolve OQ-01/02/03/04/05 and publish reviewed ADRs/contracts.

- [ ] Specify integration constant and real-domain equivalence policy
- [ ] Approve topic x difficulty template matrix and expression grammar/resource bounds
- [ ] Agree profile counting, invalid-attempt storage and reveal semantics
- [ ] Define API DTOs, failure/retry behavior and atomic persistence boundary

## PL-003: Apply and integration-test Supabase schema

Type: Security. Priority: P0. Status: Backlog. Owner: Unassigned.
Suggested pairing: Developer 2 + Claude Code. Dependencies: PL-002.
Related PRs: none.

Review ADR-002 and migrate a disposable Supabase project.

- [ ] Validate four public tables, private answers, indexes and composite ownership FK
- [ ] Test two real authenticated users and anonymous PostgREST clients; private schema is not exposed
- [ ] Demonstrate client writes rejected; document service-role bypass and API ownership tests required by PL-004
- [ ] Document profile provisioning and rollback/backup plan

## PL-004: Verify Supabase JWTs and enforce API ownership

Type: Security. Priority: P0. Status: Backlog. Owner: Unassigned.
Suggested pairing: Developer 2 + Claude Code. Dependencies: PL-002, PL-003.
Related PRs: none.

Implement verified identity dependency and user-scoped backend persistence.

- [ ] Check JWT signature/allowed algorithm/issuer/audience/expiry and signing-key rotation
- [ ] Reject missing/expired/tampered/wrong-project tokens
- [ ] User ID comes solely from verified identity; every problem/attempt/reveal query enforces ownership
- [ ] Integration tests deny cross-user IDs even with service_role persistence

## PL-005: Implement Google login, session restore and logout

Type: Feature. Priority: P1. Status: Backlog. Owner: Unassigned.
Suggested pairing: Developer 1 + Codex. Dependencies: PL-004.
Related PRs: none.

Wire Supabase Auth and protected client routes.

- [ ] Configure Google/Supabase callbacks and deployment origins in dev environment
- [ ] Login/session restore/token expiry/logout work across reload
- [ ] Protected routes handle unauthenticated state; keys in browser are public only
- [ ] Exercise redirect errors without logging tokens

## PL-006: Build basic-integral generator across five levels

Type: Feature. Priority: P1. Status: Backlog. Owner: Unassigned.
Suggested pairing: Developer 2 + Claude Code. Dependencies: PL-002.
Related PRs: none.

Extend internal trusted fixture using approved versioned template matrix.

- [ ] Every approved level has bounded valid parameters and deterministic replay
- [ ] Check derivative correctness and domain assumptions across parameter corpus
- [ ] Store versioned primitive parameters with no executable expression serialization
- [ ] Validate each solution step and final +C policy

## PL-007: Implement a safe bounded math-input parser

Type: Security. Priority: P0. Status: Backlog. Owner: Unassigned.
Suggested pairing: Developer 2 + Claude Code. Dependencies: PL-002.
Related PRs: none.

Normalize common notation into allowlisted expressions without string eval.

- [ ] Support 3pi, 3*pi, 3π, 3/5, sqrt(3), √3, e^2 and pi/4 + 2
- [ ] Reject imports, attributes, arbitrary calls, malformed input and non-allowlisted symbols
- [ ] Bound input length, nesting, node count, exponent size and numeric literal length before construction
- [ ] Run CPU/memory/wall-limited killable worker tests for pathological expressions; no request-thread-only timeout

## PL-008: Verify mathematical equivalence and integration constants

Type: Feature. Priority: P0. Status: Backlog. Owner: Unassigned.
Suggested pairing: Developer 2 + Claude Code. Dependencies: PL-006, PL-007.
Related PRs: none.

Return Correct, Incorrect or Invalid expression using agreed domain/constant policy.

- [ ] Accept equivalent fractions and alternative valid antiderivatives
- [ ] Test constants, logs/absolute values, trig identities and domain differences
- [ ] Malformed input never causes execution or a 500; timeout is not Incorrect
- [ ] Adversarial corpus verifies process termination and resource limits

## PL-009: Add remaining four Integration topic families

Type: Feature. Priority: P1. Status: Backlog. Owner: Unassigned.
Suggested pairing: Developer 2 + Claude Code. Dependencies: PL-006, PL-008.
Related PRs: none.

Substitution, integration by parts, rational functions and trigonometric integrals.

- [ ] Split into separate topic Issues with non-overlapping owners before implementation
- [ ] Each topic implements the approved five-level template matrix
- [ ] Check domain-valid parameters, exact derivative invariants and deterministic replay
- [ ] Each template includes verified step-by-step solutions and versioning

## PL-010: Persist generation, attempts and authorized reveals

Type: Feature. Priority: P1. Status: Backlog. Owner: Unassigned.
Suggested pairing: Developer 2 + Claude Code. Dependencies: PL-003, PL-004, PL-006, PL-008.
Related PRs: none.

Implement problem/attempt/reveal API with trusted outcomes.

- [ ] Save public problem and private solution atomically before generation response
- [ ] Persist every attempt including agreed invalid state; no client-controlled correctness
- [ ] Reveal only after owner verification and persist flags
- [ ] Test DB failure, concurrency, retries/idempotency policy, no internal-data leak and rate limits

## PL-011: Implement practice flow and KaTeX problem card

Type: Feature. Priority: P1. Status: Backlog. Owner: Unassigned.
Suggested pairing: Developer 1 + Codex. Dependencies: PL-005, PL-010.
Related PRs: none.

Build topic/difficulty selection, answer/check/reveal/next flows.

- [ ] All MVP card controls and five levels use agreed API contracts
- [ ] Trust-disabled KaTeX and accessible math/labels/keyboard controls
- [ ] Handle loading, invalid expressions, server failures, stale responses and duplicate submissions
- [ ] Never prefetch answers/solution internals into public problem state

## PL-012: Implement history, reopen and basic profile

Type: Feature. Priority: P1. Status: Backlog. Owner: Unassigned.
Suggested pairing: Developer 1 + Codex with Developer 2 API support. Dependencies: PL-002, PL-005, PL-010.
Related PRs: none.

Own paginated history and agreed profile counters.

- [ ] Show topic, level, date, attempts and answer/solution-reveal flags
- [ ] Reopen any owned previous problem with persisted state
- [ ] Profile shows account, generated, attempted and correct counts with tested repeated-attempt semantics
- [ ] Pagination is stable; users cannot read others' rows

## PL-013: Verify complete MVP end to end

Type: Testing. Priority: P0. Status: Backlog. Owner: Unassigned.
Suggested pairing: Both developers + cross-agent reviewers. Dependencies: PL-009, PL-011, PL-012.
Related PRs: none.

Exercise complete authenticated practice flow against disposable Supabase.

- [ ] Google session -> choose -> generate/persist -> attempt -> reveal -> reopen -> profile is verified
- [ ] Cross-user API/PostgREST/private data denial tested
- [ ] Math corpus, malicious input, worker saturation and DB failure checks pass
- [ ] Independent diff review and independent human acceptance; no out-of-scope features

## PL-014: Prepare Cloudflare and Oracle deployment

Type: Infrastructure. Priority: P1. Status: Backlog. Owner: Unassigned.
Suggested pairing: Owner + Developer 2; Codex reviews frontend setup. Dependencies: PL-004, PL-007, PL-013.
Related PRs: none.

Owner-approved hosting configuration for existing specified platforms.

- [ ] Confirm Oracle Free Tier capacity/region and killable worker isolation
- [ ] Deploy static frontend and FastAPI only after owner approval; HTTPS/CORS/health/rate limits verified
- [ ] Secrets remain backend-only, Google redirects correct, backups/log redaction/restore documented
- [ ] Document rollbacks and verify deployed smoke checks

## PL-015: Document operations, review gates and MVP release

Type: Documentation. Priority: P1. Status: Backlog. Owner: Unassigned.
Suggested pairing: Both developers + both agents. Dependencies: PL-001, PL-013, PL-014.
Related PRs: none.

Record actual deployed behavior and acceptance evidence.

- [ ] README/API/ADRs reflect implementation and all limitations
- [ ] Second developer can clone, run tests and use each agent with isolated worktrees
- [ ] No missing hosted CI/review/approval/merge gate is marked Done
- [ ] Owner selects license; record meaningful user-facing release changelog

Start serially with repository setup and shared architecture, then split independent
frontend/backend tasks after contracts are fixed. PL-009 is an epic to split per
topic before implementation; do not implement all families in one giant PR.
