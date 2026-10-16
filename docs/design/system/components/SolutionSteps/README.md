Show Solution reveals the full step-by-step solution. Each step is a short plain-language lead ("Let", "Then", "Therefore") in `small`/`ink-muted` and one expression in `math-solution`.

The consumer provides an ordered array of `{ say, latex }` from the solution generator. The last step gets the `final` class: its number badge fills `action` and its row lifts to `surface-hover`.

- Steps are numbered in a mono badge (`radius-sm`), separated by `line` hairlines inside a `surface-raised` block.
- Reveal the block under the problem card with no animation beyond a 150ms fade; do not collapse previous results.
- Never show the solution before the user asks.
