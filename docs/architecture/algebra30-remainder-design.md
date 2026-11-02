# Algebra30: remainder modulo a quadratic

Issue #221; proposed next incremental slice. Exercise 63(b) asks for the
remainder of a large power modulo a product of two distinct linear factors.

## Approaches

1. Use the remainder theorem at the two roots and interpolate the linear
   remainder. This gives short exact steps and fits the existing expression
   answer type.
2. Expand the power and perform polynomial division. This produces much larger
   intermediate expressions and obscures the intended method.

The first approach is proposed. Generate bounded integer roots and exponents,
calculate both values exactly, and interpolate the unique polynomial of degree
less than two. The task must ask for the remainder, with solution steps showing
the two substitutions and interpolation. Use a new version and prefix so
existing problem codes remain stable; add it to polynomial division at an
appropriate level using the existing topic selection and answer checking.

Tests should cover the PDF example, deterministic replay, equivalent and wrong
answers, seed bounds, golden codes, and integration with the existing practice
and limited-worker checks. This slice does not claim coverage of exercise 63(c)
or of the rest of #221; those remain in development.
