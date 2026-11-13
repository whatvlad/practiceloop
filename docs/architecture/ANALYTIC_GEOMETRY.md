# Analytic geometry practice

Local extension approved on 2026-11-13. Base commit:
`78b8ef0c5650fffab9420d7b2ceec54cf9bfbfde`. Implementation follows the
[approved scope](../superpowers/specs/2026-11-12-remaining-analytic-geometry-design.md)
and the personal MathLoop task standard. This document describes the local
implementation, not a deployed release.

## Scope and reference

The reference is the owner's `1-algebra30.pdf`, pages 10–13, exercises 72–96.
The PDF is not bundled with the application. The coverage below describes
bounded generated exercise types inspired by the collection; it does not claim
every original letter, number, degeneracy or possible configuration.

Five navigation sections are active, in addition to the existing Vectors,
areas and volumes section. They reuse the canonical topics `vectors` and
`lines-and-planes`; no topic database rows or duplicate version ownership were
added. There are 35 new modes, each at levels 1–3: 105 supported combinations.
The type and difficulty selectors are independent.

### Exact three-level matrix

The following repeated descriptions are literal data formats, not merely
larger numbers:

- **Line L1/L2/L3:** a parametric line / two distinct points / intersection of
  two independent planes, with direction and a base point reconstructed.
- **Plane P1/P2/P3:** an equation / a point and two independent spanning
  directions / a midpoint P and points C,D, with two directions and a normal
  reconstructed. Angle exercises use the separate data formats in their rows.
- Every mode uses bounded small coordinates and exact arithmetic. More levels
  add reconstruction or a different constraint structure; they do not raise
  the sampling range.

| Mode | Level 1 | Level 2 | Level 3 | Reference |
|---|---|---|---|---|
| `point-collinearity` | P,Q,R given | R reconstructed as a midpoint | P and R reconstructed as midpoints | 75 |
| `parallel-vector` | v and prescribed scalar product | v from two endpoints | v from a combination of two displacements | 77 |
| `unit-perpendiculars` | two independent coordinate-axis vectors | one vector reconstructed, one given | both vectors reconstructed from three points | 76 |
| `constrained-vector` | a,b, endpoint plane and volume | reconstruct a from two endpoints | reconstruct a as a linear combination, then combine all constraints | 85 |
| `plane-equation` | P and normal | P and two directions | midpoint P and two further points | 80 |
| `plane-parameterisation` | P and two directions | equation to a point and independent basis | midpoint P and two further points | 80 |
| `line-equation` | P and direction | two points | midpoint P, direction parallel to the intersection of two planes | 81,83 |
| `containing-plane` | line and point outside it | two distinct parallel lines | two intersecting lines, each as two plane equations | 80,84 |
| `perpendicular-line` | through P, perpendicular to two vectors | recover two directions from lines | through P, perpendicular to u and meeting a given line | 81,84 |
| `parallel-parameter` | given direction, unknown plane coefficient | direction from endpoints | direction from a linear combination | 90 |
| `normal-parameters` | plane equation and parametric line | parametric plane with a parameter | plane from points with a parameter | 90 |
| `planes-common-point` | three equations | first two planes from point/normal data | additionally reconstruct their point | 91 |
| `planes-common-line` | three equations | first two planes from point/normal data | additionally reconstruct their point | 91 |
| `planes-three-lines` | three equations | first two planes from point/normal data | additionally reconstruct their point | 91 |
| `line-angle` | L1 for both lines | L2 for both lines | directions from normals of four defining planes | 88 |
| `plane-angle` | normals from equations | normals from spanning directions | normals from triples of points | 89 |
| `point-line-distance` | L1 and point S | L2 and S | L3 and midpoint S | 86 |
| `point-plane-distance` | P1 and S | P2 and S | P3 and S | 86 |
| `parallel-line-distance` | L1 and a parallel line | L2 and a parallel line | L3 and a parallel line | 86 |
| `skew-line-distance` | two nonparallel L1 lines | two L2 lines | two L3 lines, common perpendicular from a linear system | 86 |
| `parallel-plane-distance` | two equations | rescale proportional normals first | P3 and a parallel plane through S | 86 |
| `line-line-intersection` | two L1 lines | two L2 lines | two L3 lines | 82 |
| `line-plane-intersection` | L1 and P1 | L2 and P2 | L3 and P3 | 82 |
| `equidistant-plane` | P1 and S | P2 and S | P3 and S | 87 |
| `point-line-projection` | L1 and S | L2 and S | L3 and midpoint S | 92 |
| `point-plane-projection` | P1 and S | P2 and S | P3 and S | 92 |
| `line-plane-projection` | L1 and P1 | L2 and P2 | L3 and P3 | 92 |
| `directed-point-line-projection` | L1, S and projection direction | L2, S and direction | L3, S and direction | 93 |
| `directed-point-plane-projection` | P1, S and direction | P2, S and direction | P3, S and direction | 93 |
| `directed-line-plane-projection` | L1, P1 and direction | L2, P2 and direction | L3, P3 and direction | 93 |
| `same-side` | P1 and two points | P2 and two points | P3 and two points | 94 |
| `line-reflection` | L1 and S | L2 and S | L3 and midpoint S | 95 |
| `plane-reflection` | P1 and S | P2 and S | P3 and S | 96 |
| `line-position` | two L1 lines | two L2 lines | two L3 lines | 82,84 |
| `line-plane-position` | L1 and P1 | L2 and P2 | L3 and P3 | 82,90 |

Existing vector/scalar expressions, vector lengths and triangle angles are
reused in the new sections. Existing area and volume families, original links,
levels 4–5 and permanent codes remain compatible.

### Deliberate bounds

- Angles between lines and planes currently sample 0°, 45° and 90°. Their
  answer is the angle in degrees, not just its cosine. This is a bounded angle
  family, not arbitrary inverse-trigonometric angle coverage.
- Ordinary intersection tasks have one intersection point. Separate position
  tasks classify intersecting, distinct parallel, skew and coincident lines;
  line/plane cases distinguish one point, no point and the whole line.
- Distance tasks include zero distances. The nonparallel-line distance mode
  includes both skew and intersecting lines; its UI does not promise strictly
  skew input. Side-of-plane tasks include a point on the plane.
- Directed point-to-line examples are constructed to have a unique image.
  Directions parallel to a target plane and whole lines projecting to a point
  are excluded from modes whose contract asks for a projected line.
- Common-point means **at least one** common point. The three-plane family asks
  for A,B in the explicitly given complete criteria `a != A or b = B`,
  `a = A and b = B`, or `a = A and b != B`. This is scaffolded parameter-set
  practice; it is not an arbitrary condition-expression checker. Representative
  diagrams explicitly state their chosen parameter pair.
- The endpoint-plane constant in constrained-vector tasks is generated so an
  explicit perpendicular particular solution exists; the absolute volume
  condition then produces two answers. This is not every possible system of
  vector constraints.
- Deliberately invalid expressions from 72(d,j), proofs/counterexamples in 97,
  arbitrary conics and interactive diagrams in exported worksheet PDFs are
  outside this approved stage. No proof is replaced with a classification quiz.

## Engine and answer contracts

The extension uses the existing registry, deterministic seed, private prepared
catalogue, bounded worker, practice API and authorised reveal flow. It does not
add a separate client generator or symbolic runtime in the browser.

`GeometryPractice` versions are `geometry-practice-<mode>-v1`. The append-only
mode order assigns permanent JAA… code prefixes. Changing a published drawing,
answer or mathematical task requires a new compatible version; never reorder
the list to recycle prefixes. Seeds encode the level using the existing
`(level - 1) * 10**12 + variation` convention.

Plane answers accept nonzero constant multiples of the affine left-hand side.
Line and plane parameterisations accept shifted base points and equivalent
nonzero directions/independent bases. Only affine parameterisations over the
declared full real parameter domain are accepted; zero directions, lost rank,
nonlinear formulae and cancelled domain holes fail. Vector-pair answers require
both members and accept either order, including equivalent radical coordinates.
These use the existing formula/tuple grammar, not string equality.
Write the simplified affine form: nonlinear intermediate operations are outside
this bounded grammar even when a more general simplifier could cancel them.

The public JSON contains IDs, labels, canonical topic and section membership.
It contains no seeds, expected values, constructions or checker internals.
The request path reads rendered pools and input metadata without rebuilding a
symbolic task. Public lookup of a new geometry code already in the pool also
uses its verified record, without competing for a worker slot. An arbitrary
code outside the pool is still rebuilt in the existing bounded worker.
Lines-and-planes levels 1–3 have 80 records; vectors retain 64.
Each new type has at least two examples. Extra angle, position, side and
zero-distance cases are reserved. Practice chooses a type before an example
among available candidates, so larger boundary-case pools do not increase that
type's probability. Tiny custom test pools need not contain every type.

## Drawings and resources

The same exact construction data drives mathematical steps and progressive
geometry DTOs. Statements show only givens. A foot, reflected point or solved
parameter-dependent plane appears at its corresponding revealed action.
Active formulae and constructions share the site's theme colour. Names,
dashed connectors, arrows and the written explanation provide non-colour cues.

Later drawings may omit finished auxiliary objects to preserve readability;
the initial drawing and earlier steps retain the derivation. Bounded plane
patches and segments represent infinite objects. Normal arrows are scaled and
labelled as such. Coordinate axes are present. The 2D button is an orthographic
projection, not a promise of true angles or lengths; the existing altitude
section is separately identified when applicable.

The visible line and plane extents include incident named points and vector
endpoints. Test both incidence and containment in the drawn fragment: a correct
intersection formula still gives a misleading diagram if its point lies beyond
that fragment. Extents are calculated in the object's own line/plane basis.

Reuse the existing lazy Three.js viewer, keyboard/touch controls, reset,
viewport lifecycle, context disposal and fallback. Scenes remain within the
existing limits: 16 points, 32 lines, 8 triangles and 8192 encoded bytes.
Ordinary labels are shown once, kept inside the 2D viewport and placed near
free positions to reduce overlap. No new graphics dependency was introduced.

## Repeatable completion cycle

Goal: every advertised type/level must have a complete correct solution,
equivalent-answer checking and a readable drawing in the existing site.

1. Add a numerical fixture and an independent invariant for the proposed case;
   observe the relevant failure, then extend the existing provider/grammar.
2. As mathematician, check domains, incidence, dimensions, all solution branches
   and substitutions independently of the expected-answer expression.
3. As first-semester teacher, follow every substantial transformation, define
   each symbol, expose the rule and make the increase in difficulty structural.
4. As UI/UX reviewer, inspect real cards on wide/narrow screens, both themes,
   axes, label overlap, active colours, controls and scene lifecycle.
5. Exercise generate → wrong/equivalent correct answer → reveal → reopen;
   verify privacy before reveal, prepared-pool availability and old codes.
6. Record a reproducible mode/level/seed, fix blocking findings and repeat the
   affected checks. Stop only when the agreed matrix is supported and the
   relevant checks pass; do not call a bounded sample universally perfect.

Ordinary seed sweeps stay within the repository's 50-seed cap. Local worker
checks run in Linux; persistence uses disposable PostgreSQL and a synthetic
identity. No production data, push, CI run or deployment is part of this cycle.
Report unrelated baseline failures separately, and ask before every future
push. Evidence and external-review limits are recorded in
[the local role audit](../LOCAL_GEOMETRY_REVIEW.md).
