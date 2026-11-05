# Elementary functions and logic (#235)

This delivery adds 81 immutable `elementary-*-v1` providers, with explicitly
allocated `EFAA` through `EFDC` prefixes. The 239 previously shipped versions,
their permanent codes and all existing golden entries remain unchanged.
There are now 320 registered versions and 49 served topics. This is the
computational subset of AM1 1-23, plus the domain components of four exam
questions; learner proof/sketch tasks remain #244.

The [source index](analysis_pdf_source_index.json) is authoritative: 102 source
references/components link to concrete verified versions under 20 family
contracts. It retains all 830 original IDs, original PDF identities, duplicate
labels and unresolved components belonging to other delivery issues. A mixed
exam question is still partial when its derivative/asymptote component is pending.
No original PDF, extracted sheet text, source figure or fixed source-answer bank
is an application asset. Generated parameters and method families supply fresh
variants, worked solutions and reference visuals.

## Mathematical families and source routes

Names below omit the common `elementary-` prefix and `-v1` suffix. The index
records exact per-letter mappings; this table summarizes methods rather than
claiming coverage from a topic's name.

| Source | Generated computation and principal versions |
|---|---|
| 1 | Definite arithmetic/geometric propositions versus open sentences: `proposition`, `proposition-triangle` |
| 2 | Full equivalent negations: `logic-negation-not/and/or/implication/equivalence/xor`; equivalence includes three atoms and a conjunction |
| 3 | Compound truth from computed arithmetic atoms, a quadratic monotonicity counterexample, periodicity and polynomial parity: `compound-truth` |
| 4 | Explicit real-domain witnesses/counterexamples, quantifier order, cubic witnesses, total order and periodic phases: `quantifier-*` |
| 5 | Rational poles, radical over a positive quadratic, quartic radicand and radical quotient: `domain-rational/root-rational/quartic-root/root-quotient` |
| 6 | Even/odd/neither, checking natural-domain symmetry before algebra: `parity` |
| 8 | All four ordered compositions, each with its own complete domain: `composition-affine/reciprocal-square/root-power/abs-root` |
| 10 | Repeated roots, biquadratic substitution, common rational poles and cubic denominator exclusions: `equation-*` |
| 11 | Squared factors with isolated solutions, odd polynomial sign charts and rational inequalities: `inequality-*` |
| 13 | Mobius, restricted semicircle/quadratic/fourth-power, exponential and logarithmic inverses, each including domain/range: `inverse-*` |
| 14 | Equal-base, quadratic substitution, trig exponents, decreasing-base rational exponents, mixed products and rational exponential expressions |
| 15 | Product/quotient laws, rational powers, change of base and ratios of logarithmic differences: `log-value-*` |
| 16 | Power/difference/quadratic log equations and increasing/decreasing/opposite-base inequalities, with original argument domains |
| 17 | Different-base equations, product inequalities and reciprocal-exponential substitution |
| 18 | Complete identity domains before cancellation: tangent ratio/sum, half angles and everywhere-defined double-angle identities: `trig-domain-*` |
| 19 | Exact cosine linearizations of squared/fourth powers: `trig-linearization-*` |
| 20 | Exact principal inverse-trig values, arithmetic combinations and arccot conventions: `inverse-trig-values/atan-cot` |
| 21 | Nested principal functions and nonstandard radian branch reduction: `inverse-trig-nested/cot-branch` |
| 22 | Affine/squared inverse-sine/cosine domains, rational arctangent and total affine arccot domains |
| 23 | Complete sine-sum, mixed-frequency cosine and tangent equations; shifted sine, sine-plus-cosine and cotangent inequalities |
| First test B2 | `domain-exponential-root`; derivative component remains #237 |
| First test D1 | `domain-arcsin-square`, including disconnected domains; derivative remains #237 |
| Resit A2/C1 | `domain-quadratic-rational`, preserving cancelled poles; asymptotes remain #236 and learner sketch remains #244 where requested |

AM1 7, 9 and 12 remain wholly deferred learner proof/sketch tasks. Computed
parity, identity domains and other mixed results do not grade the associated
learner proof. Every computational variant still has its own worked reference
derivation. Additional domain/quantifier variants extend these bounded methods;
they do not assert an unrestricted natural-language or theorem-proving service.

## Parameter bounds and exact answer policies

The frozen draw uses integers `a,b,c` in 1-4 and a structural variant in 0-5,
with the existing deterministic PRNG and seed range. A provider's difficulty
identifies a method: roots/domain restrictions, complete sign charts, branch
inversion, nested compositions, mixed frequencies or quantifier order. Topics
offer only appropriate levels; no five-level padding by coefficient size.

All calculations are real and exact. Roots/logarithms/principal angles remain
symbolic, not rounded decimals. Log/exponential bases used in new variants are
explicit and positive, unequal to one. Decreasing-base inequalities reverse
their direction. Original denominators and log/root arguments are checked
before cancellation. Repeated roots collapse as set elements, never as lost
solutions; zeros, poles and strict/nonstrict endpoints have separate roles.

- `RealSetAnswer` checks the complete interval/point union by exact set equality.
- `OrderedAnswer` requires every displayed slot. Compositions use eight slots
  (FF expression/domain, FG, GF, GG); inverses use formula/domain/range.
- `DomainFormulaAnswer` proves univariate identity on the explicitly stated
  private domain and checks every intermediate expression there. A hole outside
  that domain is harmless; an additional hole inside it is invalid. Unknown
  symbolic equivalence remains inconclusive rather than sampled acceptance.
  For a constant candidate, an exact nonzero derivative certificate inside the
  trusted target's domain proves nonidentity without constructing an enormous
  inverse root. Empty/finite domains and flat restricted branches retain the
  complete domain equality policy; an undecided certificate falls through.
- `FourierAnswer` additionally requires a linear cosine representation with
  the declared harmonics. Re-entering the original trigonometric power does
  not satisfy a linearization question merely because it is equivalent.
- `LogicAnswer` compares every row of the full truth table over at most three
  declared atoms. Formula syntax is `! & | ^ -> <->`, constants 0/1 and
  parentheses; precedence descends in that order except that `|` and `^` share
  a level. Implication associates to the right; other binary operations to the
  left. Quantifier questions use exact named truth categories, with global
  mathematical witnesses/counterexamples in their reference solutions.
- Periodic answers use the explicitly requested period and canonical half-open
  base cell. They retain excluded poles and endpoint closure. For
  `cos(4u)=sin(u/2)`, the full result is a union of two canonical root lattices,
  ordered by their declared periods; each branch has an independent integer
  index. Both lattices must pass. The zero-product factorization proves their
  completeness, without enumerating a larger common-period answer beyond the
  existing container budget.

Arccot has range `(0,pi)`. Principal arcsin/arccos/arctan ranges are stated in
the worked methods. Restricted inverse branches are part of the question, not
chosen by a learner. Positive-domain power predicates are explicitly stated;
there is no ambiguous unrestricted real `x^x` predicate.

## Grammar and privacy

The [shared contracts](COMPUTATIONAL_ANSWERS.md) retain the same aggregate
256-byte / 128-token / 96-node / depth-12 / 16-function budgets. Each exponent
part remains bounded by 12; for example a sixteenth power can be entered as
`(x^4)^4`. Formula contracts alone opt into positive numeric literal bases
(including a ratio of two literals) with a symbolic exponent. The historical
parser still only allows variable exponents on `e`; no old variable allowlist
or grammar is broadened. A computed power tower is never evaluated to decide
whether it qualifies as a positive literal base.

Public `answerInput` contains only grammar, allowed atoms/symbols, labels and
choices. It contains no truth-table mask, expected value, domain solution,
sampled parameter record, derivation or figure. Helpers use the same plain
frozen draw without building a symbolic task during normal issuance/projection.
The browser validates syntax and renders previews; correctness remains on the
server. CPU/memory/wall/admission/output limits remain unchanged.

## Reference diagrams and replay

Private number lines show exact complete solution/domain sets, open/closed
endpoints and infinite rays in a labelled plotting window. Periodic diagrams
show the canonical base cell, with the full integer-translate meaning in the
question and solution. Four-composition domains have separate labelled rows.

Inverse questions have parameter-derived function curves and their reflections
across `y=x`, including the chosen branch and finite included endpoints. The
inverse points are reflections of the same sampled curve points, not an
unrelated regeneration. Mobius branches never connect across a pole; displayed
unmarked/arrow ends indicate continuation. This is explanatory reference
geometry, not learner sketch/graph grading.

Pure logic, arithmetic values, parity identities and trigonometric algebra
need no geometric target: their exact truth tables/identities are the reference
explanation. An empty set has no invented geometry. These are explicit
not-applicable visual policies. Other diagrams are validated before catalogue
publication and remain private until authorized solution reveal. Generation,
history/reopen, permanent codes, owner copies/shares and worksheets reuse the
identical version/code. A four-row append-only topic-seed migration enables
saved problems for the new views; it changes no schema, RLS, grants or old IDs.

## Verification and limits

`test_engine_elementary.py` checks canonical targets, shared aggregate budgets,
deterministic replay and 1,000 seeds per provider. Sixteen hand-worked fresh
parameter examples include full sets, all four compositions, branch inversion,
log domains, three-atom negation and the two-lattice periodic union. Golden
fixtures append three samples per new version and preserve every old entry.

Independent tests use exact complete polynomial/rational/log-transformed
solvers, continuity domains, whole function ranges and inverse compositions,
original inner/outer composition constraints, complete angle sets/sign charts,
exact trig identities and principal-branch certificates. Numerical samples
never prove equality. Equivalent atan/asin boundary forms are reconciled by an
exact tangent identity plus their principal ranges. Trig sign charts cover
the entire declared cell rather than trusting a solver's single subperiod.

API tests cover saved issuance, history/reopen, attempts, reveal, another
owner's 404 and independent copy, safe shares, immutable private visuals and
worksheet drawing. Separate actual Linux children check each provider's right
and wrong target under the original limits. Public-projection profiling rejects
request-time SymPy/build/visual regeneration. Browser tests share the bounded
logic corpus; KaTeX tests render every new golden statement, answer and step.
Hosted Database isolation remains the real SQL ownership/RLS check; in-memory
HTTP fixtures alone are not described as database isolation proof.

This is bounded computational coverage, not arbitrary symbolic solving,
natural-language proof assessment, learner graph interaction, generic ODE or
region equivalence, or worksheet redesign. Those remain their separate issues.
