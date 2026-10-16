Topic selection for the first release is one category, Calculus → Integration, with five topics: Basic integrals, Substitution, Integration by parts, Rational functions, Trigonometric integrals.

The consumer provides the topic list and the selected slug; exactly one chip has `aria-pressed="true"`. The selected chip fills with `action` and carries a check icon so selection never relies on colour contrast alone.

- Chips are pills (`radius-pill`), 40px tall, unselected border `control-border`.
- Wrap to multiple rows; never scroll horizontally.
- When more categories arrive, group chips under a `label` heading per category.
