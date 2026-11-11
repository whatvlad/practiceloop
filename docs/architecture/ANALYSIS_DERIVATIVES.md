# Analysis I differential calculus (#237)

#237 extends Differential calculus with new immutable generator versions named
`analysis1-derivatives-*`. They share the deterministic three-parameter provider
of the [sequence and continuity expansion](ANALYSIS_LIMITS.md): each version
draws integers \(a,b,c\in[1,5]\), declares a permanent prefix and adds itself to
one level of the existing topic. Earlier versions, codes and mixed-practice
weights are unchanged. Learner proof and sketch components stay deferred to
#244.

## Derivatives, domains and tangents (#260)

Prefixes `DVAA` to `DVAZ` and `DVBA` to `DVBK` cover every computational
reference of AM1/40 to AM1/43 and the exam forms of those families.

| Reference | Version | Generated form and answer |
|---|---|---|
| AM1/40/a | `definition-power` | \(ax^{k}+cx\), derivative from the binomial difference quotient |
| AM1/40/b | `definition-reciprocal` | \(a/(x-b)\) on \(x\ne b\) |
| AM1/40/c | `definition-root` | \(a\sqrt{x+c}\) on \(x>-c\), conjugate quotient |
| AM1/40/d | `definition-sine` | \(a\sin bx\), sum-to-product quotient |
| AM1/41/a | `trig-sum` | \(a\sin x+b\cot x\): derivative and excluded points \(k\pi\) |
| AM1/41/b | `exponential-quadratic` | \(e^{ax}(x^2+bx+c)\) on \(\mathbb R\) |
| AM1/41/c | `rational-quotient` | \((x^2+a)/(x-b)\) on \(\mathbb R\setminus\{b\}\) |
| AM1/41/d | `exponential-square` | \(e^{-ax}(bx+c)^2\) |
| AM1/41/e | `log-arctan-root` | \(\ln(x^2+a+1)\arctan(b\sqrt x)\) differentiable on \((0,\infty)\); arctan replaces the source tangent so the domain stays decidable |
| AM1/41/f | `exponential-arctan` | \(e^{a/x}\arctan(b-x)\) on \(x\ne0\) |
| AM1/41/g | `log-cosine` | \(\ln(a\cos^2x+b)\) |
| AM1/41/h | `root-arccos` | \(a\sqrt{\arccos(x^2/c^2)}\) on \((-c,c)\) |
| AM1/41/i | `constant-over-power` | \(\sqrt a/(x^2+b)^c\) |
| AM1/41/j | `exponential-trig-powers` | \((a+1)^{\sin^2x}/(b+1)^{\cos^2x}\) |
| AM1/41/k | `power-of-exponential` | \((e^{-ax}+b)^{c+1}\) |
| AM1/41/l | `variable-power` | \((\sin ax)^{bx}\) on \((0,\pi/a)\), logarithmic differentiation |
| AM1/41/m | `inverse-trig-constant` | \((a(\arcsin\frac xc+\arccos\frac xc)+b)^2\): \(f'=0\) on \((-c,c)\) |
| AM1/41/n | `logarithm-constant` | \(\ln ax+\ln(b/x)+cx\): \(f'=c\) on \((0,\infty)\) |
| AM1/41/o | `log-constant-quotient` | \(\ln N/(x^2+c)\) with a constant numerator |
| AM1/41/p | `constant-coefficients` | \(e^a\sin bx+\sqrt\pi\cos cx\) |
| AM1/42/a | `tangent-arctan` | \(a\arctan(x/b)\) at \(x_0=b\) |
| AM1/42/b | `tangent-logarithm` | \(\ln(x^2+b)\) at \(x_0=c-3\) |
| AM1/42/c | `tangent-tangent-square` | \(a\tan^2bx\) at \(\pi/(4b)\) |
| AM1/42/d | `tangent-root-exponential` | \(\sqrt{(a+1)^x+c}\) at \(x_0=b\) |
| AM1/42/e | `tangent-rational` | \(ax/(b+x^2)\) at \(\sqrt c\) |
| AM1/42/f | `tangent-exponential-level` | \(e^{a+b/x}\) at the point with ordinate \(1\) |
| AM1/43/a | `tangent-parallel-quartic` | \(x^4-ax+b\) parallel to a given line |
| AM1/43/b | `tangent-angle-root` | \(a\sqrt x\) at angle \(\pi/4\) or \(\pi/3\) |
| AM1/43/c | `tangent-perpendicular-xlogx` | \(x\ln x\) perpendicular to \(x+my-c=0\) |
| AM1/43/d | `tangent-line-intersection` | \(ax\arctan(b/x)\) where it meets \(4y=a\pi x\) |
| AM1/43/e | `tangent-axis-intersection` | \(\sin ax-\cos bx+c\) at the \(y\)-axis |
| exam first/A/3 | `tangent-arctan-quotient` | \(a\arctan x/x\) at \(\sqrt3\), \(1\) or \(1/\sqrt3\) |
| exam first/B/2 | `root-exponential-domain` | \(e^{a\sqrt{2bx-x^2}}\) differentiable on \((0,2b)\) |
| exam first/C/3 | `tangent-horizontal` | \((x-b)e^{-ax}\) parallel to a horizontal line |
| exam first/D/1 | `arcsine-shifted-square` | \(a\arcsin(x^2-b-1)\) on two open intervals |
| exam first/D/4 | `tangent-exponential-cubic` | \(e^{x^3-a}\) at the point with a given ordinate |
| exam main/C/4 | `tangent-pair-perpendicular` | \(ax/(1+x^2)\): both tangents perpendicular to a line |

## Answer policy

A derivative is a formula in \(x\) checked as an identity on the stated
domain (`DomainFormulaAnswer`); where the task asks for it, the domain is a
separate real-set component, or a period and base set of excluded points.
Tangents give the contact point coordinates that are not stated and the line
as a formula in \(x\). The checker now decides continuity on a stated interval
when the complement over \(\mathbb R\) is a periodic set it cannot simplify
(for example \(\cot x\) on \((0,\pi)\)); the answer is unchanged otherwise.
Before its symbolic steps it now evaluates the difference between the entered
and the expected formula at a few rational points inside the domain, at 30
digits. A clearly nonzero value certifies a wrong answer at once; equality is
still only ever accepted symbolically. Without this, a wrong constant answer to
a trigonometric derivative was either undecided or took over a minute and
exceeded the math worker's limits.

## Verification

`backend/tests/test_engine_derivatives.py` rewrites every displayed function for
mpmath and compares the generated derivative at sample points of its domain
with 40-digit numerical differentiation. Tangent contact points are found
independently (by root finding where the task fixes them by a condition), and
each line is compared with \(f(x_0)+f'(x_0)(x-x_0)\). The same test parses and
checks the exact answer and renders every distinct variant; goldens and
worker tests cover replay.

## Differentials, L'Hopital limits and differentiability joins (#261)

Prefixes `DVBL` to `DVBZ` and `DVCA` to `DVCI` cover AM1/44, AM1/45, the
differentiability-parameter exam family and the exam L'Hopital forms. Two exam
references repeat a numbered task exactly (second/A/1 is AM1/45/c, main/C/6 is
AM1/45/l), so they name the same version.

| Reference | Version | Generated form and answer |
|---|---|---|
| AM1/44/a | `error-triangle-area` | area \(\tfrac12b^2\sin\alpha\), error \(\tfrac12b^2\cos\alpha\,\Delta\alpha\) |
| AM1/44/b | `error-sphere-volume` | \(V=\pi d^3/6\), error \(\tfrac\pi2d^2\Delta d\) |
| AM1/44/c | `error-fall-depth` | \(h=gt^2/2\), error \(gt\Delta t\) |
| AM1/44/d | `error-average-speed` | \(v=s/t\), error \(s\Delta t/t^2\) |
| AM1/45/a | `log-exponential-growth` | \(\ln((a+1)^x+b)/(cx)\to\ln(a+1)/c\) |
| AM1/45/b | `log-sine-ratio` | \(\ln\sin\frac{\pi x}{2a}/(b\ln\frac xa)\to0\) at \(a\) |
| AM1/45/c, exam second/A/1 | `arctan-difference` | \((ax-\arctan ax)/x^k\): \(0\) or \(a^3/3\) |
| AM1/45/d | `double-root-quotient` | \((x^{2n}-2nx+2n-1)/(x^n-nx+n-1)\to2(2n-1)/(n-1)\) |
| AM1/45/e | `log-cosine-ratio` | \(\ln\cos ax/\ln\cos bx\to a^2/b^2\) |
| AM1/45/f | `root-arccot` | \(ax^p\operatorname{arccot}bx\): \(0\) for \(p=\tfrac12\), \(a/b\) for \(p=1\) |
| AM1/45/g | `power-log-zero` | \(ax^b\ln x\to0\) |
| AM1/45/h | `tangent-half-angle` | \(a(b\pi-x)\tan\frac{x}{2b}\to2ab\) |
| AM1/45/i | `cosine-difference` | \(\frac{a}{1-\cos x}-\frac{k}{x^2}\): \(a/6\) or \(\pm\infty\) |
| AM1/45/j | `cotangent-difference` | \(\frac ax-k\cot x\) as \(x\to0^-\): \(0\) or \(\pm\infty\) |
| AM1/45/k | `log-reciprocal-sum` | \(a(\frac1{\ln x}+\frac1{1-x})\to a/2\) |
| AM1/45/l, exam main/C/6 | `log-power-zero` | \((-a\ln x)^{bx}\to1\) |
| AM1/45/m | `arctan-power` | \((\frac2\pi\arctan ax)^{bx}\to e^{-2b/(a\pi)}\) |
| AM1/45/n | `log-exponent-power` | \((1+ax)^{b\ln x}\to1\) |
| AM1/45/o | `tangent-cosine-power` | \((a\tan x)^{b\cos x}\to1\) at \(\pi/2^-\) |
| exam second/D/2 | `exponential-cosh` | \((e^{ax}+e^{-ax}-2)/(bx^2)\to a^2/b\) |
| exam main/A/5 | `one-minus-power` | \((a(1-x))^{\sin b\pi x}\to1\) at \(1^-\) |
| exam resit/B/5 | `tangent-log` | \(\tan(ax)\ln x\to0\) |
| exam resit/D/1 | `log-tangent-product` | \(ax\ln\tan bx\to0\) |
| exam main/A/6 | `differentiable-join` | \(e^{ax}+bx\) and \(x^2+px+q\): \(q=1\), \(p=a+b\) |

The error tests compare each answer with half the change of the stated
quantity over a small symmetric step, and the limits with 50-digit values next
to the limit point.

## Monotonicity, extrema and optimization (#262)

Prefixes `DVCJ` to `DVCZ` and `DVDA` to `DVDW` cover AM1/46 to AM1/49 and the
exam forms of those families.

Monotonicity answers are two real sets: the union of the open intervals of
strict increase and of strict decrease, with `{}` for none. Local extrema are
four finite sets: minimum points, minimum values, maximum points, maximum
values. Global extrema give the least and the greatest value. Optimization
tasks give the requested dimensions or quantity.

| Reference | Version | Generated form |
|---|---|---|
| AM1/46/a | `monotone-cubic` | cubic with \(f'=3(x-p)(x-q)\) |
| AM1/46/b | `monotone-trig-difference` | \(a(\sin bx-\cos bx)\) on \([0,2\pi/b]\) |
| AM1/46/c | `monotone-linear-reciprocal` | \(ax+b/x\) |
| AM1/46/d | `monotone-cubic-over-quadratic` | \(x^3/(c-x^2)\) |
| AM1/46/e | `monotone-root-quotient` | \(\sqrt{x^2-c^2}/(ax)\) |
| AM1/46/f | `monotone-exponential-product` | \((x-b)e^{-ax}\) |
| AM1/46/g | `monotone-log-square` | \(x\ln^2(x/b)\) |
| AM1/46/h | `monotone-log-quotient` | \(ax/\ln(x/b)\) |
| AM1/46/i | `monotone-exponential-difference` | \(c\,A^{x+1}-A^{2x}\) |
| exam second/B/1 | `monotone-reciprocal-log` | \(a/x+b\ln x\) |
| exam main/B/5 | `monotone-power-log` | \(ax^k\ln x\) |
| AM1/47/a | `extrema-cubic` | \(x^3-ax^2+c\) |
| AM1/47/b | `extrema-linear-reciprocal` | \(ax+b/x\) |
| AM1/47/c | `extrema-exponential-quotient` | \(A^x/(bx)\) |
| AM1/47/d | `extrema-shifted-exponential` | \((x+b)e^{-ax}\) |
| AM1/47/e | `extrema-rational` | \((x+b)/(x^2+1)\) |
| AM1/47/f | `extrema-absolute-quadratic` | \(|(x-p)(x-q)|\): corner minima |
| AM1/47/g | `extrema-x-log` | \(ax\ln(x/b)\) |
| AM1/47/h | `extrema-root-cubic` | \(a\sqrt{3c^2x-x^3}\): minima at the closed domain ends |
| AM1/47/i | `extrema-arctan-log` | \(a\arctan x-b\ln(1+x^2)\) |
| exam second/C/1 | `extrema-none` | \(a(\arctan x-x)-bx^3\): strictly decreasing, no extrema |
| exam main/C/2 | `extrema-exponential-shift` | \((x-b)e^{ax}\) |
| AM1/48/a | `global-cubic` | cubic on a closed interval |
| AM1/48/b | `global-reciprocal-quadratic` | \(1/((x-b)^2+c)\) |
| AM1/48/c | `global-root-difference` | \(\sqrt{a+x}-\sqrt{b-x}\) on its natural domain |
| AM1/48/d | `global-absolute-exponential` | \((x-k)^2e^{|x|}\), not differentiable at \(0\) |
| AM1/48/e | `global-absolute-parabola` | \(1-|k^2-x^2|\) |
| AM1/48/f | `global-sine-cubic` | \(\sin^3x-m\sin x\) via \(u=\sin x\) |
| AM1/48/g | `global-semicircle-root` | \(a\sqrt{c^2-(x-b)^2}\) |
| AM1/48/h | `global-cosine-quotient` | \(\cos x/(p+q\sin x)\) on \(\mathbb R\) |
| exam second/A/2 | `global-rational-interval` | \(ax/(x^2-cx+c^2)\) on \([0,2c]\) |
| exam main/A/4 | `global-root-product` | \(x\sqrt{r^2-x^2}\) on \([-3a,4a]\) |
| AM1/49/a | `fenced-plots` | three plots, least total fence |
| AM1/49/b | `pipeline` | sea and land pipe, cost ratio \(2\) or \(3\) |
| AM1/49/c | `container` | square-based box of least cost |
| AM1/49/d | `incircle-triangle` | isosceles triangle of fixed area, largest incircle |
| AM1/49/e | `parabola-rectangle` | rectangle under \(a(k^2-x^2)\) |
| exam second/B/2 | `semicircle-rectangle` | largest rectangle in a half-disc |
| exam resit/A/5 | `semicircle-waste` | material lost cutting that rectangle |
| exam resit/C/5 | `circle-square` | least-waste rectangle from a disc |

`backend/tests/test_engine_extrema.py` checks every variant against numerical
scans of the stated function: the sign of difference quotients on a grid for
monotonicity, grid local extrema (plus the closed domain ends) for local
extrema, a refined dense grid for global values, and a grid plus golden-section
search of the stated objective for optimization.

## Convexity and polynomial reconstruction (#263)

Prefixes `DVDX` to `DVDZ` and `DVEA` to `DVEM` cover AM1/69, AM1/51 and the
exam forms of the convexity and monotonicity-convexity families. Exam
second/D/1 repeats AM1/69/i and names the same version.

Convexity answers are three real sets: the union of open intervals of
convexity, of concavity, and the finite set of inflection abscissas. The
monotonicity-convexity exam tasks ask for one real set where both conditions
hold. Reconstructed polynomials are formulas in \(x\); the leading coefficient
is stated so the lowest-degree polynomial is unique.

| Reference | Version | Generated form |
|---|---|---|
| AM1/69/a | `convex-cubic` | \(ax(x-b)(x-b-c)\) |
| AM1/69/b | `convex-exponential-product` | \((x-b)e^{-ax}\) |
| AM1/69/c | `convex-cubic-quotient` | \(x^3/(x^2+3c^2)\): three inflections |
| AM1/69/d | `convex-log-quadratic` | \(a\ln(c^2+x^2)\) |
| AM1/69/e | `convex-reciprocal` | \(a/(c^2-x^2)\): no inflection, the sign changes at poles |
| AM1/69/f | `convex-log-absolute` | \(x-\frac b3x^3-2bk^3\ln|x|\) |
| AM1/69/g | `convex-trig` | \(a(\sin bx+\frac18\sin2bx)\) on one period |
| AM1/69/h | `convex-exponential-arctan` | \(e^{a\arctan x}\) |
| AM1/69/i, exam second/D/1 | `convex-log-root` | \(a\ln(x/b)/\sqrt x\) |
| exam main/D/2 | `convex-reversed-exponential` | \((c-x)e^{ax}\) |
| exam resit/A/3 | `increasing-convex-quadratic-exponential` | \((x^2+2x-c)e^{-x}\) |
| exam resit/B/3 | `increasing-convex-root-log` | \(a\sqrt x\ln(x/b)\) |
| exam resit/C/3 | `decreasing-concave-quadratic-exponential` | \((x^2-6x+c)e^x\) |
| exam resit/D/4 | `increasing-concave-arccot` | \(\frac{x^3}3+c^2\operatorname{arccot}\frac1x\) |
| AM1/51/a | `polynomial-extrema` | cubic with given leading coefficient, minimum, maximum and \(p(0)\) |
| AM1/51/b | `polynomial-inflection` | cubic with given leading coefficient through an inflection with value and slope |

Exam distinction/single/3 (a polynomial with prescribed extrema and a single
inflection, without a degree) is recorded as deferred in the source index: the
conditions admit infinitely many polynomials and need a property-checking
answer, which belongs to #244.

`backend/tests/test_engine_convexity.py` compares the answers with the sign of
numerical second (and first) differences of the stated function on a grid, with
sign changes of \(f''\) inside the domain, and checks the polynomial conditions
exactly.

## Taylor formulas, error bounds and certified approximations (#264)

Prefixes `DVEN` to `DVEZ` and `DVFA` to `DVFD` cover AM1/70 to AM1/73 and exam
second/C/2.

A Taylor or Maclaurin task states the order \(n\) and asks for \(T_{n-1}(x)\)
and \(f^{(n)}(x)\); the remainder is then \(f^{(n)}(\xi)(x-x_0)^n/n!\). Hyperbolic
derivatives are entered with `exp`. An error-bound task fixes the method
(\(\max|f^{(n)}|\cdot|x|^n/n!\) over the stated interval), so the certified bound is a
single exact number. An approximation task asks for the least order \(n\) whose
Lagrange bound meets the accuracy, and the exact value of \(T_{n-1}\) at the point.

| Reference | Version | Generated form |
|---|---|---|
| AM1/70/a | `taylor-cubic` | \(ax^3+bx\) at \(-c\), \(n=4\) (remainder zero) |
| AM1/70/b | `taylor-reciprocal-power` | \(x^{-k}\) at \(b\), \(n=2\) |
| AM1/70/c | `taylor-sine-at-pi` | \(\sin bx\) at \(\pi\), \(n=3\) |
| AM1/70/d | `taylor-exponential` | \(e^{-ax}\) at \(0\), \(n=3\) to \(5\) |
| AM1/71/a | `maclaurin-sine` | \(\sin(x/m)\) |
| AM1/71/b | `maclaurin-cosh` | \(\cosh ax\) |
| AM1/71/c | `maclaurin-cosine` | \(\cos ax\) |
| AM1/71/d | `maclaurin-exponential-product` | \(x/e^{ax}\) |
| AM1/72/a | `error-tangent` | \(\tan x\approx x\), \(|x|\le\pi/(6(b+1))\), \(n=3\) |
| AM1/72/b | `error-cosine-square` | \(\cos^2x\approx1-x^2\), \(n=4\) |
| AM1/72/c | `error-square-root` | \(\sqrt{1+x}\) to second order, \(n=3\) |
| AM1/72/d | `error-logarithm` | \(\ln(1-x)\) to third order, \(n=4\) |
| exam second/C/2 | `error-inverse-root` | \(1/\sqrt{x+1}\) to second order, \(n=3\) |
| AM1/73/a | `approximate-reciprocal-e` | \(e^{-1/a}\) |
| AM1/73/b | `approximate-cube-root` | \(\sqrt[3]{1-a/1000}\) |
| AM1/73/c | `approximate-logarithm` | \(\ln(1+a/20)\) |
| AM1/73/d | `approximate-sine` | \(\sin(a/10)\) |

`backend/tests/test_engine_taylor.py` compares the polynomials with
`mpmath.taylor`, the derivatives with numerical differentiation, the bounds with
a sampled maximum of \(|f^{(n)}|\), and finds the least order of each
approximation by brute force, also checking the true error.
