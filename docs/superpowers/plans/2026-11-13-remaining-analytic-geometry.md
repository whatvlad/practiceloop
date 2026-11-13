# Remaining analytic geometry implementation plan

> **For agentic workers:** Use superpowers:executing-plans. Work serially in
> this worktree; AGENTS.md forbids additional agents without human approval.

**Goal:** Complete the five remaining analytic-geometry sections with exact
answer checking, progressive diagrams and three meaningful levels per type.

**Architecture:** Extend the existing deterministic engine and visual grammar.
New compatible generator versions use the existing registry, catalogue and
generate/check/reveal/reopen path. Reuse the current 3D/2D viewer and typed inputs.

**Tech stack:** Python 3.12, Pydantic, SymPy, FastAPI; React, TypeScript, Three.js,
Vitest. No new application dependency or service.

**Spec:** `docs/superpowers/specs/2026-11-12-remaining-analytic-geometry-design.md`.
**Base:** `78b8ef0c5650fffab9420d7b2ceec54cf9bfbfde`.

**Local outcome (2026-11-13):** Tasks 1–5 implemented and checked. Coverage and
the repeatable completion cycle are in `docs/architecture/ANALYTIC_GEOMETRY.md`;
evidence, self-review findings and unrelated full-suite failures are in
`docs/LOCAL_GEOMETRY_REVIEW.md`. No push, merge or deployment was performed.

## Global constraints

- Local edits, tests and preview only; a push requires separate approval.
- Keep old versions, saved codes, privacy and existing practice sections intact.
- One exercise per card; independent exercise-type and three-level selectors.
- Include every significant transformation, rule and corresponding construction.
- Statement diagrams contain givens only; solution diagrams appear on reveal.
- Show genuine coordinate axes, labels and redundant non-colour cues.
- Correctly label 2D projection/section; preserve automatic resource management.
- Ordinary seed sweeps stay at 50. Report Windows-only skips; check workers in Linux.

## Review focus

- Equivalent plane equations and reparameterised lines/planes must be accepted.
- Missing members of an unordered answer, zero directions and rank loss must fail.
- Parallel/coincident/intersecting/skew objects must not share incorrect formulas.
- Special parameter values, two signs of a volume and zero distances need coverage.
- Public statement/history/code responses must not leak derived solution objects.

## Task 1: Exact geometric answers

**Files:** `backend/app/engine/answers/geometry.py`,
`backend/tests/test_geometry_answers.py`.
**Consumes:** MathNode, FormulaAnswer, OrderedAnswer, InputContract.
**Produces:** PlaneEquationAnswer, ParametricGeometryAnswer and VectorSetAnswer,
using existing formula/tuple input grammars and immutable Answer protocol.

- [x] Add hand-derived tests for scaled plane equations, shifted/scaled line
  parameters, alternate plane bases and unordered complete vector pairs.
- [x] Observe failure; implement exact affine-span equivalence and whole-domain
  validation. Reject zero/variable-dependent scaling, holes and lost rank.
- [x] Run the answer suite and adjacent computational-answer tests.

## Task 2: Geometry families and three-level matrix

**Files:** `backend/app/engine/generators/geometry_practice.py`, related focused
construction modules if needed; `backend/tests/test_geometry_practice.py`.
**Consumes:** Task/Step, DeterministicRNG, existing eigen_geometry helpers and Task 1.
**Produces:** Compatible versioned generators, geometry_seed, mode catalogue,
input_contract, public settings and exact parameter-derived constructions.

- [x] Add failing numerical fixtures and independent geometric invariants.
- [x] Implement vector collinearity, prescribed parallel vector, all unit common
  perpendiculars and constrained vectors (75–77, 85).
- [x] Implement plane/line equations and parameterisations, containing planes,
  perpendicular lines, parallel/perpendicular parameters and three-plane cases
  (80–81, 83–84, 90–91). Parameter-set answers must state the complete criterion.
- [x] Implement line/plane angles, intersections, point/line/plane distances and
  equidistant planes (82, 86–89), retaining valid zero cases.
- [x] Implement orthogonal and directed point/line projections, side of a plane,
  and line/plane reflections (92–96).
- [x] Use direct data at level 1, reconstructed directions/normal at level 2,
  and combined reconstruction/constraints at level 3. Include the exact matrix
  of supported cases in the coverage document; do not count larger numbers.
- [x] Sweep each supported mode and level, validate all expected solutions by
  substitution and preserve every old generator test.

## Task 3: Progressive diagrams and explanations

**Files:** `backend/app/visuals/geometry_practice.py`, existing rendering and
statement-visual dispatch, `backend/tests/test_geometry_practice_visuals.py`.
**Consumes:** Validated parameters and ordered construction steps from Task 2.
**Produces:** Existing geometry3d/plot2d DTOs and rule details at the exact steps.

- [x] Test that feet, normals, images and sought lines/planes are absent from
  statements and appear at the appropriate revealed step.
- [x] Build bounded planes, infinite-line representations, perpendiculars and
  images. Keep earlier relevant constructions and semantic active/previous tones.
- [x] Verify that drawings, named objects, formulas and rule counts match.
- [x] Reuse the current 3D viewer, coordinate axes, 2D projection/fallback and
  resource management; add a correct section only when pedagogically useful.

## Task 4: Existing production flow and five-section navigation

**Files:** engine topics/catalogue, catalogue seeds, practice; API exercise-mode
validation; frontend algebraGroups, shared geometry modes, types/parsers,
TopicPage and PracticePage; their API/selection/reopen tests.
**Consumes:** Modes, versioned generators, contracts and visuals from Tasks 1–3.
**Produces:** All five selectable sections with working modes at levels 1–3.

- [x] Add failing availability, API validation, typed parsing and saved-flow tests.
- [x] Connect every mode to the existing catalogue; guarantee each advertised
  combination can issue and preserve equal random-mode selection.
- [x] Reuse existing vector expression/length/angle modes where appropriate;
  preserve the original vectors section, all other topics and old code lookup.
- [x] Render concise type/level controls and appropriate existing answer inputs.
- [x] Check generation, wrong/correct/equivalent answers, reveal and reopening.

## Task 5: Cyclic role review and final local verification

**Files:** coverage matrix, local audit record and developer preview fixtures;
product files only when a finding requires a fix.

- [x] Run relevant backend/frontend suites, lint, formatting, types and build.
- [x] Check real Linux workers and a temporary local database for saved flows.
- [x] Inspect varied examples in desktop/mobile emulation and both themes;
  check axes, labels, colours, 3D/2D, keyboard/touch, reset and WebGL fallback.
- [x] Review each family as mathematician, first-semester teacher and senior
  UI/UX developer. Record seeds/codes, findings, fixes and repeated verification.
- [x] Fix blocking findings and repeat affected checks until the spec is met.
- [x] Report actual coverage, limitations, local evidence and external review
  still useful. Do not claim publication, independent reviewers or device tests.
