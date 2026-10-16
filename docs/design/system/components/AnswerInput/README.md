The answer field takes typed mathematical notation, not plain text matching. Set the value in `answer-input` (Geist Mono 20px) so characters such as `^`, `/` and `*` stay unambiguous.

The consumer provides the controlled value, an `id`/`label` pair, and the validity state from the backend: `is-correct`, `is-incorrect` or `is-invalid` change only the border, never the whole field. Always show a message alongside a coloured border.

- Label is a `label` style eyebrow above the field: "Your answer".
- Placeholder is an example in `ink-subtle`; the hint line lists accepted notation in `code` style.
- Border is `control-border`; focus uses the solid `focus` ring plus an `ink` border.
- Do not live-validate while typing; validate on Check Answer.
