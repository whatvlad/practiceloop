The problem card is the one lifted surface in the product (`shadow-lift`, `radius-xl`). It contains, in order: topic tag and difficulty, the instruction ("Calculate:"), the rendered expression, the answer field, Check Answer, Show Answer, Show Solution, and Generate Next Problem.

The consumer provides: topic name, difficulty (1–5), problem LaTeX (rendered with KaTeX, display mode), the controlled answer value, and handlers for each button. The correct answer and generator data never reach this component until Show Answer or Show Solution returns them from the backend.

- The expression sits in a `surface-raised` well in `math-problem` (44px), centred, scrolling horizontally if long.
- Check Answer is the only `primary` button and is full width; Show Answer and Show Solution are `secondary`; Generate Next Problem is `ghost` with an arrow, right-aligned.
- Results appear directly under the field as a ResultBanner, never in a modal.
- After a Correct result, promote Generate Next Problem to `primary` and demote Check Answer to disabled.
