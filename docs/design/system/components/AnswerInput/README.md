The answer field takes typed mathematical notation, not plain text matching. Set the value in `answer-input` (Geist Mono 20px) so characters such as `^`, `/` and `*` stay unambiguous.

The consumer provides the controlled value, an `id`/`label` pair, and the validity state from the backend: `is-correct`, `is-incorrect` or `is-invalid` change only the border, never the whole field. Always show a message alongside a coloured border.

- Label is a `label` style eyebrow above the field: "Your answer".
- Placeholder is an example in `ink-subtle`; the hint line lists accepted notation in `code` style.
- Border is `control-border`; focus uses the solid `focus` ring plus an `ink` border.
- Correctness is decided only on Check Answer. While typing, the `assist` mode (used on the practice card) shows a "Reads as" KaTeX preview of how the backend parser reads the answer and flags syntax mistakes in `invalid` text under the field, with a one-tap fix when the correction is unambiguous (`x(x+1)` → `x*(x+1)`). Unfinished input, such as an open bracket, is a muted note, not a mistake. Live flags never change the border.
- The math keypad under the field inserts accepted notation at the caret (`√` → `sqrt()`, `x²` → `^2`) and wraps a selection. Keys are 44px high for touch and keep focus in the field; More reveals the less common functions.
