"""Domains, gradients, differentials and constrained optimization over R2/R3."""

from functools import cache

import sympy as sp

from app.engine.blocks.analysis_two import AnalysisTwoData, AnalysisTwoForm, T, X, Y, Z, finish


@cache
def evaluate(kind: str, form: AnalysisTwoForm) -> AnalysisTwoData:
    a, b, c = map(sp.Integer, (form.a, form.b, form.c))
    details: tuple[str, ...]
    if kind in {"multivariable-domain-two", "multivariable-domain-three"}:
        three = kind == "multivariable-domain-three"
        radial = a**2 - X**2 - Y**2 - (Z**2 if three else 0)
        function = sp.log(radial) if three else sp.sqrt(radial)
        expected = a
        radius = sp.Symbol("r", nonnegative=True)
        proof = sp.solve(a**2 - radius**2, radius)[0]
        dimension = "3" if three else "2"
        given = "(x,y,z)" if three else "(x,y)"
        prompt = (
            rf"Find the radius of the real domain in \(\mathbb R^{dimension}\) "
            rf"of \(f{given}={sp.latex(function)}\)."
        )
        norm = "x^2+y^2+z^2" if three else "x^2+y^2"
        relation = "<" if three else r"\leq"
        details = (
            rf"{sp.latex(radial)}{'>0' if three else r'\geq0'}",
            rf"D=\{{{given}\in\mathbb R^{dimension}:{norm}{relation}{a**2}\}}",
        )
    elif kind in {"multivariable-value-two", "multivariable-value-three"}:
        three = kind == "multivariable-value-three"
        function = a * X + b * Y**2 + c * Z**3 if three else a * X**2 + b * X * Y + c * Y**2
        point = {X: b, Y: c, Z: a} if three else {X: b, Y: c}
        expected = a * b + b * c**2 + c * a**3 if three else a * b**2 + b**2 * c + c**3
        proof = function.subs(point)
        args = "x,y,z" if three else "x,y"
        coordinates = f"{b},{c},{a}" if three else f"{b},{c}"
        prompt = (
            rf"For \(f({args})={sp.latex(function)}\) on all real coordinates, "
            rf"find \(f({coordinates})\)."
        )
        details = (rf"({args})=({coordinates})", rf"f({coordinates})={sp.latex(proof)}")
    elif kind == "multivariable-gradient-two":
        function = a * X**2 + b * X * Y + c * Y**2
        gradient = sp.Matrix([sp.diff(function, v) for v in (X, Y)])
        at = gradient.subs({X: b, Y: c})
        expected = sp.sqrt((2 * a * b + b * c) ** 2 + (b * b + 2 * c * c) ** 2)
        proof = sp.sqrt(at.dot(at))
        prompt = (
            rf"For \(f(x,y)={sp.latex(function)}\) on \(\mathbb R^2\), "
            rf"find \(\|\nabla f({b},{c})\|\)."
        )
        details = (
            rf"\nabla f={sp.latex(gradient)}",
            rf"\nabla f({b},{c})={sp.latex(at)}",
            r"\|\nabla f\|=\sqrt{f_x^2+f_y^2}",
        )
    elif kind == "multivariable-directional":
        i, j, length = ((3, 4, 5), (5, 12, 13), (8, 15, 17))[form.b % 3]
        ux, uy = sp.Rational(i, length), sp.Rational(j, length)
        if ux**2 + uy**2 != 1:
            raise ValueError("Direction must have unit length")
        function = a * X**2 + b * Y**2 + c * X * Y
        expected = ux * (2 * a + c) + uy * (2 * b + c)
        proof = sp.diff(function.subs({X: 1 + T * ux, Y: 1 + T * uy}), T).subs(T, 0)
        prompt = (
            rf"For \(f(x,y)={sp.latex(function)}\), find its directional derivative "
            rf"at \((1,1)\) in the unit direction \(u=({sp.latex(ux)},{sp.latex(uy)})\)."
        )
        details = (
            rf"\|u\|^2={sp.latex(ux**2)}+{sp.latex(uy**2)}=1",
            rf"\nabla f(1,1)=({2 * a + c},{2 * b + c})",
            r"D_u f=\nabla f\cdot u",
        )
    elif kind == "multivariable-third-partial":
        function = a * X**3 * Y**2 + b * Y**3 + c * X
        third = sp.diff(function, X, 2, Y)
        if sp.simplify(third - sp.diff(function, Y, X, 2)) != 0:
            raise ValueError("Mixed third partials must agree for a polynomial")
        expected = 12 * a * b * c
        proof = third.subs({X: b, Y: c})
        prompt = (
            rf"For \(f(x,y)={sp.latex(function)}\), find "
            rf"\(f_{{xxy}}({b},{c})\)."
        )
        details = (
            rf"f_x={sp.latex(sp.diff(function, X))}",
            rf"f_{{xx}}={sp.latex(sp.diff(function, X, 2))}",
            rf"f_{{xxy}}=f_{{yxx}}={sp.latex(third)}",
        )
    elif kind in {"multivariable-differential-two", "multivariable-differential-three"}:
        three = kind == "multivariable-differential-three"
        variables = (X, Y, Z) if three else (X, Y)
        function = a * X * Y + b * Y * Z + c * X * Z if three else a * X**2 + b * X * Y + c * Y**2
        changes = (1 / a, 1 / b, 1 / c) if three else (1 / a, -1 / b)
        point = dict.fromkeys(variables, sp.Integer(1))
        gradient = [sp.diff(function, v).subs(point) for v in variables]
        expected = sum(g * d for g, d in zip(gradient, changes, strict=True))
        path = function.subs({v: 1 + T * d for v, d in zip(variables, changes, strict=True)})
        proof = sp.diff(path, T).subs(T, 0)
        args = "x,y,z" if three else "x,y"
        coords = "1,1,1" if three else "1,1"
        displacement = ",".join(sp.latex(d) for d in changes)
        prompt = (
            rf"Find the total differential \(df\) of \(f({args})={sp.latex(function)}\) "
            rf"at \(({coords})\) for \((d{args.replace(',', ',d')})=({displacement})\)."
        )
        formula = "+".join(
            f"({sp.latex(g)})({sp.latex(d)})" for g, d in zip(gradient, changes, strict=True)
        )
        details = (
            rf"\nabla f({coords})=({','.join(sp.latex(g) for g in gradient)})",
            rf"df=\nabla f\cdot d\mathbf x={formula}",
        )
    elif kind == "multivariable-gradient-three":
        function = a * X**2 + b * Y**2 + c * Z**2
        gradient = sp.Matrix([sp.diff(function, v) for v in (X, Y, Z)])
        at = gradient.subs({X: 1, Y: 1, Z: 1})
        expected = 2 * sp.sqrt(a * a + b * b + c * c)
        proof = sp.sqrt(at.dot(at))
        prompt = (
            rf"For \(f(x,y,z)={sp.latex(function)}\), find "
            r"\(\|\nabla f(1,1,1)\|\)."
        )
        details = (
            rf"\nabla f={sp.latex(gradient)}",
            rf"\nabla f(1,1,1)={sp.latex(at)}",
            r"\|\nabla f\|=\sqrt{f_x^2+f_y^2+f_z^2}",
        )
    elif kind == "multivariable-local-minimum":
        function = a * (X - b) ** 2 + c * (Y - a) ** 2 + b
        hessian = sp.hessian(function, (X, Y))
        if hessian[0, 0] <= 0 or hessian.det() <= 0:
            raise ValueError("Minimum Hessian must be positive definite")
        expected = b
        proof = function.subs({X: b, Y: a})
        prompt = (
            rf"Find the local minimum value of \(f(x,y)={sp.latex(function)}\) "
            r"on \(\mathbb R^2\)."
        )
        details = (
            rf"\nabla f=0\iff(x,y)=({b},{a})",
            rf"H={sp.latex(hessian)}",
            rf"f(x,y)-{b}={sp.latex(function - b)}\geq0",
        )
    elif kind == "multivariable-classify":
        sx, sy = ((1, 1), (-1, -1), (1, -1))[form.b % 3]
        function = sx * a * X**2 + sy * c * Y**2 + b
        hessian = sp.hessian(function, (X, Y))
        expected = 0 if sx * sy < 0 else (1 if sx > 0 else 2)
        proof = 0 if hessian.det() < 0 else (1 if hessian[0, 0] > 0 else 2)
        prompt = (
            rf"Classify \((0,0)\) for \(f(x,y)={sp.latex(function)}\): "
            "enter 1 for a local minimum, 2 for a local maximum, 0 for a saddle."
        )
        details = (
            r"\nabla f(0,0)=(0,0)",
            rf"H={sp.latex(hessian)},\quad\det H={sp.latex(hessian.det())}",
            rf"f_{{xx}}={sp.latex(hessian[0, 0])}",
        )
    elif kind == "multivariable-constrained":
        function = a * X**2 + b * Y**2
        stationary = b * c / (a + b)
        reduced = function.subs(Y, c - X)
        root = sp.solve(sp.diff(reduced, X), X)[0]
        expected = a * b * c**2 / (a + b)
        proof = reduced.subs(X, root)
        if sp.simplify(reduced - (a + b) * (X - stationary) ** 2 - expected) != 0:
            raise ValueError("Constrained global-minimum certificate failed")
        prompt = (
            rf"Use Lagrange multipliers to minimize \(f(x,y)={sp.latex(function)}\) "
            rf"subject to \(x+y={c}\). Enter the minimum value."
        )
        details = (
            rf"{2 * a}x=\lambda,\quad {2 * b}y=\lambda,\quad x+y={c}",
            rf"x={sp.latex(stationary)},\quad y={sp.latex(a * c / (a + b))}",
            rf"f(x,{c}-x)={a + b}(x-{sp.latex(stationary)})^2+{sp.latex(expected)}",
        )
    elif kind == "multivariable-box":
        volume = X * Y * (a - X - Y)
        stationary = sp.solve((sp.diff(volume, X), sp.diff(volume, Y)), (X, Y), dict=True)
        interior = [p for p in stationary if p[X] > 0 and p[Y] > 0 and p[X] + p[Y] < a]
        if len(interior) != 1 or any(
            sp.simplify(v) != 0
            for v in (volume.subs(X, 0), volume.subs(Y, 0), volume.subs(Y, a - X))
        ):
            raise ValueError("Box must have one interior critical point and zero boundary volume")
        expected = a**3 / 27
        proof = volume.subs(interior[0])
        prompt = (
            rf"A box has positive edges \(x,y,z\) with \(x+y+z={a}\). "
            "Use constrained optimization to find its largest volume."
        )
        details = (
            r"V=xyz,\quad\nabla\log V=(1/x,1/y,1/z)",
            rf"1/x=1/y=1/z=\lambda\implies x=y=z={sp.latex(a / 3)}",
            r"V=0\text{ on the boundary; the unique interior critical point is the maximum}",
        )
    else:
        raise ValueError("Unknown multivariable form")
    return finish(prompt, expected, proof, details)
