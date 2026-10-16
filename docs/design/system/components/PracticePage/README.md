The `/practice` route. It is one ProblemCard in a narrow column with nothing else competing: no sidebar, no topic picker (change topic from the dashboard). The reveal order is user-controlled: Show Answer reveals only the final result, Show Solution reveals the full steps; both are independent.

States, in sequence: idle → result banner (Correct / Incorrect / Invalid expression) → optional reveals. After Correct, Generate Next Problem becomes the `primary` button.

The preview is interactive. Type `sin(x^2)+C` for Correct. Its checker is a stand-in: the real equivalence check runs on the backend and returns exactly one of the three states.
