# ADR-005: multiple integrals and derivatives

Date: 2026-10-21. Status: proposed for accountable human Vlad (whatvlad);
accepted when he approves and merges the pull request that adds it. Issue #95.

Feijhoaaaaa asked on 2026-10-21 to add double and triple integrals, solved in
Cartesian, polar and cylindrical coordinates, and to do the same for
derivatives. The [original MVP](../PRACTICELOOP_MVP.md) recommends one category,
Calculus → Integration. This ADR widens it to two areas of calculus. It is the
dated scope amendment: the specification file itself stays byte-for-byte
unchanged because `scripts/check_repository.py` verifies its hash. Everything
else in the specification still holds: rule-based generation verified by SymPy
and never by an LLM, symbolic equivalence, history and reveals, and the
exclusions in its section 17. This is one subject, mathematics, so "multiple
school subjects" stays excluded.

ADR-003 still governs everything this ADR does not change. In particular the
level meaning (1 direct, 2 one preparation, 3 one primary method, 4 method plus
preparation, 5 two compatible techniques), pedagogically clean values, the
availability rule for cells, the parser limits and the bounded worker.

## Areas and topics

Practice has two areas. A topic belongs to exactly one area, and mixed practice
draws only within the chosen area.

| Area | Topic slug | Generator version | Answer |
|---|---|---|---|
| Integrals | the five existing topics | unchanged | unchanged |
| Integrals | `double-integrals` | `double-v1` | exact value |
| Integrals | `triple-integrals` | `triple-v1` | exact value |
| Derivatives | `derivatives` | `derivatives-v1` | expression in `x` |
| Derivatives | `partial-derivatives` | `partial-v1` | expression in the declared variables |

New topics are seeded by an additive migration. Existing problems, attempts and
statistics keep their meaning.

## Coordinate systems

- Cartesian: `x`, `y` (and `z`), with `dA = dx dy`, `dV = dx dy dz`.
- Polar: `x = r cos θ`, `y = r sin θ`, `r ≥ 0`, `dA = r dr dθ`.
- Cylindrical: polar in the plane plus `z`, `dV = r dz dr dθ`.

At levels 1–3 the statement names the coordinate system. At levels 4–5 the
learner chooses. The worked solution always shows the system it uses: the region
or solid, the bounds, the Jacobian factor `r` where it applies, and every
iterated integration as its own step. Where the region is reasonable in both
systems, the solution also shows the other set-up and its value as a check.
Spherical coordinates are not offered.

## Level matrices

Each cell lists the templates its first version must include. Values are exact
and clean (small integers, simple fractions, multiples of `π`, `e − 1`), and
every value below was computed with SymPy for this ADR.

### Double integrals (`double-v1`)

| Level | Content | Example → value |
|---|---|---|
| 1 | Cartesian rectangle, separable product integrand | `∬ 3xy dA`, `[0,2]×[0,1]` → `3` |
| 2 | Cartesian rectangle, inner result depends on the outer variable | `∫₀¹∫₀² (x + y) dy dx` → `3` |
| 3 | One stated method: Cartesian iterated integral with a variable bound, or polar over a disk, annulus or sector | `∫₀¹∫₀ˣ y dy dx` → `1/6`; `∬ 2(x² + y²) dA`, `x² + y² ≤ 4`, polar → `16π` |
| 4 | Method plus preparation: bounds from a set description, or reverse the order of integration | `∫₀¹∫ᵧ¹ e^(x²) dx dy` → `(e − 1)/2`; `∬ y dA` over the upper half-disk of radius 2 → `16/3` |
| 5 | Two compatible techniques: a Cartesian integral that is only clean in polar, plus an inner substitution | `∫₋₁¹∫₀^√(1−x²) e^(x²+y²) dy dx` → `π(e − 1)/2` |

### Triple integrals (`triple-v1`)

| Level | Content | Example → value |
|---|---|---|
| 1 | Cartesian box, separable product integrand | `∭ xyz dV`, `[0,1]×[0,2]×[0,1]` → `1/2` |
| 2 | Cartesian box, inner results depend on the outer variables | `∭ (x + yz) dV`, `[0,1]×[0,1]×[0,2]` → `2` |
| 3 | One stated method: Cartesian iterated integral over a simplex, or cylindrical over a cylinder | `∫₀¹∫₀^(1−x)∫₀^(1−x−y) dz dy dx` → `1/6`; `∭ (x² + y²) dV`, `x² + y² ≤ 1`, `0 ≤ z ≤ 3` → `3π/2` |
| 4 | Method plus preparation: bounds from a described solid (tetrahedron under a plane, inside a cone, under a paraboloid) | volume between `z = √(x² + y²)` and `z = 2` → `8π/3`; under `z = 4 − x² − y²`, above `z = 0` → `8π` |
| 5 | Two compatible techniques: a Cartesian integral to convert to cylindrical, plus an inner substitution | `∫₀¹∫₀^√(1−x²)∫₀² z e^(x²+y²) dz dy dx` → `π(e − 1)/2` |

### Derivatives (`derivatives-v1`)

The learner enters `f'(x)`. There is no arbitrary constant: an answer that adds
one is incorrect.

| Level | Content | Example |
|---|---|---|
| 1 | One standard term: power, `e^x`, `sin`, `cos`, `ln` | `d/dx (3x⁴)` |
| 2 | One preparation: sums and constant multiples, roots and negative powers rewritten as powers, a linear inner argument | `d/dx (2√x − 3/x)`, `d/dx sin(3x)` |
| 3 | One rule: chain rule with a nonlinear inner function, product rule or quotient rule | `d/dx e^(x²)`, `d/dx x sin x` |
| 4 | One rule plus a simplifying rewrite, such as log laws before differentiating | `d/dx ln(x²(x + 1))` on `x > 0` |
| 5 | Two compatible rules: product or quotient with a chain-rule factor | `d/dx x² e^(3x)` → `(3x² + 2x) e^(3x)`; `d/dx sin(x²)/x` |

### Partial derivatives and coordinate changes (`partial-v1`)

| Level | Content | Example |
|---|---|---|
| 1 | First partial of a polynomial in `x, y` | `∂/∂x (x³y + 2y²)` |
| 2 | First partial needing one single-variable rule | `∂/∂y e^(xy)`, `∂/∂x x ln y` on `y > 0` |
| 3 | Second or mixed partials, or first partials of `f(x, y, z)` | `∂²/∂x∂y x² e^(xy)` → `x²(xy + 3) e^(xy)` |
| 4 | Chain rule after changing to polar or cylindrical coordinates; answer in `r`, `θ` (and `z`) | `f = xy`, find `∂f/∂θ` → `r² cos 2θ` |
| 5 | Jacobian determinant of a scaled polar or cylindrical map | `x = 2r cos θ`, `y = 3r sin θ`: `∂(x, y)/∂(r, θ)` → `6r` |

Level 5 ties the topic to the `r` factor learners use in multiple integrals.

Considered and left for a later decision: the slope `dy/dx` of a polar curve
`r = f(θ)` at a given angle, which some courses call "derivatives in polar
coordinates". It fits as a second level 4 template if the owners want it.

## Answers and variables

- A multiple-integral answer is a constant expression: numbers, `pi`, `e`,
  functions of numbers. It uses no variable, so these topics need no parser
  change. The learner never enters the integral set-up; the solution shows it.
- A derivative answer uses only the variables its template declares, each with
  a real domain: `x`, `y`, `z` real unless the template restricts them; `r > 0`;
  `theta` real. `theta` and `θ` read the same, as `pi` and `π` do. Any other
  symbol is `invalid`. A template that asks for an answer in `r, θ` does not
  accept the same function written in `x, y`.
- Explicit `*` always works between variables. Implicit products such as `2xy`,
  `r theta` and `x y` follow one tokenizer rule, which Issue #96 fixes with
  corpus cases on both backend and frontend before any template uses it.
  The rule (longest name from the left) is in
  [MATH_INPUT.md](../architecture/MATH_INPUT.md#declared-answer-variables-adr-005-issue-96).
- Equivalence follows ADR-003: symbolic proof over the declared domain is
  authoritative, bounded samples from that domain can only find a
  counterexample, and an undecided check is `503 math_check_inconclusive`.
- For indefinite integrals ADR-003 lets any one-letter symbol other than `x`
  name the constant. That stays true for integration topics: the new variable
  names are declared only by derivative templates.

## Mistakes

Each template declares its common mistakes and they are diagnosed only on an
unambiguous match, as in `generators/mistakes.py`. The first versions declare at
least: a missing `r` factor (polar and cylindrical integrals), swapped or
unreversed bounds (order reversal), a missing inner derivative (chain rule), a
quotient-rule sign error, differentiating a variable that should be held
constant, and a dropped chain-rule term after a coordinate change.

## Check budget

The 2-second CPU limit and the other worker limits do not change. The canonical
answer and each declared alternative form of every new template must check in
at most 1 second of CPU in CI, half the limit, measured by a corpus test like
`test_family_check_fits_the_worker_limits`. A template that cannot meet this is
redesigned or not offered; the limit is not raised. Multiple-integral values are
compared as exact constants, which is much cheaper than today's antiderivative
checks.

## Delivery

| Issue | Delivers | Depends on |
|---|---|---|
| #97 | `derivatives-v1` generator | this ADR |
| #98 | Areas in the API, migration and dashboard; derivatives live | #97 |
| #99 | `double-v1`, live | this ADR, #98 |
| #100 | `triple-v1`, live | #99 |
| #96 | Variables `y`, `z`, `r`, `theta` in the parser and editor | this ADR |
| #101 | `partial-v1`, live | #96, #98 |

The order on the Implementation Queue decides which comes first.

## Out of scope

Spherical coordinates; line, surface and flux integrals; improper multiple
integrals; gradients, directional derivatives, implicit differentiation,
optimization and Hessians; learner-entered integral set-ups; region and solid
plots unless they are cheap static images; any change to the existing five
integration topics.

## Amendment: practice areas (#144, 2026-10-26)

The product owner approved Algebra and Mathematical Analysis as the top-level
areas, with English content and an Area -> Topic -> Template hierarchy.
All shipped integral and derivative topics move to `mathematical-analysis`;
their existing slugs and generator records keep their meaning. `algebra` is a
recognized area, hidden until #147 ships a verified topic. No empty practice
choice is offered. The existing topic rows retain their IDs.

Mixed Mathematical Analysis uses the existing fixed topic weights across the
combined pool. The old `integrals` and `derivatives` request selectors remain
accepted for in-flight requests and old worksheet groups, with their former
pool boundaries. They are not advertised as areas in the new catalogue.

The next curriculum releases are Algebra (#147), Analysis I (#145), then
Analysis II (#146). The original specification remains unchanged; this amendment
records the approved direction rather than enabling unverified new cells.

## Consequences

The product now spans two areas. Topics need an area, and mixed practice and
statistics are grouped by it. The parser gains a per-template variable
allowlist, so templates become the trusted source of which symbols an answer may
use. Multiple integrals reuse the definite-integral checking path because their
answers are constants. Each new family needs invariant, domain, rejection,
equivalence, mistake and check-budget tests before it is advertised, as ADR-003
requires.
