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
