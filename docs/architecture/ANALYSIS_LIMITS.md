# Analysis I sequences, limits and continuity (#236)

This implementation checkpoint extends Functions and sequences and Limits and
continuity with 61 independent generator versions. The two topic slugs, mixed
practice weights, prior versions and permanent codes are preserved. The generator
registry declares each prefix explicitly. The catalogue fixture retains every
entry from the base commit, including the prior curriculum expansions.

[The source index](analysis_pdf_source_index.json) records 62 matched
computational references, the additional generated variants and the remaining
references that need separate coverage. Learner proof and sketch components
remain routed to #244. This checkpoint leaves #236 in progress.

## Parameters and levels

Each version draws three independent integers in [1,5] from the existing
deterministic generator. Sequences use positive integer indices. The scaled
conjugate starts at 3 so its radicand is positive throughout the stated domain.
Exponential bases exceed 1. At finite approach points, the worked steps retain
the punctured domain and indicated side. Piecewise branches specify endpoint
membership in the question and the reference plot. The cubic bracket uses exact
rationals for every sign and narrows to zero width for an exact midpoint root.
The exponential root bracket uses rational Taylor enclosures.

| Topic | Level | Computational methods introduced at this stage |
|---|---|---|
| Functions and sequences | 1 | One-sided boundedness and sharp bound from a monotone radical |
| | 2 | Trigonometric and conjugate bounds, elementary epsilon and threshold calculations, lower-degree rational limits |
| | 3 | Shifted radical tails, leading coefficients, finite sums, bounded and divergent oscillation, dominant exponentials |
| | 4 | Factorial ratios and tails, conjugation, competing bases, floors, bounded nth roots, exponential limits |
| | 5 | Growing sums, exponential nth-root ratios, logarithmic scales, differences of nearby powers |
| Limits and continuity | 1 | Sequential continuity and one-sided infinite limits |
| | 2 | Cancellation, trigonometric identities, one-sided absolute values, sequential limits at infinity, elementary squeeze |
| | 3 | Radical conjugation, oscillatory squeeze, first-order equivalents, simple continuity joins, horizontal asymptotes and single discontinuities |
| | 4 | Transcendental equivalents, exponential essential limits, directional lines, poles, coupled and free continuity parameters, exact monotone roots |
| | 5 | Logarithmic treatment of variable powers, radical-domain asymptotes, oscillatory and multiple discontinuities, certified root brackets |

## Exact answer policy

Limits accept a real exact expression, `inf`, `-inf`, or `does_not_exist`.
Use `exp(k)` for large integer exponents that exceed the grammar's power
bound. Bounds and tails use labelled tuples with a category and the requested
values. The bounds requested are either specified by the displayed method or
are sharp. Discontinuity tuples identify locations, one-sided limits and
classifications. Asymptote tuples pair an exact set of vertical locations with
formulas for the left and right lines. Continuity joins accept exact parameter
values and a real set for a free parameter. Root tasks that request a
certificate accept the rational midpoint and half-width of the specified
bisection.

The existing computational answer grammar handles these contracts. Solutions
and plots are rendered from the same deterministic draw and kept in the
private catalogue. Public issuance, history, code previews and anonymous
shares carry the question and public input shape. The existing authorized
reveal and worksheet paths use the matching private solution fields.

## Independent worked samples

These checks use the parameter triple (5,4,2), drawn from seed 123.

- Factorial tail, `SLAC-1-0000000000000123-46`. The terms are
  \(4\cdot7^n/(n+2)!\). The ratio of consecutive terms is \(7/(n+3)\).
  Equality occurs at \(n=4\), so strict decrease starts at \(n=5\).
- Floor ratio, `SLAK-1-0000000000000123-52`. Divide the numerator and
  denominator by \(n\). Each floor changes its argument by less than one, so
  the quotient tends to \(\sqrt6/(4\sqrt3)=\sqrt2/4\).
- Two discontinuities, `FLBG-1-0000000000000123-82`. On the punctured domain
  the quotient reduces to \(2/(x+5)\). Its pole at \(-5\) has limits
  \(-\infty,+\infty\). At \(4\) the common limit is \(2/9\) and the assigned
  value is zero, giving a removable discontinuity.
- Cubic certificate, `FLAX-1-0000000000000123-07`. In the shifted variable
  \(t=x-2\), the residual \(t^3+5t-5\) is strictly increasing. After five
  bisections the endpoints in \(t\) are \(3/4,15/16\). Their residuals are
  \(-53/64,2095/4096\), so the midpoint and error bound in \(x\) are
  \(91/32,3/32\).
- Exponential pole, `FLBJ-1-0000000000000123-95`. The denominator
  \(6^x-36\) has its unique zero at \(x=2\), and the numerator is nonzero
  there. At the left end \(6^x\) tends to zero, giving the line \(y=0\).
  At the right end divide by \(6^x\), giving \(y=4\).

Finite algebraic limits and squeeze bounds are explained by exact derivations.
Plots accompany geometric outcomes such as one-sided jumps, discontinuities,
asymptotes, joins and root brackets. A root plot shows the computed bracket
separately from the residual curve.

## Pending source work

The source index lists the remaining numbered and exam references individually.
They include periodic poles, additional radical and trigonometric limits,
product and reciprocal power forms, and mixed exam contracts. A shared answer
shape is insufficient evidence of coverage.
