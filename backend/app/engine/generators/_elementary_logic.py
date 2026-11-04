"""Generated arithmetic propositions, logical negations and quantified statements."""

from itertools import product

from app.engine.answers.computational import CategoryAnswer
from app.engine.answers.logic import LogicAnswer, truth
from app.engine.generators._elementary_common import Built, ElementaryParams, category, finish
from app.math_input.logic import parse_logic


def evaluate(template: str, p: ElementaryParams) -> Built:
    a, b, c, v = p.a, p.b, p.c, p.variant
    if template in {"proposition", "proposition-triangle"}:
        choices = ("true_proposition", "false_proposition", "not_a_proposition")
        if template == "proposition-triangle":
            if v % 3 == 0:
                sides = (a, a, a)
                value = True
            elif v % 3 == 1:
                sides = (3 * a, 4 * a, 5 * a)
                value = False
            else:
                sides = (a, b, a + b + c)
                value = False
            first, second, last = sorted(sides)
            statement = (
                f"Classify the statement: the lengths {sides[0]}, {sides[1]} and {sides[2]} "
                "form an acute triangle."
            )
            expected = choices[0] if value else choices[1]
            side_relation = ">" if first + second > last else r"\le"
            squares = first**2 + second**2
            angle_relation = ">" if squares > last**2 else "=" if squares == last**2 else "<"
            derivation = (
                rf"{first}+{second}{side_relation}{last};"
                rf"\quad {first**2}+{second**2}{angle_relation}{last**2}."
            )
        elif v % 3 == 0:
            statement = (
                f"Classify the open sentence \\(x+{a}={b}\\), where x has no assigned value."
            )
            expected = choices[2]
            derivation = r"x\text{ is free, so no fixed truth value is assigned.}"
        else:
            number, divisor = a * b + v % 2, a
            value = number % divisor == 0
            statement = f"Classify the statement: the integer {number} is divisible by {divisor}."
            expected = choices[0] if value else choices[1]
            derivation = rf"{number}={divisor}\cdot {number // divisor}+{number % divisor}"
        return finish(
            statement,
            CategoryAnswer(expected, choices),
            r"\text{A proposition has a definite truth value.}",
            derivation,
        )
    if template.startswith("logic-negation-"):
        atoms: tuple[str, ...]
        if template == "logic-negation-not":
            original, atoms = "!" * a + "p", ("p",)
        elif template == "logic-negation-equivalence":
            original = (
                f"{'!p' if v % 2 else 'p'}<->"
                f"({'!q' if v // 2 % 2 else 'q'}&{'!r' if c % 2 else 'r'})"
            )
            atoms = ("p", "q", "r")
        else:
            op = {"and": "&", "or": "|", "implication": "->", "equivalence": "<->", "xor": "^"}[
                template.removeprefix("logic-negation-")
            ]
            original = f"{'!p' if v % 2 else 'p'}{op}{'!q' if v // 2 % 2 else 'q'}"
            atoms = ("p", "q")
        model = parse_logic(original, atoms)
        answer = LogicAnswer(parse_logic(f"!({original})", atoms), atoms)
        rows = []
        for assignment in product((False, True), repeat=len(atoms)):
            value = truth(model, dict(zip(atoms, assignment, strict=True)))
            rows.append("&".join(str(int(v)) for v in (*assignment, value, not value)))
        header = "&".join(atoms) + r"&F&\neg F\\\hline"
        return finish(
            f"Write a formula equivalent to the negation of "
            f"\\({LogicAnswer(model, atoms).latex()}\\). "
            f"Atoms {', '.join(atoms)} are arbitrary propositions.",
            answer,
            r"\neg F\text{ reverses every truth-table value of }F.",
            r"\begin{array}{"
            + "c" * len(atoms)
            + "|cc}"
            + header
            + r"\\".join(rows)
            + r"\end{array}",
        )
    if template == "compound-truth":
        if v == 0:
            formula = (
                rf"\neg\big(x\mapsto (x-{a})^2\text{{ is strictly increasing on }}\mathbb{{R}}\big)"
            )
            return finish(
                f"Determine the truth of \\({formula}\\).",
                category(True),
                r"\text{Refute strict increase using two ordered inputs.}",
                rf"{a - 1}<{a},\quad f({a - 1})=1>0=f({a}).",
            )
        if v == 2:
            odd = bool(c % 2)
            expression = rf"{a}x^3-{b}x" if odd else rf"{a}x^3-{b}x+{c}"
            formula = (
                rf"\big(\sin({b}x)+{a}\text{{ is periodic}}\big)"
                rf"\land\big({expression}\text{{ is odd}}\big)"
            )
            return finish(
                f"Determine the truth of \\({formula}\\).",
                category(odd),
                r"\text{Check the period and the identity }g(-x)=-g(x).",
                rf"T=2\pi/{b},\quad g(-x)+g(x)={0 if odd else 2 * c}.",
            )
        ops = ("&", "|", "->", "<->", "^")
        op = ops[v % 5]
        left, right = a % 2 == 0, b % 2 == 0
        tree = parse_logic(f"p{op}q", ("p", "q"))
        formula = LogicAnswer(tree, ("p", "q")).latex()
        return finish(
            f"Let p mean that {a} is even and q mean that {b} is even. "
            f"Determine the truth of \\({formula}\\).",
            category(truth(tree, {"p": left, "q": right})),
            r"\text{Evaluate the atoms, then apply the stated logical connective.}",
            rf"p={int(left)},\quad q={int(right)},"
            rf"\quad {formula}={int(truth(tree, {'p': left, 'q': right}))}",
        )
    if template == "quantifier-order":
        # Quantification is over all reals; witnesses/counterexamples are explicit.
        if v % 2:
            formula = rf"\exists y\in\mathbb{{R}}\ \forall x\in\mathbb{{R}}:\ y=x+{a}"
            value = False
            proof = rf"x=0\Rightarrow y={a};\quad x=1\Rightarrow y={a + 1}."
        else:
            formula = rf"\forall x\in\mathbb{{R}}\ \exists y\in\mathbb{{R}}:\ y=x+{a}"
            value = True
            proof = rf"\text{{For each }}x,\quad y=x+{a}\in\mathbb{{R}}."
        return finish(
            f"Determine the truth of \\({formula}\\).",
            category(value),
            r"\text{Respect quantifier order; a universal witness cannot depend }"
            r"\text{on the later variable.}",
            proof,
        )
    if template == "quantifier-polynomial":
        existential = bool(v % 2)
        quantifier = r"\exists" if existential else r"\forall"
        formula = rf"{quantifier} x\in\mathbb{{R}}:\ (x-{a})^2>{b}"
        return finish(
            f"Determine the truth of \\({formula}\\).",
            category(existential),
            r"\text{Use an exact witness or counterexample over the whole real line.}",
            rf"x={a}:\ 0\le{b};\quad x={a + b + 1}:\ ({b + 1})^2>{b}.",
        )
    if template == "quantifier-cubic-witness":
        if v % 2:
            formula = rf"\exists y\in\mathbb{{R}}\ \forall x\in\mathbb{{R}}:\ x^2+{a}y^3+{b}=0"
            value = False
            calculation = rf"x=0\Rightarrow {a}y^3=-{b};\quad x=1\Rightarrow {a}y^3=-{b + 1}."
        else:
            formula = rf"\forall x\in\mathbb{{R}}\ \exists y\in\mathbb{{R}}:\ x^2+{a}y^3+{b}=0"
            value = True
            calculation = (
                rf"y=-\sqrt[3]{{(x^2+{b})/{a}}}\in\mathbb{{R}}"
                r"\text{ is an exact witness for every }x."
            )
        return finish(
            f"Determine the truth of \\({formula}\\).",
            category(value),
            r"\text{A real cube root exists for every real argument;}"
            r"\text{ quantifier order still matters.}",
            calculation,
        )
    if template == "quantifier-total-order":
        weak = not v % 2
        relation = r"\le" if weak else "<"
        formula = rf"\forall x,y\in\mathbb{{R}}:\ (y{relation}{a}x+{b})\lor(y>{a}x+{b})"
        calculation = (
            r"s\le t\ \lor\ s>t\text{ exhausts all pairs of reals.}"
            if weak
            else rf"y={a}x+{b}\text{{ makes both strict inequalities false.}}"
        )
        return finish(
            f"Determine the truth of \\({formula}\\).",
            category(weak),
            r"\text{Check equality as well as both strict-order cases.}",
            calculation,
        )
    if template == "quantifier-power":
        existential = not v % 2
        quantifier = r"\exists" if existential else r"\forall"
        formula = rf"{quantifier} x\in(0,\infty):\ x^x={a**a}"
        calculation = (
            rf"x={a}\text{{ is a witness; }}x={a + 1}\text{{ gives }}"
            rf"x^x={(a + 1) ** (a + 1)}\ne {a**a}."
        )
        return finish(
            f"Determine the truth of \\({formula}\\).",
            category(existential),
            r"x^x\text{ is defined and positive on the stated positive domain.}",
            calculation,
        )
    if template == "quantifier-trigonometric":
        prefix = (
            r"\exists x\in\mathbb{R}\ \exists y\in\mathbb{R}",
            r"\forall x\in\mathbb{R}\ \exists y\in\mathbb{R}",
            r"\exists y\in\mathbb{R}\ \forall x\in\mathbb{R}",
        )[v % 3]
        formula = prefix + rf":\ \sin({a}x)+\cos({a}x+y)=0"
        return finish(
            f"Determine the truth of \\({formula}\\).",
            category(True),
            r"\text{Find a single real phase that works for every }x.",
            rf"y=\pi/2+2\pi\cdot {b}\Rightarrow\cos({a}x+y)=-\sin({a}x).",
        )
    if template == "quantifier-product":
        target = 0 if v % 2 else c
        formula = rf"\exists y\in\mathbb{{R}}\ \forall x\in\mathbb{{R}}:\ (x-{a})(y-{b})={target}"
        calculation = (
            rf"y={b}\Rightarrow(x-{a})(y-{b})=0\text{{ for every }}x."
            if target == 0
            else rf"x={a}\Rightarrow0={target}\text{{ is impossible for every choice of }}y."
        )
        return finish(
            f"Determine the truth of \\({formula}\\).",
            category(target == 0),
            r"\text{A single constant witness must work for every real }x.",
            calculation,
        )
    raise ValueError(template)
