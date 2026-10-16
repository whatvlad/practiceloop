Use `primary` for the single most important action in a view: Generate Problem on the dashboard, Check Answer on the practice page. Show Answer and Show Solution are `secondary`; low-stakes actions such as Sign out are `ghost` or `secondary` at `sm`.

The consumer provides the label (a verb, sentence case) and the click handler. A trailing arrow icon means "moves forward"; never put icons on every button.

- Fill is `action` with text `on-action`; hover is `action-hover`. Never use a status colour on a button.
- Radius is `radius-md`; use `pl-btn--pill` only for the sign-in call to action.
- Disabled buttons drop to 40% opacity and stay in the tab order only if they explain why.
- Focus ring is the global solid `focus` ring.

Do not put two `primary` buttons in one card.
