"""Check matrix answer serialization used by the end-to-end flow."""

import unittest

from e2e_local import answer_text

from app.engine.generators.matrix_full import MatrixAnswer
from app.math_input.structured import parse_answer_input


class MatrixAnswerTest(unittest.TestCase):
    def test_correct_and_wrong_matrix(self) -> None:
        answer = MatrixAnswer(((1, -2), (3, 4)))
        for wrong, expected in ((False, "correct"), (True, "incorrect")):
            text = answer_text(answer, wrong=wrong)
            tree = parse_answer_input(text, "tuple", contract=answer.contract)
            self.assertEqual(answer.check(tree), expected)


if __name__ == "__main__":
    unittest.main()
