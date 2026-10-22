# ADR-006: interactive visualizations in solutions

Date: 2026-10-22. Status: proposed for accountable human Vlad (whatvlad);
accepted when he approves and merges the pull request that adds it. Issue #111.

Vlad asked on 2026-10-22 for interactive, textbook-style visualizations inside
"Show solution": the area and Riemann sums of single integrals, the region and
surface of double integrals, and the solid of triple integrals. ADR-005 lists
"region and solid plots unless they are cheap static images" as out of scope.
This ADR replaces that one exclusion for the cases below. Everything else in
ADR-005 and ADR-003 still holds, and the specification file stays unchanged.

## Where visuals appear

A visual appears only together with the worked solution: wherever the API returns
solution steps (`reveal-solution`, a reopened problem whose solution was
revealed, the demo and the shared-problem page). It never appears before a
solution reveal and never changes reveal flags, attempts or statistics. The
visual adds to the steps and never replaces them.

## The spec

A response that carries `steps` may also carry `visual`, a declarative spec the
server builds from the replayed exercise. The browser receives no plotting code,
no generator record and nothing that the steps do not already reveal.

```json
{"steps": [...], "visual": {"kind": "definite", "version": 1, ...}}
```

| Kind | For | Fields |
|---|---|---|
| `definite` | `definite-v1` | `f` (in `x`), `a`, `b`, `range` (the closed interval of continuity of `f` that contains `[a, b]`, clipped to a readable window), `y` (window), `value` (the exact value as LaTeX, for the original bounds) |
| `indefinite` | `basic-v1`, `substitution-v1`/`-v2`, `parts-v1`, `rational-v1`, `trigonometric-v1` | `f`, `F` (the solution's antiderivative), `x` and `y` windows, `points` (list of `{x, kind}` with kind `zero`, `extremum`, `inflection`, `pole`) |
| `region2d` | `double-v1` | `system`, `bounds` (innermost first, as in `Setup`), `f` (the integrand in the system's variables, without the Jacobian), `window` |
| `solid3d` | `triple-v1` | `system`, `bounds` (innermost first), `window` |

`version` lets the frontend skip a spec it does not understand. A spec is at most
8 KB of JSON. A record whose spec cannot be built returns no `visual`; this is
declared per template and tested, never decided by catching an exception at
request time.

### Expressions

Expressions are JSON trees built from trusted SymPy objects on the server:

- a number: a JSON number (plotting needs floats, not exact values);
- a name: `"x"`, `"y"`, `"z"`, `"r"`, `"theta"`, `"pi"`, `"e"`;
- an operation: `["add", ...]`, `["mul", ...]`, `["pow", base, exponent]`,
  `["exp", u]`, `["log", u]`, `["sin", u]`, `["cos", u]`, `["tan", u]`,
  `["abs", u]`, `["sqrt", u]`.

These are all the heads that today's catalogue uses, plus `tan` and `sqrt`. A
template that needs another head adds it to the server builder and the client
evaluator in the same pull request, with tests; that needs no new ADR. The
browser evaluates the tree with a small evaluator of its own. It never uses
`eval`, `Function` or a computer-algebra library, and the Content Security Policy
does not change. An evaluation that gives a non-finite number leaves a gap in the
curve, not an error.

## What each kind shows

- **Definite.** The graph of `y = f(x)`, the signed area over `[a, b]` shaded
  (positive and negative parts in two colours), two sliders for the bounds,
  limited to `range`, and a Riemann sum with a partition slider (1 to 100,
  midpoint rule, with left and right as an option). At the original bounds the
  label shows the exact value; at other bounds it shows a numerical value
  (Simpson's rule) marked as approximate.
- **Indefinite.** `f` and `F` on the same axes, a slider for the constant `C`
  that moves `F`, and the marked points: zeros of `f` (extrema of `F`), sign
  changes of `f′` (inflection points of `F`) and poles with their vertical
  asymptotes. SymPy computes the points on the server inside the window; the
  browser does not search for them.
- **Region2d.** The region in the xy-plane, drawn from the bounds: for an outer
  variable `u ∈ [a, b]` and an inner `v ∈ [g(u), h(u)]`, the area between the two
  curves, with polar `(r, θ)` mapped to `(x, y)`. A second view shows the surface
  `z = f(x, y)` meshed over the same parameter grid, so it stops exactly at the
  region's edge. Iterated integrals show the region only; there are no moving
  cross-sections.
- **Solid3d.** The solid from its bounds: for `z ∈ [g, h]` over a planar region,
  the bottom and top surfaces over the region mesh and the side walls along the
  region's boundary, in Cartesian and cylindrical coordinates. The integrand
  (a scalar field) is not shown.

Derivatives (`derivatives-v1`, `partial-v1`) get no visual in this ADR. A graph of
`f` and `f′` with a tangent line is a later candidate with its own Issue.

## Rendering

- 2D (`definite`, `indefinite`, the region of `region2d`): a component of our own
  that draws SVG with the design-system tokens, light and dark. The needs are
  small (curves, shading, rectangles, points, sliders), so a plotting library
  would add more weight than value.
- 3D (the surface of `region2d`, `solid3d`): three.js with OrbitControls, in a
  chunk loaded by dynamic import only when such a solution opens. The main
  bundle may grow by a few KB at most.
- Rejected: Plotly (about 1 MB, and its WebGL traces need `unsafe-eval`), Desmos
  (an external script and an API key, against the CSP) and JSXGraph (good, but
  more than the 2D needs).

## Fallback, mobile and accessibility

- A missing or unknown spec, an evaluator error or a render error hides the
  visual behind an error boundary; the steps show as before. Without WebGL the
  3D view is left out and the 2D region view stays.
- Touch: drag sliders, pinch to zoom, one-finger rotate in 3D. The 3D canvas
  captures touch only inside itself, is at most about 60 % of the viewport
  height, and the page still scrolls outside it.
- Every visual has a text alternative (the region as inequalities, the bounds,
  the value), and every slider is a labelled range input that works from the
  keyboard.

## Testing

- Backend: every catalogue record of a supported version builds a valid spec or
  is declared as having none; expressions round-trip numerically against SymPy
  at sample points.
- Frontend: evaluator unit tests (every head, gaps for non-finite values, no
  unknown heads), a component test that a broken spec hides only the visual,
  and slider limits.
- Live: Vlad checks each stage on a phone and a desktop on the deployed preview.

## Delivery

| Issue | Delivers | Depends on |
|---|---|---|
| #112 | Spec, evaluator and 2D component; `definite` and `indefinite` | this ADR |
| #113 | `region2d`: region view and lazy three.js surface | #112 |
| #114 | `solid3d` | #113 |

## Out of scope

Visuals outside the solution, derivatives, scalar-field views of triple
integrals, spherical coordinates, cross-section sliders, printed visuals in
worksheets (ADR-007 may reuse the spec later) and any change to the steps, the
answer check or the reveal rules.
