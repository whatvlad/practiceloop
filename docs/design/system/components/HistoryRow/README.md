History rows list every generated problem with: the problem (KaTeX), topic, difficulty, creation date, the attempt result, and whether the answer or the solution was revealed. Clicking a row reopens that problem in the practice view.

The consumer provides problem LaTeX, topic name, difficulty, a timestamp, the latest attempt result (`correct`, `incorrect`, or none) and the two reveal flags. Reveal flags render as a small `ink-subtle` line under the result ("Answer revealed", "Solution viewed").

- Result uses icon + word: check/Correct (`correct`), cross/Incorrect (`incorrect`), dash/Not attempted (`ink-subtle`).
- Rows hover to `surface-hover`; the whole row is the link.
- Truncate long expressions with an ellipsis; never wrap them.
